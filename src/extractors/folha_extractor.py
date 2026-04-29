from datetime import date
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel

from src.extractors.base import extract_pdf

PROMPT = """Extraia os totalizadores deste resumo de folha de pagamento.
Use vírgula brasileira convertida para Decimal (ex.: "1.234,56" → 1234.56).
CNPJ sem máscara (apenas 14 dígitos).
Competência no formato YYYY-MM-01."""


class FolhaTotalizadores(BaseModel):
    competencia: date
    cnpj: str
    razao_social: str
    salario_contribuicao_empregados: Decimal = Decimal(0)
    base_total_inss: Decimal = Decimal(0)
    inss_segurados: Decimal = Decimal(0)
    inss_empresa: Decimal = Decimal(0)
    inss_rat: Decimal = Decimal(0)
    inss_terceiros: Decimal = Decimal(0)
    inss_total: Decimal = Decimal(0)
    base_fgts: Decimal = Decimal(0)
    valor_fgts: Decimal = Decimal(0)
    base_irrf_mensal: Decimal = Decimal(0)
    valor_irrf_mensal: Decimal = Decimal(0)
    folha_bruta: Decimal = Decimal(0)
    pro_labore: Decimal = Decimal(0)
    qtd_empregados: int = 0


async def extract_folha(pdf_path: Path) -> FolhaTotalizadores:
    result = await extract_pdf(pdf_path, FolhaTotalizadores, PROMPT)
    soma = (
        result.inss_segurados + result.inss_empresa + result.inss_rat + result.inss_terceiros
    )
    if result.inss_total > 0 and abs(soma - result.inss_total) > Decimal("0.05"):
        from src.extractors.base import LLMExtractionError

        raise LLMExtractionError(
            f"Soma INSS divergente: partes={soma}, total={result.inss_total}"
        )
    if len(result.cnpj) != 14 or not result.cnpj.isdigit():
        from src.extractors.base import LLMExtractionError

        raise LLMExtractionError(f"CNPJ inválido: {result.cnpj!r}")
    return result
