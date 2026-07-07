import asyncio
from verificador_pdfa import validar_pdfa
from pathlib import Path


def test_validar_amostra_existente():
    sample = Path("documents/test_samples/sample.pdf")
    assert sample.exists()
    res = asyncio.run(validar_pdfa(str(sample)))
    assert isinstance(res, dict)
    assert res.get("status") in {"conforme", "nao_conforme", "erro"}
