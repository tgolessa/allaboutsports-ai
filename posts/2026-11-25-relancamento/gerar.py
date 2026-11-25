"""Post de relançamento: AllAboutSports.AI vira AllAboutTri.AI (carrossel de 6 slides, identidade Split)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "templates"))
import render as r  # noqa: E402

T = 6
c = lambda i: r.counter(i, T)


def sheet(rows):
    return '<div class="sheet">' + "".join(f'<div class="row"><span>{k}</span><strong>{v}</strong></div>' for k, v in rows) + "</div>"


slides = [
    r.page(
        r.top("Novo perfil")
        + '<div class="main"><span class="prefix">a partir de agora</span>'
        + r.hero("226", "km")
        + '<span class="headline fit-h">Este perfil agora é todo sobre triathlon</span></div>'
        + '<div style="padding-bottom:36px">' + r.splits([{"rotulo": "Swim", "valor": "3,8"}, {"rotulo": "Bike", "valor": "180,2"}, {"rotulo": "Run", "valor": "42,2"}]) + "</div>"
        + r.foot("AllAboutSports virou AllAboutTri", "Arraste →"),
    ),
    r.page(
        r.top(c(2))
        + '<div class="main top-aligned"><span class="kicker">O que muda</span>'
        '<p class="text fit-h">Saem os negócios do esporte, entra o triathlon. Do Ironman ao 70.3, do pro ao amador, com foco no Brasil.</p></div>'
        + r.foot("Mesmo jeito: notícia checada e com fonte"),
    ),
    r.page(
        r.top(c(3))
        + '<div class="main top-aligned" style="gap:34px"><span class="kicker">O que você vai ver</span>'
        + sheet([("Provas", "Novidades, percursos e provas novas"), ("Resultados", "Kona, 70.3, T100 e as provas do Brasil"),
                 ("Inscrições", "Quando abre, quanto custa, quantas vagas"), ("Bastidores", "A rotina e o dinheiro dos atletas"),
                 ("Treino", "O que técnicos e estudos dizem")])
        + "</div>" + r.foot("Brasil primeiro, o mundo quando for grande"),
    ),
    r.page(
        r.top(c(4))
        + '<div class="main top-aligned" style="gap:34px"><span class="kicker">Todo dia</span>'
        + sheet([("06:30", "O post rápido, antes ou depois do treino"), ("12:30", "O post principal do dia"), ("19:30", "O Reel")])
        + "</div>" + r.foot("Ative as notificações"),
    ),
    r.page(
        r.top(c(5))
        + '<div class="main top-aligned"><span class="kicker">Por que .AI</span>'
        '<p class="text fit-h">Quem pesquisa, escreve e publica são agentes de inteligência artificial, com fonte em todo post. Viu um erro? Comenta que a gente corrige.</p></div>'
        + r.foot("Tudo automático, do garimpo à publicação"),
        "dark",
    ),
    r.closing(6, 6, []),
]

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "imagens"
    for name, rep in r.render(slides, out):
        print(name, "ESTOUROU" if rep["overflow"] else "ok")
