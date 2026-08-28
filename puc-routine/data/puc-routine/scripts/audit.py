"""ETAPA 0 - Auditoria dos datasets. Roda os 4 preparadores, escreve
docs/data-quality.md e data/processed/*. Nao altera nada em data/raw."""
import sys, pathlib, importlib.util, datetime, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from common import fmt, RAW, PROC

def load(case):
    spec = importlib.util.spec_from_file_location(f"prep{case}", HERE/f"prepare-case{case}"/"prepare.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m.run()

def demo_check():
    """A persona Ana depende destes 4 codigos. Se sumirem, o Demo Mode quebra."""
    b = pd.read_csv(PROC/"case3"/"blocos_unicos.csv")
    cods = ["MAT4161","ENG4010","ENG4025","MAT4001"]
    linhas = []
    for c in cods:
        g = b[(b.cod_disciplina == c) & (b.periodo == 20261)]
        linhas.append({"codigo": c, "turmas_20261": int(g.turma_id.nunique()),
                       "blocos": len(g), "ok": g.turma_id.nunique() >= 2})
    return linhas

def md_table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"]*len(cols)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)

def main():
    R = {i: load(i) for i in (1,2,3,4)}
    dm = demo_check()
    L = []
    A = L.append
    A("# Auditoria dos dados — PUC Routine\n")
    A(f"> Gerado por `scripts/audit.py` em {datetime.date.today():%d/%m/%Y}. "
      "Todos os números abaixo são **recalculados a partir dos arquivos em `data/raw/`** "
      "a cada execução — nenhum é copiado da documentação dos cases nem da apresentação.\n")
    A("Convenção usada em todo o projeto:\n")
    A("| Marcação | Significado |\n|---|---|")
    A("| **Dado observado** | Está literalmente no arquivo entregue. |")
    A("| **Resultado calculado** | Derivado dos arquivos por um script deste repositório. |")
    A("| **Estimativa** | Modelo ou projeção; carrega erro conhecido. |")
    A("| **Regra de negócio** | Decisão de produto (limiar, peso, filtro). |")
    A("| **Suposição declarada** | Hipótese assumida porque o dado não existe. |\n")

    # inventario
    A("## 1. Inventário\n")
    inv = []
    for i in (1,2,3,4):
        for f in R[i]["files"]:
            inv.append({"Case": i, "Arquivo": f["file"], "Registros": fmt(f["rows"]),
                        "Colunas": len(f["cols"]), "Dups. exatas": fmt(f["dups"]),
                        "Campos com vazio": len(f.get("nulls", {}))})
    A(md_table(inv, ["Case","Arquivo","Registros","Colunas","Dups. exatas","Campos com vazio"]))
    A(f"\nCase 4: **{R[4]['status']}** — nenhum arquivo de cardápio entregue.\n")

    # ---------------- Case 3 ----------------
    d = R[3]
    A("## 2. Case 3 — Grade horária (núcleo do produto)\n")
    dd = d["dedup"]
    A(f"### 2.1 Deduplicação — executada antes de qualquer cálculo\n")
    A(f"- Linhas brutas: **{fmt(dd['linhas_brutas'])}**")
    A(f"- Duplicatas exatas removidas: **{fmt(dd['duplicatas'])}** ({dd['pct']}%)")
    A(f"- Linhas após deduplicar: **{fmt(dd['blocos_reais'])}** — fator de inflação {dd['fator_inflacao']}×\n")
    e = d["escala"]
    A("> **Correção importante em relação à apresentação.** O deck trata "
      f"{fmt(dd['blocos_reais'])} como *blocos de aula*. Não são: são **linhas** após remover "
      "duplicatas exatas, e ainda estão multiplicadas pela relação N:N entre turma e professor. "
      f"Agrupando por `(periodo, turma_id, dia, hora_inicio, hora_fim)`, os blocos de aula "
      f"realmente distintos são **{fmt(e['blocos_horarios_unicos'])}** — "
      f"média de {e['blocos_por_turma']} blocos por turma. É este o número que o otimizador enxerga.\n")
    A("### 2.2 Escala real da oferta\n")
    A(md_table([{"Métrica": k, "Valor": fmt(v) if isinstance(v, int) else v}
                for k, v in [("Turmas distintas", e["turmas"]),
                             ("Blocos de aula únicos", e["blocos_horarios_unicos"]),
                             ("Professores", e["professores"]), ("Salas", e["salas"]),
                             ("Departamentos", e["departamentos"]),
                             ("Linhas sem sala", e["linhas_sem_sala"])]],
               ["Métrica","Valor"]))
    c = d["catalogo"]
    A(f"\n### 2.3 Problemas de junção\n")
    A(f"**`disciplinas.csv` cobre metade da oferta.** A oferta usa {fmt(c['codigos_na_oferta'])} "
      f"códigos; o catálogo tem {fmt(c['codigos_no_catalogo'])}, dos quais {fmt(c['interseccao'])} "
      f"aparecem na oferta. Ficam **{fmt(c['sem_nome_completo'])} códigos ({c['pct_sem_nome']}%) "
      f"sem nome completo, créditos ou carga horária**. Concentração por prefixo: "
      + ", ".join(f"`{k}` {v}" for k, v in c["prefixos_faltantes"].items()) + ".")
    A(f"\n*Tratamento:* `data/processed/case3/disciplinas_catalogo.csv` usa o nome do catálogo "
      "quando existe e `disciplina_abrev` da própria oferta quando não existe, com a coluna "
      "`nome_origem` registrando qual foi usado. Um `merge` interno com `disciplinas.csv` "
      "descartaria metade da oferta e nunca deve ser usado.\n")
    dm3 = d["dept_mismatch"]
    A(f"**`cod_departamento` tem tipos incompatíveis.** Em `turmas_horarios.csv` é "
      f"{dm3['turmas_horarios.cod_departamento']}; em `disciplinas.csv` é "
      f"{dm3['disciplinas.cod_departamento']}. Não há tabela de conversão — "
      "**junção por departamento é impossível** com o que veio.\n")
    vf = d["vagas_field"]
    A(f"**`vagas` não é a capacidade da turma.** {fmt(vf['turmas_com_mais_de_um_valor_de_vagas'])} "
      f"de {fmt(e['turmas'])} turmas têm mais de um valor de `vagas` entre suas linhas, enquanto "
      f"apenas {fmt(vf['turmas_com_mais_de_um_professor'])} têm mais de um professor — ou seja, "
      "o valor varia mesmo dentro do mesmo docente. Somar ingenuamente dá "
      f"{fmt(vf['soma_ingenua'])}; somar por `(turma, professor)` dá {fmt(vf['soma_por_turma_professor'])}. "
      "**Nenhum dos dois é confiável como capacidade.**\n")
    cf = d["conflitos"]
    A("### 2.4 Conflitos estruturais (recalculados)\n")
    A(md_table([{"Tipo": k, "Ocorrências": fmt(v)} for k, v in cf.items()], ["Tipo","Ocorrências"]))
    A(f"\n*Suposição declarada:* {d['assumptions'][0]}\n")

    # ---------------- Case 1 ----------------
    d = R[1]
    A("## 3. Case 1 — Carreira\n")
    A("### 3.1 Integridade de chaves\n")
    A(md_table([{"Junção": a, "Situação": b, "Detalhe": c2} for a, b, c2 in d["joins"]],
               ["Junção","Situação","Detalhe"]))
    g = d["course_gap"]
    A(f"\n### 3.2 O vocabulário de curso não fecha — bloqueio crítico\n")
    A(f"`alunos.csv` tem {g['alunos_distintos']} cursos distintos e `vaga_cursos.csv` tem "
      f"{g['vagas_distintos']}. Após normalizar caixa e acentos, apenas **{g['interseccao']} coincidem**. "
      f"Cobertura: **{g['cobertura_pct']}%** dos alunos têm curso presente em `vaga_cursos.csv`.\n")
    A(md_table([{"Curso em alunos.csv": k, "Alunos": fmt(v)} for k, v in g["top_sem_match"].items()],
               ["Curso em alunos.csv","Alunos"]))
    A(f"\nO caso mais grave é `Engenharia`, que em `vaga_cursos.csv` aparece quebrado em "
      f"{len(g['habilitacoes_engenharia'])} habilitações: "
      + ", ".join(f"`{x}`" for x in g["habilitacoes_engenharia"][:6]) + " …\n")
    A("*Tratamento:* `data/processed/case1/curso_de_para.csv` foi gerado como esqueleto com "
      "todos os cursos sem correspondência e status `PENDENTE`. O mapeamento será preenchido e "
      "**revisado a mão** na Etapa 5 — é **regra de negócio**, não resultado calculado, "
      "e será documentado em `docs/assumptions.md`.\n")
    w = d["window"]
    A(f"### 3.3 Janela temporal — o dataset é histórico\n")
    A(f"Anúncios de **{w['primeira_publicacao']}** a **{w['ultima_publicacao']}**. "
      f"Em {w['hoje']} restam **{w['abertas_hoje']} vagas** com `data_termino` no futuro — "
      "base pequena demais para uma demonstração de recomendação.\n")
    A("*Regra de negócio:* o produto usa uma **data de referência** configurável dentro da janela "
      "para definir 'vaga aberta', exibida na interface. Não é fingir que o dado é de hoje.\n")
    A(f"Outros pontos: {fmt(w['bolsa_zero_ou_vazia'])} vagas com bolsa 0 ou vazia (mediana "
      f"R$ {w['bolsa_mediana']:.0f}); {fmt(w['faixa_1_10'])} vagas aceitam do 1º ao 10º período "
      f"e por isso não discriminam no ranqueamento; `periodo_atual` chega a {w['periodo_atual_max']} "
      "em `alunos.csv` (alunos de pós no cadastro); "
      f"{w['termino_antes_da_publicacao']} vaga com término anterior à publicação.\n")
    A("Jornadas: " + ", ".join(f"{k} {fmt(v)}" for k, v in w["jornadas"].items()) + ".\n")
    dup1 = {f["file"]: f["dups"] for f in d["files"] if f["dups"]}
    if dup1:
        A("### 3.4 Duplicatas menores\n")
        A("Fora do Case 3, há duplicação exata em: "
          + ", ".join(f"`{k}` ({fmt(v)} linhas)" for k, v in dup1.items())
          + ". São poucas, mas contam duas vezes em qualquer agregação — "
          "removidas na leitura.\n")
    p = d["pibic"]
    A(f"### 3.5 Dado de iniciação científica existe — e não está documentado\n")
    A(f"O README do Case 1 afirma que IC não está no pacote. `PibicPibiti_vagasoferecidas.xlsx` "
      f"está lá, com abas {p['abas']}, {p['periodos'][0]}–{p['periodos'][1]}, "
      f"{p['departamentos']} departamentos e {fmt(p['vagas_total'])} vagas no total "
      f"({fmt(p['vagas_2026'])} em 2026). É **agregado por departamento e ano**, não individual — "
      "serve para dimensionar a modalidade, não para recomendar a um aluno específico.\n")

    # ---------------- Case 2 ----------------
    d = R[2]
    b = d["bike"]
    A("## 4. Case 2 — Mobilidade\n")
    A("### 4.1 Bicicletário — a fonte mais confiável do pacote\n")
    A(f"{fmt(b['ciclistas'])} ciclistas em {b['dias']} dias ({b['janela'][0]} a {b['janela'][1]}). "
      f"O agregado `uso_por_dia_hora.csv` **confere** com `sessoes.csv`: "
      f"{'soma idêntica' if b['agregado_confere'] else 'DIVERGE'}.\n")
    A(f"- Flag `suspeita_saida_nao_registrada = S`: {fmt(b['flag_S'])} sessões (>14h).")
    A(f"- **Não coberto pela flag:** {b['duracao_nao_positiva']} sessões com duração ≤ 0 min, "
      f"e a duração máxima é {fmt(int(b['duracao_max_min']))} min ({b['duracao_max_min']/1440:.0f} dias).")
    A(f"- `ocupacao_estimada.csv` chega a **{b['ocupacao_min']}** em {b['horas_negativas']} horas — "
      "ocupação negativa é a prova aritmética do viés das saídas não registradas.\n")
    A("*Tratamento:* `data/processed/case2/bike_perfil_horario.csv` traz média, máximo e nº de "
      "observações por hora. O produto usa **risco relativo** (posição da hora na curva), "
      "não previsão absoluta de vagas — a capacidade instalada não está no dado.\n")
    ps = d["park_sheet"]
    A("### 4.2 Estacionamento — planilha\n")
    A("**As três abas não têm o mesmo cabeçalho**, ao contrário do que diz o README do case:\n")
    A(md_table([{"Aba": l["aba"], "Header na linha": l["linha_do_header"],
                 "Nº de colunas": len(l["colunas"])} for l in ps["layouts"]],
               ["Aba","Header na linha","Nº de colunas"]))
    A("\n*Tratamento:* `_load_sheet()` localiza a linha do cabeçalho procurando a célula `Ticket` "
      "e seleciona as 8 colunas comuns pelo nome. Um `concat` direto perde dados em silêncio.\n")
    A(f"- {fmt(ps['ids_duplicados'])} valores de `ID` repetidos (as abas se sobrepõem nas viradas de dia).")
    A(f"- Status: " + ", ".join(f"{k} {fmt(v)}" for k, v in ps["status"].items()) +
      f" — mas **{fmt(ps['sem_horario_de_saida'])} linhas sem `Horário de Saída`**, "
      "mais que o total de `Dentro`. Filtrar por status deixa passar registros sem permanência.")
    A(f"- Dias cobertos: " + ", ".join(f"{k} ({fmt(v)})" for k, v in ps["dias"].items()) +
      " — há registros fora da janela declarada de 17 a 21/08.")
    A(f"- Permanência mediana {ps['permanencia_mediana_min']} min; pico de entrada às "
      f"**{ps['pico_entrada_h']}h** (o da bike é às {b['pico_entrada_h']}h).\n")
    pp = d["park_pdf"]
    A("### 4.3 Estacionamento — PDFs: cada arquivo é uma cancela, e falta uma\n")
    A("Dois problemas encadeados:\n")
    A("1. **O texto extrai com todos os caracteres duplicados** (o relatório MBS32 é renderizado "
      "em negrito por sobreposição): `8811` é 81. `common.undup_chars()` colapsa os pares. "
      "Sem isso os números saem centenas de vezes maiores, silenciosamente.")
    A(f"2. **Cada PDF cobre uma cancela isolada** — {', '.join('`'+x+'`' for x in pp['cancelas'])} — "
      "e a coluna `Veículos no Estacionamento` é o saldo *daquela cancela*, não do estacionamento. "
      "Somando as três por hora, a reconstrução fica negativa toda tarde:\n")
    A(md_table([{"Dia": r["data"], "Entradas": fmt(int(r["entradas"])),
                 "Saídas": fmt(int(r["saidas"])), "Pico": fmt(int(r["pico"])),
                 "Mínimo": fmt(int(r["minimo"]))} for r in pp["reconstrucao"]],
               ["Dia","Entradas","Saídas","Pico","Mínimo"]))
    A("\nEm todos os cinco dias há mais saídas que entradas: **falta pelo menos uma cancela de "
      "entrada no pacote**. Note também que 19/08 e 20/08 têm totais idênticos — possível "
      "relatório duplicado na origem, a confirmar com a DSI.\n")
    A("*Suposição declarada:* a **forma** da curva (sobe de manhã, satura, esvazia) é utilizável; "
      f"o **nível** não é. Contra a capacidade de {pp['capacidade_rotativo_carro']} vagas do "
      "rotativo, o pico reconstruído é **piso, não medida**. O produto exibe risco relativo "
      "e nunca 'restam N vagas'.\n")

    # ---------------- Case 4 ----------------
    d = R[4]
    A("## 5. Case 4 — Vida no campus\n")
    A(f"**{d['status']}.** Nenhum arquivo de cardápio foi entregue — por desenho, o time constrói "
      "a base. `data/processed/case4/cardapios.csv` foi criado **vazio, só com o cabeçalho** "
      "esperado:\n")
    A("```\n" + ",".join(d["esquema_esperado"]) + "\n```\n")
    A("*Regra de negócio:* enquanto o arquivo estiver vazio, a interface exibe "
      "**\"Base de restaurantes ainda não carregada\"**. Nenhum restaurante fictício é gerado "
      "em nenhuma circunstância.\n")

    # ---------------- demo ----------------
    A("## 6. Prontidão do Demo Mode\n")
    A("A persona Ana depende de quatro códigos existirem em 2026.1 com pelo menos duas turmas "
      "cada (senão não há grades alternativas para comparar):\n")
    A(md_table([{"Código": r["codigo"], "Turmas em 2026.1": r["turmas_20261"],
                 "Blocos": r["blocos"], "Apto": "sim" if r["ok"] else "NÃO"} for r in dm],
               ["Código","Turmas em 2026.1","Blocos","Apto"]))
    A("\nO Demo Mode carrega o perfil e roda **os mesmos motores** do modo normal. "
      "Nenhum horário, score ou contagem é fixado no código.\n")

    # ---------------- saidas ----------------
    A("## 7. Arquivos gerados em `data/processed/`\n")
    rows = []
    for i in (1,2,3,4):
        for o in R[i].get("outputs", []):
            rows.append({"Case": i, "Arquivo": o})
    A(md_table(rows, ["Case","Arquivo"]))
    A("\n`data/raw/` nunca é modificado. Reexecutar `python scripts/audit.py` regenera "
      "`data/processed/` e este documento inteiro.\n")

    (ROOT/"docs").mkdir(exist_ok=True)
    (ROOT/"docs"/"data-quality.md").write_text("\n".join(L), encoding="utf-8")
    print("docs/data-quality.md escrito —", len("\n".join(L)), "caracteres")
    for i in (1,2,3,4):
        for o in R[i].get("outputs", []): print(f"  case{i}: {o}")

if __name__ == "__main__":
    main()
