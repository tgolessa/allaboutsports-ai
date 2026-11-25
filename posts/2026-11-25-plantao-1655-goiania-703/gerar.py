"""Plantão 25/11: Goiânia deve ganhar um IRONMAN 70.3 em julho de 2027 (O Popular, coluna Giro). Capa com foto de @tgolessa."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "templates"))
import render as r  # noqa: E402

SRC = "O Popular, coluna Giro"
FOTO = (HERE / "foto-feed.jpg").as_uri()


def sheet(rows):
    return '<div class="sheet">' + "".join(f'<div class="row"><span>{k}</span><strong>{v}</strong></div>' for k, v in rows) + "</div>"


capa = r.page(
    r.top("Provas")
    + f'<div style="margin:30px -72px 0;height:760px;background:url({FOTO}) center/cover"></div>'
    + '<div class="main" style="gap:18px;padding:34px 0 30px"><span class="kicker">Em negociação</span>'
    '<span class="headline fit-h" style="font-size:80px">Goiânia deve ganhar um IRONMAN 70.3 em julho de 2027</span></div>'
    + r.foot(f"Fonte: O Popular · Foto: @tgolessa", "Arraste →"),
).replace('<div class="tribar"><i class="s"></i><i class="b"></i><i class="r"></i></div>', '<div class="tribar" style="margin-top:30px"><i class="s"></i><i class="b"></i><i class="r"></i></div>', 1)
# a foto já fica logo abaixo da barra
capa = capa.replace('margin:30px -72px 0;height:760px', 'margin:0 -72px;height:760px')

slides = [
    capa,
    r.page(
        r.top(r.counter(2, 3))
        + '<div class="main top-aligned" style="gap:34px"><span class="kicker">O que se sabe</span>'
        + sheet([
            ("Prova", "IRONMAN 70.3: 1,9 km de natação, 90 km de bike e 21,1 km de corrida"),
            ("Cidade", "Goiânia (GO)"),
            ("Quando", "Julho de 2027, segundo a coluna"),
            ("Status", "Fase final de negociação"),
            ("Quem contou", "O prefeito Sandro Mabel, em discurso na noite de 24/11"),
        ])
        + "</div>" + r.foot(f"Fonte: {SRC}"),
    ),
    r.page(
        r.top(r.counter(3, 3))
        + '<div class="main top-aligned"><span class="kicker">O que falta</span>'
        '<p class="text fit-h">O anúncio oficial. Ainda não há confirmação da IRONMAN nem da Unlimited Sports, que organiza as provas no Brasil. Data, local e inscrições só valem depois disso. A gente avisa quando sair.</p></div>'
        + r.foot(f"Siga {r.HANDLE}", "Fim"),
        "dark",
    ),
]

STORY = f"""<div class="slide" style="padding:0;position:relative;background:#101114 url({(HERE / 'foto-story.jpg').as_uri()}) center/cover">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(16,17,20,.55) 0%,rgba(16,17,20,0) 18%,rgba(16,17,20,0) 30%,rgba(16,17,20,.95) 62%)"></div>
<div style="position:absolute;left:72px;right:150px;top:230px" class="top"><span style="color:#F2F1EC">AllAboutTri<b>.AI</b></span></div>
<div style="position:absolute;left:72px;right:150px;bottom:440px;display:flex;flex-direction:column;gap:22px;color:#F2F1EC">
<span class="kicker">Em negociação</span>
<span class="headline" style="font-size:96px">Goiânia deve ganhar um IRONMAN 70.3 em julho de 2027</span>
<span style="font-family:var(--mono);font-size:26px;color:#C9C9CC">Post novo no perfil ↑</span></div></div>"""

if __name__ == "__main__":
    for name, rep in r.render(slides, HERE / "imagens"):
        print(name, "ESTOUROU" if rep["overflow"] else "ok")
    import shutil, tempfile
    with tempfile.TemporaryDirectory() as t:
        doc = r.page("").replace('<div class="slide "></div>', STORY)
        r.render([doc], Path(t), "vertical")
        shutil.copy(Path(t) / "01.jpg", HERE / "story.jpg")
    print("story ok")
