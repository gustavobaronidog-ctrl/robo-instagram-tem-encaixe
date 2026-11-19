# SOCORRO: o robô do Instagram sem o Claude

Tudo aqui roda no GitHub, mesmo com o limite do Claude acabado.

## Como rodar um botão
1. Clique na aba **Actions** (Ações) deste repositório.
2. No menu da esquerda, clique no nome do botão que quer.
3. Clique no botão verde **Run workflow** e depois em **Run workflow** de novo.

## Botões disponíveis
- **Garantia diária dos posts**: confere os 9 posts do dia e publica o que faltou. Use se passou das 18h e faltou algum post.
- **Publicar no Instagram**: posta o próximo carrossel agora.
- **Publicar Reel no Instagram**: posta o próximo Reel de carrossel agora.
- **Publicar anúncio no Instagram**: posta o próximo vídeo de dica agora.
- **Vigia**: confere se o site está no ar, quanto estoque de posts resta e se os arquivos existem.

## Recebi um e-mail "Run failed"
É o Vigia ou o robô avisando. Abra o link do e-mail e leia a linha vermelha:
- "site fora do ar": veja o site no navegador; se estiver fora, entre na Vercel e faça Redeploy do último deploy que funcionava.
- "estoque para menos de 2 dias" ou "fila ACABOU": falta criar conteúdo. Peça ao Claude quando voltar.
- "arquivos que faltam no GitHub": uma imagem ou vídeo da fila não foi enviado. Suba o arquivo na pasta indicada (imagens ou reels) em Add file > Upload files.
- Falha ao publicar: rode o botão **Garantia diária** e espere 5 minutos. Se repetir, o token do Instagram pode ter vencido; avise o Claude.

## Quando o robô para de postar
1. Abra Actions e veja a última linha de cada botão: verde é ok, vermelho é erro.
2. Rode o botão do post que faltou.
3. Confira no Instagram em 5 minutos.

## O que só o Claude resolve
Código novo, criar conteúdo novo (carrosséis, vídeos) e trocar o token do Instagram.
