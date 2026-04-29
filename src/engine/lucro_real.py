from decimal import Decimal

from src.engine.inputs import DadosFiscaisCompetencia
from src.engine.outputs import ResultadoApuracao, Tributos

ALIQ_PIS_NAO_CUMUL = Decimal("0.0165")
ALIQ_COFINS_NAO_CUMUL = Decimal("0.076")
ALIQ_IRPJ = Decimal("0.15")
ALIQ_ADICIONAL_IRPJ = Decimal("0.10")
ALIQ_CSLL = Decimal("0.09")
EXCEDENTE_MENSAL = Decimal("20000")


class CalculadoraLucroReal:
    def apurar(self, dados: DadosFiscaisCompetencia) -> ResultadoApuracao:
        receita = dados.receita_bruta

        pis_debito = receita * ALIQ_PIS_NAO_CUMUL
        cofins_debito = receita * ALIQ_COFINS_NAO_CUMUL
        pis_credito = dados.base_credito_pis_cofins * ALIQ_PIS_NAO_CUMUL
        cofins_credito = dados.base_credito_pis_cofins * ALIQ_COFINS_NAO_CUMUL
        pis = max(pis_debito - pis_credito, Decimal(0))
        cofins = max(cofins_debito - cofins_credito, Decimal(0))

        custos_e_despesas = (
            dados.folha_bruta
            + dados.pro_labore
            + dados.inss_patronal_total
            + dados.fgts
            + dados.despesas_administrativas
            + dados.despesas_comerciais
            + dados.despesas_tributarias
            + pis
            + cofins
        )
        lucro_liquido = receita - custos_e_despesas

        if lucro_liquido > 0:
            irpj = lucro_liquido * ALIQ_IRPJ
            if lucro_liquido > EXCEDENTE_MENSAL:
                irpj += (lucro_liquido - EXCEDENTE_MENSAL) * ALIQ_ADICIONAL_IRPJ
            csll = lucro_liquido * ALIQ_CSLL
        else:
            irpj = Decimal(0)
            csll = Decimal(0)

        icms = max(dados.debito_icms - dados.credito_icms, Decimal(0))
        inss_cpp = dados.inss_patronal_total

        tributos = Tributos(
            irpj=irpj, csll=csll, pis=pis, cofins=cofins,
            inss_cpp=inss_cpp, icms=icms,
        )
        aliq_efetiva = tributos.total / receita if receita > 0 else Decimal(0)

        return ResultadoApuracao(
            regime="LR",
            competencia=dados.competencia,
            cnpj=dados.cnpj,
            tributos=tributos,
            receita_base=receita,
            aliquota_efetiva=aliq_efetiva,
            detalhamento={
                "lucro_liquido": str(lucro_liquido),
                "custos_e_despesas": str(custos_e_despesas),
                "pis_credito": str(pis_credito),
                "cofins_credito": str(cofins_credito),
            },
        )
