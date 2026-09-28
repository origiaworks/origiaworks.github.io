#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOZCRISIS Member Page Static Site Generator (SSG)
- 入力: data/members.json
- 出力: members/{mid}.html
- 資産参照: members/files/img/...
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "data", "members.json")  # data/members.json を参照
MEMBERS_DIR = os.path.join(BASE_DIR, "members")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PROFILE: {name_upper} ({name}) | MOZCRISIS</title>
    <meta name="description" content="MOZCRISISメンバー「{name}（{real_name}）」公式プロフィール。担当：{role}。{quote}">
    
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
        
        /* 背景の巨大立ち絵（ウォーターマーク） */
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
        .header-area {{ margin-bottom: 60px; border-left: 5px solid var(--member-color); padding-left: 30px; }}
        .role-title {{ font-family: var(--code-font); color: var(--member-color); font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; }}
        .name-main {{ font-size: clamp(3rem, 8vw, 5rem); font-weight: 900; margin: 10px 0; }}
        .name-sub {{ font-size: 1rem; color: #777; font-family: var(--code-font); }}
        
        .quote-box {{ 
            font-size: clamp(1.1rem, 3vw, 1.4rem); 
            font-style: italic; 
            margin: 40px 0; 
            color: #fff; 
            padding-bottom: 20px; 
            border-bottom: 2px solid var(--member-color); 
            width: fit-content; 
            line-height: 1.6;
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
    <!-- 立ち絵参照先: members/files/img/{mid}_stand.png -->
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
            <div class="name-sub">{real_name}</div>
        </header>

        <div class="quote-box">{quote}</div>

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
</body>
</html>
"""

def build():
    if not os.path.exists(JSON_PATH):
        print(f"[ERROR] {JSON_PATH} が見つかりません。")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        members = json.load(f)

    print(f"[*] data/members.json から全 {len(members)} 名の静的HTMLを生成します...")

    for mid, data in members.items():
        name = data.get("name", mid)
        real_name = data.get("realName", "")
        role = data.get("role", "")
        color = data.get("color", "#ff3e3e")
        quote = data.get("quote", "")
        bio = data.get("bio", "")
        gear = data.get("gear", "")
        specs = data.get("specs", [])

        specs_html = ""
        for spec in specs:
            label = spec.get("label", "")
            value = spec.get("value", "")
            specs_html += f"""
            <div class="spec-item">
                <div class="spec-label">{label}</div>
                <div class="spec-value">{value}</div>
            </div>"""

        html_content = HTML_TEMPLATE.format(
            mid=mid,
            name=name,
            name_upper=mid.upper(),
            real_name=real_name,
            role=role,
            color=color,
            quote=quote,
            bio=bio,
            gear=gear,
            specs_html=specs_html
        )

        out_path = os.path.join(MEMBERS_DIR, f"{mid}.html")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(html_content)

        print(f"[OK] 生成/上書き完了: members/{mid}.html")

    print("[SUCCESS] 全メンバーの静的HTML化が完了しました！")

if __name__ == "__main__":
    build()
