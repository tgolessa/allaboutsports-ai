"""Post de apresentação do perfil (carrossel de 6 slides, identidade A)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "templates"))
import render as r  # noqa: E402

T = 6
top = lambda i: r.a_top(i, total=T)
label = lambda t: f'<div class="label"><i></i><span>{t}</span></div>'


def items(rows):
    return '<div class="items">' + "".join(
        f'<div class="item"><span class="k">{k:02d}</span><span class="t">{t}'
        + (f"<small>{s}</small>" if s else "") + "</span></div>"
        for k, (t, s) in enumerate(rows, 1)
    ) + "</div>"


slides = [
    r.page(
        '<div class="top"><span class="brand">AllAboutSports<b>.AI</b></span><span class="pillar">Apresentação</span></div>'
        '<div class="cover-hero"><span class="cover-prefix">até</span>'
        '<span class="cover-number fit-w">6</span>'
        '<span class="cover-title">posts por dia sobre o negócio por trás dos esportes</span></div>'
        + r.a_foot("Prazer, AllAboutSports.AI", "Arraste →"),
        "a",
    ),
    r.page(
        top(2) + '<div class="body">' + label("O que é")
        + '<p class="text">As principais notícias de negócios do esporte mundial: deals, mídia, marcas, tecnologia e parcerias, explicadas em português.</p></div>'
        + r.a_foot("NFL, NBA, Premier League, F1, UFC, tênis e mais"),
        "a",
    ),
    r.page(
        top(3) + '<div class="body">' + label("O que você vai ver")
        + items([
            ("Deals & dinheiro", "Contratos, compras de clubes, valuations"),
            ("Mídia & streaming", "Direitos de transmissão e audiência"),
            ("Marcas & patrocínio", "Naming rights, camisas, atletas como marca"),
            ("Ligas & modelos de negócio", "Teto salarial, novas ligas, SAF"),
            ("Tech, produto & parcerias", "Dados, IA, parcerias entre marcas e a experiência do fã"),
        ]) + "</div>"
        + r.a_foot("Direto ao ponto, com fonte em todo post"),
        "a",
    ),
    r.page(
        top(4) + '<div class="body">' + label("Como funciona")
        + items([
            ("Todo dia", "Carrosséis completos e notas rápidas"),
            ("Toda sexta", "O top 10 da semana"),
            ("A cada 15 dias", "O ranking dos maiores valores do esporte"),
        ]) + "</div>"
        + r.a_foot("Ative as notificações para não perder"),
        "a",
    ),
    r.page(
        top(5) + '<div class="body">' + label("Por que .AI")
        + '<p class="text">O conteúdo é produzido por agentes de inteligência artificial, com fonte citada em cada post e revisão humana.</p></div>'
        + r.a_foot("Viu um erro? Comente que a gente corrige"),
        "a cobalt",
    ),
    r.page(
        top(6)
        + '<div class="body" style="gap:72px"><span class="closing">O negócio do esporte, todo dia<b>.</b></span>'
        '<div class="actions"><span class="btn">Siga @allaboutsports.ai</span><span class="btn ghost">Salve este post</span></div></div>'
        + r.a_foot("Conteúdo produzido por IA com revisão humana", "Fim"),
        "a",
    ),
]

out = Path(__file__).resolve().parent / "imagens"
for name, rep in r.render(slides, out):
    print(name, "ESTOUROU" if rep["overflow"] else "ok")
