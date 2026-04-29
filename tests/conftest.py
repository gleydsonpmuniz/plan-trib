from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Diretório com SPEDs e PDFs reais (link/copy de .claude/documentos/)."""
    return ROOT / ".claude" / "documentos"


@pytest.fixture(scope="session")
def sample_sped_fiscal(fixtures_dir: Path) -> Path:
    """Retorna 1 arquivo SPED Fiscal pequeno para testes rápidos."""
    candidates = sorted((fixtures_dir / "sped_fiscal_icms_ipi").glob("*.txt"))
    if not candidates:
        pytest.skip("Sem amostras de SPED Fiscal")
    candidates.sort(key=lambda p: p.stat().st_size)
    return candidates[0]


@pytest.fixture(scope="session")
def sample_sped_contrib(fixtures_dir: Path) -> Path:
    candidates = sorted((fixtures_dir / "sped_contribuicoes").glob("PISCOFINS_*.txt"))
    if not candidates:
        pytest.skip("Sem amostras de SPED Contribuições")
    candidates.sort(key=lambda p: p.stat().st_size)
    return candidates[0]


@pytest.fixture(scope="session")
def sample_pdf_folha(fixtures_dir: Path) -> Path:
    candidates = sorted((fixtures_dir / "folhas de pagamento").glob("*.pdf"))
    if not candidates:
        pytest.skip("Sem amostras de PDF folha")
    return candidates[0]


@pytest.fixture(scope="session")
def sample_pdf_pgdas(fixtures_dir: Path) -> Path:
    candidates = sorted((fixtures_dir / "PGDAS").glob("PGDASD-*.pdf"))
    if not candidates:
        pytest.skip("Sem amostras de PGDAS")
    return candidates[0]
