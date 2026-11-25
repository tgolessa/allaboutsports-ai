# Agente diário — AllAboutTri.AI

Instruções para o agente que, toda madrugada, escolhe as pautas do dia, produz os 3 posts e deixa tudo agendado. **A publicação é automática:** o agente grava os posts na `main` com `"status": "aprovado"` e o workflow `publicar.yml` (a cada 15 minutos) publica cada um no horário marcado. Não há aprovação manual, então a checagem é responsabilidade do agente: **na dúvida sobre um fato, o post não sai.**

## 0. Preparação

```bash
git clone https://github.com/tgolessa/allaboutsports-ai && cd allaboutsports-ai
pip install --break-system-packages playwright pillow numpy
```

Leia antes de começar: `docs/linha-editorial.md` (regras de conteúdo), `docs/calendario.md` (provas e inscrições), `docs/aprendizados.md` (o que funcionou), `README.md` (formatos e limites de texto) e os exemplos em `templates/exemplos/`.

Datas e horários sempre no fuso de Brasília (America/Sao_Paulo, `-03:00`).

## 1. Os 3 posts do dia

| Horário | Post | Formatos |
| --- | --- | --- |
| **06:30** | Rápido, para quem abre o celular antes ou depois do treino | `nota`, `inscricao` ou `resultado` |
| **12:30** | O post principal do dia | `noticia` (carrossel) ou `resultado` de prova grande |
| **19:30** | Reel, sobre uma pauta diferente das outras duas | `reel` feito a partir de um `pauta.json` de `noticia` |

- **Segunda:** o post das 06:30 é o resultado mais importante do fim de semana, se houver prova relevante (IRONMAN Pro Series, T100, IRONMAN ou 70.3 no Brasil, brasileiro em pódio).
- **Sexta:** o post das 12:30 é o `semanal` (Top 10 da semana, de segunda a sexta).
- **Calendário:** se houver prova grande ou abertura de inscrições nos próximos 7 dias (`docs/calendario.md`), pelo menos 1 post do dia trata disso.
- **Mistura de editorias:** respeite os pesos da linha editorial ao longo da semana e cerca de metade dos posts com ângulo brasileiro.
- **Story em todos os posts.**
- **Menos é melhor que errado:** se não houver 3 pautas que passem na checagem, publique 2, ou 1. Diga isso na mensagem final.

## 2. Pesquisa

1. **Histórico:** leia os `pauta.json` dos posts dos últimos 14 dias em `posts/` e não repita assunto já publicado, a não ser que haja fato novo relevante (e então diga o que mudou). Veja também se o plantão já publicou algo hoje.
2. **Janela:** notícias das últimas 24 a 48 horas; inscrições e calendário podem ter anúncio mais antigo se a data de abertura ainda não passou.
3. **Busca:** inclua sempre buscas pela imprensa regional brasileira ("Ironman" + nome de capital, "triathlon" + estado, "etapa do Ironman", "nova prova de triathlon"): prova nova no Brasil costuma aparecer primeiro em jornal local. Faça buscas separadas por editoria e por circuito, em português e em inglês (ex.: "IRONMAN Brasil", "IRONMAN 70.3 inscrições", "triathlon resultado", "IRONMAN Pro Series results", "T100 triathlon", "Kona qualifying", "triathlon training study", nomes dos principais pros brasileiros). Abra as matérias e as páginas oficiais (WebFetch); não confie só no resumo da busca.
4. **Critérios** (nota de 1 a 5; escolha as maiores somas):
   - é útil ou interessante para o triatleta amador brasileiro (vai salvar, mandar no grupo de treino ou comentar);
   - tem um dado concreto (tempo, distância, data, preço, vagas) ou uma história forte;
   - envolve prova, atleta ou marca conhecida aqui;
   - é novo ou muda o que se sabia;
   - equilibra as editorias da semana.
5. **Checagem:** siga a seção "Checagem e fontes" da linha editorial. Resultado e inscrição só com fonte oficial. Confira nome, país, tempo, data e preço um a um.

## 3. Produção

Para cada post, crie a pasta `posts/AAAA-MM-DD-NN-<slug>/` (NN = 01, 02, 03 na ordem do dia) com:

**`pauta.json`** — os campos do formato, seguindo os exemplos em `templates/exemplos/` e os limites de texto do README.

**Imagens:**
```bash
python templates/render.py posts/<pasta>/pauta.json --out posts/<pasta>/imagens
```
Se aparecer `ESTOUROU`, encurte o texto e gere de novo.

**Story** (todos os posts):
```bash
python agente/story.py posts/<pasta>/pauta.json
```

**Reel** (post das 19:30): na pasta do Reel, escreva um `pauta.json` de `noticia` sobre a pauta escolhida (ele não vira carrossel no feed) e gere o vídeo:
```bash
python agente/reel.py posts/<pasta>/pauta.json
python agente/story.py posts/<pasta>/pauta.json
```
Isso cria `reel.mp4` e `reel_capa.jpg`. Confira pelo menos 3 quadros (`ffmpeg -ss <segundos> -i reel.mp4 -frames:v 1 quadro.png`). O `post.json` do Reel usa `"tipo": "reel"`, `"video": "reel.mp4"`, `"capa": "reel_capa.jpg"` (sem `imagens`).

**`post.json`:**
```json
{
  "status": "aprovado",
  "publicar_em": "2026-11-26T12:30:00-03:00",
  "tipo": "noticia",
  "legenda": "...",
  "imagens": ["imagens/01.jpg", "imagens/02.jpg"]
}
```

**Legenda** (até ~1.000 caracteres; no Reel, mais curta):
1. Primeira linha: o gancho da capa, em outras palavras.
2. Duas a quatro frases com o fato e por que importa para quem treina.
3. Uma pergunta para os comentários (ex.: "Você vai?", "Qual foi seu tempo nessa prova?").
4. `Fontes: <fonte> (<data>), <fonte>.`
5. 5 a 8 hashtags: sempre `#triathlon #triatlo #ironman`, mais as do tema (`#ironman703`, `#triathlonbrasil`, `#ironmanbrasil`, `#kona`, `#t100`, `#treinodetriathlon`).

## 4. Revisão antes de gravar

- Abra (Read) cada imagem e cada story: nada cortado, sem erro de digitação, nomes, tempos e datas iguais aos da fonte.
- Releia os textos procurando as expressões proibidas da linha editorial e frases com cara de texto de IA.
- Confira se nenhum post afirma mais do que a fonte diz. Se houver dúvida que você não consegue resolver, tire o post.

## 5. Entrega (direto na `main`)

```bash
git add posts docs/calendario.md
git commit -m "Posts de DD/MM: <manchete 1> · <manchete 2> · <manchete 3>"
git pull --rebase origin main && git push origin main
```

Às segundas, revise também `docs/calendario.md`: confirme as datas "a confirmar" e acrescente aberturas de inscrição anunciadas, sempre com o link da fonte.

Ao terminar, mande ao Tiago uma mensagem curta: os horários e as manchetes do dia, e qualquer alerta (fonte única, tema sensível, pauta descartada por falta de checagem). Se algo impediu a entrega, diga exatamente o quê.

## O que o agente não faz

- Não publica direto no Instagram: quem publica é o workflow.
- Não altera `publicador/`, `.github/`, `templates/` nem este arquivo.
- Não usa fotos, logos ou imagens de terceiros.
- Não prescreve treino, dieta ou suplemento.
