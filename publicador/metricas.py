"""
AllAboutSports.AI — coleta de métricas do Instagram.

Salva um retrato do dia em metricas/AAAA-MM-DD.json com:
  - dados da conta (seguidores, total de posts);
  - métricas diárias da conta (alcance, seguidores ganhos), quando disponíveis;
  - métricas de cada post dos últimos DIAS dias (alcance, salvamentos,
    compartilhamentos, interações, visualizações...), cruzadas com o que
    está em posts/*/post.json e pauta.json (formato, pilar, horário).

A Meta muda nomes de métricas com o tempo: cada métrica é pedida em
lote e, se o lote falhar, uma por uma; as que não existirem são ignoradas
e listadas em "metricas_indisponiveis".

Uso: python publicador/metricas.py [--dias 35]
Requer IG_ACCESS_TOKEN e IG_USER_ID (permissões instagram_basic e
instagram_manage_insights).
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish import IG_USER, ROOT, TOKEN, GraphError, graph  # noqa: E402

POST_METRICS = ["reach", "views", "saved", "shares", "likes", "comments",
                "total_interactions", "profile_visits", "follows"]
ACCOUNT_METRICS = ["reach", "follower_count"]


def insights(obj_id, metrics, extra=None, missing=None):
    params = {"metric": ",".join(metrics)}
    params.update(extra or {})
    try:
        data = graph("GET", f"{obj_id}/insights", params).get("data", [])
        return {d["name"]: d for d in data}
    except GraphError:
        out = {}
        for m in metrics:
            try:
                p = dict(params, metric=m)
                for d in graph("GET", f"{obj_id}/insights", p).get("data", []):
                    out[d["name"]] = d
            except GraphError:
                if missing is not None:
                    missing.add(m)
        return out


def value(d):
    if "values" in d and d["values"]:
        return d["values"][-1].get("value")
    if "total_value" in d:
        return d["total_value"].get("value")
    return None


def local_posts():
    by_media = {}
    for meta_path in ROOT.glob("posts/*/post.json"):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if not meta.get("media_id"):
            continue
        pauta_path = meta_path.parent / "pauta.json"
        pauta = json.loads(pauta_path.read_text(encoding="utf-8")) if pauta_path.exists() else {}
        by_media[meta["media_id"]] = {
            "pasta": meta_path.parent.name,
            "formato": meta.get("tipo") or pauta.get("tipo"),
            "pilar": pauta.get("pilar"),
            "manchete": (pauta.get("capa") or {}).get("manchete") or pauta.get("manchete"),
            "slides": len(meta.get("imagens", [])),
        }
    return by_media


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=35)
    a = ap.parse_args()
    if not TOKEN or not IG_USER:
        sys.exit("Faltam IG_ACCESS_TOKEN e/ou IG_USER_ID.")

    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(days=a.dias)
    missing = set()

    conta = graph("GET", IG_USER, {"fields": "username,followers_count,media_count"})
    conta_dia = {k: value(v) for k, v in insights(IG_USER, ACCOUNT_METRICS, {"period": "day"}, missing).items()}

    locais = local_posts()
    posts, after = [], None
    while True:
        params = {"fields": "id,caption,media_type,timestamp,permalink,like_count,comments_count", "limit": "50"}
        if after:
            params["after"] = after
        page = graph("GET", f"{IG_USER}/media", params)
        stop = False
        for m in page.get("data", []):
            ts = dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
            if ts < since:
                stop = True
                break
            met = {k: value(v) for k, v in insights(m["id"], POST_METRICS, None, missing).items()}
            local = locais.get(m["id"], {})
            hora_brt = ts.astimezone(dt.timezone(dt.timedelta(hours=-3)))
            posts.append({
                "media_id": m["id"],
                "publicado_em": m["timestamp"],
                "dia_semana": hora_brt.strftime("%a"),
                "hora_brt": hora_brt.strftime("%H:%M"),
                "tipo_meta": m.get("media_type"),
                "link": m.get("permalink"),
                "legenda_inicio": (m.get("caption") or "")[:140],
                "curtidas": m.get("like_count"),
                "comentarios": m.get("comments_count"),
                "metricas": met,
                **local,
            })
        after = page.get("paging", {}).get("cursors", {}).get("after")
        if stop or not page.get("paging", {}).get("next"):
            break

    out = {
        "coletado_em": now.isoformat(),
        "conta": conta,
        "conta_dia": conta_dia,
        "posts": posts,
        "metricas_indisponiveis": sorted(missing),
    }
    dest = ROOT / "metricas" / f"{now.astimezone(dt.timezone(dt.timedelta(hours=-3))).date()}.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{dest.relative_to(ROOT)}: @{conta.get('username')} · {conta.get('followers_count')} seguidores · {len(posts)} posts")
    if missing:
        print("Métricas indisponíveis:", ", ".join(sorted(missing)))


if __name__ == "__main__":
    main()
