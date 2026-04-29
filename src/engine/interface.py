from typing import Protocol, runtime_checkable

from src.engine.inputs import DadosFiscaisCompetencia
from src.engine.outputs import ResultadoApuracao


@runtime_checkable
class Calculadora(Protocol):
    def apurar(self, dados: DadosFiscaisCompetencia) -> ResultadoApuracao: ...
