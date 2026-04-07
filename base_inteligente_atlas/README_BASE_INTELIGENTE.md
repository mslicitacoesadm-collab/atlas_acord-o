# Base Inteligente — Atlas de Acórdãos

Este pacote foi montado para servir como modelo de implantação da **Base Inteligente** do Atlas de Acórdãos.

## Objetivo

Transformar a base atual de acórdãos, jurisprudência e súmulas em um **motor de recomendação jurídica**, capaz de:

- identificar tese dominante;
- localizar precedentes compatíveis por contexto;
- diferenciar precedentes por utilidade prática;
- priorizar o lado favorecido (licitante, administração ou neutro);
- sugerir onde e como usar o precedente na peça.

---

## Arquivos deste pacote

### 1. `schema_base_inteligente.sql`
Cria a estrutura SQLite principal com:
- tabela central `precedentes_inteligentes`;
- índices para consulta rápida;
- tabela opcional de teses;
- tabela opcional de log de uso/aprendizado.

### 2. `modelo_registro_base_inteligente.json`
Exemplo de registro já enriquecido e pronto para consulta híbrida.

### 3. `dicionario_campos_base_inteligente.md`
Explica, um por um, os campos que devem existir na base inteligente.

### 4. `pipeline_enriquecimento_exemplo.py`
Script-base para:
- ler as bases atuais;
- normalizar os campos;
- gerar tese, subtema, uso recomendado e lado favorecido;
- gravar na nova base inteligente.

### 5. `teses_nucleares.json`
Núcleo inicial de teses para classificação jurídica.

---

## Estrutura recomendada

### Camada 1 — Base bruta
Você mantém as bases por ano, como já faz hoje:
- acórdãos por ano;
- jurisprudência;
- súmulas.

### Camada 2 — Base inteligente
Você cria uma base mestra nova, com registros já enriquecidos.

### Camada 3 — Busca híbrida
A pesquisa ideal deve combinar:
- busca exata por número;
- busca por tese;
- busca textual;
- score semântico;
- utilidade prática;
- adequação ao tipo de peça.

---

## Fluxo ideal de uso no sistema

1. O usuário envia a peça.
2. O sistema identifica:
   - tipo de peça;
   - tese principal;
   - tese secundária;
   - contexto argumentativo.
3. O sistema consulta a base inteligente.
4. O sistema ranqueia os precedentes.
5. O sistema devolve:
   - precedente principal;
   - alternativas;
   - motivo da aderência;
   - texto sugerido para inserção.

---

## Ordem prática de implantação

### Etapa 1
Criar a nova base SQLite com `schema_base_inteligente.sql`.

### Etapa 2
Executar o `pipeline_enriquecimento_exemplo.py` apontando para a pasta das bases `.db` atuais.

### Etapa 3
Ajustar o `search_engine.py` para consultar primeiro a nova tabela `precedentes_inteligentes`.

### Etapa 4
Adicionar embedding leve futuramente, sem quebrar a estrutura já criada.

---

## Recomendação estratégica

Não tente começar com tudo ao mesmo tempo.

A ordem mais segura e forte é:

1. normalização;
2. tese central;
3. lado favorecido;
4. uso recomendado;
5. score de utilidade;
6. embeddings.

---

## Resultado esperado

Quando estiver implantada, essa base permitirá que o Atlas de Acórdãos deixe de ser apenas um buscador e passe a funcionar como:

**um motor de reforço jurídico orientado por tese, contexto e utilidade prática.**
