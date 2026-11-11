# AllAboutSports.AI

O negócio por trás dos esportes, explicado em português. Perfil de Instagram com notícias globais de sports business, produzido por agentes no Claude com revisão humana.

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

| Tipo | Uso | Slides | Identidade |
| --- | --- | --- | --- |
| `noticia` | Carrossel completo, 2 por dia | 7 | A · cobalto |
| `nota` | Nota rápida, 2 a 4 por dia | 1 ou 2 | A · cobalto |
| `semanal` | Top 10 da semana, toda sexta | 7 | C · terminal |
| `ranking` | Ranking dos 10 maiores valores, a cada 15 dias | 7 | C · terminal |
| `reel` | Versão em vídeo 9:16 de um carrossel (`agente/reel.py`), terça e quinta | 1 vídeo | A ou C |

Os campos de cada tipo estão nos exemplos em `templates/exemplos/`.

### Regras de texto

| Campo | Limite |
| --- | --- |
| Manchete | até 10 palavras |
| Fato, contexto, por que importa, o que observar | até 30 palavras cada |
| Número da capa | curto: `10bi`, `3x`, `40%` |
| `titulo_curto` (lista do semanal) | até 6 palavras |

No ranking, todos os itens usam o mesmo tipo de valor (total do negócio, convertido para a mesma moeda) para a comparação fazer sentido.

### Identidade

Cores, fontes e margens ficam em `templates/base.css`. Fontes: Archivo, Archivo Black e IBM Plex Mono (licença SIL OFL).

## Agentes e automações

| Arquivo | O que faz | Quando |
| --- | --- | --- |
| `AGENTE.md` | Pesquisa notícias, produz o pacote de posts e abre a proposta | 7h45 todo dia · 15h45 seg–sex |
| `ANALISTA.md` | Relatório de desempenho e ajustes em `docs/aprendizados.md` | segunda 8h15 |
| `COMENTARIOS.md` | Responde comentários simples e separa os sensíveis | 12h05 · 18h05 · 22h05 |
| `PARCERIAS.md` | Sugere 5 parcerias com convites prontos | quarta 9h45 |
| `publicar.yml` | Publica no Instagram (e no Threads, se configurado) os posts aprovados | a cada 15 min |
| `metricas.yml` | Coleta as métricas do dia | 23h30 |
| `comentarios.yml` | Busca comentários e publica respostas | 11h50 · 17h50 · 21h50 |
| `threads-chave.yml` | Renova a chave do Threads | dias 1 e 16 |

Collab post: no `post.json`, `"colaboradores": ["@usuario"]` (até 3). Threads: `"legenda_threads"` opcional, até 500 caracteres; sem ela, o texto é gerado da legenda do Instagram.
