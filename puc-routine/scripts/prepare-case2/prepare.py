"""Case 2 - Mobilidade (bicicletario + estacionamento). Auditoria + processed/case2."""
import sys, pathlib, re, glob, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import RAW, undup_chars, out

B = RAW/"case2"/"bicicletario"
E = RAW/"case2"/"estacionamento"
COLS = ['ID','Ticket','Data de Entrada','Horário de Entrada',
        'Data de Saída','Horário de Saída','Status','Valor']

def _load_sheet(f, sh):
    """As 3 abas NAO tem o mesmo cabecalho: linha do header varia e a aba
    '19 e 20' tem coluna extra 'Placa'. Localiza o header pela celula 'Ticket'."""
    raw = pd.read_excel(f, sh, header=None)
    hdr = next(i for i in range(6) if raw.iloc[i].astype(str).str.contains('Ticket').any())
    d = pd.read_excel(f, sh, header=hdr)
    d.columns = [str(c).strip() for c in d.columns]
    return d[[c for c in COLS if c in d.columns]], hdr, list(d.columns)

def _parse_pdf(path):
    import pdfplumber
    with pdfplumber.open(path) as p:
        t = p.pages[0].extract_text() or ""
    gate = re.search(r'(AC\d[A-Z_0-9]*)', undup_chars(t))
    rows = {}
    for line in t.split("\n"):
        l = undup_chars(line)
        mm = re.match(r'^(\d{2}):00 a \d{2}:59\s+(.*)$', l)
        if mm:
            n = [int(x) for x in mm.group(2).split()]
            rows[int(mm.group(1))] = {"tot_ent": n[-3], "tot_sai": n[-2], "saldo": n[-1]}
    return (gate.group(1) if gate else "?"), rows

