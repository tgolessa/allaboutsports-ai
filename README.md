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
