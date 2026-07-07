import asyncio
from verificador_pdfa import validar_pdfa


def test_validar_arquivo_inexistente():
    res = asyncio.run(validar_pdfa("arquivo_que_nao_existe_12345.pdf"))
    assert isinstance(res, dict)
    assert res.get("status") == "erro"
    assert "arquivo" in res.get("detalhes", [""])[0]
