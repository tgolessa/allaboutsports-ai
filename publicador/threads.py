"""
AllAboutSports.AI — espelhamento no Threads.

Chamado pelo publish.py depois que um post sai no Instagram. Usa as mesmas
imagens (ou o vídeo do Reel) e um texto de até 500 caracteres:
  - "legenda_threads" do post.json, se existir;
  - senão, a legenda do Instagram sem as hashtags, cortada no último
    parágrafo que couber.

Variáveis: THREADS_TOKEN, THREADS_USER_ID (segredos do repositório).
Sem elas, o espelhamento é simplesmente pulado.

  python publicador/threads.py --check     # valida a chave
  python publicador/threads.py --refresh   # imprime uma chave renovada (60 dias)
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TOKEN = os.environ.get("THREADS_TOKEN", "")
USER = os.environ.get("THREADS_USER_ID", "")
BASE = os.environ.get("THREADS_BASE", "https://graph.threads.net/v1.0")
MAX_TEXT = 500
MAX_ITEMS = 20


def enabled():
    return bool(TOKEN and USER)


def call(method, path, params=None):
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
        raise RuntimeError(f"Threads {method} {path} -> HTTP {e.code}: {e.read().decode(errors='replace')[:400]}") from None


def text_for(meta):
    if meta.get("legenda_threads"):
        return meta["legenda_threads"][:MAX_TEXT]
    paras = [p.strip() for p in meta["legenda"].split("\n\n")]
    paras = [p for p in paras if p and not p.startswith("#")]
    fontes = next((p for p in paras if p.lower().startswith("fonte")), "")
    corpo = [p for p in paras if p != fontes]
    budget = MAX_TEXT - (len(fontes.encode("utf-8")) + 2 if fontes else 0)
    out = ""
    for p in corpo:
        cand = (out + "\n\n" + p).strip()
        if len(cand.encode("utf-8")) > budget:
            break
        out = cand
    out = out or corpo[0][: budget - 1]
    return f"{out}\n\n{fontes}" if fontes else out


def wait(container_id, tries=40, delay=5):
    for _ in range(tries):
        st = call("GET", container_id, {"fields": "status,error_message"})
        if st.get("status") == "FINISHED":
            return
        if st.get("status") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {st.get('status')}: {st.get('error_message')}")
        time.sleep(delay)
    raise RuntimeError("container não ficou pronto a tempo")


def publish(post_dir, meta, raw_url):
    text = text_for(meta)
    if meta.get("video"):
        c = call("POST", f"{USER}/threads", {"media_type": "VIDEO", "video_url": raw_url(post_dir, meta["video"]), "text": text})
        creation = c["id"]
    else:
        urls = [raw_url(post_dir, rel) for rel in meta["imagens"][:MAX_ITEMS]]
        if len(urls) == 1:
            c = call("POST", f"{USER}/threads", {"media_type": "IMAGE", "image_url": urls[0], "text": text})
            creation = c["id"]
        else:
            children = [call("POST", f"{USER}/threads", {"media_type": "IMAGE", "image_url": u, "is_carousel_item": "true"})["id"] for u in urls]
            for cid in children:
                wait(cid)
            creation = call("POST", f"{USER}/threads", {"media_type": "CAROUSEL", "children": ",".join(children), "text": text})["id"]
    wait(creation)
    pub = call("POST", f"{USER}/threads_publish", {"creation_id": creation})
    info = call("GET", pub["id"], {"fields": "permalink"})
    return {"threads_id": pub["id"], "threads_link": info.get("permalink")}


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("Falta THREADS_TOKEN.")
    if "--refresh" in sys.argv:
        # O endpoint de renovação fica fora da versão (graph.threads.net/refresh_access_token).
        url = BASE.rsplit("/", 1)[0] + "/refresh_access_token?" + urllib.parse.urlencode(
            {"grant_type": "th_refresh_token", "access_token": TOKEN})
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = json.load(resp)
        print(data["access_token"])
    else:
        me = call("GET", "me", {"fields": "id,username"})
        print(f"Threads: @{me.get('username')} (id {me.get('id')})")
