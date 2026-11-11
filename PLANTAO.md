# Plantão — AllAboutSports.AI

Instruções para o agente que, a cada 2 horas, procura **notícia quente** de negócios do esporte. Em sports business, quem posta primeiro uma venda bilionária ou um contrato recorde leva o alcance. O plantão existe para isso, e **só para isso**: na grande maioria das rodadas, o certo é não fazer nada.

## 0. Preparação

```bash
git clone https://github.com/tgolessa/allaboutsports-ai && cd allaboutsports-ai
pip install --break-system-packages playwright pillow
```

Leia `docs/linha-editorial.md`, `docs/aprendizados.md` e a seção 3 (Produção) do `AGENTE.md`, que vale também aqui.

## 1. A régua: o que conta como notícia quente

Publicada nas **últimas 2 horas** e que cumpra **todas** as condições:

1. **Grande:** valor de US$ 500 milhões ou mais (ou equivalente), recorde histórico, ou movimento estratégico de uma das maiores ligas, clubes, marcas ou atletas do mundo (venda de franquia ou clube, contrato de mídia de liga, patrocínio recorde, nova liga, fusão ou aquisição, contrato histórico de atleta).
2. **Confirmada:** comunicado oficial ou publicada por veículo de primeira linha (Bloomberg, Reuters, Sportico, Front Office Sports, The Athletic, Financial Times, ESPN, CNBC). Rumor não entra.
3. **Inédita no perfil:** não está nos posts dos últimos 3 dias (`posts/`) nem em propostas abertas (`gh api "repos/tgolessa/allaboutsports-ai/pulls?state=open"`).

Se nada cumprir as três, **encerre sem fazer nada e sem mandar mensagem**.

## 2. Produção

Uma única **nota rápida** (`"tipo": "nota"`), com o slide de "por que importa", na pasta `posts/AAAA-MM-DD-plantao-HHMM-<slug>/`:

```bash
python templates/render.py posts/<pasta>/pauta.json --out posts/<pasta>/imagens
python agente/story.py posts/<pasta>/pauta.json
```

- Confira cada número na fonte, abra as imagens e revise o texto (expressões proibidas, nada além do que a fonte diz).
- `post.json` com `"status": "aprovado"`, `"plantao": true` e `"publicar_em"` = agora + 20 minutos, arredondado para os próximos 5 minutos. Se o Tiago aprovar depois disso, o post sai na rodada seguinte do publicador, respeitando o intervalo mínimo de 1 hora entre posts.
- Legenda começando por "Acabou de sair:" ou equivalente, com a fonte e a hora da notícia.

## 3. Entrega

```bash
git checkout -b plantao/AAAA-MM-DD-HHMM
git add posts && git commit -m "Plantão: <manchete>" && git push -u origin plantao/AAAA-MM-DD-HHMM
```

Abra a proposta pela API REST do GitHub com o título `PLANTÃO · <manchete curta>` e, no corpo, a imagem do primeiro slide (link raw da branch), a fonte com link e horário da publicação original, e: "Para publicar, faça o merge. Notícia quente perde valor rápido: se não fizer sentido em até 2 horas, feche a proposta."

Mande ao Tiago uma mensagem curta e direta, começando por "Plantão:", com a manchete e o link da proposta.

## O que o plantão não faz

- Não publica sem aprovação, não grava na `main` e não altera arquivos fora da pasta do post.
- Não cobre rumor, especulação de mercado ou notícia de outra área só porque está em alta.
- Não abre mais de uma proposta por rodada.
