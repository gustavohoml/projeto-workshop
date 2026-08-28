# PUC ROUTINE
### A rotina acadêmica como sistema de decisão

Impact Lab · SIEng 2026 · PUC-Rio — Case 3 (Grade Horária Automatizada) como núcleo,
Cases 1, 2 e 4 como dimensões da mesma decisão.

---

## Problema

Um aluno da PUC-Rio toma quatro decisões que dependem umas das outras, em quatro
sistemas que não conversam: monta a grade no SGU, procura estágio no Vagas Online da
CCESP, descobre se há vaga de estacionamento quando chega, e organiza alimentação
lendo o cardápio de cada ponto de venda. Cada decisão é tomada no escuro em relação
às outras três.

## Insight

**A grade é a variável que amarra tudo.** Ela define quando o aluno pode trabalhar,
a que horas precisa chegar ao campus e quais intervalos tem ao longo do dia.

## Solução

O Case 3 é o motor. As demais dimensões são consequências da grade escolhida — não
funcionalidades adicionais. O objetivo não é encontrar *uma* grade válida, e sim
**comparar configurações de semestre e tornar explícitos os trade-offs**.

## Arquitetura

```
                 Perfil do aluno
                        │
                        ▼
                 Schedule Optimizer          ← Case 3 (motor de restrições)
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Career        Mobility       Campus    ← Cases 1, 2 e 4 (dimensões)
          └─────────────┼─────────────┘
                        ▼
                PUC Routine Score
```

O solver garante que a grade é **válida**. A camada de IA **explica** a escolha entre
grades válidas. A IA não substitui o motor de restrições — essa separação é parte
explícita da arquitetura.

## Datasets

Nove CSV, dois XLSX e quinze PDF entregues pela DSI da PUC-Rio, mais a base de
cardápios que o time constrói. Os arquivos **não são versionados**; ver
[`data/README.md`](data/README.md) para o que colocar em `data/raw/`.

## Tratamento dos dados

Auditoria completa e recalculável em [`docs/data-quality.md`](docs/data-quality.md),
gerada por `python scripts/audit.py`. Os pontos que mudam resultado:

- **Case 3** — 64,2% das linhas de `turmas_horarios.csv` são duplicatas exatas;
  o catálogo de disciplinas cobre metade da oferta; `cod_departamento` tem tipos
  incompatíveis entre os dois arquivos; `vagas` não é a capacidade da turma.
- **Case 1** — os nomes de curso não casam entre `alunos.csv` e `vaga_cursos.csv`
  (30% dos alunos sem correspondência); o pacote é histórico, não uma bolsa ativa.
- **Case 2** — os PDFs extraem com caracteres duplicados e cada um cobre uma cancela
  isolada; falta pelo menos uma cancela de entrada, então a ocupação do estacionamento
  é usada como risco relativo, nunca como nível absoluto.
- **Case 4** — sem dataset entregue, por desenho.

Cada número exibido na interface é marcado como **dado observado**, **resultado
calculado**, **estimativa**, **regra de negócio** ou **suposição declarada**.

## Como executar

```bash
npm install
python scripts/audit.py     # gera data/processed/ e docs/data-quality.md
npm run dev
```

## Demo Mode

Botão **▶ Executar Demo** no header, ou `?demo=true` na URL. Percorre os oito passos
da história da Ana usando **os mesmos motores** do modo normal — nenhum horário,
score ou contagem é fixado no código.

## Limitações

- Não há matrícula de aluno em turma nem estrutura curricular nos dados: as disciplinas
  são escolhidas pelo aluno, nunca sugeridas pelo sistema.
- O horário de chegada é estimado a partir da primeira aula, não medido.
- A ocupação do estacionamento é relativa; o bicicletário tem série horária real.
- A base de cardápios depende de coleta em campo.

## Próximos passos

Ver [`docs/assumptions.md`](docs/assumptions.md) e o roadmap por etapas no histórico
de commits.

---

Dados: Diretoria de Sistemas de Informação (DSI) — PUC-Rio.
Uso restrito ao Impact Lab da SIEng 2026. Não redistribuir; não reidentificar.
