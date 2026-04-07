from modules.citation_extractor import detect_thesis, extract_references_with_context, classify_piece_type
from modules.search_engine import build_short_reference


def test_detect_thesis_inexequibilidade():
    result = detect_thesis('A proposta foi tida por inexequível sem permitir diligência e planilha de custos.')
    assert result['chave'] in {'inexequibilidade', 'diligencia'}


def test_extract_reference():
    refs = extract_references_with_context('Conforme Acórdão 1234/2024, houve formalismo moderado.')
    assert refs
    assert refs[0]['numero'] == '1234'
    assert refs[0]['ano'] == '2024'


def test_classify_piece_type():
    result = classify_piece_type('Trata-se de recurso administrativo com pedido de reforma da decisão.')
    assert result['chave'] == 'recurso'


def test_build_short_reference():
    rec = {'tribunal': 'TCM/BA', 'tipo': 'Acórdão', 'numero': '1418', 'ano': '2024', 'colegiado': '1ª Câmara'}
    ref = build_short_reference(rec)
    assert 'TCM/BA' in ref and '1418/2024' in ref
