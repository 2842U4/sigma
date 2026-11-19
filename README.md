import urllib.request
import xml.etree.ElementTree as ET
import json
import html
import re
from datetime import datetime, timezone, timedelta

# 涵蓋歐美高廣告單價市場 + 亞洲高流量市場，不預設任何垂直領域
REGIONS = [
    {"code": "US", "label": "🇺🇸 美國熱搜"},
    {"code": "GB", "label": "🇬🇧 英國熱搜"},
    {"code": "TW", "label": "🇹🇼 台灣熱搜"},
    {"code": "JP", "label": "🇯🇵 日本熱搜"}
]

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()

def fetch_region(region):
    urls = [
        f"https://trends.google.com/trending/rss?geo={region['code']}",
        f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={region['code']}"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    
    xml_data = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
                if xml_data:
                    break
        except Exception:
            continue

    if not xml_data:
        print(f"Failed to fetch {region['code']}")
        return []

    items_out = []
    try:
        root = ET.fromstring(xml_data)
        for item in root.findall(".//item")[:10]:
            keyword = ""
            traffic = "🔥 熱搜中"
            picture = ""
            news_title = ""
            news_url = ""
            news_source = ""

            # 動態解析標籤（相容不同 XML 命名空間）
            for el in item.iter():
                tag = el.tag.split('}')[-1]
                if tag == "title" and not keyword:
                    keyword = clean_text(el.text)
                elif tag == "approx_traffic" and el.text:
                    traffic = f"🔥 {clean_text(el.text)}"
                elif tag == "picture" and el.text and not picture:
                    picture = el.text.strip()
                elif tag == "news_item_title" and el.text and not news_title:
                    news_title = clean_text(el.text)
                elif tag == "news_item_url" and el.text and not news_url:
                    news_url = el.text.strip()
                elif tag == "news_item_source" and el.text and not news_source:
                    news_source = clean_text(el.text)

            if keyword:
                fallback_url = f"https://www.google.com/search?q={urllib.parse.quote(keyword)}"
                items_out.append({
                    "region": region["label"],
                    "code": region["code"],
                    "keyword": keyword,
                    "traffic": traffic,
                    "picture": picture,
                    "hook": news_title if news_title else f"點擊查看「{keyword}」最新爆紅原因與完整報導",
                    "source": news_source if news_source else "Google Trends",
                    "url": news_url if news_url else fallback_url
                })
    except Exception as e:
        print(f"Parse error for {region['code']}: {e}")

    return items_out

def main():
    all_trends = []
    for r in REGIONS:
        all_trends.extend(fetch_region(r))

    tz = timezone(timedelta(hours=8))
    output = {
        "updated_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M"),
        "total": len(all_trends),
        "items": all_trends
    }
    with open("trends.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
