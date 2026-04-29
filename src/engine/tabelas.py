from decimal import Decimal
from functools import lru_cache
from pathlib import Path

import yaml

from src.config import settings


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=1)
def tabelas_simples() -> dict:
    """Carrega specs/tabelas-simples-anexos.yaml do KB."""
    raw = _load_yaml(settings.kb_dir / "specs" / "tabelas-simples-anexos.yaml")
    for anexo_key in ("anexo_I", "anexo_II", "anexo_III", "anexo_IV", "anexo_V"):
        for faixa in raw[anexo_key]["faixas"]:
            faixa["receita_min"] = Decimal(str(faixa["receita_min"]))
            faixa["receita_max"] = Decimal(str(faixa["receita_max"]))
            faixa["aliquota_nominal"] = Decimal(str(faixa["aliquota_nominal"]))
            faixa["parcela_deduzir"] = Decimal(str(faixa["parcela_deduzir"]))
    raw["fator_r"]["threshold"] = Decimal(str(raw["fator_r"]["threshold"]))
    raw["sublimites"]["federal"]["valor"] = Decimal(str(raw["sublimites"]["federal"]["valor"]))
    raw["sublimites"]["estadual_icms_iss"]["valor"] = Decimal(
        str(raw["sublimites"]["estadual_icms_iss"]["valor"])
    )
    return raw


@lru_cache(maxsize=1)
def tabelas_presuncao_lp() -> dict:
    """Carrega specs/presuncao-irpj-csll.yaml do KB."""
    raw = _load_yaml(settings.kb_dir / "specs" / "presuncao-irpj-csll.yaml")
    raw["adicional_irpj"]["aliquota"] = Decimal(str(raw["adicional_irpj"]["aliquota"]))
    raw["adicional_irpj"]["base_excedente_trimestral"] = Decimal(
        str(raw["adicional_irpj"]["base_excedente_trimestral"])
    )
    raw["aliquotas_base"]["irpj"] = Decimal(str(raw["aliquotas_base"]["irpj"]))
    raw["aliquotas_base"]["csll"] = Decimal(str(raw["aliquotas_base"]["csll"]))
    for item in raw["presuncao_irpj"]:
        item["percentual"] = Decimal(str(item["percentual"]))
    for item in raw["presuncao_csll"]:
        item["percentual"] = Decimal(str(item["percentual"]))
    raw["pis_cofins_cumulativo"]["pis"]["aliquota"] = Decimal(
        str(raw["pis_cofins_cumulativo"]["pis"]["aliquota"])
    )
    raw["pis_cofins_cumulativo"]["cofins"]["aliquota"] = Decimal(
        str(raw["pis_cofins_cumulativo"]["cofins"]["aliquota"])
    )
    return raw


def reload_tabelas() -> None:
    tabelas_simples.cache_clear()
    tabelas_presuncao_lp.cache_clear()