def run():
    r = {"case": "Case 2 - Mobilidade", "files": [], "assumptions": []}

    # ---------- bicicletario ----------
    s = pd.read_csv(B/"sessoes.csv")
    o = pd.read_csv(B/"ocupacao_estimada.csv")
    u = pd.read_csv(B/"uso_por_dia_hora.csv")
    for nm, df in [("bicicletario/sessoes.csv",s),("bicicletario/ocupacao_estimada.csv",o),
                   ("bicicletario/uso_por_dia_hora.csv",u)]:
        r["files"].append({"file": nm, "rows": len(df), "cols": list(df.columns),
                           "dups": int(df.duplicated().sum()),
                           "nulls": {k:int(x) for k,x in df.isna().sum().items() if x}})
    r["bike"] = {
        "ciclistas": int(s.ciclista_id.nunique()), "dias": int(s.data.nunique()),
        "janela": [s.data.min(), s.data.max()],
        "flag_S": int((s.suspeita_saida_nao_registrada == 'S').sum()),
        "duracao_max_min": float(s.duracao_min.max()),
        "duracao_nao_positiva": int((s.duracao_min <= 0).sum()),
        "agregado_confere": int(u.entradas.sum()) == len(s),
        "ocupacao_max": int(o.bicicletas_no_bicicletario.max()),
        "ocupacao_min": int(o.bicicletas_no_bicicletario.min()),
        "horas_negativas": int((o.bicicletas_no_bicicletario < 0).sum()),
        "pico_entrada_h": int(s.faixa_hora_entrada.value_counts().idxmax()),
    }
    perfil = o.groupby("hora").bicicletas_no_bicicletario.agg(["mean","max","count"]).round(1)
    perfil.to_csv(out("case2")/"bike_perfil_horario.csv")

    # ---------- estacionamento: planilha ----------
    f = E/"FLUXO ESTACIONAMENTO PUC - 17 a 21 de Agosto.xlsx"
    xl = pd.ExcelFile(f); parts, layouts = [], []
    for sh in xl.sheet_names:
        d, hdr, cols = _load_sheet(f, sh)
        layouts.append({"aba": sh, "linha_do_header": hdr + 1, "colunas": cols})
        parts.append(d)
    df = pd.concat(parts, ignore_index=True).dropna(subset=["Ticket"])
    ent = pd.to_datetime(df["Data de Entrada"].astype(str).str[:10] + " " +
                         df["Horário de Entrada"].astype(str), errors="coerce")
    sai = pd.to_datetime(df["Data de Saída"].astype(str).str[:10] + " " +
                         df["Horário de Saída"].astype(str), errors="coerce")
    dur = (sai - ent).dt.total_seconds()/60
    r["files"].append({"file": "estacionamento/FLUXO ...xlsx (3 abas unidas)",
                       "rows": len(df), "cols": COLS, "dups": int(df.duplicated().sum()), "nulls": {}})
    r["park_sheet"] = {
        "layouts": layouts,
        "tickets_distintos": int(df.Ticket.nunique()),
        "ids_duplicados": int(df.ID.duplicated().sum()),
        "status": df.Status.value_counts().to_dict(),
        "sem_horario_de_saida": int(sai.isna().sum()),
        "dias": {str(k): int(x) for k, x in ent.dt.date.value_counts().sort_index().items()},
        "permanencia_mediana_min": round(float(dur.median()), 1),
        "permanencia_acima_24h": int((dur > 1440).sum()),
        "pico_entrada_h": int(ent.dt.hour.value_counts().idxmax()),
        "entradas_por_hora": ent.dt.hour.value_counts().sort_index().to_dict(),
    }
    df.assign(_entrada=ent, _saida=sai, _duracao_min=dur).to_csv(
        out("case2")/"estacionamento_tickets.csv", index=False)

    # ---------- estacionamento: PDFs ----------
    gates, curvas = [], {}
    for p in sorted(glob.glob(str(E/"*.pdf"))):
        gate, rows = _parse_pdf(p)
        dia = re.match(r'(\d+) de [Aa]gosto', pathlib.Path(p).name)
        dia = f"2026-08-{int(dia.group(1)):02d}" if dia else "?"
        tot_e = sum(x["tot_ent"] for x in rows.values())
        tot_s = sum(x["tot_sai"] for x in rows.values())
        gates.append({"arquivo": pathlib.Path(p).name, "cancela": gate, "dia": dia,
                      "entradas": tot_e, "saidas": tot_s, "saldo_final": rows.get(23,{}).get("saldo")})
        curvas.setdefault(dia, {})
        for h, x in rows.items():
            c = curvas[dia].setdefault(h, {"ent":0,"sai":0})
            c["ent"] += x["tot_ent"]; c["sai"] += x["tot_sai"]
    recon = []
    for dia, hrs in sorted(curvas.items()):
        acc = 0
        for h in range(24):
            c = hrs.get(h, {"ent":0,"sai":0}); acc += c["ent"] - c["sai"]
            recon.append({"data": dia, "hora": h, "entradas": c["ent"],
                          "saidas": c["sai"], "ocupacao_acumulada": acc})
    rec = pd.DataFrame(recon)
    rec.to_csv(out("case2")/"estacionamento_ocupacao_reconstruida.csv", index=False)
    piv = rec.groupby("data").agg(entradas=("entradas","sum"), saidas=("saidas","sum"),
                                  pico=("ocupacao_acumulada","max"),
                                  minimo=("ocupacao_acumulada","min")).reset_index()
    r["park_pdf"] = {
        "cancelas": sorted({g["cancela"] for g in gates}),
        "arquivos_por_cancela": gates,
        "reconstrucao": piv.to_dict("records"),
        "capacidade_rotativo_carro": 360,
    }
    r["outputs"] = ["bike_perfil_horario.csv", "estacionamento_tickets.csv",
                    "estacionamento_ocupacao_reconstruida.csv"]
    return r

if __name__ == "__main__":
    import json; print(json.dumps(run(), ensure_ascii=False, indent=1, default=str))
