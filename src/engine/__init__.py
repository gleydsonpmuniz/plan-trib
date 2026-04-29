from src.engine.inputs import DadosFiscaisCompetencia
from src.engine.lucro_presumido import CalculadoraLucroPresumido
from src.engine.lucro_real import CalculadoraLucroReal
from src.engine.outputs import ResultadoApuracao, Tributos
from src.engine.simples import CalculadoraSimples


def comparar_regimes(dados: DadosFiscaisCompetencia) -> dict[str, ResultadoApuracao]:
    return {
        "SIMPLES": CalculadoraSimples().apurar(dados),
        "LP": CalculadoraLucroPresumido().apurar(dados),
        "LR": CalculadoraLucroReal().apurar(dados),
    }


__all__ = [
    "DadosFiscaisCompetencia",
    "ResultadoApuracao",
    "Tributos",
    "CalculadoraSimples",
    "CalculadoraLucroPresumido",
    "CalculadoraLucroReal",
    "comparar_regimes",
]
