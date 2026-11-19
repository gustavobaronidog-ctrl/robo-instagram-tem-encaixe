#!/usr/bin/env python3
"""Troca o mascote antigo (borrado) dentro dos Reels ja prontos que ainda vao sair,
sobrepondo o avatar novo no mesmo lugar. Nao mexe em texto, tempo nem animacao."""
import json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

AV = Image.open("avatar_mascote.png").convert("RGBA")
RING = (255, 194, 26)
FEITO = "reels_avatar_feito.txt"
feito = set(open(FEITO).read().split()) if os.path.exists(FEITO) else set()
LOTE = int(os.environ.get("LOTE", "12"))

def achar_anel(a):
    reg = a[:1000, :460].astype(int)
    r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
    m = (r > 200) & (g > 130) & (g < 220) & (b < 110)
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    melhor = None
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if not (70 <= w <= 170 and 0.88 <= w / h <= 1.12): continue
        if (lab[sl] == i).sum() / (w * h) > 0.40: continue
        if melhor is None or w > melhor[2]: melhor = (sl[1].start, sl[0].start, w, h)
    return melhor


def achar_disco(a, y0, y1):
    """Avatar redondo sem anel (fundo branco): acha o disco escuro a esquerda do nome."""
    reg = a[y0:y1, 40:205].astype(int)
    lum = reg.mean(axis=2)
    m = lum < 215
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    melhor = None
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if not (80 <= w <= 140 and 0.85 <= w / h <= 1.15): continue
        if (lab[sl] == i).sum() / (w * h) < 0.55: continue
        if melhor is None or w > melhor[2]: melhor = (sl[1].start + 40, sl[0].start + y0, w, h)
    return melhor

def novo_avatar(d):
    k = 4; D = d * k; esp = max(4, round(D * 0.045))
    base = AV.resize((D - 2 * esp, D - 2 * esp), Image.LANCZOS)
    ring = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, D - 1, D - 1), fill=RING + (255,))
    inner = Image.new("L", (D, D), 0)
    ImageDraw.Draw(inner).ellipse((esp, esp, D - 1 - esp, D - 1 - esp), fill=255)
    foto = Image.new("RGBA", (D, D), (0, 0, 0, 0)); foto.paste(base, (esp, esp))
    ring.paste(foto, (0, 0), inner)
    mask = Image.new("L", (D, D), 0); ImageDraw.Draw(mask).ellipse((0, 0, D - 1, D - 1), fill=255)
    ring.putalpha(mask)
    return ring.resize((d, d), Image.LANCZOS)

def guardar(msg):
    subprocess.run(["git", "config", "user.name", "robo"], check=True)
    subprocess.run(["git", "config", "user.email", "robo@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", "reels", FEITO], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=False)
    subprocess.run(["git", "pull", "--rebase", "--autostash"], check=True)
    subprocess.run(["git", "push"], check=True)

fila = json.load(open("fila_reels.json", encoding="utf-8"))
est = json.load(open("estado_reels.json"))
nomes = []
for it in fila[est["proximo"]:]:
    if it["video"] not in nomes: nomes.append(it["video"])

tmp = tempfile.mkdtemp(); feitos_lote = 0; total = 0; falhas = []
for nome in nomes:
    if nome in feito: continue
    src = os.path.join("reels", nome)
    if not os.path.exists(src): falhas.append(nome + " (nao existe)"); continue
    fr = os.path.join(tmp, "f.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "3.0", "-i", src, "-frames:v", "1", fr], check=True)
    quadro = np.array(Image.open(fr).convert("RGB"))
    an = achar_anel(quadro) or achar_disco(quadro, 300, 620)
    if not an:
        falhas.append(nome + " (anel nao achado)"); continue
    x, y, w, h = an
    d = w + 6
    avp = os.path.join(tmp, "av.png"); novo_avatar(d).save(avp)
    out = os.path.join(tmp, "out.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", avp,
        "-filter_complex", f"[0:v][1:v]overlay={x-3}:{y-3}:format=auto,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", "30",
        "-movflags", "+faststart", "-an", out], check=True)
    if os.path.getsize(out) < 50_000:
        falhas.append(nome + " (saida pequena)"); continue
    os.replace(out, src)
    feito.add(nome); feitos_lote += 1; total += 1
    open(FEITO, "w").write("\n".join(sorted(feito)) + "\n")
    print("ok", nome, (x, y, w), flush=True)
    if feitos_lote >= (1 if total == 1 else LOTE):
        guardar(f"reels com mascote novo ({total} ate agora)"); feitos_lote = 0
if feitos_lote: guardar(f"reels com mascote novo ({total} no total)")
print("reels refeitos:", total, "falhas:", falhas)
