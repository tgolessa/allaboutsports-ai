"""Post de lançamento em collab com @tgolessa (carrossel de 6 slides, identidade A), em tom leve para amigos."""
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
        '<div class="top"><span class="brand">AllAboutSports<b>.AI</b></span><span class="pillar">Projeto novo</span></div>'
        '<div class="cover-hero"><span class="cover-prefix">um perfil</span>'
        '<span class="cover-number fit-w">100%</span>'
        '<span class="cover-title">feito por agentes de IA. Eu só aprovo.</span></div>'
        + r.a_foot("Com @tgolessa", "Arraste →"),
        "a",
    ),
    r.page(
        top(2) + '<div class="body">' + label("O que é")
        + '<p class="text">O negócio por trás dos esportes, explicado em português. Contratos, direitos de TV, patrocínios, tecnologia e o dinheiro que move clubes, ligas e atletas.</p></div>'
        + r.a_foot("De NFL e F1 a Brasileirão e triathlon"),
        "a",
    ),
    r.page(
        top(3) + '<div class="body">' + label("O experimento")
        + '<p class="text">Quero ver até onde dá para tocar um perfil de notícias de verdade só com agentes de IA. E com qualidade, não com conteúdo genérico.</p></div>'
        + r.a_foot("Fonte citada em todo post"),
        "a",
    ),
    r.page(
        top(4) + '<div class="body">' + label("Como funciona")
        + items([
            ("Um agente garimpa as notícias", "Lê as principais fontes do mundo todo dia"),
            ("Outro escreve e faz a arte", "Carrossel, Reel, Story e newsletter"),
            ("Eu reviso e aprovo", "Duas vezes por dia, pelo celular"),
            ("Os agentes publicam", "E depois analisam o que funcionou"),
        ]) + "</div>"
        + r.a_foot("Até 6 posts por dia"),
        "a",
    ),
    r.page(
        top(5) + '<div class="body">' + label("Onde você entra")
        + '<p class="text">Segue, comenta e critica. Achou um erro, um texto chato ou uma arte feia? Pode falar. É assim que os agentes (e eu) aprendem.</p></div>'
        + r.a_foot("Crítica sincera vale mais que like"),
        "a cobalt",
    ),
    r.page(
        top(6)
        + '<div class="body" style="gap:72px"><span class="closing">Bora acompanhar<b>?</b></span>'
        '<div class="actions"><span class="btn">Siga @allaboutsports.ai</span><span class="btn ghost">Mande para quem curte esporte</span></div></div>'
        + r.a_foot("Conteúdo produzido por IA com revisão humana", "Fim"),
        "a",
    ),
]

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "imagens"
    for name, rep in r.render(slides, out):
        print(name, "ESTOUROU" if rep["overflow"] else "ok")
