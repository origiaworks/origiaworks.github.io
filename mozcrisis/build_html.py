#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOZCRISIS Unified Static Site Generator (SSG)
- 楽曲個別HTML生成: data/songs.json -> songs/{sid}.html
- 全曲カタログ生成: data/songs.json -> discography.html
- メンバーHTML生成: data/members.json -> members/{mid}.html
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ==========================================
# 1. 楽曲（Songs）および カタログ ビルド処理
# ==========================================
SONGS_JSON = os.path.join(DATA_DIR, "songs.json")
SONGS_DIR = os.path.join(BASE_DIR, "songs")
SONGS_FILES_DIR = os.path.join(SONGS_DIR, "files")
DISCOGRAPHY_HTML_PATH = os.path.join(BASE_DIR, "discography.html")

SONG_HTML_TEMPLATE = """<!DOCTYPE html>
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

DISCOGRAPHY_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DISCOGRAPHY | MOZCRISIS [No Copyright Music Archive]</title>
    <meta name="description" content="MOZCRISIS（モズクライシス）が放つ全楽曲の完全カタログ。商用利用可能なアルゴリズム・ロックのフリーBGM音源（WAV/MP3）および歌詞をシーズン別に網羅。">
    <style>
        :root {{
            --main-red: #ff3e3e;
            --cyber-blue: #00f3ff;
            --bg-black: #0a0a0a;
            --card-bg: #151515;
            --text-white: #e0e0e0;
            --code-font: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        body {{ background-color: var(--bg-black); color: var(--text-white); font-family: 'Segoe UI', sans-serif; margin: 0; line-height: 1.6; }}
        nav {{ padding: 15px 20px; font-family: var(--code-font); border-bottom: 1px solid #222; background: rgba(0, 0, 0, 0.9); position: fixed; width: 100%; top: 0; z-index: 1000; box-sizing: border-box; }}
        nav a {{ color: var(--main-red); text-decoration: none; font-size: 0.8rem; font-weight: bold; }}
        nav a:hover {{ color: var(--cyber-blue); }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 100px 20px 80px; }}
        header {{ margin-bottom: 50px; border-left: 5px solid var(--main-red); padding-left: 30px; }}
        h1 {{ font-family: var(--code-font); font-size: clamp(2rem, 5vw, 3rem); margin: 0; text-transform: uppercase; letter-spacing: 2px; }}
        .subtitle {{ color: var(--cyber-blue); font-size: 0.85rem; font-family: var(--code-font); margin-top: 10px; }}
        .season-block {{ margin-bottom: 60px; border-top: 1px solid #222; padding-top: 30px; }}
        .season-header {{ margin-bottom: 25px; border-left: 4px solid var(--cyber-blue); padding-left: 15px; }}
        .season-title {{ font-family: var(--code-font); font-size: 1.3rem; color: #fff; margin: 0; letter-spacing: 2px; }}
        .song-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 15px; }}
        .song-card {{ background: var(--card-bg); border: 1px solid #222; text-decoration: none; color: inherit; display: block; transition: 0.3s; }}
        .song-card:hover {{ border-color: var(--cyber-blue); transform: translateY(-3px); box-shadow: 0 0 10px rgba(0, 243, 255, 0.2); }}
        .song-jacket {{ width: 100%; aspect-ratio: 1 / 1; background: #111; object-fit: cover; display: block; }}
        .song-info {{ padding: 8px; }}
        .song-meta {{ font-family: var(--code-font); font-size: 0.55rem; color: var(--main-red); margin-bottom: 2px; display: block; }}
        .song-title {{ font-size: 0.8rem; font-weight: bold; color: #fff; display: block; line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        footer {{ background: #050505; padding: 40px 20px; text-align: center; border-top: 1px solid #1a1a1a; font-family: var(--code-font); font-size: 0.7rem; color: #555; }}
        @media (max-width: 768px) {{ .container {{ padding: 80px 12px 30px; }} .song-grid {{ grid-template-columns: repeat(3, 1fr); gap: 10px; }} .song-info {{ padding: 6px; }} .song-title {{ font-size: 0.7rem; }} }}
    </style>
</head>
<body>
    <nav><a href="index.html">&lt;&lt; RETURN_TO_DASHBOARD</a></nav>
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

        html_content = SONG_HTML_TEMPLATE.format(
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
                <img src="songs/files/{sid}/{sid}_artwork.jpg" class="song-jacket" alt="{title}">
                <div class="song-info">
                    <span class="song-meta">{edition}</span>
                    <span class="song-title">{title}</span>
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

    discography_content = DISCOGRAPHY_HTML_TEMPLATE.format(seasons_html=seasons_html)
    with open(DISCOGRAPHY_HTML_PATH, "w", encoding="utf-8") as out:
        out.write(discography_content)
    print("  [Catalog OK] discography.html 生成完了")


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
    <title>PROFILE: {name_upper} ({name}) | MOZCRISIS</title>
    <meta name="description" content="MOZCRISISメンバー「{name}（{real_name}）」公式プロフィール。担当：{role} (CV: {cv})。{quote}">
    
    <!-- OGP (SNSシェア対策) -->
    <meta property="og:title" content="{name} ({real_name}) | MOZCRISIS PROFILE">
    <meta property="og:description" content="{quote} 担当：{role}">
    <meta property="og:image" content="files/img/{mid}.png">
    <meta property="og:type" content="profile">

    <style>
        :root {{ 
            --member-color: {color}; 
            --bg-black: #0a0a0a; 
            --text-white: #e0e0e0; 
            --code-font: 'Consolas', 'Monaco', 'Courier New', monospace; 
        }}
        body {{ 
            background-color: var(--bg-black); 
            color: var(--text-white); 
            font-family: 'Segoe UI', 'Hiragino Kaku Gothic ProN', sans-serif; 
            margin: 0; 
            line-height: 1.6; 
            overflow-x: hidden; 
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
        nav {{ 
            padding: 20px; 
            font-family: var(--code-font); 
            border-bottom: 1px solid #222; 
            background: rgba(0,0,0,0.8); 
            backdrop-filter: blur(8px);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        nav a {{ color: var(--member-color); text-decoration: none; font-weight: bold; font-size: 0.85rem; }}
        nav a:hover {{ text-decoration: underline; }}
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
        <a href="../index.html">&lt;&lt; RETURN_TO_HOME</a>
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
            label = spec.get("label", "")
            value = spec.get("value", "")
            specs_html += f"""
            <div class="spec-item">
                <div class="spec-label">{label}</div>
                <div class="spec-value">{value}</div>
            </div>"""

        html_content = MEMBER_HTML_TEMPLATE.format(
            mid=mid,
            name=name,
            name_upper=mid.upper(),
            real_name=real_name,
            role=role,
            color=color,
            quote=quote,
            cv=cv,
            voice_button_html=voice_button_html,
            bio=bio,
            gear=gear,
            specs_html=specs_html
        )

        out_path = os.path.join(MEMBERS_DIR, f"{mid}.html")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(html_content)

        print(f"  [Member OK] members/{mid}.html")


# ==========================================
# 3. 統合実行
# ==========================================
if __name__ == "__main__":
    print("=== MOZCRISIS BUILD SYSTEM STARTED ===")
    build_songs()
    build_members()
    print("\n=== ALL BUILD TASKS COMPLETED SUCCESSFULLY ===")