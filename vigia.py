#!/usr/bin/env python3
"""Vigia do robo do Instagram. Roda no GitHub Actions, sem depender do Claude.
Se algo estiver errado o job FALHA e o proprio GitHub manda e-mail ao dono do repositorio.
Confere: (1) site no ar, (2) estoque de cada fila, (3) arquivos das proximas postagens existem."""
import json, os, sys, urllib.request

problemas, avisos = [], []

REPO = "https://github.com/gustavobaronidog-ctrl/robo-instagram-tem-encaixe"
ESTADO_DE = {"carrosseis": "estado.json", "reels de carrossel": "estado_reels.json", "videos de dica": "estado_anuncios.json"}

def prob(msg, sem, com):
    """Registra problema com a solucao: o que o Gustavo faz sozinho e o que o Claude faz."""
    problemas.append((msg, sem, com))

def fmt(msg, sem, com):
    # %0A = quebra de linha nos avisos do GitHub (aparece tambem no e-mail)
    return f"{msg}%0A>> SEM O CLAUDE: {sem}%0A>> COM O CLAUDE: {com}%0A>> Guia completo: {REPO}/blob/main/SOCORRO.md"

SEM_CONTEUDO = ("abra {repo}/blob/main/{est} , clique no lapis, troque o numero de \"proximo\" por 0 (a fila recomeca do inicio e "
                "reposta conteudo antigo, sem parar o robo), clique em Commit changes. Depois crie conteudo novo com calma.")
COM_CONTEUDO = "abra o Claude e escreva: criar mais conteudo para a fila do robo do Tem Encaixe ({nome})."

FILAS = [
    ("carrosseis", "fila.json", "estado.json", 3),
    ("reels de carrossel", "fila_reels.json", "estado_reels.json", 3),
    ("videos de dica", "fila_anuncios.json", "estado_anuncios.json", 3),
]

SEM_SITE = ("abra vercel.com , entre no projeto do Tem Encaixe, aba Deployments, ache o ultimo deploy marcado 'Ready' que "
            "funcionava, clique nos 3 pontinhos e em 'Promote to Production' (volta o site anterior em 1 minuto). Se o site abrir normal no seu celular, foi so uma falha passageira: ignore.")
COM_SITE = "abra o Claude e escreva: o site temencaixe.com caiu, diagnostique e corrija."

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
        prob(f"{nome}: nao consegui ler {fila}/{est} ({e})",
             f"abra {REPO}/commits/main , clique no ultimo commit que mexeu em {fila} ou {est}, depois em 'Revert' (desfazer) e confirme.",
             "abra o Claude e escreva: o vigia do robo do Tem Encaixe nao consegue ler a fila, conserte.")
        continue
    resta = len(q) - p
    dias = resta / por_dia
    print(f"{nome}: faltam {resta} posts = {dias:.0f} dias de estoque")
    if resta <= 0:
        prob(f"{nome}: a fila ACABOU, nada sera postado",
             SEM_CONTEUDO.format(repo=REPO, est=ESTADO_DE[nome]), COM_CONTEUDO.format(nome=nome))
    elif dias < 2:
        prob(f"{nome}: estoque para menos de 2 dias ({resta} posts)",
             SEM_CONTEUDO.format(repo=REPO, est=ESTADO_DE[nome]), COM_CONTEUDO.format(nome=nome))
    elif dias < 5:
        avisos.append(f"{nome}: estoque baixo, {dias:.0f} dias")
    faltando = [a for it in q[p:p + 12] for a in arquivos(it) if not os.path.exists(a)]
    if faltando:
        prob(f"{nome}: arquivos que faltam no GitHub: {', '.join(faltando[:8])}",
             f"para o robo nao travar, abra {REPO}/blob/main/{ESTADO_DE[nome]} , clique no lapis, some 1 ao numero de 'proximo' (pula o post com defeito) e clique em Commit changes. "
             "Depois suba os arquivos que faltam: Add file > Upload files na pasta imagens/ (fotos) ou reels/ (videos).",
             "abra o Claude e escreva: conferir os arquivos que faltam no robo do Tem Encaixe e subir.")

for url in ["https://www.temencaixe.com"]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "vigia-github"})
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"site {url}: HTTP {r.status}")
            if r.status >= 400:
                prob(f"site fora do ar: {url} HTTP {r.status}", SEM_SITE, COM_SITE)
    except Exception as e:
        prob(f"site fora do ar: {url} ({e})", SEM_SITE, COM_SITE)

for a in avisos:
    print(f"::warning::{a}")
if problemas:
    resumo = os.environ.get("GITHUB_STEP_SUMMARY")
    for m, sem, com in problemas:
        print(f"::error title=Robo Tem Encaixe::{fmt(m, sem, com)}")
        if resumo:
            with open(resumo, "a", encoding="utf-8") as f:
                f.write(f"### Problema: {m}\n- **Sem o Claude:** {sem}\n- **Com o Claude:** {com}\n\n")
    sys.exit(1)
print("Tudo certo.")
