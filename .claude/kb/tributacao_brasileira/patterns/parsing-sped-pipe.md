# Pattern: Parsing SPED Pipe-Delimited

> **Purpose**: Estratégia robusta e versionada para parsear arquivos SPED (EFD ICMS/IPI, EFD-Contribuições) em Python, com tipagem forte via Pydantic e tolerância a evoluções de leiaute.
> **MCP Validated**: 2026-04-28

## When to Use

- Importação de arquivos SPED em sistemas de planejamento tributário
- Necessidade de extrair dados específicos (faturamento, créditos, apuração) sem reescrever todo o leiaute
- Multi-tenant ou multi-empresa onde diferentes leiautes (versões) podem coexistir
- Validação cruzada com totalizadores (ex.: bloco 9 vs. soma real de registros)

## Implementation

```python
from __future__ import annotations
from decimal import Decimal
from datetime import date
from pathlib import Path
from typing import Iterator, ClassVar, Type
from pydantic import BaseModel, Field, field_validator


class SpedRecord(BaseModel):
    """Base de todos os registros SPED. Subclasses definem o leiaute."""
    REG: ClassVar[str]                    # ex.: "0000"
    POSITIONS: ClassVar[dict[str, int]]   # campo → índice (1-based, após o tipo)

    @classmethod
    def parse(cls, line: str) -> "SpedRecord":
        # Linha: |0000|019|0|01012025|31012025|EMPRESA|...|
        parts = line.strip().strip("|").split("|")
        # parts[0] = REG; demais conforme POSITIONS
        kwargs = {}
        for field, idx in cls.POSITIONS.items():
            kwargs[field] = parts[idx] if idx < len(parts) else None
        return cls(**kwargs)


class Reg0000(SpedRecord):
    """Identificação da escrituração — EFD ICMS/IPI v019."""
    REG: ClassVar[str] = "0000"
    POSITIONS: ClassVar[dict[str, int]] = {
        "cod_ver": 1, "cod_fin": 2, "dt_ini": 3, "dt_fin": 4,
        "nome": 5, "cnpj": 6, "cpf": 7, "uf": 8, "ie": 9,
        "cod_mun": 10, "im": 11, "suframa": 12, "ind_perfil": 13, "ind_ativ": 14,
    }
    cod_ver: str
    cod_fin: str
    dt_ini: date
    dt_fin: date
    nome: str
    cnpj: str | None
    uf: str
    ie: str | None
    cod_mun: str
    ind_ativ: str  # 0=Industrial, 1=Outros

    @field_validator("dt_ini", "dt_fin", mode="before")
    @classmethod
    def parse_date(cls, v: str) -> date:
        # Formato SPED: DDMMAAAA
        return date(int(v[4:8]), int(v[2:4]), int(v[0:2]))


class RegistryParser:
    """Stream-based parser. Carrega só registros do interesse — não precisa
    modelar todos os ~200 tipos do leiaute."""

    def __init__(self, registry: dict[str, Type[SpedRecord]]):
        self.registry = registry  # ex.: {"0000": Reg0000, "C100": RegC100}

    def parse_file(self, path: Path) -> Iterator[SpedRecord]:
        # Encoding ISO-8859-1 é o padrão dos SPED brasileiros
        with path.open("r", encoding="iso-8859-1") as f:
            for line in f:
                if not line.startswith("|"):
                    continue  # ignora certificado digital ICP-Brasil ao final
                reg_type = line[1:].split("|", 1)[0]
                if reg_type in self.registry:
                    yield self.registry[reg_type].parse(line)
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `encoding` | `"iso-8859-1"` | SPED usa ISO-8859-1 (Latin-1), nunca UTF-8 |
| `decimal_separator` | `","` | Valores monetários usam vírgula; converter antes do `Decimal` |
| `date_format` | `"DDMMAAAA"` | Sem separadores |
| `layout_version` | detectado em `0000.cod_ver` | Tratar versionamento explicitamente |
| `cnpj_format` | só dígitos | Sem máscara; 14 caracteres |

## Versionamento de Leiaute

```python
PARSER_REGISTRY = {
    ("EFD_ICMS_IPI", "019"): {"0000": Reg0000_v019, "C100": RegC100_v019, ...},
    ("EFD_ICMS_IPI", "018"): {"0000": Reg0000_v018, "C100": RegC100_v018, ...},
    ("EFD_CONTRIB", "006"): {"0000": Reg0000_Contrib_v006, ...},
}

def select_parser(file_path: Path) -> dict:
    # Lê primeira linha 0000 e seleciona o registry adequado
    with file_path.open("r", encoding="iso-8859-1") as f:
        first = f.readline()
    cod_ver = first.strip().strip("|").split("|")[1]
    return PARSER_REGISTRY[("EFD_ICMS_IPI", cod_ver)]
```

## Bibliotecas Existentes (referência)

| Lib | Uso recomendado |
|-----|-----------------|
| `python-sped` ([github.com/sped-br](https://github.com/sped-br/python-sped)) | Leiautes pré-definidos (mas data de manutenção pode estar desatualizada) |
| `sped-extractor` ([PyPI](https://pypi.org/project/sped-extractor/)) | Extrai leiautes oficiais dos PDFs da RFB → CSV/JSON. Útil para regenerar registries quando RFB publica nova versão |

## Anti-Patterns

| Don't | Do |
|-------|-----|
| `open(file, "r")` (UTF-8 default) | `open(file, "r", encoding="iso-8859-1")` |
| Float para valores monetários | `Decimal(str(parts[i]).replace(",", "."))` |
| Modelar todos os ~200 registros | Modelar só os do interesse via registry seletivo |
| Validar leiaute na ingestão estrita | Stream parser tolerante; validações em camada superior |

## See Also

- [sped-fiscal-efd](../concepts/sped-fiscal-efd.md)
- [sped-contribuicoes](../concepts/sped-contribuicoes.md)
- Spec: `../specs/leiautes-sped-versoes.yaml`
