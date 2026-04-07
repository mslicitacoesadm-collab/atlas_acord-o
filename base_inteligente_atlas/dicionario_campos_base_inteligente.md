# Dicionário de Campos — Base Inteligente

## Identificação

### `id_unico`
Identificador único e estável do precedente.

Exemplo:
`acordao_1418_2024_1camara`

### `tipo`
Tipo documental do registro.
Valores esperados:
- `acordao`
- `jurisprudencia`
- `sumula`

### `numero`
Número principal do precedente.

### `ano`
Ano do precedente.

### `tribunal`
Órgão emissor. Ex.: `TCM/BA`, `TCU`, `STJ`.

### `colegiado`
Câmara, turma, plenário ou equivalente.

---

## Origem

### `origem_db`
Nome da base física de onde o registro foi extraído.

### `origem_tabela`
Nome da tabela original na base de origem.

---

## Inteligência jurídica

### `tema_principal`
Tema jurídico dominante do precedente.

Exemplos:
- `inexequibilidade`
- `habilitacao`
- `formalismo_moderado`
- `julgamento_objetivo`

### `subtemas_json`
Lista de subtópicos específicos.

Exemplo:
- diligência prévia
- excesso formal
- atestado técnico
- planilha de custos

### `tese_central`
Síntese jurídica objetiva do que o precedente realmente sustenta.

Esse é um dos campos mais valiosos da base.

### `ementa_resumida`
Resumo curto e claro para exibição no painel.

### `trecho_chave`
Trecho ou síntese curta que possa virar citação útil.

---

## Base legal e indexação

### `fundamentos_legais_json`
Lista de artigos, leis, decretos ou instruções normativas citadas ou inferidas.

### `palavras_chave_json`
Palavras relevantes para busca rápida.

---

## Inteligência de aplicação

### `lado_favorecido_json`
Indica quem tende a ser beneficiado pelo precedente.

Valores sugeridos:
- `licitante`
- `administracao`
- `neutro`

### `tipo_de_uso_json`
Como o precedente pode ser usado.

Exemplos:
- `citacao`
- `substituicao`
- `reforco`
- `fundamentacao_principal`
- `contraponto`

### `aplicavel_em_json`
Tipos de peça em que o precedente funciona melhor.

Exemplos:
- recurso administrativo
- contrarrazões
- impugnação ao edital
- defesa de exequibilidade
- resposta à inabilitação

### `contexto_licitatorio_json`
Contextos concretos da licitação onde o precedente é útil.

Exemplos:
- habilitação
- fase recursal
- julgamento da proposta
- diligência
- inexequibilidade

---

## Scoring

### `grau_utilidade`
Score de utilidade prática do precedente no sistema.
Faixa sugerida: `0.00` a `1.00`

### `score_confianca_interno`
Score interno para o processo de classificação e recomendação.
Faixa sugerida: `0.00` a `1.00`

---

## Saída amigável

### `resumo_uso_pratico`
Explicação curta para o usuário entender por que aquele precedente apareceu.

Exemplo:
`Útil para sustentar a necessidade de diligência antes da desclassificação da proposta.`

---

## Texto bruto e busca

### `texto_base`
Texto original consolidado do precedente.

### `texto_indexavel`
Texto preparado para indexação e busca híbrida.
Pode juntar:
- número
- tema
- tese
- ementa
- fundamentos
- palavras-chave

### `embedding_blob`
Campo reservado para embeddings futuros.
Pode começar vazio.

### `hash_texto`
Hash do conteúdo para evitar duplicidade e facilitar controle de atualização.
