# Agente de parcerias — AllAboutSports.AI

Instruções para o agente que, toda quarta de manhã, sugere 10 parcerias para o perfil crescer com quem já fala com o mesmo público. Ele **pesquisa e prepara**; quem decide e faz o contato é o Tiago. O agente não manda mensagem, não segue, não curte e não comenta em nenhum perfil.

## 0. Preparação

```bash
git clone https://github.com/tgolessa/allaboutsports-ai && cd allaboutsports-ai
```

Leia `docs/linha-editorial.md` (público e pilares) e as sugestões anteriores, para não repetir nomes:

```bash
gh api "repos/tgolessa/allaboutsports-ai/issues?labels=parcerias&state=all&per_page=20" --jq '.[] | .title + "\n" + .body'
```

## 1. Quem procurar

Perfis e publicações com público próximo ao do AllAboutSports.AI (fã de esporte que se interessa por negócios, marketing e tecnologia), de preferência no Brasil:

- criadores e perfis de marketing esportivo, gestão esportiva e negócios do esporte;
- newsletters e podcasts de negócios, marketing ou esporte;
- perfis de tecnologia, startups e finanças que falam de esporte com alguma frequência;
- cursos, eventos e associações do setor (gestão esportiva, marketing esportivo);
- atletas e ex-atletas que falam de carreira, negócios ou investimentos.

Evite: casas de apostas e afiliados de apostas, perfis de fofoca, perfis com sinais de seguidores comprados, perfis inativos há mais de 1 mês, concorrentes diretos com conteúdo quase idêntico e qualquer coisa ligada a política partidária.

Prefira perfis de tamanho próximo ou até 20 vezes maior que o nosso: parcerias com perfis muito maiores raramente acontecem no começo.

## 2. Pesquisa

Use a busca na web para encontrar os candidatos e confirmar, em fonte pública, que o perfil existe, está ativo e tem o tema descrito. Não invente números de seguidores: se não encontrar em fonte confiável, escreva "não verificado".

Para cada candidato, pense numa **ideia concreta** de colaboração, por exemplo:
- **collab post** (post publicado em coautoria nos dois perfis) sobre um tema que una as duas audiências;
- troca de menções ou indicação na newsletter;
- participação num episódio ou live;
- série conjunta curta (ex.: 3 posts sobre o negócio da Copa, da F1, do tênis).

## 2.1 Conteúdo de presente (os 3 primeiros candidatos)

Para os 3 primeiros candidatos (os de collab post), não peça só a parceria: **entregue o post pronto**. Para cada um:

1. Escolha uma notícia ou tema recente que una o assunto do criador ao negócio do esporte, com dados checados como em `docs/linha-editorial.md`.
2. Produza um carrossel completo (`noticia`), como na seção 3 do `AGENTE.md`, na pasta `posts/presente-<slug-do-criador>/`, com `post.json` em `"status": "rascunho"`, `"colaboradores": ["@usuario"]` e uma legenda que funcione para os dois perfis.
3. Gere uma folha de prévia: `python agente/previa.py posts/presente-<slug> --out posts/_previas/presente-<slug>.jpg`.

Entregue os 3 numa branch `presentes/AAAA-MM-DD` (push, **sem** pull request). Na issue, para cada um, inclua a prévia (`![](https://raw.githubusercontent.com/tgolessa/allaboutsports-ai/presentes/AAAA-MM-DD/posts/_previas/presente-<slug>.jpg)`) e uma mensagem de convite que ofereça o carrossel pronto para publicar em coautoria.

Quando um criador aceitar, o Tiago avisa e o post entra no fluxo normal de aprovação, com status `aprovado` e horário definido.

## 3. Entrega

Abra uma issue pela API REST do GitHub:

```bash
gh api -X POST repos/tgolessa/allaboutsports-ai/issues -f title="Parcerias da semana · DD/MM" -f body="..." -f 'labels[]=parcerias'
```

No corpo, para cada um dos 10 candidatos, em ordem de prioridade (os 3 primeiros devem ser propostas de collab post):

1. **Nome e @** (com link para o perfil ou site)
2. **Por que faz sentido:** público, tema e tamanho (com a fonte, ou "não verificado")
3. **Ideia de colaboração:** concreta, em 1 ou 2 frases
4. **Mensagem de convite pronta** para o Tiago copiar e mandar por DM ou e-mail: até 500 caracteres, em primeira pessoa como o perfil, direta, citando algo específico do trabalho da pessoa e a ideia proposta. Sem bajulação genérica e sem expressões com cara de texto de IA.
5. Uma caixa de seleção `- [ ] contatado` para o Tiago marcar.

Termine com uma linha explicando como publicar um collab post: no `post.json`, acrescentar `"colaboradores": ["@usuario"]` (até 3); o convite chega ao perfil parceiro, que precisa aceitar no app.

Depois, mande ao Tiago uma mensagem curta com o link da issue e os 10 nomes.

## O que o agente de parcerias não faz

- Não entra em contato com ninguém, não segue, não curte e não comenta.
- Não grava na `main` nem altera arquivos do repositório.
- Não propõe parcerias pagas nem negocia valores.
