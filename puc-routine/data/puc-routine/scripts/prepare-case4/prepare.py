"""Case 4 - Vida no campus. Sem dataset entregue: o time constroi a base."""
import sys, pathlib, glob
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import RAW, out
import pandas as pd

D = RAW/"case4"
ESQUEMA = ["ponto_venda","categoria","item","preco_brl","vegetariano","vegano",
           "sem_gluten","sem_lactose","tempo_estimado_min","horario_abre","horario_fecha",
           "data_coleta","origem"]

def run():
    achados = [p for p in glob.glob(str(D/"**"/"*"), recursive=True)
               if pathlib.Path(p).is_file() and not p.endswith("README.md")]
    r = {"case": "Case 4 - Vida no campus", "files": [], "assumptions": [],
         "status": "SEM DADOS" if not achados else "DADOS PARCIAIS",
         "esquema_esperado": ESQUEMA,
         "arquivos_encontrados": [pathlib.Path(p).name for p in achados]}
    o = out("case4")
    if not achados:
        pd.DataFrame(columns=ESQUEMA).to_csv(o/"cardapios.csv", index=False)
        r["outputs"] = ["cardapios.csv (vazio, apenas o cabecalho esperado)"]
        r["assumptions"].append(
            "Nenhum cardapio coletado ate agora. A interface deve exibir "
            "'Base de restaurantes ainda nao carregada' em vez de dados de exemplo.")
    return r

if __name__ == "__main__":
    import json; print(json.dumps(run(), ensure_ascii=False, indent=1, default=str))
