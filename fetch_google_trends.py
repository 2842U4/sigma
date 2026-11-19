import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import html
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

# 依全球網路用戶數與市場價值排序的 54 個 Google Trends 支援國家/地區
COUNTRIES = [
    {"code": "IN", "flag": "🇮🇳", "en": "India", "zh": "印度", "ja": "インド", "group": "ASIA", "tier1": False},
    {"code": "US", "flag": "🇺🇸", "en": "United States", "zh": "美國", "ja": "アメリカ", "group": "AMERICAS", "tier1": True},
    {"code": "ID", "flag": "🇮🇩", "en": "Indonesia", "zh": "印尼", "ja": "インドネシア", "group": "ASIA", "tier1": False},
    {"code": "BR", "flag": "🇧🇷", "en": "Brazil", "zh": "巴西", "ja": "ブラジル", "group": "AMERICAS", "tier1": False},
    {"code": "RU", "flag": "🇷🇺", "en": "Russia", "zh": "俄羅斯", "ja": "ロシア", "group": "EUROPE", "tier1": False},
    {"code": "JP", "flag": "🇯🇵", "en": "Japan", "zh": "日本", "ja": "日本", "group": "ASIA", "tier1": True},
    {"code": "NG", "flag": "🇳🇬", "en": "Nigeria", "zh": "奈及利亞", "ja": "ナイジェリア", "group": "MEA", "tier1": False},
    {"code": "MX", "flag": "🇲🇽", "en": "Mexico", "zh": "墨西哥", "ja": "メキシコ", "group": "AMERICAS", "tier1": False},
    {"code": "PH", "flag": "🇵🇭", "en": "Philippines", "zh": "菲律賓", "ja": "フィリピン", "group": "ASIA", "tier1": False},
    {"code": "VN", "flag": "🇻🇳", "en": "Vietnam", "zh": "越南", "ja": "ベトナム", "group": "ASIA", "tier1": False},
    {"code": "EG", "flag": "🇪🇬", "en": "Egypt", "zh": "埃及", "ja": "エジプト", "group": "MEA", "tier1": False},
    {"code": "DE", "flag": "🇩🇪", "en": "Germany", "zh": "德國", "ja": "ドイツ", "group": "EUROPE", "tier1": True},
    {"code": "TR", "flag": "🇹🇷", "en": "Turkey", "zh": "土耳其", "ja": "トルコ", "group": "MEA", "tier1": False},
    {"code": "GB", "flag": "🇬🇧", "en": "United Kingdom", "zh": "英國", "ja": "イギリス", "group": "EUROPE", "tier1": True},
    {"code": "TH", "flag": "🇹🇭", "en": "Thailand", "zh": "泰國", "ja": "タイ", "group": "ASIA", "tier1": False},
    {"code": "FR", "flag": "🇫🇷", "en": "France", "zh": "法國", "ja": "フランス", "group": "EUROPE", "tier1": True},
    {"code": "IT", "flag": "🇮🇹", "en": "Italy", "zh": "義大利", "ja": "イタリア", "group": "EUROPE", "tier1": True},
    {"code": "KR", "flag": "🇰🇷", "en": "South Korea", "zh": "韓國", "ja": "韓国", "group": "ASIA", "tier1": True},
    {"code": "ES", "flag": "🇪🇸", "en": "Spain", "zh": "西班牙", "ja": "スペイン", "group": "EUROPE", "tier1": True},
    {"code": "ZA", "flag": "🇿🇦", "en": "South Africa", "zh": "南非", "ja": "南アフリカ", "group": "MEA", "tier1": False},
    {"code": "CO", "flag": "🇨🇴", "en": "Colombia", "zh": "哥倫比亞", "ja": "コロンビア", "group": "AMERICAS", "tier1": False},
    {"code": "AR", "flag": "🇦🇷", "en": "Argentina", "zh": "阿根廷", "ja": "アルゼンチン", "group": "AMERICAS", "tier1": False},
    {"code": "PL", "flag": "🇵🇱", "en": "Poland", "zh": "波蘭", "ja": "ポーランド", "group": "EUROPE", "tier1": False},
    {"code": "CA", "flag": "🇨🇦", "en": "Canada", "zh": "加拿大", "ja": "カナダ", "group": "AMERICAS", "tier1": True},
    {"code": "SA", "flag": "🇸🇦", "en": "Saudi Arabia", "zh": "沙烏地阿拉伯", "ja": "サウジアラビア", "group": "MEA", "tier1": True},
    {"code": "MY", "flag": "🇲🇾", "en": "Malaysia", "zh": "馬來西亞", "ja": "マレーシア", "group": "ASIA", "tier1": False},
    {"code": "UA", "flag": "🇺🇦", "en": "Ukraine", "zh": "烏克蘭", "ja": "ウクライナ", "group": "EUROPE", "tier1": False},
    {"code": "PE", "flag": "🇵🇪", "en": "Peru", "zh": "秘魯", "ja": "ペルー", "group": "AMERICAS", "tier1": False},
    {"code": "AU", "flag": "🇦🇺", "en": "Australia", "zh": "澳洲", "ja": "オーストラリア", "group": "ASIA", "tier1": True},
    {"code": "TW", "flag": "🇹🇼", "en": "Taiwan", "zh": "台灣", "ja": "台湾", "group": "ASIA", "tier1": True},
    {"code": "KE", "flag": "🇰🇪", "en": "Kenya", "zh": "肯亞", "ja": "ケニア", "group": "MEA", "tier1": False},
    {"code": "CL", "flag": "🇨🇱", "en": "Chile", "zh": "智利", "ja": "チリ", "group": "AMERICAS", "tier1": False},
    {"code": "RO", "flag": "🇷🇴", "en": "Romania", "zh": "羅馬尼亞", "ja": "ルーマニア", "group": "EUROPE", "tier1": False},
    {"code": "NL", "flag": "🇳🇱", "en": "Netherlands", "zh": "荷蘭", "ja": "オランダ", "group": "EUROPE", "tier1": True},
    {"code": "BE", "flag": "🇧🇪", "en": "Belgium", "zh": "比利時", "ja": "ベルギー", "group": "EUROPE", "tier1": True},
    {"code": "SE", "flag": "🇸🇪", "en": "Sweden", "zh": "瑞典", "ja": "スウェーデン", "group": "EUROPE", "tier1": True},
    {"code": "CZ", "flag": "🇨🇿", "en": "Czechia", "zh": "捷克", "ja": "チェコ", "group": "EUROPE", "tier1": False},
    {"code": "AE", "flag": "🇦🇪", "en": "UAE", "zh": "阿聯酋", "ja": "UAE", "group": "MEA", "tier1": True},
    {"code": "GR", "flag": "🇬🇷", "en": "Greece", "zh": "希臘", "ja": "ギリシャ", "group": "EUROPE", "tier1": False},
    {"code": "PT", "flag": "🇵🇹", "en": "Portugal", "zh": "葡萄牙", "ja": "ポルトガル", "group": "EUROPE", "tier1": False},
    {"code": "HU", "flag": "🇭🇺", "en": "Hungary", "zh": "匈牙利", "ja": "ハンガリー", "group": "EUROPE", "tier1": False},
    {"code": "AT", "flag": "🇦🇹", "en": "Austria", "zh": "奧地利", "ja": "オーストリア", "group": "EUROPE", "tier1": True},
    {"code": "CH", "flag": "🇨🇭", "en": "Switzerland", "zh": "瑞士", "ja": "スイス", "group": "EUROPE", "tier1": True},
    {"code": "IL", "flag": "🇮🇱", "en": "Israel", "zh": "以色列", "ja": "イスラエル", "group": "MEA", "tier1": True},
    {"code": "HK", "flag": "🇭🇰", "en": "Hong Kong", "zh": "香港", "ja": "香港", "group": "ASIA", "tier1": True},
    {"code": "DK", "flag": "🇩🇰", "en": "Denmark", "zh": "丹麥", "ja": "デンマーク", "group": "EUROPE", "tier1": True},
    {"code": "SG", "flag": "🇸🇬", "en": "Singapore", "zh": "新加坡", "ja": "シンガポール", "group": "ASIA", "tier1": True},
    {"code": "FI", "flag": "🇫🇮", "en": "Finland", "zh": "芬蘭", "ja": "フィンランド", "group": "EUROPE", "tier1": True},
    {"code": "NO", "flag": "🇳🇴", "en": "Norway", "zh": "挪威", "ja": "ノルウェー", "group": "EUROPE", "tier1": True},
    {"code": "IE", "flag": "🇮🇪", "en": "Ireland", "zh": "愛爾蘭", "ja": "アイルランド", "group": "EUROPE", "tier1": True},
    {"code": "NZ", "flag": "🇳🇿", "en": "New Zealand", "zh": "紐西蘭", "ja": "ニュージーランド", "group": "ASIA", "tier1": True},
    {"code": "SK", "flag": "🇸🇰", "en": "Slovakia", "zh": "斯洛伐克", "ja": "スロバキア", "group": "EUROPE", "tier1": False},
    {"code": "BG", "flag": "🇧🇬", "en": "Bulgaria", "zh": "保加利亞", "ja": "ブルガリア", "group": "EUROPE", "tier1": False},
    {"code": "HR", "flag": "🇭🇷", "en": "Croatia", "zh": "克羅埃西亞", "ja": "クロアチア", "group": "EUROPE", "tier1": False}
]

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()

