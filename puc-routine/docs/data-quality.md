# Auditoria dos dados — PUC Routine

> Gerado por `scripts/audit.py` em 28/08/2026. Todos os números abaixo são **recalculados a partir dos arquivos em `data/raw/`** a cada execução — nenhum é copiado da documentação dos cases nem da apresentação.

Convenção usada em todo o projeto:

| Marcação | Significado |
|---|---|
| **Dado observado** | Está literalmente no arquivo entregue. |
| **Resultado calculado** | Derivado dos arquivos por um script deste repositório. |
| **Estimativa** | Modelo ou projeção; carrega erro conhecido. |
| **Regra de negócio** | Decisão de produto (limiar, peso, filtro). |
| **Suposição declarada** | Hipótese assumida porque o dado não existe. |

## 1. Inventário

| Case | Arquivo | Registros | Colunas | Dups. exatas | Campos com vazio |
|---|---|---|---|---|---|
| 1 | vagas.csv | 3.550 | 16 | 0 | 4 |
| 1 | vaga_cursos.csv | 7.994 | 2 | 0 | 0 |
| 1 | alunos.csv | 2.187 | 10 | 0 | 4 |
| 1 | aluno_interesses.csv | 1.444 | 2 | 2 | 0 |
| 1 | monitorias.csv | 283 | 5 | 29 | 1 |
| 1 | PibicPibiti_vagasoferecidas.xlsx :: aba 'pibiti' | 197 | 3 | 0 | 0 |
| 1 | PibicPibiti_vagasoferecidas.xlsx :: aba 'pibic' | 530 | 3 | 0 | 0 |
| 2 | bicicletario/sessoes.csv | 23.429 | 10 | 0 | 0 |
| 2 | bicicletario/ocupacao_estimada.csv | 1.055 | 4 | 0 | 0 |
| 2 | bicicletario/uso_por_dia_hora.csv | 89 | 3 | 0 | 0 |
| 2 | estacionamento/FLUXO ...xlsx (3 abas unidas) | 6.858 | 8 | 183 | 0 |
| 3 | turmas_horarios.csv | 74.381 | 13 | 47.726 | 1 |
| 3 | disciplinas.csv | 1.017 | 6 | 0 | 0 |

Case 4: **SEM DADOS** — nenhum arquivo de cardápio entregue.

## 2. Case 3 — Grade horária (núcleo do produto)

### 2.1 Deduplicação — executada antes de qualquer cálculo

- Linhas brutas: **74.381**
- Duplicatas exatas removidas: **47.726** (64.2%)
- Linhas após deduplicar: **26.655** — fator de inflação 2.79×

> **Correção importante em relação à apresentação.** O deck trata 26.655 como *blocos de aula*. Não são: são **linhas** após remover duplicatas exatas, e ainda estão multiplicadas pela relação N:N entre turma e professor. Agrupando por `(periodo, turma_id, dia, hora_inicio, hora_fim)`, os blocos de aula realmente distintos são **7.952** — média de 1.61 blocos por turma. É este o número que o otimizador enxerga.

### 2.2 Escala real da oferta

| Métrica | Valor |
|---|---|
| Turmas distintas | 4.947 |
| Blocos de aula únicos | 7.952 |
| Professores | 1.048 |
| Salas | 210 |
| Departamentos | 30 |
| Linhas sem sala | 2.930 |

### 2.3 Problemas de junção

**`disciplinas.csv` cobre metade da oferta.** A oferta usa 1.825 códigos; o catálogo tem 1.017, dos quais 898 aparecem na oferta. Ficam **927 códigos (50.8%) sem nome completo, créditos ou carga horária**. Concentração por prefixo: `ENG` 162, `DSG` 124, `ADM` 81, `COM` 49, `GEO` 48, `ECO` 46, `SER` 36, `MAT` 29.

*Tratamento:* `data/processed/case3/disciplinas_catalogo.csv` usa o nome do catálogo quando existe e `disciplina_abrev` da própria oferta quando não existe, com a coluna `nome_origem` registrando qual foi usado. Um `merge` interno com `disciplinas.csv` descartaria metade da oferta e nunca deve ser usado.

**`cod_departamento` tem tipos incompatíveis.** Em `turmas_horarios.csv` é texto, ex. ['ADM', 'ART', 'BIO', 'COM']; em `disciplinas.csv` é int64, ex. [np.int64(244), np.int64(246), np.int64(256), np.int64(259)]. Não há tabela de conversão — **junção por departamento é impossível** com o que veio.

**`vagas` não é a capacidade da turma.** 4.708 de 4.947 turmas têm mais de um valor de `vagas` entre suas linhas, enquanto apenas 520 têm mais de um professor — ou seja, o valor varia mesmo dentro do mesmo docente. Somar ingenuamente dá 290.106; somar por `(turma, professor)` dá 35.992. **Nenhum dos dois é confiável como capacidade.**

### 2.4 Conflitos estruturais (recalculados)

