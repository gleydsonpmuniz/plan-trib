# Pattern: Extração de PDF via LLM com Saída Estruturada

> **Purpose**: Extrair campos estruturados de PDFs heterogêneos (folha de pagamento, PGDAS-D) usando LLM (Gemini) com saída validada por Pydantic, robusto a variações de leiaute.
> **MCP Validated**: 2026-04-28

## When to Use

- PDFs com **leiaute padronizado mas não estruturado** (folha gerada por sistemas como Domínio, Sage; PGDAS-D oficial RFB)
- Necessidade de **schema rígido** na saída (Pydantic) para alimentar engine de cálculo
- **Múltiplos provedores** de PDF (não dá para hard-codear regex para cada sistema)
- Variações de versão/leiaute ao longo do tempo

## Implementation

```python
from __future__ import annotations
from decimal import Decimal
from datetime import date
import base64
from pathlib import Path
from pydantic import BaseModel, Field
from google import genai
from google.genai import types


# ─────────────────────── Schemas Pydantic ───────────────────────

class FolhaTotalizadores(BaseModel):
    """Resumo mensal de uma folha de pagamento."""
    competencia: date              # Mês/ano
    cnpj: str                      # 14 dígitos, sem máscara
    razao_social: str

    # Bases e valores INSS
    salario_contribuicao_empregados: Decimal
    base_total_inss: Decimal
    inss_segurados: Decimal
    inss_empresa: Decimal
    inss_rat: Decimal
    inss_terceiros: Decimal
    inss_total: Decimal

    # FGTS
    base_fgts: Decimal
    valor_fgts: Decimal

    # IRRF (competência de pagamento)
    base_irrf_mensal: Decimal
    valor_irrf_mensal: Decimal

    # Quantidades
    qtd_empregados: int
    qtd_contribuintes: int

    # Apuração tributos federais
    saldo_a_recolher_inss: Decimal


# ─────────────────────── Cliente Gemini ───────────────────────

client = genai.Client(api_key="...")  # via env var GOOGLE_API_KEY

def extract_folha(pdf_path: Path) -> FolhaTotalizadores:
    pdf_bytes = pdf_path.read_bytes()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            (
                "Extraia os totalizadores deste resumo de folha de pagamento. "
                "Use vírgula brasileira para decimais; converta para Decimal. "
                "CNPJ sem máscara (14 dígitos). Competência no formato AAAA-MM-01."
            ),
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FolhaTotalizadores,
            temperature=0.0,  # determinístico
        ),
    )
    return FolhaTotalizadores.model_validate_json(response.text)
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `model` | `gemini-2.5-flash` | Custo/latência baixos; `gemini-2.5-pro` para PDFs complexos |
| `temperature` | `0.0` | Sempre zero — extração não é criativa |
| `response_mime_type` | `"application/json"` | Garante JSON parseável |
| `response_schema` | classe Pydantic | Schema enforced pelo SDK |
| `mime_type` | `"application/pdf"` | Para PDFs nativos |

## Few-Shot Grounding (recomendado para precisão)

Quando o leiaute do PDF varia entre sistemas (ex.: Domínio × Sage), inclua 1–2 exemplos no prompt:

```python
EXAMPLES = [
    types.Part.from_bytes(data=Path("samples/folha_dominio.pdf").read_bytes(),
                          mime_type="application/pdf"),
    types.Part.from_text(text=FolhaTotalizadores(...).model_dump_json()),
    # depois o PDF a ser extraído
]
```

## Validação Pós-Extração

```python
def validate_extraction(extracted: FolhaTotalizadores) -> None:
    # Soma dos componentes deve bater com o total
    soma = (extracted.inss_segurados + extracted.inss_empresa
            + extracted.inss_rat + extracted.inss_terceiros)
    if abs(soma - extracted.inss_total) > Decimal("0.02"):
        raise ValueError(f"INSS total divergente: {soma} vs {extracted.inss_total}")

    # CNPJ deve ter 14 dígitos
    if len(extracted.cnpj) != 14 or not extracted.cnpj.isdigit():
        raise ValueError(f"CNPJ inválido: {extracted.cnpj}")
```

## Custo e Latência (referência)

| Modelo | Custo/PDF (~80KB) | Latência |
|--------|-------------------|----------|
| Gemini 2.5 Flash | ~US$ 0,001 | 2–5s |
| Gemini 2.5 Pro | ~US$ 0,01 | 5–15s |

Para um escritório com 100 empresas × 12 meses = 1200 extrações/ano = ~US$ 1,20/ano (Flash). Custo desprezível.

## Anti-Patterns

| Don't | Do |
|-------|-----|
| `temperature=0.7` para extração | `temperature=0.0` (determinístico) |
| `pdfplumber` + regex frágil | LLM com schema Pydantic |
| Validar só no Pydantic | Adicionar checks de consistência (soma de partes = total) |
| Usar `float` | Sempre `Decimal` |

## See Also

- [pgdas-d](../concepts/pgdas-d.md)
- KB Pydantic: `../../pydantic/concepts/structured-output.md`
- KB Gemini: `../../gemini/patterns/structured-output.md`
