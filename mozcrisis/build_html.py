#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOZCRISIS Unified Static Site Generator (SSG)
- 楽曲個別HTML生成: data/songs.json -> songs/{sid}.html
- 全曲カタログ生成: data/songs.json -> discography.html
- トップページ更新: data/songs.json -> index.html (最新4曲を静的埋め込み)
- メンバーHTML生成: data/members.json -> members/{mid}.html
- オーディオドラマ生成: data/audio_dramas.json -> audio_drama.html
- サイトマップ生成: sitemap.xml (全ページ)
- 全ページに title/description/canonical/OGP/Twitter/JSON-LD を自動付与
"""

import json
import os
import re
import html as html_lib
from urllib.parse import quote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ==========================================
# 0. SEO 共通設定・ヘルパー
# ==========================================
SITE_URL = "https://origiaworks.github.io/mozcrisis/"   # 末尾スラッシュ必須
SITE_NAME = "MOZCRISIS"
# SNSシェア用の既定画像。可能なら 1200x630 の専用画像(例: images/ogp.png)を用意して差し替える
DEFAULT_OG_IMAGE = "members/files/img/rose.png"


def esc(value):
    """HTML属性・本文の両方で安全になるようエスケープ"""
    return html_lib.escape(str(value), quote=True)


def abs_url(path=""):
    return SITE_URL + quote(path.lstrip("/"), safe="/#")


def trunc(text, limit=120):
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def iso_date(release):
    """'2026.08.07' -> '2026-08-07' (不正な形式は None)"""
    m = re.fullmatch(r"(\d{4})\.(\d{2})\.(\d{2})", str(release))
    return "-".join(m.groups()) if m else None


def jsonld_tag(obj):
    body = json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n    {body}\n    </script>'


def breadcrumb(items):
    """items: [(表示名, 相対パス), ...]"""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": abs_url(path)}
            for i, (name, path) in enumerate(items)
        ],
    }


def seo_head(title, description, path, image=None, og_type="website",
             twitter_card="summary_large_image", jsonld=None):
    """<title> / description / canonical / OGP / Twitter / JSON-LD をまとめて生成"""
    url = abs_url(path)
    img = abs_url(image or DEFAULT_OG_IMAGE)
    t, d = esc(title), esc(description)
    canonical = url.split("#")[0]
    lines = [
        f'<title>{t}</title>',
        f'<meta name="description" content="{d}">',
        f'<link rel="canonical" href="{esc(canonical)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta name="theme-color" content="#0a0a0a">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        '<meta property="og:locale" content="ja_JP">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:title" content="{t}">',
        f'<meta property="og:description" content="{d}">',
        f'<meta property="og:url" content="{esc(canonical)}">',
        f'<meta property="og:image" content="{esc(img)}">',
        f'<meta name="twitter:card" content="{twitter_card}">',
        f'<meta name="twitter:title" content="{t}">',
        f'<meta name="twitter:description" content="{d}">',
        f'<meta name="twitter:image" content="{esc(img)}">',
    ]
    for obj in (jsonld or []):
        lines.append(jsonld_tag(obj))
    return "\n    ".join(lines)


MUSIC_GROUP = {"@type": "MusicGroup", "name": SITE_NAME, "alternateName": "モズクライシス", "url": SITE_URL}

# ==========================================
# 1. 楽曲（Songs）および カタログ ビルド処理
# ==========================================
SONGS_JSON = os.path.join(DATA_DIR, "songs.json")
SONGS_DIR = os.path.join(BASE_DIR, "songs")
SONGS_FILES_DIR = os.path.join(SONGS_DIR, "files")
DISCOGRAPHY_HTML_PATH = os.path.join(BASE_DIR, "discography.html")
INDEX_HTML_PATH = os.path.join(BASE_DIR, "index.html")

SONG_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../css/style.css">
    {seo_head}

    <style>        
        .hero-visual {{ width: 100%; height: 45vh; background-position: center; background-size: cover; position: relative; margin-top: 50px; background-color: #111; background-image: url('files/{sid}/{sid}_keyvisual.png'); }}
        .hero-visual::after {{ content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, var(--bg-black), transparent); }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; position: relative; z-index: 10; box-sizing: border-box; }}
        .song-header {{ display: flex; gap: 30px; margin-top: -80px; flex-wrap: wrap; border-left: none; padding-left: 0; }}
        .artwork-area {{ flex: 0 0 220px; }}
        .artwork-img {{ width: 100%; aspect-ratio: 1/1; border: 1px solid var(--main-red); object-fit: cover; background: #000; }}
        .title-area {{ flex: 1; min-width: 300px; }}
        .track-id {{ font-family: var(--code-font); color: var(--main-red); font-size: 1rem; }}
        .meta-list {{ display: flex; gap: 30px; border-top: 1px solid #333; padding-top: 15px; margin-top: 15px; flex-wrap: wrap; }}
        .meta-label {{ font-size: 0.7rem; color: #666; display: block; }}
        .meta-value {{ font-family: var(--code-font); color: var(--cyber-blue); }}
        .action-area {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 30px 0 60px; }}
        .btn {{ padding: 12px 25px; font-family: var(--code-font); font-size: 0.9rem; font-weight: bold; text-decoration: none; border: 1px solid; transition: 0.3s; text-align: center; flex: 1; min-width: 200px; box-sizing: border-box; }}
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
    <nav><a href="../discography.html">&lt;&lt; RETURN</a></nav>
    <div class="hero-visual"></div>
    <div class="container">
        <header class="song-header">
            <div class="artwork-area">
                <img src="files/{sid}/{sid}_artwork.jpg" class="artwork-img" alt="{title} アートワーク - MOZCRISIS">
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

DISCOGRAPHY_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/style.css">
    {seo_head}
    <style>
        :root {{
            --main-red: #ff3e3e;
            --cyber-blue: #00f3ff;
            --bg-black: #0a0a0a;
            --card-bg: #151515;
            --text-white: #e0e0e0;
            --code-font: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        body {{ background-color: var(--bg-black); color: var(--text-white); font-family: 'Segoe UI', sans-serif; margin: 0; line-height: 1.6; overflow-x: hidden; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 100px 20px 80px; box-sizing: border-box; width: 100%; }}
        
        /* 一番上のメインヘッダー：赤の1本線 */
        header {{ margin-bottom: 50px; border-left: 5px solid var(--main-red); padding-left: 30px; background: linear-gradient(90deg, rgba(255, 62, 62, 0.08) 0%, transparent 100%); }}
        h1 {{ font-family: var(--code-font); font-size: clamp(2rem, 5vw, 3rem); margin: 0; text-transform: uppercase; letter-spacing: 2px; }}
        .subtitle {{ color: var(--cyber-blue); font-size: 0.85rem; font-family: var(--code-font); margin-top: 10px; }}
        
        .season-block {{ margin-bottom: 60px; border-top: 1px solid #222; padding-top: 30px; }}
        
        /* 各シーズンのヘッダー：青の1本線 */
        .season-header {{ margin-bottom: 25px; border-left: 4px solid var(--cyber-blue); padding-left: 15px; background: linear-gradient(90deg, rgba(0, 243, 255, 0.06) 0%, transparent 100%); }}
        .season-title {{ font-family: var(--code-font); font-size: 1.3rem; color: #fff; margin: 0; letter-spacing: 2px; }}
        
        /* スマホ対応を強化したグリッド */
        .song-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 15px; box-sizing: border-box; }}
        .song-card {{ background: var(--card-bg); border: 1px solid #222; text-decoration: none; color: inherit; display: block; transition: 0.3s; box-sizing: border-box; min-width: 0; }}
        .song-card:hover {{ border-color: var(--cyber-blue); transform: translateY(-3px); box-shadow: 0 0 10px rgba(0, 243, 255, 0.2); }}
        .song-jacket {{ width: 100%; aspect-ratio: 1 / 1; background: #111; object-fit: cover; display: block; }}
        .song-info {{ padding: 10px; box-sizing: border-box; }}
        .song-meta {{ font-family: var(--code-font); font-size: 0.55rem; color: var(--main-red); margin-bottom: 2px; display: block; }}
        .song-title {{ font-size: 0.8rem; font-weight: bold; color: #fff; display: block; line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        
        footer {{ background: #050505; padding: 40px 20px; text-align: center; border-top: 1px solid #1a1a1a; font-family: var(--code-font); font-size: 0.7rem; color: #555; }}
        
        @media (max-width: 768px) {{ 
            .container {{ padding: 80px 12px 30px; }} 
            .song-grid {{ grid-template-columns: repeat(2, 1fr); gap: 10px; }} 
            .song-info {{ padding: 6px; }} 
            .song-title {{ font-size: 0.75rem; }} 
        }}
    </style>
</head>
<body>
    <nav><a href="index.html">&lt;&lt; RETURN</a></nav>
    <div class="container">
        <header>
            <h1>DISCOGRAPHY</h1>
            <div class="subtitle">// ALL AUDIO ASSETS &amp; LYRICS ARCHIVE</div>
        </header>
        {seasons_html}
    </div>
    <footer>
        MOZCRISIS / ORIGIAWORKS - SYSTEM CATALOG NODE
    </footer>
</body>
</html>
"""