def fetch_country(country):
    code = country["code"]
    urls = [
        f"https://trends.google.com/trending/rss?geo={code}",
        f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={code}"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }

    xml_data = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                xml_data = resp.read()
                if xml_data:
                    break
        except Exception:
            continue

    if not xml_data:
        print(f"[SKIP] {code} failed")
        return []

    items_out = []
    try:
        root = ET.fromstring(xml_data)
        for item in root.findall(".//item")[:10]:
            keyword = ""
            traffic = "🔥 Trending"
            picture = ""
            news_title = ""
            news_url = ""
            news_source = ""

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
                    "code": code,
                    "flag": country["flag"],
                    "name_en": country["en"],
                    "name_zh": country["zh"],
                    "name_ja": country["ja"],
                    "group": country["group"],
                    "tier1": country["tier1"],
                    "keyword": keyword,
                    "traffic": traffic,
                    "picture": picture,
                    "hook": news_title if news_title else f"Breaking viral surge around '{keyword}' — tap for full context & updates.",
                    "source": news_source if news_source else "Google Trends",
                    "url": news_url if news_url else fallback_url
                })
    except Exception as e:
        print(f"[ERR] {code}: {e}")

    print(f"[OK] {code}: {len(items_out)} items")
    return items_out

def main():
    results_map = {}
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_code = {executor.submit(fetch_country, c): c["code"] for c in COUNTRIES}
        for future in as_completed(future_to_code):
            code = future_to_code[future]
            try:
                results_map[code] = future.result()
            except Exception:
                results_map[code] = []

    # 維持高人口/高價值國家順序輸出
    all_trends = []
    active_countries = 0
    for c in COUNTRIES:
        items = results_map.get(c["code"], [])
        if items:
            active_countries += 1
            all_trends.extend(items)

    tz = timezone(timedelta(hours=8))
    output = {
        "updated_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M"),
        "countries_count": active_countries,
        "total": len(all_trends),
        "countries": [
            {
                "code": c["code"],
                "flag": c["flag"],
                "en": c["en"],
                "zh": c["zh"],
                "ja": c["ja"],
                "group": c["group"],
                "tier1": c["tier1"],
                "count": len(results_map.get(c["code"], []))
            }
            for c in COUNTRIES if len(results_map.get(c["code"], [])) > 0
        ],
        "items": all_trends
    }

    with open("trends.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Done: {active_countries} countries, {len(all_trends)} trends saved.")

if __name__ == "__main__":
    main()
