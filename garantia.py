#!/usr/bin/env python3
# Conferencia diaria (18h de Brasilia): confere se tudo que devia ter ido ao ar hoje foi,
# e publica na hora o que faltar: carrosseis, Reels dos carrosseis e videos de anuncio.
import datetime, json, sys, time, urllib.parse
import publicar as P
import publicar_reel as R
import publicar_anuncio as A

ESPERADO_CARROSSEIS = 3   # 08h, 12h e 15h
ESPERADO_REELS = 3        # 10h, 14h e 17h
ESPERADO_ANUNCIOS = 3     # 09h, 12h30 e 16h


def agora_brt():
    return datetime.datetime.utcnow() - datetime.timedelta(hours=3)


def tipos_de_hoje():
    q = urllib.parse.quote(P.TOKEN)
    url = f"{P.API}/{P.IG}/media?fields=id,timestamp,media_type&limit=50&access_token={q}"
    dados = P._get(url).get("data", [])
    hoje = agora_brt().strftime("%Y-%m-%d")
    tipos = []
    for m in dados:
        t = datetime.datetime.strptime(m["timestamp"][:19], "%Y-%m-%dT%H:%M:%S") - datetime.timedelta(hours=3)
        if t.strftime("%Y-%m-%d") == hoje:
            tipos.append(m["media_type"])
    return tipos, hoje


def main():
    tipos, hoje = tipos_de_hoje()
    carrosseis = tipos.count("CAROUSEL_ALBUM")
    videos = tipos.count("VIDEO")
    estado = json.load(open("estado_anuncios.json"))
    anuncios = estado.get("por_dia", {}).get(hoje, 0)
    reels = max(0, videos - anuncios)
    print(f"Hoje ({hoje}) ja no ar: carrosseis={carrosseis}, reels={reels}, anuncios={anuncios}", flush=True)
    tarefas = [
        ("carrossel", ESPERADO_CARROSSEIS - carrosseis, P.main),
        ("reel", ESPERADO_REELS - reels, R.main),
        ("anuncio", ESPERADO_ANUNCIOS - anuncios, A.main),
    ]
    falhas = 0
    for nome, falta, fn in tarefas:
        for _ in range(max(0, falta)):
            print(f"FALTOU {nome}: publicando agora", flush=True)
            try:
                fn()
            except Exception as e:
                print(f"ERRO ao publicar {nome}: {e}", flush=True)
                falhas += 1
                break
            time.sleep(20)
    if falhas:
        print(f"Conferencia terminou com {falhas} falha(s). Veja acima.", flush=True)
    else:
        print("Conferencia ok.", flush=True)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
