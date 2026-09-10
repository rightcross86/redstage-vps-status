#!/usr/bin/env python3
"""Render public/index.html from the history/*.yml files that upptime/uptime-monitor writes.

Kept deliberately simple (no JS framework, no build step) so it stays reliable
and easy to debug from inside a GitHub Actions job.
"""
import glob
import html
from datetime import datetime, timezone

import yaml

STATUS_LABEL = {
    "up": ("稼働中", "#16a34a"),
    "down": ("停止中", "#dc2626"),
}


def load_sites() -> list[dict]:
    sites = []
    for path in sorted(glob.glob("history/*.yml")):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        sites.append(data)
    return sites


def render(sites: list[dict]) -> str:
    all_up = all(s.get("status") == "up" for s in sites)
    banner_text = "全システム稼働中" if all_up else "一部のシステムで問題が発生しています"
    banner_color = "#16a34a" if all_up else "#dc2626"

    rows = []
    for s in sites:
        label, color = STATUS_LABEL.get(s.get("status"), ("不明", "#6b7280"))
        name = html.escape(str(s.get("url", "")))
        last_updated = s.get("lastUpdated", "")
        response_time = s.get("responseTime", "")
        rows.append(f"""
        <tr>
          <td>{name}</td>
          <td><span style="color:{color}; font-weight:600;">{label}</span></td>
          <td>{html.escape(str(response_time))} ms</td>
          <td>{html.escape(str(last_updated))}</td>
        </tr>""")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ハレノヒのれん サービスステータス</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", sans-serif; background:#f9fafb; color:#111827; margin:0; padding:2rem 1rem; }}
  main {{ max-width: 720px; margin: 0 auto; }}
  h1 {{ font-size: 1.4rem; margin-bottom: 0.25rem; }}
  .banner {{ background:{banner_color}; color:white; padding:1rem 1.25rem; border-radius:8px; font-weight:600; margin: 1rem 0 1.5rem; }}
  table {{ width:100%; border-collapse: collapse; background:white; border-radius:8px; overflow:hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  th, td {{ text-align:left; padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb; font-size:0.9rem; }}
  th {{ background:#f3f4f6; font-weight:600; }}
  tr:last-child td {{ border-bottom: none; }}
  footer {{ margin-top: 1.5rem; font-size: 0.75rem; color:#6b7280; }}
</style>
</head>
<body>
<main>
  <h1>ハレノヒのれん サービスステータス</h1>
  <p style="color:#6b7280; font-size:0.9rem;">各サービスの稼働状況を5分おきに確認し、このページに反映しています。</p>
  <div class="banner">{banner_text}</div>
  <table>
    <thead><tr><th>URL</th><th>状態</th><th>応答時間</th><th>最終確認</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
  <footer>最終生成: {generated_at} / <a href="https://github.com/rightcross86/redstage-vps-status">監視設定・履歴</a></footer>
</main>
</body>
</html>
"""


def main() -> None:
    sites = load_sites()
    page = render(sites)
    import os
    os.makedirs("public", exist_ok=True)
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(page)


if __name__ == "__main__":
    main()