| Tipo | Ocorrências |
|---|---|
| professor_em_2+_turmas | 654 |
| sala_com_2+_turmas | 1.092 |
| mesma_sala_e_mesmo_professor (provavel co-oferta) | 470 |

*Suposição declarada:* Choque de professor/sala e contado sobre (periodo, dia, hora_inicio). Quando sala E professor coincidem, tratamos como co-oferta (uma aula so), nao conflito.

## 3. Case 1 — Carreira

### 3.1 Integridade de chaves

| Junção | Situação | Detalhe |
|---|---|---|
| vagas.vaga_id -> vaga_cursos | OK | 0 divergencias entre qtd_cursos_elegiveis e a contagem real; 0 vagas sem curso |
| aluno_interesses.aluno_id -> alunos | OK | 0 ids orfaos; cobre 713 de 2187 alunos (32.6%) |
| monitorias.aluno_id -> alunos | QUEBRA ESPERADA | 0 cruzamentos. Sistemas distintos (SGU x Vagas Online), pseudonimizacao separada. Documentado no README do case. |

### 3.2 O vocabulário de curso não fecha — bloqueio crítico

`alunos.csv` tem 56 cursos distintos e `vaga_cursos.csv` tem 51. Após normalizar caixa e acentos, apenas **23 coincidem**. Cobertura: **69.9%** dos alunos têm curso presente em `vaga_cursos.csv`.

| Curso em alunos.csv | Alunos |
|---|---|
| Engenharia | 296 |
| Ciências Econômicas | 172 |
| S/E - Sem Especificacao | 75 |
| Teologia | 13 |
| Pos-Graduacao Em Informatica | 11 |
| Pos-Graduacao Em Administracao | 9 |
| Pos-Graduacao Relacoes Internacionais | 9 |
| Inteligência Artificial | 9 |

O caso mais grave é `Engenharia`, que em `vaga_cursos.csv` aparece quebrado em 16 habilitações: `ENGENHARIA AMBIENTAL`, `ENGENHARIA CIVIL`, `ENGENHARIA DE COMPUTACAO`, `ENGENHARIA DE CONTROLE E AUTOMACAO`, `ENGENHARIA DE MATERIAIS`, `ENGENHARIA DE PETROLEO` …

*Tratamento:* `data/processed/case1/curso_de_para.csv` foi gerado como esqueleto com todos os cursos sem correspondência e status `PENDENTE`. O mapeamento será preenchido e **revisado a mão** na Etapa 5 — é **regra de negócio**, não resultado calculado, e será documentado em `docs/assumptions.md`.

### 3.3 Janela temporal — o dataset é histórico

Anúncios de **2025-08-01** a **2026-08-17**. Em 2026-08-28 restam **39 vagas** com `data_termino` no futuro — base pequena demais para uma demonstração de recomendação.

*Regra de negócio:* o produto usa uma **data de referência** configurável dentro da janela para definir 'vaga aberta', exibida na interface. Não é fingir que o dado é de hoje.

Outros pontos: 115 vagas com bolsa 0 ou vazia (mediana R$ 1150); 230 vagas aceitam do 1º ao 10º período e por isso não discriminam no ranqueamento; `periodo_atual` chega a 32 em `alunos.csv` (alunos de pós no cadastro); 1 vaga com término anterior à publicação.

Jornadas: A Combinar 1.664, Integral 1.444, Tarde 336, Manhã 106.

### 3.4 Duplicatas menores

Fora do Case 3, há duplicação exata em: `aluno_interesses.csv` (2 linhas), `monitorias.csv` (29 linhas). São poucas, mas contam duas vezes em qualquer agregação — removidas na leitura.

### 3.5 Dado de iniciação científica existe — e não está documentado

O README do Case 1 afirma que IC não está no pacote. `PibicPibiti_vagasoferecidas.xlsx` está lá, com abas ['pibiti', 'pibic'], 2006–2026, 27 departamentos e 5.518 vagas no total (300 em 2026). É **agregado por departamento e ano**, não individual — serve para dimensionar a modalidade, não para recomendar a um aluno específico.

## 4. Case 2 — Mobilidade

### 4.1 Bicicletário — a fonte mais confiável do pacote

1.358 ciclistas em 65 dias (2026-05-04 a 2026-07-31). O agregado `uso_por_dia_hora.csv` **confere** com `sessoes.csv`: soma idêntica.

- Flag `suspeita_saida_nao_registrada = S`: 1.720 sessões (>14h).
- **Não coberto pela flag:** 70 sessões com duração ≤ 0 min, e a duração máxima é 87.812 min (61 dias).
- `ocupacao_estimada.csv` chega a **-1** em 4 horas — ocupação negativa é a prova aritmética do viés das saídas não registradas.

*Tratamento:* `data/processed/case2/bike_perfil_horario.csv` traz média, máximo e nº de observações por hora. O produto usa **risco relativo** (posição da hora na curva), não previsão absoluta de vagas — a capacidade instalada não está no dado.

### 4.2 Estacionamento — planilha

