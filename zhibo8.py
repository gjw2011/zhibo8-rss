import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

BASE_URL = "https://wap.zhibo8.com/wap/news.html"
ITEM_URL = "https://wap.zhibo8.com"
OUTPUT = "zhibo8_football_fulltext.xml"

headers = {"User-Agent": "Mozilla/5.0"}

def clean_html(html):
    soup = BeautifulSoup(html, "lxml")
    for img in soup.find_all("img"):
        img.decompose()
    return str(soup)

def fetch_full_text(url):
    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "lxml")
    content = soup.find("div", class_="content")
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
    rss = f"""
<?xml version="1.0" encoding="UTF-8"?>
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
    resp = requests.get(BASE_URL, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "lxml")
    raw_items = soup.find_all("a", href=re.compile("news/detail"))
    result_items = []
    for a in raw_items[:50]:
        title = a.text.strip()
        link = ITEM_URL + a["href"]
        pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        full_text = fetch_full_text(link)
        result_items.append((title, link, pub_date, full_text))
        time.sleep(0.3)
    generate_rss(result_items)

if __name__ == "__main__":
    main()
