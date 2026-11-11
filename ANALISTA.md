# Analista semanal — AllAboutSports.AI

Instruções para o agente que, toda segunda de manhã, analisa o desempenho do perfil e propõe ajustes nas regras de pauta. Ele **não publica nada** e **não grava direto na `main`**: entrega uma proposta (pull request) com o relatório e, se houver, mudanças em `docs/aprendizados.md`.

## 0. Preparação

```bash
git clone https://github.com/tgolessa/allaboutsports-ai && cd allaboutsports-ai
```

Leia `docs/linha-editorial.md`, `docs/aprendizados.md` (regras aprendidas até aqui) e o relatório anterior mais recente em `relatorios/`.

## 1. Dados

- `metricas/AAAA-MM-DD.json`: um retrato por dia, coletado às 23h30 pelo workflow `metricas.yml`. Use o **mais recente** para os números de cada post (os valores são acumulados) e a série de arquivos para a evolução de seguidores.
- Cada post traz: horário (`hora_brt`, `dia_semana`), formato (`formato`: noticia, nota, semanal, ranking, especial), `pilar`, `manchete`, nº de slides e as métricas da Meta (`reach`, `views`, `saved`, `shares`, `likes`, `comments`, `total_interactions`, `profile_visits`, `follows`). Algumas podem faltar; veja `metricas_indisponiveis`.
- Posts sem `formato`/`pilar` foram publicados à mão; trate como "manual".

## 2. Análise

Janela principal: os últimos 7 dias. Compare com as 4 semanas anteriores quando houver dados.

Calcule por post e resuma por **formato**, **pilar**, **faixa de horário** (manhã/tarde/noite) e **dia da semana**:
- alcance;
- taxa de salvamento = salvamentos ÷ alcance;
- taxa de compartilhamento = compartilhamentos ÷ alcance;
- seguidores ganhos (`follows`), quando disponível;
- interações ÷ alcance.

Use **mediana**, não média (um post viral distorce a média). Destaque os 3 melhores e os 3 piores posts da semana pela taxa de salvamento + compartilhamento, com o motivo provável (tema, capa, número, horário).

**Cuidado com amostra pequena.** Só proponha uma regra nova quando o padrão aparecer em pelo menos 6 posts de cada lado da comparação. Abaixo disso, registre como "hipótese para observar", sem mudar regra.

## 3. Relatório

Escreva `relatorios/AAAA-MM-DD.md` (data da segunda-feira) com, nesta ordem:

1. **Resumo em 3 linhas:** seguidores no fim da semana e variação, alcance total, o principal aprendizado.
2. **Números da semana:** tabela com seguidores, posts publicados, alcance mediano, taxa de salvamento e de compartilhamento medianas, comparados com a semana anterior.
3. **Por formato e por pilar:** tabelas curtas.
4. **Horários:** o que funcionou melhor e pior.
5. **Destaques:** 3 melhores e 3 piores posts, com link e motivo provável.
6. **Recomendações:** no máximo 3, cada uma com a evidência (números e quantidade de posts) e a mudança concreta proposta.
7. **Impulsionar:** os 2 posts da semana com maior taxa de salvamento + compartilhamento (e alcance acima da mediana), indicados para impulsionamento pago. Para cada um: link, por que foi escolhido, público sugerido (Brasil, 25–45 anos, interesses em esportes, negócios, marketing ou tecnologia, ajustado ao tema), orçamento sugerido de R$ 20 a R$ 50 por dia por 3 a 5 dias e objetivo (visitas ao perfil). A decisão e o gasto são do Tiago; você só recomenda.
8. **Reels:** compare Reels e carrosséis do mesmo assunto (alcance e seguidores ganhos) e diga se a frequência de Reels deve subir, cair ou se manter.
9. **Hipóteses para observar:** padrões ainda sem amostra suficiente.

Texto direto, em português, sem jargão desnecessário e sem expressões com cara de texto de IA (veja a lista na linha editorial).

## 3.1 Calendário de grandes eventos

Atualize `docs/calendario.md` com os grandes eventos esportivos das **próximas 8 semanas** (finais, inícios de temporada, drafts, janelas de transferência, grandes torneios, leilões de direitos), checando cada data em fonte oficial e citando a fonte na tabela. Remova os que já passaram. Inclua essa mudança na mesma proposta.

## 4. Proposta de ajustes

Se houver recomendações com evidência suficiente, edite `docs/aprendizados.md`:
- Cada regra em uma linha, com data e evidência curta. Ex.: `2026-11-23 · Notas de mídia & streaming às 19h30 têm o dobro da taxa de compartilhamento das de 11h30 (8 x 7 posts). Priorizar esse horário para o pilar.`
- Se uma regra antiga deixou de valer, mova-a para a seção "Revogadas", com o motivo.

O agente de pauta lê `docs/aprendizados.md` em toda rodada; o que você escrever ali muda o conteúdo a partir da aprovação.

## 5. Entrega

```bash
git checkout -b relatorio/AAAA-MM-DD
git add relatorios docs/aprendizados.md docs/calendario.md
git commit -m "Relatório semanal de DD/MM"
git push -u origin relatorio/AAAA-MM-DD
```

Abra a proposta pela API REST do GitHub (`gh api -X POST repos/tgolessa/allaboutsports-ai/pulls`):
- **Título:** `Relatório semanal · DD/MM` (+ ` · N ajustes propostos`, se houver)
- **Corpo:** o resumo de 3 linhas, as recomendações e a instrução: "Para aplicar os ajustes, faça o merge. Para guardar só o relatório, apague as mudanças em docs/aprendizados.md antes do merge."

Depois, mande ao Tiago uma mensagem curta com o link da proposta e o resumo de 3 linhas.

## O que o analista não faz

- Não publica, não faz merge e não grava na `main`.
- Não altera `AGENTE.md`, `templates/`, `publicador/` nem `.github/`.
- Não inventa números: se um dado não estiver nos arquivos de métricas, diga que não está.
