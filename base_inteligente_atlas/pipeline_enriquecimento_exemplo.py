from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List

# Ajuste estes caminhos conforme sua estrutura real
BASES_DIR = Path("./bases")
OUT_DB = Path("./base_inteligente.db")
SCHEMA_SQL = Path("./schema_base_inteligente.sql")
TESES_JSON = Path("./teses_nucleares.json")

TABLES = ("acordaos", "records", "jurisprudencia", "sumula")


def open_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def detect_table(conn: sqlite3.Connection) -> str | None:
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    for t in TABLES:
        if t in tables:
            return t
    return None


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def load_teses() -> List[Dict[str, Any]]:
    return json.loads(TESES_JSON.read_text(encoding="utf-8"))


def classify_tema(text: str, teses: List[Dict[str, Any]]) -> tuple[str, List[str]]:
    txt = (text or "").lower()
    best_code = "tema_geral"
    best_score = 0
    matched_subthemes: List[str] = []

    for tese in teses:
        score = 0
        local_matches = []
        for kw in tese.get("palavras_chave", []):
            if kw.lower() in txt:
                score += 2 if " " not in kw else 3
                local_matches.append(kw)
        if score > best_score:
            best_score = score
            best_code = tese["codigo"]
            matched_subthemes = local_matches[:5]

    return best_code, matched_subthemes


def infer_lado_favorecido(texto: str, tema: str) -> List[str]:
    txt = (texto or "").lower()
    if any(p in txt for p in ["oportunizar", "diligência", "formalismo moderado", "erro sanável"]):
        return ["licitante"]
    if any(p in txt for p in ["vinculação ao edital", "descumprimento do edital", "inabilitação mantida"]):
        return ["administracao"]
    if tema in {"competitividade", "proposta_mais_vantajosa"}:
        return ["neutro"]
    return ["neutro"]


def infer_aplicavel_em(tipo: str, tema: str) -> List[str]:
    base = ["recurso administrativo", "contrarrazões"]
    if tema in {"vinculacao_edital", "competitividade"}:
        base.append("impugnação ao edital")
    if tema == "inexequibilidade":
        base.append("defesa de exequibilidade")
    if tema in {"habilitacao", "capacidade_tecnica", "erro_sanavel"}:
        base.append("resposta à inabilitação")
    return list(dict.fromkeys(base))


def infer_tipo_de_uso() -> List[str]:
    return ["citacao", "substituicao", "reforco"]


def build_hash(texto: str) -> str:
    return hashlib.sha256((texto or "").encode("utf-8")).hexdigest()


