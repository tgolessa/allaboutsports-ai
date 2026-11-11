"""
AllAboutSports.AI — transforma a pauta de um carrossel em Reel (MP4 9:16).

Uso:
  python agente/reel.py posts/<pasta>/pauta.json [--out posts/<pasta>]

Gera em --out (padrão: a pasta da pauta):
  reel.mp4       1080x1920, 30 fps, H.264 + AAC, com trilha original
  reel_capa.jpg  primeiro slide em 9:16, usado como capa do Reel

Cada slide fica na tela pelo tempo de leitura do seu texto, com uma
transição lateral curta (como passar o carrossel). A trilha é gerada
por código a cada vídeo, então não há música de terceiros nem risco de
direitos autorais.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "templates"))
import render as r  # noqa: E402

FPS = 30
XFADE = 0.45
SR = 44100


def reading_time(doc_html, last=False):
    text = re.sub(r"<style.*?</style>|<[^>]+>", " ", doc_html, flags=re.S)
    words = len(html.unescape(text).split())
    if last:
        return 2.8
    # ~4,2 palavras por segundo, descontando cabeçalho e rodapé fixos
    return float(min(6.0, max(2.5, 1.0 + max(0, words - 10) / 4.2)))


def adapt_for_reel(doc):
    # No vídeo não há o que arrastar: some o "Arraste →" e as setas do rodapé.
    doc = doc.replace("<strong>Arraste →</strong>", "<strong></strong>")
    return doc.replace("<strong>→</strong>", "<strong></strong>")


def music(duration, path, seed):
    """Trilha instrumental simples (pad + pulso), original e livre de direitos."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(duration * SR)) / SR
    bpm = 100
    beat = 60 / bpm
    # Progressão Am - F - C - G, 2 compassos cada
    roots = [57, 53, 48, 55]
    chords = [[0, 3, 7], [0, 4, 7], [0, 4, 7], [0, 4, 7]]
    bar = beat * 4
    out = np.zeros_like(t)
    for i, start in enumerate(np.arange(0, duration, bar * 2)):
        idx = (i + seed) % 4
        seg = (t >= start) & (t < start + bar * 2)
        tt = t[seg] - start
        env = np.minimum(1, tt / 0.8) * np.minimum(1, (bar * 2 - tt) / 0.6)
        for semi in chords[idx]:
            f = 440 * 2 ** ((roots[idx] + semi - 69) / 12)
            for h, a in ((1, 0.5), (2, 0.18), (3, 0.08)):
                out[seg] += a * env * np.sin(2 * np.pi * f * h * tt + rng.uniform(0, 6.28))
        f_bass = 440 * 2 ** ((roots[idx] - 12 - 69) / 12)
        out[seg] += 0.35 * env * np.sin(2 * np.pi * f_bass * tt)
    # pulso suave em cada tempo
    for k in np.arange(0, duration, beat):
        n = int(k * SR)
        m = min(len(t) - n, int(0.25 * SR))
        if m <= 0:
            continue
        tt = np.arange(m) / SR
        out[n:n + m] += 0.55 * np.exp(-tt * 18) * np.sin(2 * np.pi * (55 + 60 * np.exp(-tt * 30)) * tt)
    # chimbal leve no contratempo
    for k in np.arange(beat / 2, duration, beat):
        n = int(k * SR)
        m = min(len(t) - n, int(0.05 * SR))
        if m <= 0:
            continue
        out[n:n + m] += 0.06 * np.exp(-np.arange(m) / SR * 80) * rng.standard_normal(m)
    fade = np.minimum(1, t / 1.0) * np.minimum(1, (duration - t) / 1.5)
    out *= fade
    out = out / (np.abs(out).max() + 1e-9) * 0.45
    pcm = (out * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pauta")
    ap.add_argument("--out")
    a = ap.parse_args()
    pauta_path = Path(a.pauta).resolve()
    out_dir = Path(a.out).resolve() if a.out else pauta_path.parent
    d = json.loads(pauta_path.read_text(encoding="utf-8"))
    builders = {"noticia": r.build_noticia, "nota": r.build_nota,
                "semanal": r.build_semanal, "ranking": r.build_ranking}
    docs = [adapt_for_reel(doc) for doc in builders[d["tipo"]](d)]
    durations = [reading_time(doc, i == len(docs) - 1) for i, doc in enumerate(docs)]

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        r.render(docs, tmp / "slides", "vertical")
        frames = sorted((tmp / "slides").glob("*.jpg"))

        inputs, filters = [], []
        for i, (f, dur) in enumerate(zip(frames, durations)):
            inputs += ["-framerate", str(FPS), "-i", str(f)]
            filters.append(f"[{i}:v]format=yuv420p,loop=-1:1,trim=duration={dur:.2f},setpts=PTS-STARTPTS,fps={FPS}[v{i}]")
        last, offset = "v0", durations[0] - XFADE
        for i in range(1, len(frames)):
            label = f"x{i}"
            filters.append(f"[{last}][v{i}]xfade=transition=slideleft:duration={XFADE}:offset={offset:.2f}[{label}]")
            last = label
            offset += durations[i] - XFADE
        total = sum(durations) - XFADE * (len(frames) - 1)

        video_tmp = tmp / "video.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
                        "-filter_complex", ";".join(filters), "-map", f"[{last}]",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-r", str(FPS), str(video_tmp)], check=True)

        wav = tmp / "trilha.wav"
        music(total, wav, seed=sum(map(ord, pauta_path.parent.name)) % 97)

        out_dir.mkdir(parents=True, exist_ok=True)
        final_tmp = out_dir / "reel.tmp.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_tmp), "-i", str(wav),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", "-movflags", "+faststart", str(final_tmp)], check=True)
        final_tmp.rename(out_dir / "reel.mp4")
        shutil.copy(frames[0], out_dir / "reel_capa.jpg")

    print(f"{out_dir / 'reel.mp4'}  ({total:.1f}s, {len(frames)} cenas)")


if __name__ == "__main__":
    main()