def build_songs():
    if not os.path.exists(SONGS_JSON):
        print(f"[ERROR] {SONGS_JSON} が見つかりません。")
        return

    os.makedirs(SONGS_FILES_DIR, exist_ok=True)

    with open(SONGS_JSON, "r", encoding="utf-8") as f:
        songs = json.load(f)

    print(f"\n[*] 楽曲データビルド開始 (全 {len(songs)} 曲)...")

    # 1. 各楽曲の個別HTML生成
    for sid, data in songs.items():
        title = data.get("title", sid)
        release = data.get("release", "----")
        architect = data.get("architect", "ROSE")
        edition = data.get("edition", "UNKNOWN_EDITION")
        rec_season = data.get("rec_season", "REC_000")

        lyric_path = os.path.join(SONGS_FILES_DIR, sid, f"{sid}_lyric.txt")
        lyrics = "Awaiting data stream..."
        if os.path.exists(lyric_path):
            with open(lyric_path, "r", encoding="utf-8") as lf:
                lyrics = lf.read()

        wav_file_path = os.path.join(SONGS_FILES_DIR, sid, f"{sid}.wav")
        if os.path.exists(wav_file_path):
            wav_display = "display: block;"
            wav_button = f'<a href="files/{sid}/{sid}.wav" download class="btn btn-wav">&gt;&gt; DOWNLOAD_WAV_MASTER</a>'
        else:
            wav_display = "display: none;"
            wav_button = ""

        page_path = f"songs/{sid}.html"
        artwork_path = f"songs/files/{sid}/{sid}_artwork.jpg"
        song_ld = {
            "@context": "https://schema.org",
            "@type": "MusicRecording",
            "name": title,
            "url": abs_url(page_path),
            "image": abs_url(artwork_path),
            "genre": "Algorithm Rock",
            "byArtist": MUSIC_GROUP,
            "isAccessibleForFree": True,
            "license": abs_url("policy.html"),
            "audio": {
                "@type": "AudioObject",
                "contentUrl": abs_url(f"songs/files/{sid}/{sid}.mp3"),
                "encodingFormat": "audio/mpeg",
            },
        }
        if iso_date(release):
            song_ld["datePublished"] = iso_date(release)
        seo = seo_head(
            title=f"{title}｜歌詞・フリーBGM音源 | MOZCRISIS",
            description=(f"MOZCRISIS「{title}」（{edition} / {rec_season}、{release}公開）の歌詞と音源ダウンロード。"
                         f"商用利用OK・著作権フリーのBGM（No Copyright Music）。作詞・設計：{architect}。"),
            path=page_path,
            image=artwork_path,
            og_type="music.song",
            twitter_card="summary",
            jsonld=[song_ld, breadcrumb([("HOME", ""), ("DISCOGRAPHY", "discography.html"), (title, page_path)])],
        )

        html_content = SONG_HTML_TEMPLATE.format(
            seo_head=seo,
            sid=sid,
            sid_upper=sid.upper(),
            title=esc(title),
            release=esc(release),
            architect=esc(architect),
            edition=esc(edition),
            rec_season=esc(rec_season),
            lyrics=html_lib.escape(lyrics, quote=False),
            wav_display=wav_display,
            wav_button=wav_button,
        )

        out_path = os.path.join(SONGS_DIR, f"{sid}.html")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(html_content)

    print("  [Song OK] 全個別HTML生成完了")

    # 2. discography.html の静的生成
    print("[*] カタログページ (discography.html) 生成開始...")
    seasons = {}
    for sid, data in songs.items():
        season = data.get("rec_season", "REC_000")
        if season not in seasons:
            seasons[season] = []
        seasons[season].append((sid, data))

    seasons_html = ""
    for season_name, song_list in sorted(seasons.items()):
        cards_html = ""
        for sid, data in song_list:
            title = data.get("title", sid)
            edition = data.get("edition", "UNKNOWN_EDITION")
            cards_html += f"""
            <a href="songs/{sid}.html" class="song-card">
                <img src="songs/files/{sid}/{sid}_artwork.jpg" class="song-jacket" alt="{esc(title)} - MOZCRISIS" loading="lazy" decoding="async">
                <div class="song-info">
                    <span class="song-meta">{esc(edition)}</span>
                    <span class="song-title">{esc(title)}</span>
                </div>
            </a>
            """

        seasons_html += f"""
        <div class="season-block">
            <div class="season-header">
                <h2 class="season-title">{season_name}</h2>
            </div>
            <div class="song-grid">
                {cards_html}
            </div>
        </div>
        """

    disco_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "MOZCRISIS DISCOGRAPHY",
        "url": abs_url("discography.html"),
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(songs),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": abs_url(f"songs/{sid}.html"), "name": d.get("title", sid)}
                for i, (sid, d) in enumerate(songs.items())
            ],
        },
    }
    disco_seo = seo_head(
        title="全楽曲一覧（DISCOGRAPHY）｜MOZCRISIS 著作権フリー・商用利用OKのBGM音源アーカイブ",
        description=(f"MOZCRISIS（モズクライシス）の全{len(songs)}曲を収録した公式カタログ。"
                     "商用利用OKのアルゴリズム・ロック系フリーBGM音源（WAV/MP3）と歌詞を、シーズン別に掲載。"),
        path="discography.html",
        jsonld=[disco_ld, breadcrumb([("HOME", ""), ("DISCOGRAPHY", "discography.html")])],
    )
    discography_content = DISCOGRAPHY_HTML_TEMPLATE.format(seasons_html=seasons_html, seo_head=disco_seo)
    with open(DISCOGRAPHY_HTML_PATH, "w", encoding="utf-8") as out:
        out.write(discography_content)
    print("  [Catalog OK] discography.html 生成完了")

    # 3. index.html の最新4曲を静的埋め込み
    build_index_latest_songs(songs)


