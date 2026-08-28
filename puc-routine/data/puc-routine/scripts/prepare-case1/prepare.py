"""Case 1 - Oportunidades. Auditoria + geracao de data/processed/case1."""
import sys, pathlib, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import RAW, norm, out

D = RAW / "case1"

def run():
    r = {"case": "Case 1 - Oportunidades", "files": [], "findings": [], "assumptions": []}
    v  = pd.read_csv(D/"vagas.csv")
    vc = pd.read_csv(D/"vaga_cursos.csv")
    a  = pd.read_csv(D/"alunos.csv")
    ai = pd.read_csv(D/"aluno_interesses.csv")
    m  = pd.read_csv(D/"monitorias.csv")
    xl = pd.ExcelFile(D/"PibicPibiti_vagasoferecidas.xlsx")
    pib = {sh: xl.parse(sh) for sh in xl.sheet_names}

    for nm, df in [("vagas.csv",v),("vaga_cursos.csv",vc),("alunos.csv",a),
                   ("aluno_interesses.csv",ai),("monitorias.csv",m)]:
        r["files"].append({"file": nm, "rows": len(df), "cols": list(df.columns),
                           "dups": int(df.duplicated().sum()),
                           "nulls": {k:int(x) for k,x in df.isna().sum().items() if x}})
    for sh, df in pib.items():
        r["files"].append({"file": f"PibicPibiti_vagasoferecidas.xlsx :: aba '{sh}'",
                           "rows": len(df), "cols": list(df.columns),
                           "dups": int(df.duplicated().sum()), "nulls": {}})

    # --- integridade de chaves ---
    r["joins"] = []
    cnt = vc.groupby("vaga_id").size().reindex(v.vaga_id).fillna(0)
    r["joins"].append(("vagas.vaga_id -> vaga_cursos", "OK",
        f"{int((v.set_index('vaga_id').qtd_cursos_elegiveis != cnt).sum())} divergencias entre "
        f"qtd_cursos_elegiveis e a contagem real; {int((~v.vaga_id.isin(vc.vaga_id)).sum())} vagas sem curso"))
    r["joins"].append(("aluno_interesses.aluno_id -> alunos", "OK",
        f"{int((~ai.aluno_id.isin(a.aluno_id)).sum())} ids orfaos; cobre "
        f"{ai.aluno_id.nunique()} de {a.aluno_id.nunique()} alunos "
        f"({ai.aluno_id.nunique()/a.aluno_id.nunique()*100:.1f}%)"))
    xr = int(m.aluno_id.isin(a.aluno_id).sum())
    r["joins"].append(("monitorias.aluno_id -> alunos", "QUEBRA ESPERADA",
        f"{xr} cruzamentos. Sistemas distintos (SGU x Vagas Online), pseudonimizacao separada. "
        "Documentado no README do case."))

    # --- vocabulario de curso (a quebra critica) ---
    a["_c"] = a.curso.map(norm); vc["_c"] = vc.curso.map(norm)
    sa, sv = set(a._c), set(vc._c)
    cob = a._c.isin(sv)
    sem = a[~cob].curso.value_counts()
    r["course_gap"] = {
        "alunos_distintos": len(sa), "vagas_distintos": len(sv),
        "interseccao": len(sa & sv),
        "cobertura_pct": round(cob.mean()*100, 1),
        "top_sem_match": sem.head(8).to_dict(),
        "habilitacoes_engenharia": sorted(x for x in sv if x.startswith("ENGENHARIA")),
    }

    # --- janela temporal / vagas abertas ---
    v["_pub"] = pd.to_datetime(v.data_publicacao, errors="coerce")
    v["_fim"] = pd.to_datetime(v.data_termino, errors="coerce")
    hoje = pd.Timestamp.today().normalize()
    r["window"] = {
        "primeira_publicacao": str(v._pub.min().date()),
        "ultima_publicacao": str(v._pub.max().date()),
        "termino_antes_da_publicacao": int((v._fim < v._pub).sum()),
        "abertas_hoje": int((v._fim >= hoje).sum()),
        "hoje": str(hoje.date()),
        "jornadas": v.jornada.value_counts().to_dict(),
        "bolsa_zero_ou_vazia": int(((v.bolsa_mensal_brl == 0) | v.bolsa_mensal_brl.isna()).sum()),
        "bolsa_mediana": float(v.bolsa_mensal_brl.median()),
        "faixa_1_10": int(((v.periodo_min == 1) & (v.periodo_max == 10)).sum()),
        "periodo_atual_max": int(a.periodo_atual.max()),
    }

    # --- PIBIC / PIBITI (nao mencionado no README do case) ---
    pb = pd.concat([d.assign(_prog=sh) for sh, d in pib.items()], ignore_index=True)
    pb["Departamento"] = pb.Departamento.astype(str).str.strip()
    r["pibic"] = {
        "abas": list(pib.keys()),
        "linhas": {sh: len(d) for sh, d in pib.items()},
        "periodos": [int(pb.Periodo.min()), int(pb.Periodo.max())],
        "departamentos": int(pb.Departamento.nunique()),
        "vagas_total": int(pb.VagasOferecidas.sum()),
        "vagas_2026": int(pb[pb.Periodo == 2026].VagasOferecidas.sum()),
    }

    # --- saidas processadas ---
    o = out("case1")
    depara = pd.DataFrame({"curso_aluno": sorted(sa - sv)})
    depara["curso_vaga_sugerido"] = ""   # preenchido na Etapa 5, revisado a mao
    depara["status"] = "PENDENTE"
    depara.to_csv(o/"curso_de_para.csv", index=False)
    v.drop(columns=["_pub","_fim"]).to_csv(o/"vagas_limpo.csv", index=False)
    pb.rename(columns={"_prog":"programa"}).to_csv(o/"ic_vagas_por_departamento.csv", index=False)
    r["outputs"] = ["curso_de_para.csv (esqueleto, %d cursos sem match)" % len(depara),
                    "vagas_limpo.csv", "ic_vagas_por_departamento.csv"]
    return r

if __name__ == "__main__":
    import json; print(json.dumps(run(), ensure_ascii=False, indent=1, default=str))
