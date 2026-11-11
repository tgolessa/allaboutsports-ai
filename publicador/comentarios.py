"""
AllAboutSports.AI — comentários do Instagram.

  python publicador/comentarios.py coletar --saida dados/comentarios/fila.json [--dias 7]
      Lista os comentários dos posts dos últimos DIAS dias que ainda não
      têm resposta do perfil e grava a fila em JSON.

  python publicador/comentarios.py responder dados/comentarios/respostas/<arquivo>.json
      Lê {"respostas": [{"comment_id": "...", "mensagem": "..."}]} e publica
      cada resposta, pulando as que o perfil já respondeu. Grava o resultado
      de volta no mesmo arquivo (enviado / pulado / erro).

Requer IG_ACCESS_TOKEN e IG_USER_ID (instagram_basic, instagram_manage_comments).
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish import IG_USER, TOKEN, GraphError, graph  # noqa: E402

MAX_REPLY = 2200  # limite de caracteres de comentário no Instagram


def username():
    return graph("GET", IG_USER, {"fields": "username"})["username"]


def media_since(days):
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    items, after = [], None
    while True:
        params = {"fields": "id,caption,timestamp,permalink,comments_count", "limit": "50"}
        if after:
            params["after"] = after
        page = graph("GET", f"{IG_USER}/media", params)
        for m in page.get("data", []):
            if dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z") < since:
                return items
            items.append(m)
        after = page.get("paging", {}).get("cursors", {}).get("after")
        if not page.get("paging", {}).get("next"):
            return items


def comments_of(media_id):
    out, after = [], None
    while True:
        params = {"fields": "id,text,username,timestamp,like_count,replies{id,username,text,timestamp}", "limit": "50"}
        if after:
            params["after"] = after
        page = graph("GET", f"{media_id}/comments", params)
        out += page.get("data", [])
        after = page.get("paging", {}).get("cursors", {}).get("after")
        if not page.get("paging", {}).get("next"):
            return out


def coletar(saida, dias):
    me = username()
    fila = []
    for m in media_since(dias):
        if not m.get("comments_count"):
            continue
        for c in comments_of(m["id"]):
            if c.get("username") == me:
                continue
            replies = (c.get("replies") or {}).get("data", [])
            if any(r.get("username") == me for r in replies):
                continue
            fila.append({
                "comment_id": c["id"],
                "usuario": c.get("username"),
                "texto": c.get("text"),
                "quando": c.get("timestamp"),
                "curtidas": c.get("like_count"),
                "respostas_de_outros": [{"usuario": r.get("username"), "texto": r.get("text")} for r in replies],
                "post": {
                    "media_id": m["id"],
                    "link": m.get("permalink"),
                    "legenda_inicio": (m.get("caption") or "")[:300],
                },
            })
    out = {"coletado_em": dt.datetime.now(dt.timezone.utc).isoformat(), "perfil": me, "comentarios": fila}
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    Path(saida).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(fila)} comentário(s) sem resposta -> {saida}")


def already_replied(comment_id, me):
    data = graph("GET", comment_id, {"fields": "replies{username}"})
    return any(r.get("username") == me for r in (data.get("replies") or {}).get("data", []))


def responder(arquivo):
    path = Path(arquivo)
    doc = json.loads(path.read_text(encoding="utf-8"))
    me = username()
    enviados = 0
    for r in doc.get("respostas", []):
        if r.get("status") in ("enviado", "pulado"):
            continue
        msg = (r.get("mensagem") or "").strip()
        if not msg or len(msg) > MAX_REPLY:
            r["status"], r["erro"] = "erro", "mensagem vazia ou longa demais"
            continue
        try:
            if already_replied(r["comment_id"], me):
                r["status"] = "pulado"
                continue
            res = graph("POST", f"{r['comment_id']}/replies", {"message": msg})
            r["status"], r["reply_id"] = "enviado", res.get("id")
            enviados += 1
        except GraphError as e:
            r["status"], r["erro"] = "erro", str(e)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    erros = sum(1 for r in doc.get("respostas", []) if r.get("status") == "erro")
    print(f"{enviados} resposta(s) enviada(s), {erros} erro(s)")
    if erros:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="acao", required=True)
    c = sub.add_parser("coletar")
    c.add_argument("--saida", required=True)
    c.add_argument("--dias", type=int, default=7)
    r = sub.add_parser("responder")
    r.add_argument("arquivo")
    a = ap.parse_args()
    if not TOKEN or not IG_USER:
        sys.exit("Faltam IG_ACCESS_TOKEN e/ou IG_USER_ID.")
    if a.acao == "coletar":
        coletar(a.saida, a.dias)
    else:
        responder(a.arquivo)


if __name__ == "__main__":
    main()
