#!/usr/bin/env python3
"""Scan reports/ directory and generate manifest.json"""
import json
import os
import re
from collections import defaultdict

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

# Category definitions: (id, name, description, filename_patterns)
CATEGORIES = [
    ("morning", "早间投研日报", "每日早间隔夜增量信息汇总", ["早间日报_"]),
    ("evening", "晚间投研日报", "每日晚间市场复盘与总结", ["晚间日报_"]),
    ("daily", "投研日报", "投研日报汇总", ["投研日报_"]),
    ("national_team", "国家队增减持追踪", "国家队增减持每日动向", ["每日国家队增减持动向_", "国家队增减持日报_"]),
    ("ai_bubble", "海外AI泡沫评估", "美股AI泡沫监测与分析", ["海外AI泡沫评估_"]),
    ("ai_news", "每日AI新闻", "AI行业每日新闻汇总", ["每日AI新闻_"]),
    ("deep_research", "深度研究报告", "行业与个股深度分析", [
        "钠离子电池行业研究_", "精智达FT测试机技术分析_", "石药集团分析_",
        "泡泡玛特分析_", "华通线缆深度分析_", "夏季电力主题_",
        "WorkBuddy深度研究_", "catl-dashboard"
    ]),
    ("ai_tracking", "AI人物与公司追踪", "腾讯AI/姚顺雨/WorkBuddy动态", ["AI人物与公司追踪_"]),
]

def extract_date(filename):
    """Extract YYYY-MM-DD from filename like 早间日报_2026-06-03.html"""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return match.group(1) if match else None

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
                        relative_path = f"reports/{fname}"
                        files[date] = relative_path
                    break

        if files:
            # Sort by date descending
            sorted_files = dict(sorted(files.items(), reverse=True))
            manifest["categories"].append({
                "id": cat_id,
                "name": cat_name,
                "description": cat_desc,
                "reportCount": len(sorted_files),
                "latestDate": list(sorted_files.keys())[0],
                "files": sorted_files
            })

    out_path = os.path.join(os.path.dirname(__file__), "manifest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Manifest generated: {out_path}")
    
    # Also embed manifest into index.html
    site_dir = os.path.dirname(__file__)
    index_path = os.path.join(site_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()
        manifest_json = json.dumps(manifest, ensure_ascii=False)
        old = 'window.__MANIFEST = '
        start = html.find(old)
        if start >= 0:
            end = html.find(';</script>', start)
            if end >= 0:
                html = html[:start] + old + manifest_json + html[end:]
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"Manifest embedded into: {index_path}")
    
    print(f"Categories: {len(manifest['categories'])}")
    for cat in manifest["categories"]:
        print(f"  {cat['name']}: {cat['reportCount']} reports (latest: {cat['latestDate']})")

if __name__ == "__main__":
    main()
