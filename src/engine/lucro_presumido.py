from decimal import Decimal

from src.engine.inputs import DadosFiscaisCompetencia
from src.engine.outputs import ResultadoApuracao, Tributos
from src.engine.tabelas import tabelas_presuncao_lp


def _percentuais_presuncao(dados: DadosFiscaisCompetencia) -> tuple[Decimal, Decimal]:
    """Retorna (% presunção IRPJ, % presunção CSLL) com base na composição da receita.

    Heurística simplificada — para precisão fiscal completa, deve-se classificar
    cada CFOP/atividade. Aqui, predominância:
    - Comércio/indústria/transporte de carga: IRPJ 8% / CSLL 12%
    - Serviços em geral: IRPJ 32% / CSLL 32%
    """
    receita_servicos = dados.receita_servicos
    receita_outros = dados.receita_revenda + dados.receita_industrializacao
    if receita_servicos > receita_outros:
        return Decimal("0.32"), Decimal("0.32")
    return Decimal("0.08"), Decimal("0.12")


class CalculadoraLucroPresumido:
    def apurar(self, dados: DadosFiscaisCompetencia) -> ResultadoApuracao:
        tab = tabelas_presuncao_lp()
        pct_irpj, pct_csll = _percentuais_presuncao(dados)
        aliq_irpj = tab["aliquotas_base"]["irpj"]
        aliq_csll = tab["aliquotas_base"]["csll"]
        aliq_pis = tab["pis_cofins_cumulativo"]["pis"]["aliquota"]
        aliq_cofins = tab["pis_cofins_cumulativo"]["cofins"]["aliquota"]
        aliq_adicional = tab["adicional_irpj"]["aliquota"]
        excedente_mensal = tab["adicional_irpj"]["base_excedente_trimestral"] / 3

        base_irpj = dados.receita_bruta * pct_irpj
        base_csll = dados.receita_bruta * pct_csll

        irpj = base_irpj * aliq_irpj
        if base_irpj > excedente_mensal:
            irpj += (base_irpj - excedente_mensal) * aliq_adicional
        csll = base_csll * aliq_csll

        pis = dados.receita_bruta * aliq_pis
        cofins = dados.receita_bruta * aliq_cofins
        icms = max(dados.debito_icms - dados.credito_icms, Decimal(0))

        inss_cpp = dados.inss_patronal_total

        tributos = Tributos(
            irpj=irpj, csll=csll, pis=pis, cofins=cofins,
            inss_cpp=inss_cpp, icms=icms,
        )
        aliq_efetiva = (
            tributos.total / dados.receita_bruta if dados.receita_bruta > 0 else Decimal(0)
        )

        return ResultadoApuracao(
            regime="LP",
            competencia=dados.competencia,
            cnpj=dados.cnpj,
            tributos=tributos,
            receita_base=dados.receita_bruta,
            aliquota_efetiva=aliq_efetiva,
            detalhamento={
                "presuncao_irpj_pct": str(pct_irpj),
                "presuncao_csll_pct": str(pct_csll),
                "base_irpj": str(base_irpj),
                "base_csll": str(base_csll),
            },
        )
