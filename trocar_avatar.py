#!/usr/bin/env python3
"""Troca o mascote pequeno/borrado do cabecalho pelo mascote novo (alta qualidade)
nas imagens que ainda vao ser publicadas e recolore o fundo vinho dos slides de CTA
para a paleta do Tem Encaixe (preto)."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

AV = Image.open("avatar_mascote.png").convert("RGBA")
RING = (255, 194, 26)
FEITO = "avatar_feito.txt"
feito = set(open(FEITO).read().split()) if os.path.exists(FEITO) else set()

fila = json.load(open("fila.json", encoding="utf-8"))
est = json.load(open("estado.json"))
nomes = []
for it in fila[est["proximo"]:]:
    for n in it["slides"]:
        if n not in nomes: nomes.append(n)

def achar_anel(a):
    reg = a[:480, :330].astype(int)
    r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
    m = (r > 215) & (g > 140) & (g < 215) & (b < 95)
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    melhor = None
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if not (70 <= w <= 160 and 0.88 <= w / h <= 1.12): continue
        cheio = (lab[sl] == i).sum() / (w * h)
        if cheio > 0.40: continue          # anel e vazado; texto destacado e cheio
        if melhor is None or w > melhor[2]:
            melhor = (sl[1].start, sl[0].start, w, h)
    return melhor

def novo_avatar(d):
    k = 4; D = d * k
    base = AV.resize((D, D), Image.LANCZOS)
    esp = max(4, round(D * 0.045))
    mask = Image.new("L", (D, D), 0); ImageDraw.Draw(mask).ellipse((0, 0, D - 1, D - 1), fill=255)
    ring = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ring); dr.ellipse((0, 0, D - 1, D - 1), fill=RING + (255,))
    inner = Image.new("L", (D, D), 0)
    ImageDraw.Draw(inner).ellipse((esp, esp, D - 1 - esp, D - 1 - esp), fill=255)
    foto = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    ib = base.resize((D - 2 * esp, D - 2 * esp), Image.LANCZOS)
    foto.paste(ib, (esp, esp))
    ring.paste(foto, (0, 0), inner)
    ring.putalpha(mask)
    return ring.resize((d, d), Image.LANCZOS)

VINHO = np.array([110, 15, 40], float)
def recolorir_vinho(a):
    cantos = a[[5, 5, -5, -5], [5, -5, 5, -5]].astype(float)
    if not (np.abs(cantos - cantos[0]).max() < 6 and np.abs(cantos[0] - VINHO).max() < 40): return None
    bg = cantos[0]; branco = np.array([255, 255, 255], float); preto = np.array([13, 13, 13], float)
    f = a.astype(float)
    t = ((f - bg) @ (branco - bg)) / ((branco - bg) @ (branco - bg))
    resto = np.linalg.norm(f - (bg + np.clip(t, 0, 1)[..., None] * (branco - bg)), axis=2)
    gray = resto < 40                       # so mexe no que e vinho->branco (texto); emoji/cores ficam
    novo = preto + np.clip(t, 0, 1)[..., None] * (branco - preto)
    f[gray] = novo[gray]
    return f.clip(0, 255).astype(np.uint8)

mudou = 0
for n in nomes:
    if n in feito or n.startswith("c303_"): continue
    p = os.path.join("imagens", n)
    if not os.path.exists(p): print("falta", n); continue
    im = Image.open(p).convert("RGB"); a = np.array(im); alterou = False
    v = recolorir_vinho(a)
    if v is not None: a = v; im = Image.fromarray(a); alterou = True
    an = achar_anel(a)
    if an:
        x, y, w, h = an
        av = novo_avatar(w)
        im = im.convert("RGBA"); im.alpha_composite(av, (x, y)); im = im.convert("RGB"); alterou = True
    if alterou:
        im.save(p, quality=95, subsampling=0); mudou += 1
    feito.add(n)
open(FEITO, "w").write("\n".join(sorted(feito)) + "\n")
print("imagens avaliadas:", len(nomes), "alteradas:", mudou)
