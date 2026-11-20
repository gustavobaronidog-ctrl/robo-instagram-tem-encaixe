#!/usr/bin/env python3
# Maestro dos posts (PLANTAO): fica ligado ~50 min e confere a cada 5 min o que JA DEVIA ter ido ao ar hoje
# e ainda nao foi; publica o que faltar (no maximo 1 de cada tipo por conferencia). Cada post publicado e
# gravado no GitHub na hora (nunca sai repetido se a rodada cair). No fim, o workflow liga a proxima rodada.
import sys, time, json, subprocess
import publicar as P
import publicar_reel as R
import publicar_anuncio as A
from garantia import agora_brt, tipos_de_hoje

# Horarios de Brasilia, em minutos desde 00:00
SLOTS = {
    "carrossel": [8 * 60, 12 * 60, 15 * 60],
    "reel": [10 * 60, 14 * 60, 17 * 60],
    "anuncio": [9 * 60, 12 * 60 + 30, 16 * 60],
}
INICIO = 7 * 60    # antes das 7h nao publica nada (mas o plantao continua ligado 24h)
LIMITE = 22 * 60   # depois das 22h nao publica mais nada naquele dia
ERROS = {}         # erros ainda nao resolvidos, por tipo de post
DURACAO = 50 * 60  # tempo de plantao de cada rodada
INTERVALO = 5 * 60 # de quanto em quanto tempo confere


def sh(cmd):
    return subprocess.run(cmd, shell=True).returncode


def atualizar():
    sh("git pull --rebase -q")


def gravar():
    """Grava o avanco das filas no GitHub agora mesmo."""
    sh("git add estado.json estado_reels.json estado_anuncios.json token.enc 2>/dev/null || git add estado.json estado_reels.json estado_anuncios.json")
    if sh("git diff --staged --quiet") != 0:
        sh('git commit -q -m "maestro: avanca as filas"')
        for _ in range(3):
            if sh("git pull --rebase -q && git push -q") == 0:
                break
            time.sleep(3)


def conferir(minutos):
    tipos, hoje = tipos_de_hoje()
    carrosseis = tipos.count("CAROUSEL_ALBUM")
    videos = tipos.count("VIDEO")
    anuncios = json.load(open("estado_anuncios.json")).get("por_dia", {}).get(hoje, 0)
    ja = {"carrossel": carrosseis, "reel": max(0, videos - anuncios), "anuncio": anuncios}
    fn = {"carrossel": P.main, "reel": R.main, "anuncio": A.main}
    print(f"{hoje} {minutos // 60:02d}:{minutos % 60:02d} (Brasilia) - ja no ar: {ja}", flush=True)
    atrasado = 0
    for nome in ("carrossel", "reel", "anuncio"):
        devidos = [s for s in SLOTS[nome] if s <= minutos]
        falta = len(devidos) - ja[nome]
        if falta <= 0:
            ERROS.pop(nome, None)  # nada devido (ou ja resolvido): erro antigo some
            continue
        print(f"DEVIDO e nao publicado: {nome} (faltam {falta}). Publicando 1 agora.", flush=True)
        try:
            fn[nome]()
        except Exception as e:
            print(f"ERRO ao publicar {nome}: {e}", flush=True)
            ERROS[nome] = str(e)
            if minutos - devidos[-1] > 90:
                atrasado = 1
        gravar()
        time.sleep(20)
    return atrasado


def main():
    inicio = time.time()
    erro = 0
    while True:
        agora = agora_brt()
        minutos = agora.hour * 60 + agora.minute
        if minutos < INICIO or minutos > LIMITE:
            print(f"{minutos // 60:02d}:{minutos % 60:02d} fora de 7h-22h: plantao ligado, sem publicar.", flush=True)
        else:
            atualizar()
            try:
                erro = conferir(minutos)
            except Exception as e:
                print(f"ERRO na conferencia: {e}", flush=True)
                ERROS["conferencia"] = str(e)
        if time.time() - inicio + INTERVALO > DURACAO:
            break
        time.sleep(INTERVALO)
    if ERROS:
        print("ERROS NAO RESOLVIDOS (o GitHub vai avisar por e-mail): " + "; ".join(f"{k}: {v}" for k, v in ERROS.items()), flush=True)
        erro = 1
    print("Maestro ok." if not erro else "Maestro: terminou com erro, veja acima.", flush=True)
    return erro


if __name__ == "__main__":
    sys.exit(main())
