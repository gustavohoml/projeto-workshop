"""Case 3 - Grade horaria. Deduplicacao OBRIGATORIA antes de qualquer calculo."""
import sys, pathlib, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import RAW, out

D = RAW/"case3"

def run():
    r = {"case": "Case 3 - Grade horaria (NUCLEO)", "files": [], "assumptions": []}
    th = pd.read_csv(D/"turmas_horarios.csv")
    dc = pd.read_csv(D/"disciplinas.csv")
    bruto = len(th)
    for nm, df in [("turmas_horarios.csv",th),("disciplinas.csv",dc)]:
        r["files"].append({"file": nm, "rows": len(df), "cols": list(df.columns),
                           "dups": int(df.duplicated().sum()),
                           "nulls": {k:int(x) for k,x in df.isna().sum().items() if x}})

    # ---- ETAPA OBRIGATORIA: deduplicar ----
    u = th.drop_duplicates().reset_index(drop=True)
    r["dedup"] = {"linhas_brutas": bruto, "duplicatas": bruto - len(u),
                  "pct": round((bruto-len(u))/bruto*100, 1), "blocos_reais": len(u),
                  "fator_inflacao": round(bruto/len(u), 2)}

    # bloco unico = (periodo, turma_id, dia, hora_inicio, hora_fim); professor e N:N
    blocos = u.drop_duplicates(["periodo","turma_id","dia_semana","hora_inicio","hora_fim"])
    r["escala"] = {
        "turmas": int(u.groupby(["periodo","turma_id"]).ngroups),
        "blocos_horarios_unicos": len(blocos),
        "professores": int(u.professor_id.nunique()),
        "salas": int(u.sala_id.nunique()),
        "departamentos": int(u.cod_departamento.nunique()),
        "periodos": u.periodo.value_counts().to_dict(),
        "blocos_por_turma": round(len(blocos)/u.groupby(["periodo","turma_id"]).ngroups, 2),
        "linhas_sem_sala": int(u.sala_id.isna().sum()),
    }

    # ---- catalogo ----
    ct, cd = set(u.cod_disciplina), set(dc.cod_disciplina)
    falt = ct - cd
    r["catalogo"] = {
        "codigos_na_oferta": len(ct), "codigos_no_catalogo": len(cd),
        "interseccao": len(ct & cd), "sem_nome_completo": len(falt),
        "pct_sem_nome": round(len(falt)/len(ct)*100, 1),
        "catalogo_sem_oferta": len(cd - ct),
        "prefixos_faltantes": pd.Series([c[:3] for c in falt]).value_counts().head(8).to_dict(),
    }
    r["dept_mismatch"] = {
        "turmas_horarios.cod_departamento": f"texto, ex. {sorted(u.cod_departamento.dropna().unique())[:4]}",
        "disciplinas.cod_departamento": f"{dc.cod_departamento.dtype}, ex. {sorted(dc.cod_departamento.unique())[:4]}",
        "juncao_possivel": False,
    }

    # ---- vagas fatiadas por professor ----
    g = u.groupby(["periodo","turma_id"]).agg(vagas_distintos=("vagas","nunique"),
                                              profs=("professor_id","nunique"))
    r["vagas_field"] = {
        "turmas_com_mais_de_um_valor_de_vagas": int((g.vagas_distintos > 1).sum()),
        "turmas_com_mais_de_um_professor": int((g.profs > 1).sum()),
        "soma_ingenua": int(u.vagas.sum()),
        "soma_por_turma_professor": int(u.drop_duplicates(["periodo","turma_id","professor_id"]).vagas.sum()),
    }

    # ---- conflitos (co-oferta separada de choque real) ----
    k = ["periodo","dia_semana","hora_inicio"]
    prof = u.groupby(k+["professor_id"]).turma_id.nunique()
    sala = u.dropna(subset=["sala_id"]).groupby(k+["sala_id"]).turma_id.nunique()
    co = u.dropna(subset=["sala_id"]).groupby(k+["sala_id","professor_id"]).turma_id.nunique()
    r["conflitos"] = {
        "professor_em_2+_turmas": int((prof > 1).sum()),
        "sala_com_2+_turmas": int((sala > 1).sum()),
        "mesma_sala_e_mesmo_professor (provavel co-oferta)": int((co > 1).sum()),
    }
    r["assumptions"].append(
        "Choque de professor/sala e contado sobre (periodo, dia, hora_inicio). "
        "Quando sala E professor coincidem, tratamos como co-oferta (uma aula so), nao conflito.")

    # ---- distribuicao horaria (base do motor) ----
    r["horarios"] = {
        "inicios_mais_comuns": blocos.hora_inicio.value_counts().head(6).to_dict(),
        "por_dia": blocos.dia_semana.value_counts().to_dict(),
    }

    o = out("case3")
    u.to_csv(o/"turmas_horarios_dedup.csv", index=False)
    blocos.to_csv(o/"blocos_unicos.csv", index=False)
    # catalogo enriquecido: nome do catalogo quando existe, senao disciplina_abrev da oferta
    cat = (blocos[["cod_disciplina","disciplina_abrev","cod_departamento"]]
           .drop_duplicates("cod_disciplina")
           .merge(dc[["cod_disciplina","disciplina","creditos","horas_teoria","horas_pratica"]],
                  on="cod_disciplina", how="left"))
    cat["nome"] = cat.disciplina.fillna(cat.disciplina_abrev)
    cat["nome_origem"] = cat.disciplina.notna().map({True:"catalogo", False:"abreviado_da_oferta"})
    cat.to_csv(o/"disciplinas_catalogo.csv", index=False)
    r["outputs"] = ["turmas_horarios_dedup.csv (%d linhas)" % len(u),
                    "blocos_unicos.csv (%d)" % len(blocos),
                    "disciplinas_catalogo.csv (%d, %d com nome do catalogo)" %
                    (len(cat), int(cat.disciplina.notna().sum()))]
    return r

if __name__ == "__main__":
    import json; print(json.dumps(run(), ensure_ascii=False, indent=1, default=str))
