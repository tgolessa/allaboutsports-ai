"""
AllAboutSports.AI — monta o HTML da newsletter semanal (Top 10 da semana).

Uso:
  python agente/newsletter.py posts/<pasta>/edicao.json [--previa]

edicao.json:
{
  "numero": 1,
  "data": "13/11/2026",
  "abertura": "2 ou 3 frases sobre o que marcou a semana.",
  "itens": [
    {"pilar": "Deals & dinheiro", "titulo": "...", "texto": "2 ou 3 frases.",
     "numero": "US$ 10 bi", "fonte": "Sportico", "fonte_url": "https://..."}
  ],
  "fechamento": "1 ou 2 frases."
}

Gera newsletter.html na mesma pasta (HTML de e-mail: tabelas e estilos
inline, que funcionam no Gmail, Outlook e Apple Mail). Com --previa,
gera também previa.jpg para a proposta de aprovação.
"""
import argparse
import html
import json
from pathlib import Path

INK, PAPER, ICE, MUTED, COBALT = "#0B0B0F", "#FFFFFF", "#F1F2F6", "#6B6B75", "#1F3BFF"
FONT = "'Archivo','Helvetica Neue',Helvetica,Arial,sans-serif"
INSTAGRAM = "https://www.instagram.com/allaboutsports.ai/"


def e(t):
    return html.escape(str(t or ""))


def item(i, it):
    num = (f'<div style="font-family:{FONT};font-weight:900;font-size:30px;line-height:34px;'
           f'color:{COBALT};letter-spacing:-0.5px;padding:0 0 6px 0;">{e(it["numero"])}</div>') if it.get("numero") else ""
    fonte = (f'<a href="{e(it["fonte_url"])}" style="color:{MUTED};text-decoration:underline;">{e(it["fonte"])}</a>'
             if it.get("fonte_url") else e(it.get("fonte")))
    return f'''
<tr><td style="padding:28px 0;border-top:1px solid #E3E4EA;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="52" valign="top" style="font-family:{FONT};font-weight:700;font-size:15px;color:{COBALT};padding-top:4px;">{i:02d}</td>
    <td valign="top">
      <div style="font-family:{FONT};font-weight:700;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:{COBALT};padding-bottom:8px;">{e(it.get("pilar"))}</div>
      {num}
      <div style="font-family:{FONT};font-weight:800;font-size:21px;line-height:27px;color:{INK};padding-bottom:8px;">{e(it["titulo"])}</div>
      <div style="font-family:{FONT};font-size:16px;line-height:25px;color:#33333A;padding-bottom:10px;">{e(it["texto"])}</div>
      <div style="font-family:{FONT};font-size:13px;color:{MUTED};">Fonte: {fonte}</div>
    </td>
  </tr></table>
</td></tr>'''


def build(d):
    itens = "".join(item(i, it) for i, it in enumerate(d["itens"], 1))
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;700;800;900&display=swap" rel="stylesheet">
<title>Top 10 da semana · AllAboutSports.AI</title></head>
<body style="margin:0;padding:0;background:{ICE};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{ICE};"><tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:{PAPER};">
  <tr><td style="padding:32px 36px 0 36px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
      <td style="font-family:{FONT};font-weight:900;font-size:18px;color:{INK};">AllAboutSports<span style="color:{COBALT};">.AI</span></td>
      <td align="right" style="font-family:{FONT};font-weight:700;font-size:12px;letter-spacing:1.5px;color:{MUTED};">Nº {e(d.get("numero"))} · {e(d.get("data"))}</td>
    </tr></table>
  </td></tr>
  <tr><td style="padding:36px 36px 8px 36px;">
    <div style="font-family:{FONT};font-weight:900;font-size:44px;line-height:46px;letter-spacing:-1.5px;color:{INK};">Top 10<br>da semana<span style="color:{COBALT};">.</span></div>
    <div style="font-family:{FONT};font-size:17px;line-height:27px;color:#33333A;padding-top:18px;">{e(d["abertura"])}</div>
  </td></tr>
  <tr><td style="padding:12px 36px 8px 36px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{itens}</table>
  </td></tr>
  <tr><td style="padding:8px 36px 36px 36px;">
    <div style="font-family:{FONT};font-size:16px;line-height:25px;color:#33333A;padding:24px 0;border-top:1px solid #E3E4EA;">{e(d.get("fechamento"))}</div>
    <a href="{INSTAGRAM}" style="display:inline-block;background:{COBALT};color:{PAPER};font-family:{FONT};font-weight:700;font-size:15px;text-decoration:none;padding:14px 24px;">Siga @allaboutsports.ai no Instagram</a>
    <div style="font-family:{FONT};font-size:12px;line-height:18px;color:{MUTED};padding-top:28px;">O negócio por trás dos esportes, explicado em português. Conteúdo produzido por IA, com fonte em cada notícia e revisão humana.</div>
  </td></tr>
</table>
</td></tr></table>
</body></html>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edicao")
    ap.add_argument("--previa", action="store_true")
    a = ap.parse_args()
    path = Path(a.edicao).resolve()
    d = json.loads(path.read_text(encoding="utf-8"))
    out = path.parent / "newsletter.html"
    out.write_text(build(d), encoding="utf-8")
    print(out)
    if a.previa:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
            pg = b.new_page(viewport={"width": 680, "height": 900})
            pg.goto(out.as_uri())
            pg.wait_for_timeout(800)
            pg.screenshot(path=str(path.parent / "previa.jpg"), full_page=True, type="jpeg", quality=80)
            b.close()
        print(path.parent / "previa.jpg")


if __name__ == "__main__":
    main()
