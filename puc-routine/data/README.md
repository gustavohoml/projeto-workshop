# Dados — PUC Routine

Os datasets **não são versionados** (ver `.gitignore`). O `USO-DOS-DADOS.md` do Impact Lab
restringe o uso ao workshop da SIEng 2026 e proíbe redistribuição, e os arquivos contêm
pseudônimos de pessoas. Este documento diz o que colocar onde para o projeto rodar.

`data/raw/` é **somente leitura** para o código: nenhum script escreve nela.
Tudo que é tratado nasce em `data/processed/`, regenerável por `python scripts/audit.py`.

## O que colocar em `data/raw/`

### `case1/` — Carreira (origem: Vagas Online/CCESP e SGU)

| Arquivo | Colunas necessárias |
|---|---|
| `vagas.csv` | `vaga_id, data_publicacao, tipo, jornada, bolsa_mensal_brl, periodo_min, periodo_max, num_vagas, cidade, bairro, empresa_id, qtd_cursos_elegiveis, data_termino, atividades, requisitos, beneficios` |
| `vaga_cursos.csv` | `vaga_id, curso` |
| `alunos.csv` | `aluno_id, curso, periodo_atual, habilitacao, bairro, cidade, uf, faixa_idade, matriculado, mes_cadastro` |
| `aluno_interesses.csv` | `aluno_id, area_interesse` |
| `monitorias.csv` | `periodo, aluno_id, cod_disciplina, disciplina, creditos` |
| `PibicPibiti_vagasoferecidas.xlsx` | abas `pibic` e `pibiti`, colunas `Periodo, Departamento, VagasOferecidas` |

### `case2/` — Mobilidade (origem: COBRA e MBS32 Parking Manager)

| Arquivo | Colunas necessárias |
|---|---|
| `bicicletario/sessoes.csv` | `sessao_id, ciclista_id, data, dia_semana, hora_entrada, faixa_hora_entrada, hora_saida, faixa_hora_saida, duracao_min, suspeita_saida_nao_registrada` |
| `bicicletario/ocupacao_estimada.csv` | `data, dia_semana, hora, bicicletas_no_bicicletario` |
| `bicicletario/uso_por_dia_hora.csv` | `dia_semana, faixa_hora_entrada, entradas` |
| `estacionamento/FLUXO ESTACIONAMENTO PUC - *.xlsx` | 3 abas; cabeçalho localizado pela célula `Ticket` — as abas **não** têm o mesmo layout |
| `estacionamento/*.pdf` | relatórios de fluxo do MBS32, um por cancela por dia |
| `estacionamento/capacidade_interno_zonas.csv` | `zona, vagas_carro` |

### `case3/` — Grade horária (origem: micro-horário do SGU)

| Arquivo | Colunas necessárias |
|---|---|
| `turmas_horarios.csv` | `periodo, turma_id, cod_disciplina, turma, disciplina_abrev, dia_semana, hora_inicio, hora_fim, sala_id, vagas, creditos, professor_id, cod_departamento` |
| `disciplinas.csv` | `cod_disciplina, disciplina, creditos, horas_teoria, horas_pratica, cod_departamento` |

### `case4/` — Vida no campus (coletado pelo time)

Não vem com dataset. Coloque aqui os cardápios coletados, no esquema que
`data/processed/case4/cardapios.csv` define:

```
ponto_venda, categoria, item, preco_brl, vegetariano, vegano, sem_gluten,
sem_lactose, tempo_estimado_min, horario_abre, horario_fecha, data_coleta, origem
```

`origem` distingue `real` de `ficticio`. Enquanto o arquivo estiver vazio, a interface
mostra "Base de restaurantes ainda não carregada" — nunca dados de exemplo.

## Regenerar os dados tratados

```bash
python scripts/audit.py
```

Roda os quatro preparadores, reescreve `data/processed/` e `docs/data-quality.md`.

## Privacidade

Todos os identificadores de pessoa vieram pseudonimizados na origem (HMAC-SHA256 com sal
descartado). **Não tente reidentificar ninguém** e não cruze com bases externas. Apresente
sempre padrões agregados, nunca linhas individuais.
