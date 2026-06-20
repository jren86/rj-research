#!/usr/bin/env python3
"""Scan reports/ directory and generate manifest.json + update index.html placeholder"""
import json
import os
import re
from collections import defaultdict

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
SITE_DIR = os.path.dirname(__file__)

# Category definitions: (id, name, description, filename_patterns)
CATEGORIES = [
    ("morning", "早间投研日报", "每日早间隔夜增量信息汇总", ["早间日报_"]),
    ("evening", "晚间投研日报", "每日晚间市场复盘与总结", ["晚间日报_"]),
    ("national_team", "国家队增减持追踪", "国家队增减持每日动向", ["每日国家队增减持动向_", "国家队增减持日报_"]),
    ("ai_bubble", "海外AI泡沫评估", "美股AI泡沫监测与分析", ["海外AI泡沫评估_"]),
    ("ai_news", "每日AI新闻", "AI行业每日新闻汇总", ["每日AI新闻_"]),
    ("deep_research", "深度研究报告", "行业与个股深度分析", [
        "钠离子电池行业研究_", "精智达FT测试机技术分析_", "石药集团分析_",
        "泡泡玛特分析_", "华通线缆深度分析_", "夏季电力主题_",
        "WorkBuddy深度研究_", "catl-dashboard"
    ]),
    ("ai_tracking", "AI人物与公司追踪", "腾讯AI/姚顺雨/WorkBuddy动态", ["AI人物与公司追踪_"]),
    ("market_panorama", "市场全景", "A股港股市场全景分析", ["市场全景_"]),
]

def extract_date(filename):
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return match.group(1) if match else None

def clean_title(filename):
    """Extract a clean display title from filename like 精智达FT测试机技术分析_2026-06-02.html"""
    name = filename.replace('.html', '')
    # Remove date suffix
    name = re.sub(r'_\d{4}-\d{2}-\d{2}$', '', name)
    name = re.sub(r'_\d{4}-\d{2}-\d{2}', '', name)
    # Custom short names
    short = {
        "精智达FT测试机技术分析": "精智达 · FT测试机技术分析",
        "钠离子电池行业研究": "钠离子电池行业深度投资机遇",
        "石药集团分析": "石药集团深度分析",
        "泡泡玛特分析": "泡泡玛特深度分析",
        "华通线缆深度分析": "华通线缆深度分析",
        "夏季电力主题": "夏季电力主题分析",
        "WorkBuddy深度研究": "WorkBuddy深度研究",
        "catl-dashboard": "宁德时代 CATL Dashboard",
    }
    return short.get(name, name)

def main():
    manifest = {"categories": []}
    for cat_id, cat_name, cat_desc, patterns in CATEGORIES:
        files = {}
        for fname in sorted(os.listdir(REPORTS_DIR)):
            if not fname.endswith('.html'):
                continue
            for pat in patterns:
                if fname.startswith(pat) or pat in fname:
                    date = extract_date(fname)
                    if date:
                        # For deep research, use title · date as the key
                        if cat_id == "deep_research":
                            title = clean_title(fname)
                            key = f"{title} · {date}"
                        else:
                            key = date
                        files[key] = f"reports/{fname}"
                    break
        if files:
            # Sort by date extracted from key
            def sort_key(item):
                k = item[0]
                m = re.search(r'(\d{4}-\d{2}-\d{2})', k)
                return m.group(1) if m else k
            sorted_items = sorted(files.items(), key=sort_key, reverse=True)
            latest_key = sorted_items[0][0]
            sorted_files = {k: v for k, v in sorted_items}
            manifest["categories"].append({
                "id": cat_id, "name": cat_name, "description": cat_desc,
                "reportCount": len(sorted_files),
                "latestDate": list(sorted_files.keys())[0],
                "files": sorted_files
            })

    # Write manifest.json
    manifest_path = os.path.join(SITE_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"manifest.json: {len(manifest['categories'])} categories")

    # Write inline manifest into index.html
    index_path = os.path.join(SITE_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()
        manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)
        marker_start = 'window.__MANIFEST = '
        marker_end = 'window.renderHub();'
        s = html.find(marker_start)
        e = html.find(marker_end, s)
        if s >= 0 and e > s:
            html = html[:s] + marker_start + manifest_json + '\n' + html[e:]
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"index.html: manifest embedded")
        else:
            print(f"index.html: markers not found (s={s} e={e})")

    for cat in manifest["categories"]:
        print(f"  {cat['name']}: {cat['reportCount']} reports (latest: {cat['latestDate']})")

if __name__ == "__main__":
    main()
