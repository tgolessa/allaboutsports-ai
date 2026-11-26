# As últimas 24h no triathlon — AllAboutTri.AI

Instruções para o agente que, todo fim de tarde, monta o carrossel **"As últimas 24h no triathlon"**, publicado automaticamente às **20:00** (Brasília). É o resumo do dia: quem segue o perfil abre e fica sabendo de tudo em 1 minuto.

## 0. Preparação

```bash
git clone https://github.com/tgolessa/allaboutsports-ai && cd allaboutsports-ai
pip install --break-system-packages playwright pillow
```

Leia `docs/linha-editorial.md` (regras de conteúdo e checagem), `README.md` (limites de texto) e `templates/exemplos/exemplo-ultimas24h.json`.

## 1. O que entra

- **4 a 8 notícias** de triathlon publicadas nas **últimas 24 horas** (de ontem às 18h até agora), no Brasil e no mundo.
- Misture editorias: provas, resultados, inscrições, bastidores, treino. Pelo menos 2 itens com ângulo brasileiro quando houver.
- **Pode repetir** o que o perfil publicou hoje (os posts de 06:30, 12:30, 18:30 e algum plantão), em uma linha, desde que não seja mais da metade do resumo. O valor do resumo é juntar tudo num lugar só.
- Cada item precisa de fonte identificável e checada, como em `docs/linha-editorial.md`. Item sem confirmação oficial vai com "deve", "pode" ou "segundo <veículo>".
- Ordem: o mais importante primeiro.
- Se não houver pelo menos 4 notícias que passem na checagem, **não publique** e avise o Tiago.

## 2. Pesquisa

Buscas separadas, em português e em inglês: "triathlon", "IRONMAN", "IRONMAN 70.3", "T100 triathlon", "World Triathlon", "CBTri", "Unlimited Sports", nomes dos principais pros brasileiros, imprensa regional ("Ironman" + capitais). Abra as matérias e as páginas oficiais; confira data de publicação, nomes, tempos e números.

## 3. Produção

Pasta `posts/AAAA-MM-DD-04-ultimas24h/` com:

**`pauta.json`** no formato `ultimas24h`: `data` (ex.: `26/11`) e `itens`, cada um com `titulo_curto` (até ~38 caracteres, vai na capa), `titulo` (até ~60), `resumo` (até ~30 palavras), `editoria`, `fonte` e, se houver um número forte, `numero` (tempo, distância, preço, vagas).

```bash
python templates/render.py posts/<pasta>/pauta.json --out posts/<pasta>/imagens
python agente/story.py posts/<pasta>/pauta.json
```

Abra cada imagem (Read) e corrija qualquer texto cortado ou dado diferente da fonte.

**`post.json`:**
```json
{
  "status": "aprovado",
  "publicar_em": "AAAA-MM-DDT20:00:00-03:00",
  "tipo": "ultimas24h",
  "legenda": "...",
  "imagens": ["imagens/01.jpg", "imagens/02.jpg"]
}
```

**Legenda:** primeira linha "As últimas 24h no triathlon (DD/MM)"; depois a lista das manchetes, uma por linha, com emoji de número (1️⃣ 2️⃣ ...); uma pergunta ("Qual dessas você não sabia?"); `Fontes:` com todas as fontes; hashtags `#triathlon #triatlo #ironman #ironman703 #triathlonbrasil`.

## 4. Entrega

```bash
git add posts && git commit -m "Últimas 24h · DD/MM" && git pull --rebase origin main && git push origin main
```

Mande ao Tiago uma mensagem curta: "Últimas 24h de DD/MM agendado para 20h" e a lista das manchetes. Se não publicou, diga por quê.

## O que o agente não faz

- Não altera arquivos fora da pasta do post.
- Não usa fotos, logos ou imagens de terceiros.
- Não ocupa outro horário além das 20:00.