def row_to_record(raw: sqlite3.Row, table: str, origem_db: str, teses: List[Dict[str, Any]]) -> Dict[str, Any]:
    row = dict(raw)

    if table in {"acordaos", "records"}:
        tipo = "acordao"
        numero = str(row.get("numero_acordao_num") or row.get("numero_acordao") or "")
        ano = str(row.get("ano_acordao") or "")
        colegiado = row.get("colegiado") or ""
        texto_base = normalize_spaces(" ".join([
            str(row.get("sumario") or ""),
            str(row.get("decisao") or ""),
            str(row.get("acordao_texto") or ""),
            str(row.get("ementa_match") or ""),
            str(row.get("texto_match") or "")
        ]))
        resumo = normalize_spaces(row.get("sumario") or row.get("ementa_match") or row.get("texto_match") or "")
        tema_bruto = normalize_spaces(str(row.get("assunto") or row.get("tema") or ""))

    elif table == "jurisprudencia":
        tipo = "jurisprudencia"
        numero = str(row.get("numacordao") or "")
        ano = str(row.get("anoacordao") or "")
        colegiado = row.get("colegiado") or ""
        texto_base = normalize_spaces(" ".join([
            str(row.get("enunciado") or ""),
            str(row.get("excerto") or ""),
            str(row.get("paragrafolc") or ""),
            str(row.get("indexadoresconsolidados") or "")
        ]))
        resumo = normalize_spaces(row.get("enunciado") or "")
        tema_bruto = normalize_spaces(str(row.get("tema") or row.get("area") or ""))

    else:
        tipo = "sumula"
        numero = str(row.get("numero") or "")
        ano = str(row.get("anoaprovacao") or "")
        colegiado = row.get("colegiado") or ""
        texto_base = normalize_spaces(" ".join([
            str(row.get("enunciado") or ""),
            str(row.get("excerto") or "")
        ]))
        resumo = normalize_spaces(row.get("enunciado") or "")
        tema_bruto = normalize_spaces(str(row.get("tema") or row.get("area") or ""))

    tema_principal, subtemas = classify_tema(f"{tema_bruto} {texto_base}", teses)

    fundamentos = []
    for padrao in [r"art\.\s*\d+[A-Za-zº°]*", r"Lei\s*n[ºo\.]?\s*\d+[\./]?\d*"]:
        fundamentos.extend(re.findall(padrao, texto_base, flags=re.IGNORECASE))
    fundamentos = list(dict.fromkeys(normalize_spaces(f) for f in fundamentos))[:10]

    trecho_chave = resumo[:320] if resumo else texto_base[:320]
    lado_favorecido = infer_lado_favorecido(texto_base, tema_principal)
    aplicavel_em = infer_aplicavel_em(tipo, tema_principal)
    tipo_de_uso = infer_tipo_de_uso()

    texto_indexavel = normalize_spaces(" ".join([
        numero, ano, tema_bruto, tema_principal, resumo, trecho_chave, " ".join(subtemas), " ".join(fundamentos)
    ]))

    id_unico = f"{tipo}_{numero}_{ano}_{re.sub(r'[^a-z0-9]+', '_', (colegiado or 'sem_colegiado').lower()).strip('_')}"

    return {
        "id_unico": id_unico,
        "tipo": tipo,
        "numero": numero,
        "ano": ano,
        "tribunal": "TCM/BA",
        "colegiado": colegiado,
        "origem_db": origem_db,
        "origem_tabela": table,
        "tema_principal": tema_principal,
        "subtemas_json": json.dumps(subtemas, ensure_ascii=False),
        "tese_central": resumo or f"Precedente relacionado ao tema {tema_principal}.",
        "ementa_resumida": resumo,
        "trecho_chave": trecho_chave,
        "fundamentos_legais_json": json.dumps(fundamentos, ensure_ascii=False),
        "palavras_chave_json": json.dumps(subtemas + ([tema_principal] if tema_principal else []), ensure_ascii=False),
        "lado_favorecido_json": json.dumps(lado_favorecido, ensure_ascii=False),
        "tipo_de_uso_json": json.dumps(tipo_de_uso, ensure_ascii=False),
        "aplicavel_em_json": json.dumps(aplicavel_em, ensure_ascii=False),
        "contexto_licitatorio_json": json.dumps([tema_principal], ensure_ascii=False),
        "grau_utilidade": 0.75,
        "score_confianca_interno": 0.70,
        "resumo_uso_pratico": f"Útil para peças relacionadas ao tema {tema_principal}.",
        "texto_base": texto_base,
        "texto_indexavel": texto_indexavel,
        "embedding_blob": None,
        "hash_texto": build_hash(texto_base),
    }


def create_output_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(OUT_DB))
    schema = SCHEMA_SQL.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()
    return conn


def iter_source_dbs() -> Iterable[Path]:
    return sorted(BASES_DIR.glob("*.db"))


def insert_record(conn: sqlite3.Connection, rec: Dict[str, Any]) -> None:
    cols = ", ".join(rec.keys())
    placeholders = ", ".join([":" + k for k in rec.keys()])
    sql = f"INSERT OR REPLACE INTO precedentes_inteligentes ({cols}) VALUES ({placeholders})"
    conn.execute(sql, rec)


def run() -> None:
    teses = load_teses()
    out = create_output_db()
    total = 0

    for db_path in iter_source_dbs():
        src = open_db(db_path)
        try:
            table = detect_table(src)
            if not table:
                continue

            rows = src.execute(f"SELECT * FROM {table}").fetchall()
            for row in rows:
                rec = row_to_record(row, table, db_path.name, teses)
                insert_record(out, rec)
                total += 1
        finally:
            src.close()

    out.commit()
    out.close()
    print(f"Base inteligente criada com {total} registros.")


if __name__ == "__main__":
    run()
