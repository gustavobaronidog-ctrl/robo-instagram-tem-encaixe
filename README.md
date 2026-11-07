# Robô do Instagram — Tem Encaixe

Publica 1 carrossel por vez no Instagram, 3 vezes por dia (08h, 12h e 18h, horário de Brasília), na ordem da `fila.json`.

- `imagens/` — os 162 slides (27 carrosséis x 6)
- `fila.json` — ordem de publicação + legenda de cada carrossel
- `estado.json` — qual é o próximo da fila (o robô atualiza sozinho)
- `.github/workflows/publicar.yml` — horários

Precisa de 1 segredo em Settings > Secrets and variables > Actions: `IG_TOKEN` (token do Instagram, vale 60 dias).
Para pausar: Actions > Publicar no Instagram > ... > Disable workflow.