def build_index_latest_songs(songs):
    """index.html の最新4曲を静的HTMLとして安全に埋め込む"""
    if not os.path.exists(INDEX_HTML_PATH):
        print(f"[WARN] {INDEX_HTML_PATH} が見つからないため、トップページの更新をスキップします。")
        return

    print("[*] トップページ (index.html) の静的更新開始...")

    song_keys = list(songs.keys())
    latest_keys = song_keys[-4:]
    latest_keys.reverse()

    cards_html = ""
    for sid in latest_keys:
        data = songs[sid]
        title = data.get("title", sid)
        edition = data.get("edition", "UNKNOWN_EDITION")
        cards_html += f"""
                    <a href="songs/{sid}.html" class="song-card">
                        <img src="songs/files/{sid}/{sid}_artwork.jpg" class="song-jacket" alt="{esc(title)} - MOZCRISIS" loading="lazy" decoding="async">
                        <div class="song-info">
                            <span class="song-meta">{esc(edition)}</span>
                            <span class="song-title">{esc(title)}</span>
                        </div>
                    </a>"""

    replacement_content = f"""<!-- LATEST_SONGS_START -->
                <div class="song-grid">{cards_html}
                </div>
                <div style="text-align: left; margin-top: 50px; margin-bottom: 80px;">
                    <a href="discography.html" class="protocol-btn" style="border-color: var(--cyber-blue); color: var(--cyber-blue);">
                        &gt;&gt; ALL_DISCOGRAPHY
                    </a>
                </div>
                <!-- LATEST_SONGS_END -->"""

    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    pattern = r'<!-- LATEST_SONGS_START -->.*?<!-- LATEST_SONGS_END -->'
    if re.search(pattern, html, flags=re.DOTALL):
        new_html = re.sub(pattern, replacement_content, html, flags=re.DOTALL)
        with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("  [Index OK] index.html の最新楽曲ブロックを安全に静的更新しました")
    else:
        print("  [WARN] index.html 内に <!-- LATEST_SONGS_START --> 目印が見つかりませんでした。")


