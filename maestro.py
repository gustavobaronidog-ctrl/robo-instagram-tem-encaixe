#!/usr/bin/env python3
# Maestro dos posts: roda a cada ~10 min. Publica o que JA DEVIA ter ido ao ar hoje e ainda nao foi
# (no maximo 1 de cada tipo por rodada). Assim, se o GitHub atrasar ou pular uma rodada, a proxima corrige sozinha.
import sys, time
import publicar as P
import publicar_reel as R
import publicar_anuncio as A
from garantia import agora_brt, tipos_de_hoje
import json

# Horarios de Brasilia, em minutos desde 00:00
SLOTS = {
    "carrossel": [8 * 60, 12 * 60, 15 * 60],
    "reel": [10 * 60, 14 * 60, 17 * 60],
    "anuncio": [9 * 60, 12 * 60 + 30, 16 * 60],
}
LIMITE = 22 * 60  # depois das 22h nao publica mais nada naquele dia


def main():
    agora = agora_brt()
    minutos = agora.hour * 60 + agora.minute
    if minutos > LIMITE:
        print("Depois das 22h: nada a fazer.", flush=True)
        return 0
    tipos, hoje = tipos_de_hoje()
    carrosseis = tipos.count("CAROUSEL_ALBUM")
    videos = tipos.count("VIDEO")
    anuncios = json.load(open("estado_anuncios.json")).get("por_dia", {}).get(hoje, 0)
    ja = {"carrossel": carrosseis, "reel": max(0, videos - anuncios), "anuncio": anuncios}
    fn = {"carrossel": P.main, "reel": R.main, "anuncio": A.main}
    print(f"{hoje} {agora:%H:%M} (Brasilia) - ja no ar: {ja}", flush=True)
    atrasado = 0
    for nome in ("carrossel", "reel", "anuncio"):
        devidos = [s for s in SLOTS[nome] if s <= minutos]
        falta = len(devidos) - ja[nome]
        if falta <= 0:
            continue
        print(f"DEVIDO e nao publicado: {nome} (faltam {falta}). Publicando 1 agora.", flush=True)
        try:
            fn[nome]()
        except Exception as e:
            print(f"ERRO ao publicar {nome}: {e}", flush=True)
            if minutos - devidos[-1] > 90:
                atrasado = 1
        time.sleep(20)
    print("Maestro ok." if not atrasado else "Maestro: erro com atraso grande, veja acima.", flush=True)
    return atrasado


if __name__ == "__main__":
    sys.exit(main())
