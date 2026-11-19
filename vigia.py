#!/usr/bin/env python3
"""Vigia do robo do Instagram. Roda no GitHub Actions, sem depender do Claude.
Se algo estiver errado o job FALHA e o proprio GitHub manda e-mail ao dono do repositorio.
Confere: (1) site no ar, (2) estoque de cada fila, (3) arquivos das proximas postagens existem."""
import json, os, sys, urllib.request

problemas, avisos = [], []

FILAS = [
    ("carrosseis", "fila.json", "estado.json", 3),
    ("reels de carrossel", "fila_reels.json", "estado_reels.json", 3),
    ("videos de dica", "fila_anuncios.json", "estado_anuncios.json", 3),
]

def arquivos(item):
    out = []
    for s in item.get("slides", []):
        out.append(os.path.join("imagens", s))
    for k, v in item.items():
        if isinstance(v, str) and v.lower().endswith(".mp4"):
            out.append(os.path.join("reels", v))
    return out

for nome, fila, est, por_dia in FILAS:
    try:
        q = json.load(open(fila, encoding="utf-8"))
        p = json.load(open(est))["proximo"]
    except Exception as e:
        problemas.append(f"{nome}: nao consegui ler {fila}/{est} ({e})")
        continue
    resta = len(q) - p
    dias = resta / por_dia
    print(f"{nome}: faltam {resta} posts = {dias:.0f} dias de estoque")
    if resta <= 0:
        problemas.append(f"{nome}: a fila ACABOU, nada sera postado")
    elif dias < 2:
        problemas.append(f"{nome}: estoque para menos de 2 dias ({resta} posts). Precisa criar mais conteudo")
    elif dias < 5:
        avisos.append(f"{nome}: estoque baixo, {dias:.0f} dias")
    faltando = [a for it in q[p:p + 12] for a in arquivos(it) if not os.path.exists(a)]
    if faltando:
        problemas.append(f"{nome}: arquivos que faltam no GitHub: {', '.join(faltando[:8])}")

for url in ["https://www.temencaixe.com"]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "vigia-github"})
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"site {url}: HTTP {r.status}")
            if r.status >= 400:
                problemas.append(f"site fora do ar: {url} HTTP {r.status}")
    except Exception as e:
        problemas.append(f"site fora do ar: {url} ({e})")

for a in avisos:
    print(f"::warning::{a}")
if problemas:
    for p in problemas:
        print(f"::error::{p}")
    sys.exit(1)
print("Tudo certo.")
