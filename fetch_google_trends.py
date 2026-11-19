import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import html
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

# 依全球網路用戶數與市場價值排序的 54 個國家/地區（含原生語系標記）
COUNTRIES = [
    {"code": "IN", "flag": "🇮🇳", "en": "India", "zh": "印度", "ja": "インド", "group": "ASIA", "tier1": False, "lang": "en"},
    {"code": "US", "flag": "🇺🇸", "en": "United States", "zh": "美國", "ja": "アメリカ", "group": "AMERICAS", "tier1": True, "lang": "en"},
    {"code": "ID", "flag": "🇮🇩", "en": "Indonesia", "zh": "印尼", "ja": "インドネシア", "group": "ASIA", "tier1": False, "lang": "id"},
    {"code": "BR", "flag": "🇧🇷", "en": "Brazil", "zh": "巴西", "ja": "ブラジル", "group": "AMERICAS", "tier1": False, "lang": "pt"},
    {"code": "RU", "flag": "🇷🇺", "en": "Russia", "zh": "俄羅斯", "ja": "ロシア", "group": "EUROPE", "tier1": False, "lang": "ru"},
    {"code": "JP", "flag": "🇯🇵", "en": "Japan", "zh": "日本", "ja": "日本", "group": "ASIA", "tier1": True, "lang": "ja"},
    {"code": "NG", "flag": "🇳🇬", "en": "Nigeria", "zh": "奈及利亞", "ja": "ナイジェリア", "group": "MEA", "tier1": False, "lang": "en"},
    {"code": "MX", "flag": "🇲🇽", "en": "Mexico", "zh": "墨西哥", "ja": "メキシコ", "group": "AMERICAS", "tier1": False, "lang": "es"},
    {"code": "PH", "flag": "🇵🇭", "en": "Philippines", "zh": "菲律賓", "ja": "フィリピン", "group": "ASIA", "tier1": False, "lang": "en"},
    {"code": "VN", "flag": "🇻🇳", "en": "Vietnam", "zh": "越南", "ja": "ベトナム", "group": "ASIA", "tier1": False, "lang": "vi"},
    {"code": "EG", "flag": "🇪🇬", "en": "Egypt", "zh": "埃及", "ja": "エジプト", "group": "MEA", "tier1": False, "lang": "ar"},
    {"code": "DE", "flag": "🇩🇪", "en": "Germany", "zh": "德國", "ja": "ドイツ", "group": "EUROPE", "tier1": True, "lang": "de"},
    {"code": "TR", "flag": "🇹🇷", "en": "Turkey", "zh": "土耳其", "ja": "トルコ", "group": "MEA", "tier1": False, "lang": "tr"},
    {"code": "GB", "flag": "🇬🇧", "en": "United Kingdom", "zh": "英國", "ja": "イギリス", "group": "EUROPE", "tier1": True, "lang": "en"},
    {"code": "TH", "flag": "🇹🇭", "en": "Thailand", "zh": "泰國", "ja": "タイ", "group": "ASIA", "tier1": False, "lang": "th"},
    {"code": "FR", "flag": "🇫🇷", "en": "France", "zh": "法國", "ja": "フランス", "group": "EUROPE", "tier1": True, "lang": "fr"},
    {"code": "IT", "flag": "🇮🇹", "en": "Italy", "zh": "義大利", "ja": "イタリア", "group": "EUROPE", "tier1": True, "lang": "it"},
    {"code": "KR", "flag": "🇰🇷", "en": "South Korea", "zh": "韓國", "ja": "韓国", "group": "ASIA", "tier1": True, "lang": "ko"},
    {"code": "ES", "flag": "🇪🇸", "en": "Spain", "zh": "西班牙", "ja": "スペイン", "group": "EUROPE", "tier1": True, "lang": "es"},
    {"code": "ZA", "flag": "🇿🇦", "en": "South Africa", "zh": "南非", "ja": "南アフリカ", "group": "MEA", "tier1": False, "lang": "en"},
    {"code": "CO", "flag": "🇨🇴", "en": "Colombia", "zh": "哥倫比亞", "ja": "コロンビア", "group": "AMERICAS", "tier1": False, "lang": "es"},
    {"code": "AR", "flag": "🇦🇷", "en": "Argentina", "zh": "阿根廷", "ja": "アルゼンチン", "group": "AMERICAS", "tier1": False, "lang": "es"},
    {"code": "PL", "flag": "🇵🇱", "en": "Poland", "zh": "波蘭", "ja": "ポーランド", "group": "EUROPE", "tier1": False, "lang": "pl"},
    {"code": "CA", "flag": "🇨🇦", "en": "Canada", "zh": "加拿大", "ja": "カナダ", "group": "AMERICAS", "tier1": True, "lang": "en"},
    {"code": "SA", "flag": "🇸🇦", "en": "Saudi Arabia", "zh": "沙烏地阿拉伯", "ja": "サウジアラビア", "group": "MEA", "tier1": True, "lang": "ar"},
    {"code": "MY", "flag": "🇲🇾", "en": "Malaysia", "zh": "馬來西亞", "ja": "マレーシア", "group": "ASIA", "tier1": False, "lang": "ms"},
    {"code": "UA", "flag": "🇺🇦", "en": "Ukraine", "zh": "烏克蘭", "ja": "ウクライナ", "group": "EUROPE", "tier1": False, "lang": "uk"},
    {"code": "PE", "flag": "🇵🇪", "en": "Peru", "zh": "秘魯", "ja": "ペルー", "group": "AMERICAS", "tier1": False, "lang": "es"},
    {"code": "AU", "flag": "🇦🇺", "en": "Australia", "zh": "澳洲", "ja": "オーストラリア", "group": "ASIA", "tier1": True, "lang": "en"},
    {"code": "TW", "flag": "🇹🇼", "en": "Taiwan", "zh": "台灣", "ja": "台湾", "group": "ASIA", "tier1": True, "lang": "zh-TW"},
    {"code": "KE", "flag": "🇰🇪", "en": "Kenya", "zh": "肯亞", "ja": "ケニア", "group": "MEA", "tier1": False, "lang": "en"},
    {"code": "CL", "flag": "🇨🇱", "en": "Chile", "zh": "智利", "ja": "チリ", "group": "AMERICAS", "tier1": False, "lang": "es"},
    {"code": "RO", "flag": "🇷🇴", "en": "Romania", "zh": "羅馬尼亞", "ja": "ルーマニア", "group": "EUROPE", "tier1": False, "lang": "ro"},
    {"code": "NL", "flag": "🇳🇱", "en": "Netherlands", "zh": "荷蘭", "ja": "オランダ", "group": "EUROPE", "tier1": True, "lang": "nl"},
    {"code": "BE", "flag": "🇧🇪", "en": "Belgium", "zh": "比利時", "ja": "ベルギー", "group": "EUROPE", "tier1": True, "lang": "nl"},
    {"code": "SE", "flag": "🇸🇪", "en": "Sweden", "zh": "瑞典", "ja": "スウェーデン", "group": "EUROPE", "tier1": True, "lang": "sv"},
    {"code": "CZ", "flag": "🇨🇿", "en": "Czechia", "zh": "捷克", "ja": "チェコ", "group": "EUROPE", "tier1": False, "lang": "cs"},
    {"code": "AE", "flag": "🇦🇪", "en": "UAE", "zh": "阿聯酋", "ja": "UAE", "group": "MEA", "tier1": True, "lang": "ar"},
    {"code": "GR", "flag": "🇬🇷", "en": "Greece", "zh": "希臘", "ja": "ギリシャ", "group": "EUROPE", "tier1": False, "lang": "el"},
    {"code": "PT", "flag": "🇵🇹", "en": "Portugal", "zh": "葡萄牙", "ja": "ポルトガル", "group": "EUROPE", "tier1": False, "lang": "pt"},
    {"code": "HU", "flag": "🇭🇺", "en": "Hungary", "zh": "匈牙利", "ja": "ハンガリー", "group": "EUROPE", "tier1": False, "lang": "hu"},
    {"code": "AT", "flag": "🇦🇹", "en": "Austria", "zh": "奧地利", "ja": "オーストリア", "group": "EUROPE", "tier1": True, "lang": "de"},
    {"code": "CH", "flag": "🇨🇭", "en": "Switzerland", "zh": "瑞士", "ja": "スイス", "group": "EUROPE", "tier1": True, "lang": "de"},
    {"code": "IL", "flag": "🇮🇱", "en": "Israel", "zh": "以色列", "ja": "イスラエル", "group": "MEA", "tier1": True, "lang": "he"},
    {"code": "HK", "flag": "🇭🇰", "en": "Hong Kong", "zh": "香港", "ja": "香港", "group": "ASIA", "tier1": True, "lang": "zh-TW"},
    {"code": "DK", "flag": "🇩🇰", "en": "Denmark", "zh": "丹麥", "ja": "デンマーク", "group": "EUROPE", "tier1": True, "lang": "da"},
    {"code": "SG", "flag": "🇸🇬", "en": "Singapore", "zh": "新加坡", "ja": "シンガポール", "group": "ASIA", "tier1": True, "lang": "en"},
    {"code": "FI", "flag": "🇫🇮", "en": "Finland", "zh": "芬蘭", "ja": "フィンランド", "group": "EUROPE", "tier1": True, "lang": "fi"},
    {"code": "NO", "flag": "🇳🇴", "en": "Norway", "zh": "挪威", "ja": "ノルウェー", "group": "EUROPE", "tier1": True, "lang": "no"},
    {"code": "IE", "flag": "🇮🇪", "en": "Ireland", "zh": "愛爾蘭", "ja": "アイルランド", "group": "EUROPE", "tier1": True, "lang": "en"},
    {"code": "NZ", "flag": "🇳🇿", "en": "New Zealand", "zh": "紐西蘭", "ja": "ニュージーランド", "group": "ASIA", "tier1": True, "lang": "en"},
    {"code": "SK", "flag": "🇸🇰", "en": "Slovakia", "zh": "斯洛伐克", "ja": "スロバキア", "group": "EUROPE", "tier1": False, "lang": "sk"},
    {"code": "BG", "flag": "🇧🇬", "en": "Bulgaria", "zh": "保加利亞", "ja": "ブルガリア", "group": "EUROPE", "tier1": False, "lang": "bg"},
    {"code": "HR", "flag": "🇭🇷", "en": "Croatia", "zh": "克羅埃西亞", "ja": "クロアチア", "group": "EUROPE", "tier1": False, "lang": "hr"}
]

