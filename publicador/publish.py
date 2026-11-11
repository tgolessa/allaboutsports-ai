"""
AllAboutSports.AI — publicador no Instagram (Graph API da Meta).

Cada post vive em posts/<id>/ com:
  post.json   -> {"status": "aprovado", "publicar_em": "2026-11-12T08:00:00-03:00",
                  "legenda": "...", "imagens": ["imagens/01.jpg", ...]}
  imagens/    -> JPEGs 1080x1350

Uso:
  python publicador/publish.py --due             # publica todos os aprovados com horário vencido
  python publicador/publish.py --post posts/x    # publica um post específico (ignora horário)
  python publicador/publish.py --check           # só valida a chave e mostra a conta

Variáveis de ambiente:
  IG_ACCESS_TOKEN, IG_USER_ID  (segredos do repositório)
  GITHUB_REPOSITORY            (ex.: tgolessa/allaboutsports-ai, já vem no Actions)
  RAW_BRANCH                   (padrão: main)
  GRAPH_VERSION                (opcional, ex.: v24.0; vazio usa a versão padrão do app)

Ao publicar, grava o resultado em post.json (status "publicado", media_id, link).
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG_USER = os.environ.get("IG_USER_ID", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "tgolessa/allaboutsports-ai")
BRANCH = os.environ.get("RAW_BRANCH", "main")
VERSION = os.environ.get("GRAPH_VERSION", "").strip("/")
BASE = "https://graph.facebook.com" + (f"/{VERSION}" if VERSION else "")
MAX_ITEMS = 10  # limite de itens por carrossel na API
MIN_GAP_MIN = int(os.environ.get("MIN_GAP_MIN", "60"))  # intervalo mínimo entre posts


class GraphError(RuntimeError):
    pass


def graph(method, path, params=None):
    params = dict(params or {})
    params["access_token"] = TOKEN
    url = f"{BASE}/{path.lstrip('/')}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body).get("error", {})
            msg = f'{err.get("type")}: {err.get("message")} (code {err.get("code")}, subcode {err.get("error_subcode")})'
        except ValueError:
            msg = body[:500]
        raise GraphError(f"{method} {path} -> HTTP {e.code}: {msg}") from None


def raw_url(post_dir, rel):
    rel_path = (post_dir / rel).relative_to(ROOT).as_posix()
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{urllib.parse.quote(rel_path)}"


def wait_ready(container_id, label, tries=30, delay=4):
    for _ in range(tries):
        st = graph("GET", container_id, {"fields": "status_code,status"})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise GraphError(f"{label}: container {code} ({st.get('status')})")
        time.sleep(delay)
    raise GraphError(f"{label}: container não ficou pronto a tempo")


def collab(meta):
    """Collab post: perfis convidados como coautores (precisam aceitar no app)."""
    users = [u.lstrip("@") for u in meta.get("colaboradores", []) if u.strip()]
    return {"collaborators": json.dumps(users[:3])} if users else {}


def publish_post(post_dir):
    meta_path = post_dir / "post.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    caption = meta["legenda"]

    if meta.get("video"):
        # Reel: vídeo MP4 9:16, com capa opcional.
        video = meta["video"]
        if not (post_dir / video).is_file():
            raise FileNotFoundError(f"vídeo não encontrado: {post_dir / video}")
        params = {"media_type": "REELS", "video_url": raw_url(post_dir, video),
                  "caption": caption, "share_to_feed": "true", **collab(meta)}
        if meta.get("capa") and (post_dir / meta["capa"]).is_file():
            params["cover_url"] = raw_url(post_dir, meta["capa"])
        print(f"[{post_dir.name}] reel")
        c = graph("POST", f"{IG_USER}/media", params)
        creation_id = c["id"]
        wait_ready(creation_id, "reel", tries=60, delay=6)
    else:
        images = meta["imagens"]
        if not images:
            raise ValueError("post sem imagens")
        if len(images) > MAX_ITEMS:
            raise ValueError(f"carrossel com {len(images)} imagens; o máximo é {MAX_ITEMS}")
        for rel in images:
            if not (post_dir / rel).is_file():
                raise FileNotFoundError(f"imagem não encontrada: {post_dir / rel}")
            if not rel.lower().endswith((".jpg", ".jpeg")):
                raise ValueError(f"{rel}: a Meta aceita apenas JPEG")

        urls = [raw_url(post_dir, rel) for rel in images]
        print(f"[{post_dir.name}] {len(urls)} imagem(ns)")

        if len(urls) == 1:
            c = graph("POST", f"{IG_USER}/media", {"image_url": urls[0], "caption": caption, **collab(meta)})
            creation_id = c["id"]
            wait_ready(creation_id, "imagem")
        else:
            children = []
            for i, u in enumerate(urls, 1):
                c = graph("POST", f"{IG_USER}/media", {"image_url": u, "is_carousel_item": "true"})
                children.append(c["id"])
                print(f"  item {i:02d} -> {c['id']}")
            for i, cid in enumerate(children, 1):
                wait_ready(cid, f"item {i:02d}")
            c = graph("POST", f"{IG_USER}/media", {
                "media_type": "CAROUSEL",
                "children": ",".join(children),
                "caption": caption,
                **collab(meta),
            })
            creation_id = c["id"]
            wait_ready(creation_id, "carrossel")

    pub = graph("POST", f"{IG_USER}/media_publish", {"creation_id": creation_id})
    media_id = pub["id"]
    info = graph("GET", media_id, {"fields": "permalink,timestamp"})
    meta.update({
        "status": "publicado",
        "media_id": media_id,
        "link": info.get("permalink"),
        "publicado_em": info.get("timestamp"),
    })
    meta.pop("erro", None)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[{post_dir.name}] publicado: {info.get('permalink')}")

    # Story: divulga o post nos Stories, quando houver story.jpg na pasta.
    # Falha aqui não afeta o post do feed.
    if (post_dir / "story.jpg").is_file() and not meta.get("video"):
        try:
            c = graph("POST", f"{IG_USER}/media", {"media_type": "STORIES", "image_url": raw_url(post_dir, "story.jpg")})
            wait_ready(c["id"], "story")
            meta["story_id"] = graph("POST", f"{IG_USER}/media_publish", {"creation_id": c["id"]})["id"]
            meta.pop("story_erro", None)
            print(f"[{post_dir.name}] story publicado")
        except Exception as e:  # noqa: BLE001
            meta["story_erro"] = str(e)
            print(f"[{post_dir.name}] story ERRO: {e}", file=sys.stderr)

    # Threads: espelha o post. Uma falha aqui fica registrada, mas não
    # desfaz nem marca erro na publicação do Instagram.
    try:
        import threads
        if threads.enabled():
            res = threads.publish(post_dir, meta, raw_url)
            meta.update(res)
            meta.pop("threads_erro", None)
            print(f"[{post_dir.name}] threads: {res.get('threads_link')}")
    except Exception as e:  # noqa: BLE001
        meta["threads_erro"] = str(e)
        print(f"[{post_dir.name}] threads ERRO: {e}", file=sys.stderr)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


def due_posts(now):
    found = []
    for meta_path in sorted(ROOT.glob("posts/*/post.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("status") != "aprovado":
            continue
        when = dt.datetime.fromisoformat(meta["publicar_em"])
        if when.tzinfo is None:
            raise ValueError(f"{meta_path}: publicar_em precisa de fuso horário (ex.: -03:00)")
        if when <= now:
            found.append((when, meta_path.parent))
    return [p for _, p in sorted(found)]


def minutes_since_last_post(now):
    data = graph("GET", f"{IG_USER}/media", {"fields": "timestamp", "limit": "1"}).get("data", [])
    if not data:
        return None
    ts = dt.datetime.strptime(data[0]["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
    return (now - ts).total_seconds() / 60


def mark_error(post_dir, message):
    meta_path = post_dir / "post.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["status"] = "erro"
    meta["erro"] = message
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--due", action="store_true")
    g.add_argument("--post")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not TOKEN or not IG_USER:
        sys.exit("Faltam IG_ACCESS_TOKEN e/ou IG_USER_ID.")

    if args.check:
        me = graph("GET", IG_USER, {"fields": "username,media_count"})
        lim = graph("GET", f"{IG_USER}/content_publishing_limit", {"fields": "quota_usage,config"})
        print(f"Conta: @{me.get('username')} · posts: {me.get('media_count')}")
        print(f"Limite de publicação: {json.dumps(lim.get('data', lim), ensure_ascii=False)}")
        return

    if args.post:
        publish_post((ROOT / args.post).resolve())
        return

    now = dt.datetime.now(dt.timezone.utc)
    posts = due_posts(now)
    if not posts:
        print("Nenhum post aprovado com horário vencido.")
        return
    # Um post por rodada, e só se o último post da conta (inclusive manual)
    # tiver mais de MIN_GAP_MIN minutos. Evita despejar vários posts juntos
    # quando um pacote é aprovado depois dos horários previstos.
    last = minutes_since_last_post(now)
    if last is not None and last < MIN_GAP_MIN:
        print(f"Último post há {last:.0f} min; aguardando {MIN_GAP_MIN} min. Na fila: {len(posts)}.")
        return
    post_dir = posts[0]
    try:
        publish_post(post_dir)
    except Exception as e:
        print(f"[{post_dir.name}] ERRO: {e}", file=sys.stderr)
        mark_error(post_dir, str(e))
        sys.exit(1)
    if len(posts) > 1:
        print(f"Restam {len(posts) - 1} post(s) na fila; saem nas próximas rodadas.")


if __name__ == "__main__":
    main()
