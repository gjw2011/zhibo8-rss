import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

BASE_URL = "https://wap.zhibo8.com/wap/news.html"
ITEM_URL = "https://wap.zhibo8.com"
OUTPUT = "zhibo8_football_fulltext.xml"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def clean_html(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["img", "script", "style"]):
        tag.decompose()
    return str(soup)

def fetch_full_text(url):
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(resp.text, "lxml")
    content = soup.find("div", class_=re.compile(r"article|news-content"))
    if content:
        return clean_html(str(content))
    return ""

def generate_rss(items):
    build_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    xml_items = ""
    for title, link, pub_date, fulltext in items:
        xml_items += f"""
<item>
<title><![CDATA[{title}]]></title>
<link>{link}</link>
<pubDate>{pub_date}</pubDate>
<description><![CDATA[{fulltext}]]></description>
</item>
"""
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>直播吧 - 足球新闻（全文，无图片）</title>
<link>{BASE_URL}</link>
<description>直播吧足球新闻全文版（不带图片）</description>
<language>zh-cn</language>
<lastBuildDate>{build_date}</lastBuildDate>
{xml_items}
</channel>
</rss>
"""
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(rss)

def main():
    try:
        resp = requests.get(BASE_URL, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return

    soup = BeautifulSoup(resp.text, "lxml")
    news_blocks = soup.find_all("div", class_="list-item")
    result_items = []

    for block in news_blocks:
        a = block.find("a")
        if not a:
            continue
        title = a.get_text(strip=True)
        if "足球" not in title and "足坛" not in title:
            continue
        link = ITEM_URL + a["href"]
        pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        full_text = fetch_full_text(link)
        if not full_text:
            continue
        result_items.append((title, link, pub_date, full_text))
        if len(result_items) >= 50:
            break
        time.sleep(0.5)

    if result_items:
        generate_rss(result_items)

if __name__ == "__main__":
    main()
