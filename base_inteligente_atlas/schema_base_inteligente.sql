PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS precedentes_inteligentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_unico TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL,                       -- acordao | jurisprudencia | sumula
    numero TEXT,
    ano TEXT,
    tribunal TEXT DEFAULT 'TCM/BA',
    colegiado TEXT,
    origem_db TEXT,
    origem_tabela TEXT,
    tema_principal TEXT,
    subtemas_json TEXT,
    tese_central TEXT,
    ementa_resumida TEXT,
    trecho_chave TEXT,
    fundamentos_legais_json TEXT,
    palavras_chave_json TEXT,
    lado_favorecido_json TEXT,               -- ["licitante"], ["administracao"], ["neutro"]
    tipo_de_uso_json TEXT,                   -- ex.: ["citacao", "substituicao", "reforco"]
    aplicavel_em_json TEXT,                  -- ex.: ["recurso administrativo", "contrarrazoes"]
    contexto_licitatorio_json TEXT,          -- ex.: ["habilitacao", "inexequibilidade"]
    grau_utilidade REAL DEFAULT 0.50,
    score_confianca_interno REAL DEFAULT 0.50,
    resumo_uso_pratico TEXT,
    texto_base TEXT,
    texto_indexavel TEXT,
    embedding_blob BLOB,
    hash_texto TEXT,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_precedentes_tipo ON precedentes_inteligentes(tipo);
CREATE INDEX IF NOT EXISTS idx_precedentes_numero_ano ON precedentes_inteligentes(numero, ano);
CREATE INDEX IF NOT EXISTS idx_precedentes_tema ON precedentes_inteligentes(tema_principal);
CREATE INDEX IF NOT EXISTS idx_precedentes_tribunal ON precedentes_inteligentes(tribunal);
CREATE INDEX IF NOT EXISTS idx_precedentes_colegiado ON precedentes_inteligentes(colegiado);
CREATE INDEX IF NOT EXISTS idx_precedentes_utilidade ON precedentes_inteligentes(grau_utilidade DESC);

CREATE VIRTUAL TABLE IF NOT EXISTS precedentes_fts USING fts5(
    id_unico,
    tipo,
    numero,
    ano,
    tema_principal,
    tese_central,
    ementa_resumida,
    trecho_chave,
    resumo_uso_pratico,
    texto_indexavel,
    content='precedentes_inteligentes',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS precedentes_ai AFTER INSERT ON precedentes_inteligentes BEGIN
  INSERT INTO precedentes_fts(rowid, id_unico, tipo, numero, ano, tema_principal, tese_central, ementa_resumida, trecho_chave, resumo_uso_pratico, texto_indexavel)
  VALUES (new.id, new.id_unico, new.tipo, new.numero, new.ano, new.tema_principal, new.tese_central, new.ementa_resumida, new.trecho_chave, new.resumo_uso_pratico, new.texto_indexavel);
END;

CREATE TRIGGER IF NOT EXISTS precedentes_ad AFTER DELETE ON precedentes_inteligentes BEGIN
  INSERT INTO precedentes_fts(precedentes_fts, rowid, id_unico, tipo, numero, ano, tema_principal, tese_central, ementa_resumida, trecho_chave, resumo_uso_pratico, texto_indexavel)
  VALUES ('delete', old.id, old.id_unico, old.tipo, old.numero, old.ano, old.tema_principal, old.tese_central, old.ementa_resumida, old.trecho_chave, old.resumo_uso_pratico, old.texto_indexavel);
END;

CREATE TRIGGER IF NOT EXISTS precedentes_au AFTER UPDATE ON precedentes_inteligentes BEGIN
  INSERT INTO precedentes_fts(precedentes_fts, rowid, id_unico, tipo, numero, ano, tema_principal, tese_central, ementa_resumida, trecho_chave, resumo_uso_pratico, texto_indexavel)
  VALUES ('delete', old.id, old.id_unico, old.tipo, old.numero, old.ano, old.tema_principal, old.tese_central, old.ementa_resumida, old.trecho_chave, old.resumo_uso_pratico, old.texto_indexavel);
  INSERT INTO precedentes_fts(rowid, id_unico, tipo, numero, ano, tema_principal, tese_central, ementa_resumida, trecho_chave, resumo_uso_pratico, texto_indexavel)
  VALUES (new.id, new.id_unico, new.tipo, new.numero, new.ano, new.tema_principal, new.tese_central, new.ementa_resumida, new.trecho_chave, new.resumo_uso_pratico, new.texto_indexavel);
END;

CREATE TABLE IF NOT EXISTS teses_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    titulo TEXT NOT NULL,
    descricao TEXT,
    palavras_chave_json TEXT,
    exemplos_json TEXT,
    ativa INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS log_uso_precedentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_unico TEXT NOT NULL,
    tipo_peca TEXT,
    tese_identificada TEXT,
    score_busca REAL,
    escolhido_pelo_sistema INTEGER DEFAULT 0,
    aproveitado_pelo_usuario INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);
