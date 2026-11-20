import json, os, subprocess

LIMITE = 21  # menos de 7 dias de videos (3 por dia)

fila = json.load(open("fila_anuncios.json", encoding="utf-8"))
estado = json.load(open("estado_anuncios.json", encoding="utf-8"))
restantes = len(fila) - estado.get("proximo", 0)
dias = restantes // 3
print(f"Videos restantes: {restantes} (~{dias} dias)")

if restantes >= LIMITE:
    raise SystemExit(0)

titulo = "Estoque de videos do Tem Encaixe acabando"
ja = subprocess.run(["gh", "issue", "list", "--state", "open", "--search", titulo, "--json", "number"], capture_output=True, text=True).stdout
if ja.strip() not in ("", "[]"):
    print("Ja existe alerta aberto.")
    raise SystemExit(0)

corpo = (
    f"Restam {restantes} videos de dica na fila (~{dias} dias, 3 por dia).\n\n"
    "**O que fazer:** abra o Claude e diga: `repor videos do Tem Encaixe, 7 dias`. "
    "Ele cria os videos novos (sem repetir assuntos de assuntos_videos.md), sobe em reels/ e poe na fila.\n\n"
    "Enquanto isso os carrosseis e os Reels de carrossel continuam postando normalmente; "
    "so os videos de dica ficam parados quando a fila acabar. Feche este alerta depois de repor."
)
subprocess.run(["gh", "issue", "create", "--title", titulo, "--body", corpo], check=True)
