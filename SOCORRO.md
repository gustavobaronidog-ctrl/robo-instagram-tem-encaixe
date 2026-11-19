# SOCORRO: robô do Instagram do Tem Encaixe sem o Claude

Tudo aqui roda no GitHub, mesmo com o limite do Claude acabado.
Repositório: https://github.com/gustavobaronidog-ctrl/robo-instagram-tem-encaixe

## Como apertar um botão
1. Abra o repositório e clique na aba **Actions**.
2. No menu da esquerda, clique no nome do botão.
3. Clique em **Run workflow** (a direita) e depois no botão verde **Run workflow**.

## Botões
- **Garantia diária dos posts**: confere os 9 posts do dia e publica o que faltou (roda sozinho às 18h05).
- **Publicar no Instagram**: posta o próximo carrossel agora.
- **Publicar Reel no Instagram**: posta o próximo Reel de carrossel agora.
- **Publicar anúncio no Instagram**: posta o próximo vídeo de dica agora.
- **Vigia**: confere site, estoque e arquivos. Roda sozinho 4 vezes por dia.

## Chegou e-mail "Run failed". O que fazer
O e-mail já traz o problema e a solução em duas linhas: **SEM O CLAUDE** (o que você faz) e **COM O CLAUDE** (o que pedir). Resumo:

| Problema no e-mail | Sem o Claude | Com o Claude |
|---|---|---|
| site fora do ar | Vercel > projeto > Deployments > último "Ready" > 3 pontinhos > Promote to Production | "o site temencaixe.com caiu, corrija" |
| fila acabou / estoque baixo | abrir estado.json (ou estado_reels.json / estado_anuncios.json), lápis, trocar "proximo" por 0, Commit changes (a fila recomeça e reposta conteúdo antigo) | "criar mais conteúdo para a fila do robô" |
| arquivos que faltam | no estado*.json somar 1 em "proximo" (pula o post) e subir o arquivo em imagens/ ou reels/ (Add file > Upload files) | "conferir arquivos que faltam e subir" |
| não consegui ler a fila | commits > último commit que mexeu no arquivo > Revert | "o vigia não lê a fila, conserte" |
| falha ao publicar (token) | rodar **Garantia diária** e esperar 5 min; se repetir, o token do Instagram venceu: gerar outro no painel da Meta e trocar em Settings > Secrets and variables > Actions > IG_TOKEN | "o token do Instagram venceu, troque" |

## Quando o robô para de postar
1. Actions: veja a última linha de cada botão (verde ok, vermelho erro).
2. Aperte o botão do post que faltou.
3. Confira no Instagram em 5 minutos.

## Só o Claude resolve
Código novo, criar conteúdo novo (carrosséis, vídeos) e gerar token novo.

## Para onde vão os avisos
Falhas do robô e do vigia chegam por e-mail do GitHub em gustavobaronidog@gmail.com. Os do SeparaGo também são encaminhados para separago.contato@gmail.com (filtro no Gmail).

## SeparaGo
Repositório separago-marketing, com guia próprio (SOCORRO.md dele).