# ==========================================
# 2. メンバー（Members）ビルド処理
# ==========================================
MEMBERS_JSON = os.path.join(DATA_DIR, "members.json")
MEMBERS_DIR = os.path.join(BASE_DIR, "members")
MEMBERS_FILES_DIR = os.path.join(MEMBERS_DIR, "files")
VOICE_DIR = os.path.join(MEMBERS_FILES_DIR, "voice")

MEMBER_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../css/style.css">
    {seo_head}

    <style>
        :root {{ 
            --member-color: {color}; 
            --bg-black: #0a0a0a; 
            --text-white: #e0e0e0; 
            --code-font: 'Consolas', 'Monaco', 'Courier New', monospace; 
        }}
        .watermark {{ 
            position: fixed; 
            top: 50%; 
            right: -15%; 
            transform: translateY(-50%); 
            width: 100vh; 
            aspect-ratio: 1 / 1; 
            z-index: -1; 
            opacity: 0.25; 
            filter: brightness(1.1); 
            pointer-events: none; 
        }}
        .watermark img {{ width: 100%; height: 100%; object-fit: contain; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 60px 20px; }}
        .header-area {{ margin-bottom: 50px; border-left: 5px solid var(--member-color); padding-left: 30px; }}
        .role-title {{ font-family: var(--code-font); color: var(--member-color); font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; }}
        .name-main {{ font-size: clamp(3rem, 8vw, 5rem); font-weight: 900; margin: 10px 0 5px; }}
        .cv-credit {{ font-family: var(--code-font); font-size: 0.9rem; color: #888; margin-bottom: 10px; }}
        .cv-credit span {{ color: var(--member-color); font-weight: bold; }}
        .name-sub {{ font-size: 1rem; color: #777; font-family: var(--code-font); }}
        
        .quote-container {{ margin: 40px 0; }}
        .quote-box {{ 
            font-size: clamp(1.1rem, 3vw, 1.4rem); 
            font-style: italic; 
            color: #fff; 
            padding-bottom: 15px; 
            border-bottom: 2px solid var(--member-color); 
            width: fit-content; 
            line-height: 1.6;
        }}
        .voice-btn {{
            background: transparent;
            border: 1px solid var(--member-color);
            color: var(--member-color);
            font-family: var(--code-font);
            font-size: 0.8rem;
            padding: 8px 16px;
            margin-top: 15px;
            cursor: pointer;
            transition: 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .voice-btn:hover {{
            background: var(--member-color);
            color: #000;
            box-shadow: 0 0 10px var(--member-color);
        }}

        .spec-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 60px; }}
        .spec-item {{ background: rgba(255, 255, 255, 0.03); padding: 15px; border: 1px solid #222; }}
        .spec-label {{ font-family: var(--code-font); font-size: 0.7rem; color: var(--member-color); margin-bottom: 5px; }}
        .spec-value {{ font-family: var(--code-font); font-size: 1rem; color: #fff; font-weight: bold; }}
        .bio-section h3 {{ font-family: var(--code-font); border-bottom: 1px solid #333; padding-bottom: 10px; color: var(--member-color); margin-top: 40px; letter-spacing: 1px; }}
        .bio-text {{ font-size: 1.05rem; line-height: 1.9; color: #ccc; }}
        .gear-box {{ background: #000; border: 1px dashed #444; padding: 25px; font-family: var(--code-font); font-size: 0.95rem; color: #aaa; line-height: 1.8; }}
        @media (max-width: 768px) {{ 
            .watermark {{ width: 70vh; right: -20%; opacity: 0.15; }} 
            .container {{ padding: 30px 15px; }}
        }}
    </style>
</head>
<body>
    <div class="watermark">
        <img src="files/img/{mid}_stand.png" alt="{name} Stand Visual" onerror="this.style.display='none'">
    </div>
    
    <nav>
        <a href="../index.html">&lt;&lt; RETURN</a>
    </nav>
    
    <div class="container">
        <header class="header-area">
            <div class="role-title">{role}</div>
            <h1 class="name-main">{name}</h1>
            <div class="cv-credit">CV: <span>{cv}</span></div>
            <div class="name-sub">{real_name}</div>
        </header>

        <div class="quote-container">
            <div class="quote-box">{quote}</div>
            {voice_button_html}
        </div>

        <div class="spec-grid">
            {specs_html}
        </div>

        <section class="bio-section">
            <h3>BIOGRAPHY</h3>
            <p class="bio-text">{bio}</p>
            
            <h3>EQUIPMENT &amp; PARAMETERS</h3>
            <div class="gear-box">{gear}</div>
        </section>
    </div>

    <script>
        function playVoice(audioPath) {{
            const audio = new Audio(audioPath);
            audio.play().catch(e => console.log("Audio play blocked or missing:", e));
        }}
    </script>
</body>
</html>
"""


def build_members():
    if not os.path.exists(MEMBERS_JSON):
        print(f"[ERROR] {MEMBERS_JSON} が見つかりません。")
        return

    os.makedirs(MEMBERS_DIR, exist_ok=True)
    os.makedirs(VOICE_DIR, exist_ok=True)

    with open(MEMBERS_JSON, "r", encoding="utf-8") as f:
        members = json.load(f)

    print(f"\n[*] メンバーデータビルド開始 (全 {len(members)} 名)...")

    for mid, data in members.items():
        name = data.get("name", mid)
        real_name = data.get("realName", "")
        role = data.get("role", "")
        color = data.get("color", "#ff3e3e")
        quote = data.get("quote", "")
        bio = data.get("bio", "")
        gear = data.get("gear", "")
        specs = data.get("specs", [])

        cv = data.get("cv", "TBD")
        voice_file = data.get("voiceFile", "")

        # --- SEO ---
        page_path = f"members/{mid}.html"
        img_rel = f"members/files/img/{mid}.png"
        og_img = img_rel if os.path.exists(os.path.join(BASE_DIR, img_rel)) else DEFAULT_OG_IMAGE
        cv_part = f"（CV: {cv}）" if cv and cv not in ("null", "TBD") else ""
        first_sentence = bio.split("。")[0] + "。" if bio else ""
        member_ld = {
            "@context": "https://schema.org",
            "@type": "ProfilePage",
            "url": abs_url(page_path),
            "mainEntity": {
                "@type": "Person",
                "name": name,
                "alternateName": real_name,
                "jobTitle": role,
                "description": bio,
                "image": abs_url(og_img),
                "memberOf": MUSIC_GROUP,
            },
        }
        seo = seo_head(
            title=f"{name}｜MOZCRISISメンバープロフィール（{role}）",
            description=trunc(f"MOZCRISISメンバー「{name}（{real_name}）」のプロフィール。担当：{role}{cv_part}。{first_sentence}", 120),
            path=page_path,
            image=og_img,
            og_type="profile",
            jsonld=[member_ld, breadcrumb([("HOME", ""), ("MEMBERS", "index.html#members"), (name, page_path)])],
        )

        voice_path = os.path.join(VOICE_DIR, voice_file)
        if voice_file and os.path.exists(voice_path):
            voice_button_html = f"""
            <button class="voice-btn" onclick="playVoice('files/voice/{voice_file}')">
                ▶ PLAY_VOICE_SAMPLE
            </button>
            """
        else:
            voice_button_html = ""

        specs_html = ""
        for spec in specs:
            label = esc(spec.get("label", ""))
            value = esc(spec.get("value", ""))
            specs_html += f"""
            <div class="spec-item">
                <div class="spec-label">{label}</div>
                <div class="spec-value">{value}</div>
            </div>"""

        html_content = MEMBER_HTML_TEMPLATE.format(
            seo_head=seo,
            mid=mid,
            name=esc(name),
            name_upper=mid.upper(),
            real_name=esc(real_name),
            role=esc(role),
            color=color,
            quote=esc(quote),
            cv=esc(cv),
            voice_button_html=voice_button_html,
            bio=esc(bio),
            gear=esc(gear),
            specs_html=specs_html,
        )

        out_path = os.path.join(MEMBERS_DIR, f"{mid}.html")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(html_content)

        print(f"  [Member OK] members/{mid}.html")


# ==========================================
# 3. オーディオドラマ（Audio Drama）ビルド処理
# ==========================================
AUDIO_DRAMAS_JSON = os.path.join(DATA_DIR, "audio_dramas.json")
AUDIO_DRAMA_HTML_PATH = os.path.join(BASE_DIR, "audio_drama.html")

AUDIO_DRAMA_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {seo_head}
    <link rel="stylesheet" href="css/style.css">
    <style>
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 60px 20px;
            box-sizing: border-box;
        }}

        h1 {{
            font-size: clamp(1.5rem, 5vw, 2.5rem);
            margin: 0;
            text-transform: uppercase;
            font-family: var(--code-font);
        }}

        .drama-card {{
            background: var(--card-bg);
            border: 1px solid #222;
            padding: 35px;
            margin-bottom: 50px;
            box-sizing: border-box;
        }}

        .ep-number {{
            font-family: var(--code-font);
            color: var(--main-red);
            font-size: 0.75rem;
            font-weight: bold;
            display: block;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}

        .ep-title {{
            font-family: var(--code-font);
            font-size: clamp(1.1rem, 3vw, 1.4rem);
            color: #fff;
            margin: 0 0 20px 0;
            line-height: 1.4;
        }}

        .ep-desc {{
            color: #ccc;
            font-size: 0.95rem;
            line-height: 1.8;
            margin-bottom: 30px;
            font-family: 'Segoe UI', sans-serif;
        }}

        .video-container {{
            position: relative;
            width: 100%;
            aspect-ratio: 16 / 9;
            background: #000;
            border: 1px solid #333;
            box-sizing: border-box;
        }}

        .video-container iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
        }}

        footer {{
            text-align: center;
            padding: 60px 20px;
            border-top: 1px solid #222;
            color: #444;
            font-size: 0.7rem;
            font-family: var(--code-font);
        }}

        @media (max-width: 768px) {{
            .container {{ padding: 40px 15px; }}
            .drama-card {{ padding: 20px; }}
        }}
    </style>
</head>

<body>

    <nav><a href="index.html">&lt;&lt; RETURN</a></nav>

    <div class="container">
        <header>
            <h1>AUDIO_DRAMA</h1>
            <div class="subtitle">// SYSTEM LOGS &amp; BACKSTAGE CONVERSATIONS</div>
        </header>
        {cards_html}
    </div>

    <footer>
        EXECUTION_COMPLETE: MOZCRISIS SYSTEM NODE_004
    </footer>

</body>

</html>
"""


def build_audio_dramas():
    if not os.path.exists(AUDIO_DRAMAS_JSON):
        print(f"[WARN] {AUDIO_DRAMAS_JSON} が見つからないため、オーディオドラマの生成をスキップします。")
        return

    print("\n[*] オーディオドラマデータビルド開始...")

    with open(AUDIO_DRAMAS_JSON, "r", encoding="utf-8") as f:
        dramas = json.load(f)

    cards_list = []
    for item in dramas:
        episode = item.get("episode", "EPISODE_???")
        title = item.get("title", "")
        desc = item.get("desc", "")
        yt_id = item.get("youtube_id", "")

        card = f"""        <div class="drama-card">
            <span class="ep-number">{esc(episode)}</span>
            <h2 class="ep-title">{esc(title)}</h2>
            <p class="ep-desc">
                {desc}
            </p>
            <div class="video-container">
                <iframe src="https://www.youtube.com/embed/{yt_id}" title="{esc(title)}" loading="lazy" allowfullscreen></iframe>
            </div>
        </div>"""
        cards_list.append(card)

    cards_html = "\n        <hr>\n".join(cards_list)
    drama_seo = seo_head(
        title="オーディオドラマ一覧（AUDIO_DRAMA）｜MOZCRISIS 舞台裏の日常ログ",
        description=(f"MOZCRISISのオーディオドラマ全{len(dramas)}話をYouTubeで公開。"
                     "ローズ・淀・レナ・ミオ・JIWOOたちの騒がしい日常と、音楽の裏側を描くバックステージ劇場。"),
        path="audio_drama.html",
        jsonld=[breadcrumb([("HOME", ""), ("AUDIO_DRAMA", "audio_drama.html")])],
    )
    html_content = AUDIO_DRAMA_HTML_TEMPLATE.format(cards_html=cards_html, seo_head=drama_seo)

    with open(AUDIO_DRAMA_HTML_PATH, "w", encoding="utf-8") as out:
        out.write(html_content)

    print("  [Audio Drama OK] audio_drama.html 生成完了")


# ==========================================
# 4. サイトマップ生成
# ==========================================
def build_sitemap():
    songs, members = {}, {}
    if os.path.exists(SONGS_JSON):
        with open(SONGS_JSON, "r", encoding="utf-8") as f:
            songs = json.load(f)
    if os.path.exists(MEMBERS_JSON):
        with open(MEMBERS_JSON, "r", encoding="utf-8") as f:
            members = json.load(f)

    entries = [(abs_url(p), None) for p in ["", "bio.html", "discography.html", "audio_drama.html", "policy.html"]]
    entries += [(abs_url(f"members/{mid}.html"), None) for mid in members]
    # lastmod は実際の公開日が分かる楽曲のみ記載（不正確な日付は無視されるため）
    entries += [(abs_url(f"songs/{sid}.html"), iso_date(d.get("release", ""))) for sid, d in songs.items()]

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{esc(loc)}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")

    with open(os.path.join(BASE_DIR, "sitemap.xml"), "w", encoding="utf-8") as out:
        out.write("\n".join(lines) + "\n")
    print(f"  [Sitemap OK] sitemap.xml 生成完了 ({len(entries)} URL)")


# ==========================================
# 5. 統合実行
# ==========================================
if __name__ == "__main__":
    print("=== MOZCRISIS BUILD SYSTEM STARTED ===")
    build_songs()
    build_members()
    build_audio_dramas()
    build_sitemap()
    print("\n=== ALL BUILD TASKS COMPLETED SUCCESSFULLY ===")