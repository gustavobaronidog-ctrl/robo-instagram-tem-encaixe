#!/usr/bin/env python3
# Robo do Tem Encaixe: publica 1 Reel (video feito dos slides) pela API oficial da Meta.
# Reaproveita o login e a conta do publicar.py. Fila e estado proprios.
import json, sys, time, urllib.parse, urllib.request
import publicar as P

BASE = f"https://raw.githubusercontent.com/{P.REPO}/{P.BRANCH}/reels/"


def esperar_video(cid, tentativas=40):
    for _ in range(tentativas):
        url = f"{P.API}/{cid}?fields=status_code&access_token={urllib.parse.quote(P.TOKEN)}"
        with urllib.request.urlopen(url, timeout=60) as r:
            st = json.load(r).get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"video {cid}: {st}")
        time.sleep(15)
    raise RuntimeError(f"video {cid} nao ficou pronto")


def main():
    fila = json.load(open("fila_reels.json", encoding="utf-8"))
    estado = json.load(open("estado_reels.json"))
    i = estado["proximo"]
    if i >= len(fila):
        print("Fila de reels terminada.")
        return 0
    item = fila[i]
    print(f"Publicando reel {item['carrossel']:02d} (posicao {i+1}/{len(fila)})", flush=True)
    cid = P.chamar(f"{P.IG}/media", {
        "media_type": "REELS",
        "video_url": BASE + item["video"],
        "caption": item["legenda"],
        "share_to_feed": "true",
    })["id"]
    esperar_video(cid)
    pub = P.chamar(f"{P.IG}/media_publish", {"creation_id": cid})
    print("REEL PUBLICADO:", pub, flush=True)
    estado["proximo"] = i + 1
    estado["ultimo_reel"] = item["carrossel"]
    estado["ultimo_post_id"] = pub.get("id")
    json.dump(estado, open("estado_reels.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
