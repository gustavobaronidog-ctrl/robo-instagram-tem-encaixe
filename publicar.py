#!/usr/bin/env python3
# Robo do Tem Encaixe: publica 1 carrossel no Instagram pela API oficial da Meta.
# Roda no GitHub Actions 3x por dia. Nao depende do computador do Gustavo.
import json, os, sys, time, urllib.parse, urllib.request

import re

APP_ID = "970085075765951"
REDIRECT = "https://www.temencaixe.com/"
SEGREDO = os.environ.get("IG_APP_SECRET", "").strip()
BRUTO = os.environ.get("IG_TOKEN", "").strip()


def _openssl(args, dado):
    import subprocess
    return subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-a", "-A", *args,
                           "-pass", "env:IG_APP_SECRET"], input=dado.encode(),
                          capture_output=True, check=True).stdout.decode().strip()


def obter_token():
    # 1) token ja guardado (cifrado com a chave secreta do app)
    if os.path.exists("token.enc") and SEGREDO:
        return _openssl(["-d"], open("token.enc").read().strip())
    m = re.search(r"long_lived_token=([^&#\s]+)", BRUTO) or re.search(r"access_token=([^&#\s]+)", BRUTO)
    if m:
        return urllib.parse.unquote(m.group(1))
    c = re.search(r"[?&#]code=([^&#\s]+)", BRUTO)
    if c:  # troca o codigo do login pelo token definitivo, uma vez so
        q = urllib.parse.urlencode({"client_id": APP_ID, "client_secret": SEGREDO,
                                    "redirect_uri": REDIRECT, "code": urllib.parse.unquote(c.group(1))})
        with urllib.request.urlopen(f"https://graph.facebook.com/v21.0/oauth/access_token?{q}", timeout=60) as r:
            tok = json.load(r)["access_token"]
        open("token.enc", "w").write(_openssl([], tok) + "\n")
        print("Token obtido e guardado cifrado.", flush=True)
        return tok
    return BRUTO


TOKEN = obter_token()
REPO = os.environ.get("GITHUB_REPOSITORY", "")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/imagens/"


def _get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def descobrir_conta():
    """Descobre sozinho qual API e qual ID usar a partir do token."""
    q = urllib.parse.quote(TOKEN)
    try:  # token do login do Instagram
        eu = _get(f"https://graph.instagram.com/v21.0/me?fields=user_id,username&access_token={q}")
        return "https://graph.instagram.com/v21.0", str(eu["user_id"]), eu.get("username")
    except Exception:
        pass
    # token do login do Facebook / Meta Business
    pags = _get(f"https://graph.facebook.com/v21.0/me/accounts?fields=instagram_business_account{{id,username}}&access_token={q}")
    for p in pags.get("data", []):
        ig = p.get("instagram_business_account")
        if ig:
            return "https://graph.facebook.com/v21.0", ig["id"], ig.get("username")
    try:
        eu = _get(f"https://graph.facebook.com/v21.0/me?fields=id,username&access_token={q}")
        if eu.get("username"):
            return "https://graph.facebook.com/v21.0", eu["id"], eu.get("username")
    except Exception:
        pass
    raise RuntimeError("Nao achei a conta do Instagram ligada a esse token")


API, IG, NOME = descobrir_conta()
print("Conta:", NOME, flush=True)


def chamar(caminho, dados):
    dados = dict(dados, access_token=TOKEN)
    corpo = urllib.parse.urlencode(dados).encode()
    req = urllib.request.Request(f"{API}/{caminho}", data=corpo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print("ERRO da Meta:", e.read().decode()[:600], flush=True)
        raise


def esperar_pronto(container_id, tentativas=20):
    """A Meta precisa baixar a imagem antes de publicar."""
    for _ in range(tentativas):
        url = f"{API}/{container_id}?fields=status_code&access_token={urllib.parse.quote(TOKEN)}"
        with urllib.request.urlopen(url, timeout=60) as r:
            st = json.load(r).get("status_code")
        if st == "FINISHED":
            return True
        if st == "ERROR":
            raise RuntimeError(f"container {container_id} deu ERROR")
        time.sleep(15)
    raise RuntimeError(f"container {container_id} nao ficou pronto")


def main():
    fila = json.load(open("fila.json", encoding="utf-8"))
    estado = json.load(open("estado.json"))
    i = estado["proximo"]
    if i >= len(fila):
        print("Fila terminada. Nada a publicar.")
        return 0

    item = fila[i]
    print(f"Publicando carrossel {item['carrossel']:02d} (posicao {i+1}/{len(fila)})", flush=True)

    # 1) um container por slide
    filhos = []
    for nome in item["slides"]:
        r = chamar(f"{IG}/media", {"image_url": BASE + nome, "is_carousel_item": "true"})
        filhos.append(r["id"])
        print("  slide ok:", nome, flush=True)

    for c in filhos:
        esperar_pronto(c)

    # 2) container do carrossel, com a legenda
    pai = chamar(f"{IG}/media", {
        "media_type": "CAROUSEL",
        "children": ",".join(filhos),
        "caption": item["legenda"],
    })["id"]
    esperar_pronto(pai)

    # 3) publicar
    pub = chamar(f"{IG}/media_publish", {"creation_id": pai})
    print("PUBLICADO:", pub, flush=True)

    estado["proximo"] = i + 1
    estado["ultimo_carrossel"] = item["carrossel"]
    estado["ultimo_post_id"] = pub.get("id")
    json.dump(estado, open("estado.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