TARGET_LANGS = ["en", "zh-TW", "ja", "ko", "es", "pt"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

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

    xml_data = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12) as resp:
                xml_data = resp.read()
                if xml_data:
                    break
        except Exception:
            continue

    if not xml_data:
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
                hook_text = news_title if news_title else f"Breaking viral surge around '{keyword}' — tap for full context & updates."
                items_out.append({
                    "code": code,
                    "flag": country["flag"],
                    "name_en": country["en"],
                    "name_zh": country["zh"],
                    "name_ja": country["ja"],
                    "group": country["group"],
                    "tier1": country["tier1"],
                    "native_lang": country["lang"],
                    "keyword": keyword,
                    "hook": hook_text,
                    "kw_i18n": {country["lang"]: keyword},
                    "hk_i18n": {country["lang"]: hook_text},
                    "traffic": traffic,
                    "picture": picture,
                    "source": news_source if news_source else "Google Trends",
                    "url": news_url if news_url else fallback_url
                })
    except Exception as e:
        print(f"[ERR] {code}: {e}")

    return items_out

def _call_google_translate(texts, target_lang):
    joined = "\n".join(texts)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={urllib.parse.quote(target_lang)}&dt=t"
    data = urllib.parse.urlencode({"q": joined}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
        translated_full = "".join(seg[0] for seg in raw[0] if seg and seg[0])
        lines = [clean_text(line) for line in translated_full.split("\n")]
        if len(lines) == len(texts):
            return lines
    return None

def translate_chunk_safe(texts, target_lang):
    try:
        res = _call_google_translate(texts, target_lang)
        if res:
            return res
    except Exception:
        pass

    # 若單批 20 筆行數未對齊，自動拆成 5 筆小批次重試
    if len(texts) > 5:
        out = []
        for i in range(0, len(texts), 5):
            sub = texts[i:i+5]
            try:
                sub_res = _call_google_translate(sub, target_lang)
                out.extend(sub_res if sub_res else sub)
            except Exception:
                out.extend(sub)
        return out
    return texts

def batch_translate_all(items):
    tasks = []
    for lang in TARGET_LANGS:
        # 篩選出原生語系不同於目標語系的項目進行翻譯
        kw_indices = []
        kw_texts = []
        hk_indices = []
        hk_texts = []

        for idx, item in enumerate(items):
            if item["native_lang"] != lang:
                kw_indices.append(idx)
                kw_texts.append(item["keyword"])
                hk_indices.append(idx)
                hk_texts.append(item["hook"])

        for start in range(0, len(kw_texts), 20):
            tasks.append((lang, "kw_i18n", kw_indices[start:start+20], kw_texts[start:start+20]))
        for start in range(0, len(hk_texts), 20):
            tasks.append((lang, "hk_i18n", hk_indices[start:start+20], hk_texts[start:start+20]))

    print(f"Running {len(tasks)} translation batches across {len(TARGET_LANGS)} languages...")

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {
            executor.submit(translate_chunk_safe, t[3], t[0]): (t[0], t[1], t[2])
            for t in tasks
        }
        for future in as_completed(future_map):
            lang, field, indices = future_map[future]
            try:
                translated_list = future.result()
                for idx, val in zip(indices, translated_list):
                    items[idx][field][lang] = val
            except Exception as e:
                print(f"[TRANS-WARN] {lang} {field}: {e}")

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

    all_trends = []
    active_countries = 0
    for c in COUNTRIES:
        items = results_map.get(c["code"], [])
        if items:
            active_countries += 1
            all_trends.extend(items)

    print(f"Fetched {len(all_trends)} trends from {active_countries} countries. Translating...")
    batch_translate_all(all_trends)

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

    print(f"Done: {active_countries} countries, {len(all_trends)} translated trends saved.")

if __name__ == "__main__":
    main()