**As três abas não têm o mesmo cabeçalho**, ao contrário do que diz o README do case:

| Aba | Header na linha | Nº de colunas |
|---|---|---|
| 17 e 18 de Agosto | 1 | 10 |
| 19 e 20 de Agosto | 2 | 10 |
| 21 de Agosto | 2 | 9 |

*Tratamento:* `_load_sheet()` localiza a linha do cabeçalho procurando a célula `Ticket` e seleciona as 8 colunas comuns pelo nome. Um `concat` direto perde dados em silêncio.

- 183 valores de `ID` repetidos (as abas se sobrepõem nas viradas de dia).
- Status: Fora 5.617, Dentro 1.207, Pago 34 — mas **1.323 linhas sem `Horário de Saída`**, mais que o total de `Dentro`. Filtrar por status deixa passar registros sem permanência.
- Dias cobertos: 2026-08-17 (1.445), 2026-08-18 (1.476), 2026-08-19 (1.362), 2026-08-20 (1.399), 2026-08-21 (1.164), 2026-08-22 (12) — há registros fora da janela declarada de 17 a 21/08.
- Permanência mediana 276.7 min; pico de entrada às **7h** (o da bike é às 9h).

### 4.3 Estacionamento — PDFs: cada arquivo é uma cancela, e falta uma

Dois problemas encadeados:

1. **O texto extrai com todos os caracteres duplicados** (o relatório MBS32 é renderizado em negrito por sobreposição): `8811` é 81. `common.undup_chars()` colapsa os pares. Sem isso os números saem centenas de vezes maiores, silenciosamente.
2. **Cada PDF cobre uma cancela isolada** — `AC6_ENTRADA_2`, `AC6_SAIDA_REV`, `AC7_SAIDA` — e a coluna `Veículos no Estacionamento` é o saldo *daquela cancela*, não do estacionamento. Somando as três por hora, a reconstrução fica negativa toda tarde:

| Dia | Entradas | Saídas | Pico | Mínimo |
|---|---|---|---|---|
| 2026-08-17 | 660 | 812 | 261 | -152 |
| 2026-08-18 | 689 | 868 | 241 | -179 |
| 2026-08-19 | 685 | 839 | 254 | -154 |
| 2026-08-20 | 685 | 839 | 260 | -154 |
| 2026-08-21 | 538 | 622 | 269 | -84 |

Em todos os cinco dias há mais saídas que entradas: **falta pelo menos uma cancela de entrada no pacote**. Note também que 19/08 e 20/08 têm totais idênticos — possível relatório duplicado na origem, a confirmar com a DSI.

*Suposição declarada:* a **forma** da curva (sobe de manhã, satura, esvazia) é utilizável; o **nível** não é. Contra a capacidade de 360 vagas do rotativo, o pico reconstruído é **piso, não medida**. O produto exibe risco relativo e nunca 'restam N vagas'.

## 5. Case 4 — Vida no campus

**SEM DADOS.** Nenhum arquivo de cardápio foi entregue — por desenho, o time constrói a base. `data/processed/case4/cardapios.csv` foi criado **vazio, só com o cabeçalho** esperado:

```
ponto_venda,categoria,item,preco_brl,vegetariano,vegano,sem_gluten,sem_lactose,tempo_estimado_min,horario_abre,horario_fecha,data_coleta,origem
```

*Regra de negócio:* enquanto o arquivo estiver vazio, a interface exibe **"Base de restaurantes ainda não carregada"**. Nenhum restaurante fictício é gerado em nenhuma circunstância.

## 6. Prontidão do Demo Mode

A persona Ana depende de quatro códigos existirem em 2026.1 com pelo menos duas turmas cada (senão não há grades alternativas para comparar):

| Código | Turmas em 2026.1 | Blocos | Apto |
|---|---|---|---|
| MAT4161 | 6 | 18 | sim |
| ENG4010 | 9 | 18 | sim |
| ENG4025 | 9 | 9 | sim |
| MAT4001 | 13 | 13 | sim |

O Demo Mode carrega o perfil e roda **os mesmos motores** do modo normal. Nenhum horário, score ou contagem é fixado no código.

## 7. Arquivos gerados em `data/processed/`

| Case | Arquivo |
|---|---|
| 1 | curso_de_para.csv (esqueleto, 33 cursos sem match) |
| 1 | vagas_limpo.csv |
| 1 | ic_vagas_por_departamento.csv |
| 2 | bike_perfil_horario.csv |
| 2 | estacionamento_tickets.csv |
| 2 | estacionamento_ocupacao_reconstruida.csv |
| 3 | turmas_horarios_dedup.csv (26655 linhas) |
| 3 | blocos_unicos.csv (7952) |
| 3 | disciplinas_catalogo.csv (1825, 898 com nome do catalogo) |
| 4 | cardapios.csv (vazio, apenas o cabecalho esperado) |

`data/raw/` nunca é modificado. Reexecutar `python scripts/audit.py` regenera `data/processed/` e este documento inteiro.
