from decimal import Decimal

from src.engine.inputs import DadosFiscaisCompetencia
from src.engine.outputs import ResultadoApuracao, Tributos
from src.engine.tabelas import tabelas_simples


def mapear_anexo(dados: DadosFiscaisCompetencia) -> str:
    """Mapeia atividade → Anexo. Heurística simples; refinar quando atividade textual disponível.

    Regras:
    - Receita predominante de revenda → I
    - Receita predominante de industrialização → II
    - Construção/vigilância (palavra-chave na atividade) → IV
    - Serviços com Fator R >= 28% → III; senão V
    """
    desc = (dados.atividade_descricao or "").lower()
    if any(k in desc for k in ("construção", "construcao", "vigilância", "vigilancia", "limpeza")):
        return "IV"
    if any(k in desc for k in ("industrializ", "indústria", "industria")):
        return "II"
    if any(k in desc for k in ("revenda", "comércio", "comercio")):
        return "I"

    receitas = {
        "I": dados.receita_revenda,
        "II": dados.receita_industrializacao,
        "servicos": dados.receita_servicos,
    }
    maior = max(receitas, key=lambda k: receitas[k])
    if maior == "I":
        return "I"
    if maior == "II":
        return "II"

    fator_r = calcular_fator_r(dados)
    threshold = tabelas_simples()["fator_r"]["threshold"]
    return "III" if fator_r >= threshold else "V"


def calcular_fator_r(dados: DadosFiscaisCompetencia) -> Decimal:
    if dados.receita_12m == 0:
        return Decimal(0)
    return (dados.folha_12m + dados.pro_labore_12m) / dados.receita_12m


def buscar_faixa(anexo: str, rbt12: Decimal) -> dict:
    tabelas = tabelas_simples()[f"anexo_{anexo}"]
    for faixa in tabelas["faixas"]:
        if faixa["receita_min"] <= rbt12 <= faixa["receita_max"]:
            return faixa
    return tabelas["faixas"][-1]


def aliquota_efetiva(rbt12: Decimal, faixa: dict) -> Decimal:
    if rbt12 == 0:
        return Decimal(0)
    return (rbt12 * faixa["aliquota_nominal"] - faixa["parcela_deduzir"]) / rbt12


def _distribuir_tributos(total: Decimal, anexo: str) -> Tributos:
    """Distribuição simplificada por Anexo. Para precisão completa, usar tabelas
    de repartição da LC 123/2006 — aqui usamos aproximação consistente."""
    if anexo == "I":
        return Tributos(
            irpj=total * Decimal("0.055"),
            csll=total * Decimal("0.035"),
            cofins=total * Decimal("0.1274"),
            pis=total * Decimal("0.0276"),
            inss_cpp=total * Decimal("0.42"),
            icms=total * Decimal("0.335"),
        )
    if anexo == "II":
        return Tributos(
            irpj=total * Decimal("0.055"),
            csll=total * Decimal("0.035"),
            cofins=total * Decimal("0.1151"),
            pis=total * Decimal("0.0249"),
            inss_cpp=total * Decimal("0.375"),
            icms=total * Decimal("0.32"),
            ipi=total * Decimal("0.075"),
        )
    if anexo == "III":
        return Tributos(
            irpj=total * Decimal("0.04"),
            csll=total * Decimal("0.035"),
            cofins=total * Decimal("0.1282"),
            pis=total * Decimal("0.0278"),
            inss_cpp=total * Decimal("0.435"),
            iss=total * Decimal("0.33"),
        )
    if anexo == "IV":
        return Tributos(
            irpj=total * Decimal("0.185"),
            csll=total * Decimal("0.15"),
            cofins=total * Decimal("0.1603"),
            pis=total * Decimal("0.0347"),
            iss=total * Decimal("0.47"),
        )
    return Tributos(
        irpj=total * Decimal("0.25"),
        csll=total * Decimal("0.15"),
        cofins=total * Decimal("0.1428"),
        pis=total * Decimal("0.0309"),
        inss_cpp=total * Decimal("0.2855"),
        iss=total * Decimal("0.1408"),
    )


class CalculadoraSimples:
    def apurar(self, dados: DadosFiscaisCompetencia) -> ResultadoApuracao:
        anexo = mapear_anexo(dados)
        fator_r = calcular_fator_r(dados)
        rbt12 = dados.receita_12m or dados.receita_bruta * 12
        faixa = buscar_faixa(anexo, rbt12)
        aliq_efetiva = aliquota_efetiva(rbt12, faixa)
        valor_total = dados.receita_bruta * aliq_efetiva
        tributos = _distribuir_tributos(valor_total, anexo)

        return ResultadoApuracao(
            regime="SIMPLES",
            competencia=dados.competencia,
            cnpj=dados.cnpj,
            tributos=tributos,
            receita_base=dados.receita_bruta,
            aliquota_efetiva=aliq_efetiva,
            detalhamento={
                "anexo": anexo,
                "rbt12": str(rbt12),
                "faixa": faixa["faixa"],
                "aliquota_nominal": str(faixa["aliquota_nominal"]),
                "parcela_deduzir": str(faixa["parcela_deduzir"]),
                "fator_r": str(fator_r),
            },
        )
