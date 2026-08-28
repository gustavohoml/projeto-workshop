"""Utilitarios compartilhados pelos scripts de preparacao. Nunca escreve em data/raw."""
import unicodedata, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW  = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"

def norm(s):
    """Uppercase, sem acento, sem espaco nas pontas. Para comparar vocabularios."""
    s = str(s).upper().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def undup_chars(t):
    """Os PDFs do MBS32 sao renderizados em negrito por sobreposicao: cada
    caractere sai duplicado na extracao ('8811' = 81). Colapsa os pares."""
    return re.sub(r'(.)\1', r'\1', t)

def out(case):
    p = PROC / case
    p.mkdir(parents=True, exist_ok=True)
    return p

def fmt(n):
    return f"{n:,}".replace(",", ".")
