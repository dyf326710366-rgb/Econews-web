import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
from urllib.parse import urlparse

st.set_page_config(page_title="每日经济新闻", layout="wide")
st.title("📈 每日经济与宏观新闻")
st.markdown(f"**更新时间：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

# RSS Feeds
RSS_FEEDS = {
    "新浪财经": "http://rss.sina.com.cn/roll/finance/hot_roll.xml",
    "新浪财经焦点": "http://rss.sina.com.cn/news/allnews/finance.xml",
    "WSJ Economy": "https://feeds.content.dowjones.io/public/rss/socialeconomyfeed",
}

@st.cache_data(ttl=1800)
def fetch_rss(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        news = []
        for item in root.findall('.//item')[:6]:
            title = item.find('title').text if item.find('title') is not None else '无标题'
            link = item.find('link').text if item.find('link') is not None else ''
            desc = item.find('description').text if item.find('description') is not None else ''
            pubdate = item.find('pubDate').text if item.find('pubDate') is not None else '未知'
            news.append({"title": title, "link": link, "summary": desc[:280], "published": pubdate, "source": urlparse(url).netloc})
        return news
    except:
        return []

all_news = []
for name, url in RSS_FEEDS.items():
    with st.spinner(f"获取 {name}..."):
        all_news.extend(fetch_rss(url))

# 显示
st.success(f"成功获取 {len(all_news)} 条新闻")
for i, news in enumerate(all_news[:20], 1):
    with st.expander(f"{i}. {news['title'][:70]}...", expanded=False):
        st.markdown(f"**来源**：{news['source']} | **时间**：{news['published']}")
        st.write(news['summary'] + "...")
        if news['link']:
            st.markdown(f"[🔗 阅读全文]({news['link']})")

st.caption("纯内置实现 • 无需额外依赖 • 刷新即可更新")
