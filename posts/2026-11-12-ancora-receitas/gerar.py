"""Peça-âncora: receitas dos gigantes europeus x Flamengo (Deloitte Money League 2026)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "templates"))
import render as r  # noqa: E402

T = 8
SRC = "Deloitte Football Money League 2026"
top = lambda i: r.a_top(i, total=T)
label = lambda t: f'<div class="label"><i></i><span>{t}</span></div>'

RANK = [("Real Madrid", 1161), ("Barcelona", 975), ("Bayern", 861), ("PSG", 837), ("Liverpool", 836),
        ("Manchester City", 829), ("Arsenal", 822), ("Manchester United", 793), ("Tottenham", 673), ("Chelsea", 584)]


def bar(nome, v, pos, hl=False):
    w = round(480 * v / 1161)
    cor = "var(--color-cobalt)" if hl else "var(--color-ink)"
    peso = 800 if hl else 600
    return (f'<div style="display:flex;align-items:center;gap:16px;height:66px">'
            f'<span style="width:44px;flex-shrink:0;font-family:var(--font-sans);font-weight:700;font-size:24px;color:var(--color-muted)">{pos}º</span>'
            f'<span style="width:290px;flex-shrink:0;font-family:var(--font-sans);font-weight:{peso};font-size:30px;color:{cor}">{nome}</span>'
            f'<i style="display:block;height:38px;width:{w}px;background:{"var(--color-cobalt)" if hl else "#C9CCD6"}"></i>'
            f'<span style="font-family:var(--font-sans);font-weight:700;font-size:28px;color:{cor};white-space:nowrap">{v:,}</span></div>').replace(",", ".")


chart = "".join(bar(n, v, i + 1) for i, (n, v) in enumerate(RANK))
chart += '<div style="height:26px;border-left:3px dotted #C9CCD6;margin-left:20px"></div>'
chart += bar("Flamengo", 203, 29, hl=True)

slides = [
    r.page(
        '<div class="top"><span class="brand">AllAboutSports<b>.AI</b></span><span class="pillar">Deals &amp; dinheiro</span></div>'
        '<div class="cover-hero"><span class="cover-number fit-w">5,7x</span>'
        '<span class="cover-title fit-h">é a receita do Real Madrid comparada à do Flamengo, o clube que mais fatura no Brasil</span></div>'
        + r.a_foot(f"Fonte: {SRC}", "Arraste →"), "a"),
    r.page(
        top(2) + '<div class="body" style="gap:28px">' + label("O ranking · receita em € milhões")
        + f'<div style="display:flex;flex-direction:column">{chart}</div>'
        + '<p style="font-family:var(--font-sans);font-size:24px;color:var(--color-muted)">Temporada 2024/25</p></div>'
        + r.a_foot(f"Fonte: {SRC}"), "a"),
    r.page(
        top(3) + '<div class="body">' + label("O fato")
        + '<p class="text fit-h">O Flamengo ficou em 29º no ranking anual da Deloitte, com € 202,7 milhões. É o único clube fora da Europa entre os 30 que mais faturam no mundo.</p></div>'
        + r.a_foot(f"Fonte: {SRC}"), "a"),
    r.page(
        top(4) + '<div class="body">' + label("O número")
        + '<div style="display:flex;flex-direction:column;gap:8px"><span class="big fit-w">€ 594 mi</span>'
        '<span class="big-caption fit-h">só de receita comercial do Real Madrid: quase 3 vezes tudo o que o Flamengo faturou no ranking</span></div></div>'
        + r.a_foot(f"Fonte: {SRC}"), "a"),
    r.page(
        top(5) + '<div class="body">' + label("Em reais")
        + '<div style="display:flex;flex-direction:column;gap:8px"><span class="big fit-w">R$ 2,09 bi</span>'
        '<span class="big-caption fit-h">foi a receita do Flamengo em 2025, um recorde no futebol brasileiro, com R$ 519 mi em venda de jogadores</span></div></div>'
        + r.a_foot("Fonte: balanço do Flamengo 2025"), "a"),
    r.page(
        top(6) + '<div class="body">' + label("Por que importa")
        + '<p class="text fit-h">A distância está em patrocínio, estádio e mídia global. E o câmbio pesa: mesmo crescendo em reais, a receita dos clubes brasileiros encolhe quando convertida para euro.</p></div>'
        + r.a_foot(f"Fontes: {SRC} · Flamengo"), "a cobalt"),
    r.page(
        top(7) + '<div class="body">' + label("O que observar")
        + '<p class="text fit-h">SAFs, investidores estrangeiros e a venda coletiva de direitos de TV são as apostas para encurtar a distância. Qual clube brasileiro chega primeiro ao top 20?</p></div>'
        + r.a_foot(f"Fonte: {SRC}"), "a"),
    r.page(
        top(8)
        + '<div class="body" style="gap:72px"><span class="closing">O negócio do esporte, todo dia<b>.</b></span>'
        '<div class="actions"><span class="btn">Siga @allaboutsports.ai</span><span class="btn ghost">Salve este post</span></div>'
        '<div class="sources"><h4>Fontes</h4><p>Deloitte Football Money League 2026 · 22 jan 2026<br>Balanço do Flamengo 2025 · 31 mar 2026</p></div></div>'
        + r.a_foot("Conteúdo produzido por IA com revisão humana", "Fim"), "a"),
]

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    fmt = "vertical" if "--vertical" in sys.argv else "feed"
    out = here / ("vertical" if fmt == "vertical" else "imagens")
    for name, rep in r.render(slides, out, fmt):
        print(name, "ESTOUROU" if rep["overflow"] else "ok")
