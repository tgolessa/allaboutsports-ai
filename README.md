# AllAboutTri.AI (@allabouttri.ai)

Triathlon e Ironman, explicados em português. Perfil de Instagram com notícias das provas, resultados, inscrições, bastidores e treino, produzido e publicado automaticamente por agentes no Claude. Até 25/11/2026 o perfil se chamava AllAboutSports.AI e cobria negócios do esporte; os posts dessa fase continuam em `posts/`.

## Como o repositório funciona

1. De manhã, o agente de curadoria e produção pesquisa as notícias do dia, escreve os posts e gera as imagens.
2. O pacote do dia chega como uma proposta (pull request) para aprovação.
3. Aprovada a proposta, uma automação do GitHub publica cada post no horário programado.

As imagens ficam neste repositório público porque a Meta exige um endereço aberto para buscar as fotos na hora da publicação.

## Templates (`templates/`)

Geram as imagens JPEG (1080 × 1350) a partir de um JSON de pauta.

```bash
pip install playwright
python templates/render.py templates/exemplos/exemplo-noticia.json
```

As imagens saem em `templates/out/<nome-do-json>/`. O script reduz a fonte de textos longos automaticamente e avisa com `ESTOUROU` se mesmo assim não couber.

| Tipo | Uso | Slides |
| --- | --- | --- |
| `noticia` | Carrossel de notícia (post principal das 12:30) | 7 |
| `nota` | Post de uma imagem, com slide opcional de "por que importa" | 1 ou 2 |
| `resultado` | Resultado de prova: capa com o tempo do vencedor, tabela por categoria (até 2 categorias, até 10 atletas cada) | 3 ou 4 |
| `inscricao` | Abertura de inscrições: capa com a data, ficha da prova | 3 |
| `semanal` | Top 10 da semana, toda sexta | 7 |
| `reel` | Vídeo 9:16 feito de um `pauta.json` de `noticia` (`agente/reel.py`), todo dia às 19:30 | 1 vídeo |

Os campos de cada tipo estão nos exemplos em `templates/exemplos/`.

### Regras de texto

| Campo | Limite |
| --- | --- |
| Manchete | até 10 palavras |
| Fato, contexto, por que importa, o que observar | até 30 palavras cada |
| Número da capa | curto: `10bi`, `3x`, `40%` |
| `titulo_curto` (lista do semanal) | até 6 palavras |

Tempos sempre no formato `8:31:12` (ou `52:10` abaixo de 1 hora); distâncias em km com vírgula (`3,8 km`).

### Identidade

Identidade "Split": fundo claro, barra com as três modalidades (natação azul, bike vermelho, corrida preto) e números grandes de cronômetro. Cores, fontes e margens ficam em `templates/base.css`. Fontes: Barlow Condensed, Inter e JetBrains Mono (licença SIL OFL).

## Agentes e automações

| Arquivo | O que faz | Quando |
| --- | --- | --- |
| `AGENTE.md` | Pesquisa, produz e agenda os 3 posts do dia (publicação automática) | 5h15 todo dia |
| `PLANTAO.md` | Notícia quente: resultado oficial ou anúncio importante, publicação automática | 9h20 · 13h20 · 17h20 · 21h20 |
| `ANALISTA.md` | Relatório de desempenho e ajustes em `docs/aprendizados.md` | pausado |
| `COMENTARIOS.md` | Responde comentários simples e separa os sensíveis | 12h05 · 18h05 · 22h05 |
| `PARCERIAS.md` | Sugere parcerias com convites prontos | pausado |
| `publicar.yml` | Publica no Instagram (e no Threads, se configurado) os posts aprovados | a cada 15 min |
| `metricas.yml` | Coleta as métricas do dia | 23h30 |
| `comentarios.yml` | Busca comentários e publica respostas | 11h50 · 17h50 · 21h50 |
| `threads-chave.yml` | Renova a chave do Threads | dias 1 e 16 |

Collab post: no `post.json`, `"colaboradores": ["@usuario"]` (até 3). Threads: `"legenda_threads"` opcional, até 500 caracteres; sem ela, o texto é gerado da legenda do Instagram.
