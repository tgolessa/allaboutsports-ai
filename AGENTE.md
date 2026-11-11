# Agente diário — AllAboutSports.AI

Instruções para o agente que pesquisa as notícias, produz o pacote de posts e abre a proposta de aprovação. Ele roda em duas tarefas agendadas: **manhã** (todos os dias) e **tarde** (segunda a sexta).

O agente **nunca publica** e **nunca grava direto na `main`**. Ele entrega uma proposta (pull request); o Tiago aprova com o merge e o workflow `publicar.yml` publica nos horários marcados.

## 0. Preparação

```bash
git clone https://github.com/tgolessa/allaboutsports-ai && cd allaboutsports-ai
pip install --break-system-packages playwright pillow
```

Leia antes de começar: `docs/linha-editorial.md` (regras de conteúdo), `docs/aprendizados.md` (regras aprendidas com os números do perfil, que você deve seguir), `README.md` (formatos e limites de texto) e os exemplos em `templates/exemplos/`.

Datas e horários sempre no fuso de Brasília (America/Sao_Paulo, `-03:00`).

## 1. O que entra no pacote

| Período | Pacote | Horários de publicação |
| --- | --- | --- |
| Manhã, seg–sex | 1 carrossel (`noticia`) + 1 a 3 notas (`nota`) | 09:30 · 11:30 · 13:00 · 14:30 |
| Tarde, seg–sex | 1 carrossel (`noticia`) + 1 a 3 notas (`nota`) | 17:30 · 20:00 · 21:15 · 22:30 |
| Manhã, sáb e dom | 1 carrossel + 1 a 3 notas | 10:00 · 12:30 · 15:00 · 18:00 |

- Total de 2 a 4 posts por pacote, **mais o Reel** (veja abaixo). Use os primeiros horários da tabela, na ordem; o carrossel vai no primeiro horário.
- **Sexta de manhã:** acrescente o `semanal` (Top 10 da semana, segunda a sexta), no último horário do pacote. Ele pode ser o 4º post.
- **Sexta de manhã, newsletter:** acrescente também a edição da newsletter (Top 10 da semana por e-mail), com envio às **18:00**. Ela não ocupa horário do feed. Veja "Newsletter" em Produção.
- **Sexta à tarde, semana ISO par:** acrescente o `ranking` (10 maiores valores dos últimos 14 dias, todos no mesmo tipo de valor e moeda), no último horário.
- **Reel em todo pacote:** o carrossel do pacote também vira um Reel, publicado como post separado no horário de Reel: **15:30** (manhã, seg–sex), **18:45** (tarde) e **19:30** (fim de semana). Os horários respeitam o intervalo mínimo de 1 hora entre posts do publicador. Veja a seção "Reel" em Produção.
- **Story em todo post do feed:** cada carrossel e nota ganha um `story.jpg`, publicado nos Stories logo depois do post. Veja "Story" em Produção.
- **Grandes eventos:** confira `docs/calendario.md`. Se houver um evento nos próximos 7 dias, pelo menos 1 post do pacote deve ser sobre o negócio por trás dele (e o pacote pode trazer uma série, marcada como `"serie": "<nome>"` no `post.json`). Se o assunto merecer identidade especial, sugira na proposta.
- Qualidade antes de volume: se não houver 2 pautas que passem nos critérios, entregue 1 e explique na proposta.

## 2. Pesquisa

1. **Histórico:** leia os `pauta.json` dos posts dos últimos 14 dias em `posts/` e não repita assunto já publicado, a não ser que haja fato novo relevante (e então diga o que mudou).
2. **Janela:** notícias das últimas 24 horas (manhã: desde a tarde anterior; tarde: desde a manhã). Prefira o que ainda está repercutindo.
3. **Busca:** faça buscas separadas por pilar e por liga/esporte (ex.: "NFL franchise sale", "Premier League broadcast rights", "sponsorship deal sports", "sports tech partnership", "NBA media rights"), em inglês e em português. Abra as matérias (WebFetch), não confie só no resumo da busca.
4. **Critérios** (nota de 1 a 5 em cada; escolha as maiores somas):
   - tem um número concreto e verificável, ou é uma mudança de produto/parceria relevante;
   - envolve marca, liga ou atleta conhecido do público brasileiro;
   - é novo ou muda o entendimento de um tema;
   - rende um "por que importa" claro;
   - equilibra os pesos dos pilares na semana;
   - **até 11/12/2026:** tem ângulo brasileiro. Mire em cerca de 40% dos posts da semana com conexão Brasil (veja a linha editorial) e diga na proposta quantos posts do pacote têm esse ângulo.
5. **Checagem:** confirme cada número em pelo menos uma fonte confiável, de preferência duas, e nunca afirme mais do que a fonte diz.

## 3. Produção

Para cada post, crie a pasta `posts/AAAA-MM-DD-<manha|tarde>-NN-<slug>/` (NN = 01, 02… na ordem de publicação) com:

**`pauta.json`** — os campos do formato (`noticia`, `nota`, `semanal` ou `ranking`), seguindo os limites de texto do README.

