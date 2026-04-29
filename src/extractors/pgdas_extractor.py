from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from src.extractors.base import extract_pdf

PROMPT = """Extraia os campos do extrato PGDAS-D (Declaração Simples Nacional).

Para cada estabelecimento listado em "2.7 Informações da Declaração por Estabelecimento",
identifique a atividade textual e infira o Anexo aplicável:
- "Revenda de mercadorias..." → Anexo I
- "Venda de mercadorias industrializadas pelo contribuinte..." → Anexo II
- "Locação de bens móveis", serviços auxiliares → Anexo III
- "Construção", "Vigilância", "Limpeza" → Anexo IV
- Serviços profissionais (consultoria, advocacia) sem Fator R ≥ 28% → Anexo V

Receitas anteriores: dicionário {YYYY-MM: valor}.
Período de apuração no formato YYYY-MM-01."""


class AtividadeSimples(BaseModel):
    cnpj: str
    descricao: str
    anexo_inferido: Literal["I", "II", "III", "IV", "V"]
    receita_bruta: Decimal
    irpj: Decimal = Decimal(0)
    csll: Decimal = Decimal(0)
    cofins: Decimal = Decimal(0)
    pis: Decimal = Decimal(0)
    inss_cpp: Decimal = Decimal(0)
    icms: Decimal = Decimal(0)
    ipi: Decimal = Decimal(0)
    iss: Decimal = Decimal(0)
    total: Decimal = Decimal(0)


class PgdasExtraido(BaseModel):
    cnpj_matriz: str
    razao_social: str
    periodo_apuracao: date
    rpa: Decimal
    rbt12: Decimal
    rba: Decimal = Decimal(0)
    rbaa: Decimal = Decimal(0)
    fator_r: Decimal | None = None
    receitas_anteriores_mercado_interno: dict[str, Decimal] = Field(default_factory=dict)
    folha_anterior: dict[str, Decimal] = Field(default_factory=dict)
    estabelecimentos: list[AtividadeSimples] = Field(default_factory=list)
    total_debito_declarado: Decimal = Decimal(0)


async def extract_pgdas(pdf_path: Path) -> PgdasExtraido:
    result = await extract_pdf(pdf_path, PgdasExtraido, PROMPT)
    if len(result.cnpj_matriz) != 14 or not result.cnpj_matriz.isdigit():
        from src.extractors.base import LLMExtractionError

        raise LLMExtractionError(f"CNPJ inválido: {result.cnpj_matriz!r}")
    return result
