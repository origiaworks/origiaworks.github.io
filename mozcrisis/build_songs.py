#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOZCRISIS Static Site Generator (SSG)
- HTML出力先: songs/{sid}.html
- データ参照元: songs/files/{sid}/...
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "data", "songs.json")
SONGS_DIR = os.path.join(BASE_DIR, "songs")
FILES_DIR = os.path.join(SONGS_DIR, "files")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | MOZCRISIS [Algorithm Rock]</title>
    <meta name="description" content="MOZCRISIS楽曲「{title}」（{edition} / {rec_season}）。商用利用可能なフリーBGM（No Copyright Music）。作詞・設計：{architect}。">
    
    <!-- OGP (SNSシェア対策) -->
    <meta property="og:title" content="{title} | MOZCRISIS">
    <meta property="og:description" content="MOZCRISIS「{title}」の公式音源ダウンロード・歌詞ページ。">
    <meta property="og:image" content="files/{sid}/{sid}_artwork.jpg">
    <meta property="og:type" content="music.song">

    <style>
        :root {{ --main-red: #ff3e3e; --cyber-blue: #00f3ff; --bg-black: #0a0a0a; --card-bg: #151515; --text-white: #e0e0e0; --code-font: 'Consolas', 'Monaco', 'Courier New', monospace; }}
        html, body {{ background-color: var(--bg-black) !important; color: var(--text-white) !important; font-family: 'Segoe UI', 'Hiragino Kaku Gothic ProN', sans-serif; margin: 0; line-height: 1.6; }}
        nav {{ padding: 15px 20px; font-family: var(--code-font); border-bottom: 1px solid #222; background: rgba(0, 0, 0, 0.9); position: fixed; width: 100%; top: 0; z-index: 1000; box-sizing: border-box; }}
        nav a {{ color: var(--main-red); text-decoration: none; font-size: 0.8rem; font-weight: bold; }}
        .hero-visual {{ width: 100%; height: 45vh; background-position: center; background-size: cover; position: relative; margin-top: 50px; background-color: #111; background-image: url('files/{sid}/{sid}_keyvisual.png'); }}
        .hero-visual::after {{ content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, var(--bg-black), transparent); }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; position: relative; z-index: 10; }}
        .song-header {{ display: flex; gap: 30px; margin-top: -80px; flex-wrap: wrap; }}
        .artwork-area {{ flex: 0 0 220px; }}
        .artwork-img {{ width: 100%; aspect-ratio: 1/1; border: 1px solid var(--main-red); object-fit: cover; background: #000; }}
        .title-area {{ flex: 1; min-width: 300px; }}
        .track-id {{ font-family: var(--code-font); color: var(--main-red); font-size: 1rem; }}
        h1 {{ font-family: var(--code-font); font-size: clamp(1.8rem, 5vw, 2.8rem); margin: 5px 0; }}
        .meta-list {{ display: flex; gap: 30px; border-top: 1px solid #333; padding-top: 15px; margin-top: 15px; flex-wrap: wrap; }}
        .meta-label {{ font-size: 0.7rem; color: #666; display: block; }}
        .meta-value {{ font-family: var(--code-font); color: var(--cyber-blue); }}
        .action-area {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 30px 0 60px; }}
        .btn {{ padding: 12px 25px; font-family: var(--code-font); font-size: 0.9rem; font-weight: bold; text-decoration: none; border: 1px solid; transition: 0.3s; text-align: center; flex: 1; min-width: 200px; }}
        .btn-wav {{ color: var(--main-red); border-color: var(--main-red); {wav_display} }}
        .btn-wav:hover {{ background: var(--main-red); color: #fff; box-shadow: 0 0 15px rgba(255, 62, 62, 0.4); }}
        .btn-mp3 {{ color: var(--cyber-blue); border-color: var(--cyber-blue); }}
        .btn-mp3:hover {{ background: var(--cyber-blue); color: #000; box-shadow: 0 0 15px rgba(0, 243, 255, 0.4); }}
        .terminal {{ background: #000; border: 1px solid #333; margin-bottom: 100px; }}
        .terminal-bar {{ background: #1a1a1a; padding: 10px; font-size: 0.7rem; color: #888; display: flex; justify-content: space-between; border-bottom: 1px solid #333; }}
        .lyrics-box {{ padding: 40px; font-family: var(--code-font); font-size: 1rem; color: #aaa; white-space: pre-wrap; margin: 0; line-height: 1.8; }}
        @media (max-width: 600px) {{ .song-header {{ margin-top: -40px; text-align: center; justify-content: center; }} .meta-list {{ flex-direction: column; gap: 10px; }} .btn {{ width: 100%; }} }}
    </style>
</head>
<body>
    <nav><a href="../index.html">&lt;&lt; RETURN_TO_DASHBOARD</a></nav>
    <div class="hero-visual"></div>
    <div class="container">
        <header class="song-header">
            <div class="artwork-area">
                <img src="files/{sid}/{sid}_artwork.jpg" class="artwork-img" alt="{title} Artwork">
            </div>
            <div class="title-area">
                <div class="track-id">TRACK_{sid_upper}</div>
                <h1>{title}</h1>
                <div class="meta-list">
                    <div class="meta-item"><span class="meta-label">RELEASE</span><span class="meta-value">{release}</span></div>
                    <div class="meta-item"><span class="meta-label">ARCHITECT</span><span class="meta-value">{architect}</span></div>
                    <div class="meta-item"><span class="meta-label">EDITION</span><span class="meta-value">{edition}</span></div>
                    <div class="meta-item"><span class="meta-label">REC_SEASON</span><span class="meta-value">{rec_season}</span></div>
                </div>
            </div>
        </header>

        <div class="action-area">
            {wav_button}
            <a href="files/{sid}/{sid}.mp3" download class="btn btn-mp3">&gt;&gt; DOWNLOAD_MP3_BINARY</a>
        </div>

        <div class="terminal">
            <div class="terminal-bar">
                <span>{sid}_lyric.txt</span>
                <span>RAW_LYRICS_STREAM</span>
            </div>
            <pre class="lyrics-box">{lyrics}</pre>
        </div>
    </div>
</body>
</html>
"""

def build():
    if not os.path.exists(JSON_PATH):
        print(f"[ERROR] {JSON_PATH} が見つかりません。")
        return

    # files ディレクトリの存在確認
    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR, exist_ok=True)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        songs = json.load(f)

    print(f"[*] 全 {len(songs)} 曲の静的HTMLを songs/ 直下に生成・上書きします...")

    for sid, data in songs.items():
        title = data.get("title", sid)
        release = data.get("release", "----")
        architect = data.get("architect", "ROSE")
        edition = data.get("edition", "UNKNOWN_EDITION")
        rec_season = data.get("rec_season", "REC_000")

        # 歌詞ファイル読み込み（songs/files/{sid}/ から）
        lyric_path = os.path.join(FILES_DIR, sid, f"{sid}_lyric.txt")
        lyrics = "Awaiting data stream..."
        if os.path.exists(lyric_path):
            with open(lyric_path, "r", encoding="utf-8") as lf:
                lyrics = lf.read()

        # WAV存在判定（songs/files/{sid}/ から）
        wav_file_path = os.path.join(FILES_DIR, sid, f"{sid}.wav")
        if os.path.exists(wav_file_path):
            wav_display = "display: block;"
            wav_button = f'<a href="files/{sid}/{sid}.wav" download class="btn btn-wav">&gt;&gt; DOWNLOAD_WAV_MASTER</a>'
        else:
            wav_display = "display: none;"
            wav_button = ""

        # HTML生成
        html_content = HTML_TEMPLATE.format(
            sid=sid,
            sid_upper=sid.upper(),
            title=title,
            release=release,
            architect=architect,
            edition=edition,
            rec_season=rec_season,
            lyrics=lyrics,
            wav_display=wav_display,
            wav_button=wav_button
        )

        # 出力先: songs/{sid}.html
        out_html_path = os.path.join(SONGS_DIR, f"{sid}.html")
        with open(out_html_path, "w", encoding="utf-8") as out:
            out.write(html_content)

        print(f"[OK] 生成/上書き完了: songs/{sid}.html")

    print("[SUCCESS] すべての曲の静的HTMLの配置が完了しました！")

if __name__ == "__main__":
    build()