**Imagens:**
```bash
python templates/render.py posts/<pasta>/pauta.json --out posts/<pasta>/imagens
```
Se aparecer `ESTOUROU`, encurte o texto e gere de novo.

**`post.json`:**
```json
{
  "status": "aprovado",
  "publicar_em": "2026-11-12T09:30:00-03:00",
  "tipo": "noticia",
  "legenda": "...",
  "imagens": ["imagens/01.jpg", "imagens/02.jpg"]
}
```
O status já vai como `aprovado` porque a aprovação acontece no merge da proposta.

**Story** (todo carrossel e nota):
```bash
python agente/story.py posts/<pasta>/pauta.json
```
Cria `story.jpg` na pasta do post; o publicador cuida do resto. Abra a imagem para conferir.

**Reel** (todo pacote): crie a pasta `posts/AAAA-MM-DD-<periodo>-NN-<slug>-reel/`, copie o `pauta.json` do carrossel e gere o vídeo:
```bash
python agente/reel.py posts/<pasta-reel>/pauta.json
```
Isso cria `reel.mp4` (9:16, trilha original gerada por código) e `reel_capa.jpg`. Assista a pelo menos 3 quadros (`ffmpeg -ss <segundos> -i reel.mp4 -frames:v 1 quadro.png`) para conferir. O `post.json` do Reel usa `"tipo": "reel"`, `"video": "reel.mp4"`, `"capa": "reel_capa.jpg"` (sem `imagens`) e uma legenda mais curta que a do carrossel, começando pelo gancho e terminando com um convite para salvar ou mandar para alguém.

**Newsletter** (sexta de manhã): crie a pasta `posts/AAAA-MM-DD-newsletter/` com um `edicao.json` (formato no topo de `agente/newsletter.py`): número da edição (anterior + 1), abertura de 2 a 3 frases sobre o que marcou a semana, os mesmos 10 itens do Top 10 com 2 a 3 frases cada (mais completos que no carrossel) e link da fonte, e um fechamento de 1 a 2 frases. Gere o HTML e a prévia:
```bash
python agente/newsletter.py posts/<pasta>/edicao.json --previa
```
O `post.json` usa `"tipo": "newsletter"`, `"status": "aprovado"`, `"publicar_em": "<sexta>T18:00:00-03:00"`, `"assunto"` (até 60 caracteres, com o tema mais forte da semana), `"previa"` (até 90 caracteres, complementando o assunto), `"descricao"` e `"html": "newsletter.html"`. Inclua `previa.jpg` no corpo da proposta.

**Legenda** (até ~1.200 caracteres):
1. Primeira linha: o gancho da capa, em outras palavras.
2. Duas a quatro frases explicando o fato e por que importa.
3. Uma pergunta para os comentários.
4. `Fontes: <veículo> (<data>), <veículo>.`
5. 5 a 8 hashtags: sempre `#sportsbusiness #negociosdoesporte`, mais as do tema.

## 4. Revisão antes de entregar

- Abra (Read) cada imagem gerada e confira: nada cortado, nenhum erro de digitação, números iguais aos da fonte.
- Releia os textos procurando as expressões proibidas da linha editorial e frases com cara de texto de IA.
- Confira se nenhum post afirma mais do que a fonte diz.
- Gere a folha de prévia do pacote:
  ```bash
  python agente/previa.py posts/<pasta-1> posts/<pasta-2> ... --out posts/_previas/AAAA-MM-DD-<periodo>.jpg
  ```

## 5. Entrega

```bash
git checkout -b pacote/AAAA-MM-DD-<periodo>
git add posts
git commit -m "Pacote <manhã|tarde> de DD/MM: N posts"
git push -u origin pacote/AAAA-MM-DD-<periodo>
```

Abra a proposta pela API REST do GitHub (`gh api -X POST repos/tgolessa/allaboutsports-ai/pulls`), com:

- **Título:** `Pacote <manhã|tarde> · DD/MM · N posts`
- **Corpo:**
  - a prévia: `![prévia](https://raw.githubusercontent.com/tgolessa/allaboutsports-ai/pacote/AAAA-MM-DD-<periodo>/posts/_previas/AAAA-MM-DD-<periodo>.jpg)`
  - uma linha por post: horário · formato · manchete · fontes (com links);
  - alertas: temas sensíveis, números de fonte única, pautas que você considerou e descartou por falta de checagem;
  - se algum assunto merecer tratamento **especial** (cobertura maior ou identidade visual própria), sugira em uma linha, sem criar arte nova;
  - instruções: "Para aprovar, faça o merge. Para tirar um post, apague a pasta dele nesta proposta antes do merge. Para não publicar nada, feche a proposta."

Se houver uma proposta anterior ainda aberta, não mexa nela; avise no corpo da nova.

## O que o agente não faz

- Não publica, não faz merge e não grava na `main`.
- Não altera `publicador/`, `.github/`, `templates/` nem este arquivo.
- Não usa fotos, escudos ou logos.
- Não cria identidade visual nova por conta própria.
