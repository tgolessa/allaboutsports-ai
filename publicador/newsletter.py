"""
AllAboutSports.AI — envio da newsletter pelo Kit (API v4).

Uma edição vive em posts/<pasta>/ com:
  post.json        -> {"tipo": "newsletter", "status": "aprovado",
                       "publicar_em": "...", "assunto": "...", "previa": "...",
                       "descricao": "...", "html": "newsletter.html"}
  newsletter.html  -> corpo do e-mail (gerado por agente/newsletter.py)

Quando chega o horário, o publicador chama send(): cria o broadcast no Kit
agendado para 5 minutos depois (o Kit não tem "enviar agora" na API) e
publica também na página pública da newsletter.

  python publicador/newsletter.py --check   # valida a chave e mostra a conta

Variável: KIT_API_KEY (segredo do repositório).
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

KEY = os.environ.get("KIT_API_KEY", "")
BASE = "https://api.kit.com/v4"


def enabled():
    return bool(KEY)


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}/{path.lstrip('/')}", data=data, method=method, headers={
        "X-Kit-Api-Key": KEY, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Kit {method} {path} -> HTTP {e.code}: {e.read().decode(errors='replace')[:500]}") from None


def send(post_dir, meta):
    if not enabled():
        raise RuntimeError("KIT_API_KEY não configurada")
    html = (post_dir / meta.get("html", "newsletter.html")).read_text(encoding="utf-8")
    now = dt.datetime.now(dt.timezone.utc)
    body = {
        "subject": meta["assunto"],
        "preview_text": meta.get("previa", ""),
        "description": meta.get("descricao", meta["assunto"]),
        "content": html,
        "public": True,
        "published_at": now.isoformat(),
        "send_at": (now + dt.timedelta(minutes=5)).isoformat(),
        "subscriber_filter": [{"all": [{"type": "all_subscribers"}]}],
    }
    try:
        res = call("POST", "broadcasts", body)
    except RuntimeError as e:
        if "HTTP 422" not in str(e):
            raise
        # Alguns formatos de filtro não são aceitos; sem filtro = todos os inscritos.
        body["subscriber_filter"] = []
        res = call("POST", "broadcasts", body)
    b = res.get("broadcast", res)
    return {"kit_broadcast_id": b.get("id"), "link": b.get("public_url"), "envio_agendado": b.get("send_at")}


if __name__ == "__main__":
    if not enabled():
        sys.exit("Falta KIT_API_KEY.")
    acc = call("GET", "account")
    a = acc.get("account", acc)
    print(f"Kit: {a.get('name')} · {a.get('primary_email_address')} · plano {a.get('plan_type')}")
    subs = call("GET", "subscribers?per_page=1&include_total_count=true")
    print(f"Inscritos: {subs.get('pagination', {}).get('total_count', 'n/d')}")
