"""
AllAboutSports.AI — consulta perfis públicos de contas profissionais
(Business Discovery da Graph API), para montar listas de quem seguir
ou convidar para parcerias.

Uso: python publicador/perfis.py arroba1 arroba2 ...   (ou PERFIS="a,b,c")

Imprime um JSON entre as linhas ===PERFIS=== e ===FIM=== com, para cada @:
username, nome, seguidores, posts, bio, site e data do último post.
Contas pessoais (não profissionais) e @ inexistentes voltam com "erro".

Com MENCOES=1, também lê as últimas 50 legendas de cada perfil encontrado
e lista os @ que ele mais marca (bom para descobrir perfis do mesmo meio).
"""
import collections
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish import IG_USER, TOKEN, GraphError, graph  # noqa: E402

FIELDS = "username,name,biography,followers_count,media_count,website,media.limit(1){timestamp}"


def consultar(handle):
    h = handle.strip().lstrip("@").lower()
    try:
        d = graph("GET", IG_USER, {"fields": f"business_discovery.username({h}){{{FIELDS}}}"})["business_discovery"]
        media = (d.get("media") or {}).get("data") or []
        return {
            "username": d.get("username"),
            "nome": d.get("name"),
            "seguidores": d.get("followers_count"),
            "posts": d.get("media_count"),
            "bio": (d.get("biography") or "").replace("\n", " ")[:200],
            "site": d.get("website"),
            "ultimo_post": media[0]["timestamp"][:10] if media else None,
        }
    except GraphError as e:
        return {"username": h, "erro": str(e)[:160]}


def mencoes(handle, n=50):
    try:
        d = graph("GET", IG_USER, {"fields": f"business_discovery.username({handle}){{media.limit({n}){{caption}}}}"})
    except GraphError:
        return collections.Counter()
    caps = [m.get("caption") or "" for m in d["business_discovery"].get("media", {}).get("data", [])]
    found = re.findall(r"@([A-Za-z0-9_.]{3,30})", " ".join(caps))
    return collections.Counter(h.rstrip(".").lower() for h in found if h.rstrip(".").lower() != handle)


def main():
    if not TOKEN or not IG_USER:
        sys.exit("Faltam IG_ACCESS_TOKEN e/ou IG_USER_ID.")
    handles = sys.argv[1:] or [h for h in os.environ.get("PERFIS", "").replace("\n", ",").split(",") if h.strip()]
    out = []
    for h in dict.fromkeys(x.strip().lstrip("@").lower() for x in handles if x.strip()):
        out.append(consultar(h))
        time.sleep(1)
    if os.environ.get("MENCOES"):
        total = collections.Counter()
        for p in out:
            if "erro" not in p:
                c = mencoes(p["username"])
                total.update(c)
                time.sleep(1)
        print("===MENCOES===")
        print(json.dumps(total.most_common(200), ensure_ascii=False))
    print("===PERFIS===")
    print(json.dumps(out, ensure_ascii=False))
    print("===FIM===")
    ok = sum(1 for p in out if "erro" not in p)
    print(f"{ok} de {len(out)} perfis encontrados", file=sys.stderr)


if __name__ == "__main__":
    main()
