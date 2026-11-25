# Plantão — AllAboutTri.AI

Instruções para o agente que, algumas vezes por dia, procura **notícia quente** de triathlon: resultado de prova grande que acabou de sair, abertura de inscrições muito procurada, anúncio oficial importante. Quem posta primeiro leva o alcance. Na maioria das rodadas, o certo é não fazer nada.

**A publicação é automática:** o post vai direto para a `main` e sai na rodada seguinte do publicador. Por isso a régua é alta e a checagem é obrigatória.

## 0. Preparação

```bash
git clone https://github.com/tgolessa/allaboutsports-ai && cd allaboutsports-ai
pip install --break-system-packages playwright pillow
```

Leia `docs/linha-editorial.md`, `docs/calendario.md` e as seções 3 e 4 do `AGENTE.md`, que valem também aqui.

## 1. A régua

Publicada nas **últimas 3 horas** e que cumpra **todas** as condições:

1. **Relevante:** resultado de Kona, Mundial de 70.3, IRONMAN Pro Series, T100 ou IRONMAN/70.3 no Brasil; brasileiro no pódio de prova internacional; recorde; abertura de inscrições de prova muito procurada por brasileiros; anúncio oficial de prova nova no Brasil ou mudança grande de calendário ou regra.
2. **Confirmada:** resultado oficial publicado (ironman.com, t100triathlon.com, triathlon.org, organizadora) ou comunicado oficial. Rumor e resultado extraoficial não entram.
3. **Inédita no perfil:** não está nos posts dos últimos 3 dias em `posts/`.
4. **Cabe no dia:** no máximo 1 post de plantão por dia e nunca a menos de 1 hora de outro post agendado (veja os `publicar_em` de hoje em `posts/`).

Se nada cumprir as quatro, **encerre sem fazer nada e sem mandar mensagem**.

## 2. Produção

Um único post `resultado`, `inscricao` ou `nota`, na pasta `posts/AAAA-MM-DD-plantao-HHMM-<slug>/`:

```bash
python templates/render.py posts/<pasta>/pauta.json --out posts/<pasta>/imagens
python agente/story.py posts/<pasta>/pauta.json
```

- Confira cada nome, tempo e data na fonte oficial, abra as imagens e revise o texto.
- `post.json` com `"status": "aprovado"`, `"plantao": true` e `"publicar_em"` = agora, arredondado para os próximos 5 minutos.
- Legenda começando por "Acabou de sair:" ou equivalente, com a fonte.

## 3. Entrega

```bash
git add posts && git commit -m "Plantão: <manchete>" && git pull --rebase origin main && git push origin main
```

Mande ao Tiago uma mensagem curta começando por "Plantão:", com a manchete e o horário previsto de publicação.

## O que o plantão não faz

- Não altera arquivos fora da pasta do post.
- Não cobre rumor, especulação, lesão ou saúde de atleta sem confirmação oficial.
- Não publica mais de um post por dia.
