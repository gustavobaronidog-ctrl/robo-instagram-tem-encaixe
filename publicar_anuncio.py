#!/usr/bin/env python3
# Robo do Tem Encaixe: publica 1 video de anuncio (fila propria, separada dos Reels dos carrosseis).
import json, sys, datetime
import publicar as P
import publicar_reel as R


def hoje_brt():
    return (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%Y-%m-%d")


def main():
    fila = json.load(open("fila_anuncios.json", encoding="utf-8"))
    estado = json.load(open("estado_anuncios.json"))
    i = estado["proximo"]
    if i >= len(fila):
        print("Fila de anuncios terminada.")
        return 0
    item = fila[i]
    print(f"Publicando anuncio {item['video']} (posicao {i+1}/{len(fila)})", flush=True)
    cid = P.chamar(f"{P.IG}/media", {
        "media_type": "REELS",
        "video_url": R.BASE + item["video"],
        "caption": item["legenda"],
        "share_to_feed": "true",
    })["id"]
    R.esperar_video(cid)
    pub = P.chamar(f"{P.IG}/media_publish", {"creation_id": cid})
    print("ANUNCIO PUBLICADO:", pub, flush=True)
    estado["proximo"] = i + 1
    estado["ultimo_video"] = item["video"]
    estado["ultimo_post_id"] = pub.get("id")
    dias = estado.setdefault("por_dia", {})
    dias[hoje_brt()] = dias.get(hoje_brt(), 0) + 1
    json.dump(estado, open("estado_anuncios.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
