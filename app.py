import streamlit as st
import feedparser
from bs4 import BeautifulSoup
import datetime

st.set_page_config(page_title="每日经济宏观热点", layout="wide")
st.title("📈 每日经济与宏观新闻")
st.markdown(f"**更新时间：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ==================== RSS 配置 ====================
RSS_FEEDS = {
    "新浪财经要闻": "http://rss.sina.com.cn/roll/finance/hot_roll.xml",
    "新浪财经焦点": "http://rss.sina.com.cn/news/allnews/finance.xml",
    "WSJ Economy": "https://feeds.content.dowjones.io/public/rss/socialeconomyfeed",
    "Financial Times": "https://www.ft.com/global-economy?format=rss",
    "Reuters Business": "http://feeds.reuters.com/reuters/businessNews",
}

MAX_PER_FEED = 6
TOTAL_SHOW = 25

@st.cache_data(ttl=3600)  # 每小时缓存一次
def fetch_all_news():
    all_news = []
    for name, url in RSS_FEEDS.items():
        with st.spinner(f"正在获取 {name}..."):
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:MAX_PER_FEED]:
                    summary = entry.get("summary", entry.get("description", ""))
                    soup = BeautifulSoup(summary, "html.parser")
                    clean_summary = soup.get_text(strip=True)[:280]
                    if len(clean_summary) > 280:
                        clean_summary += "..."
                    
                    all_news.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": clean_summary,
                        "published": entry.get("published", "未知"),
                        "source": name
                    })
            except:
                pass  # 跳过失败的源
    return all_news

news_list = fetch_all_news()

# 去重
seen = set()
unique_news = []
for item in news_list:
    if item["title"] not in seen:
        seen.add(item["title"])
        unique_news.append(item)

# 排序（按发布时间倒序）
unique_news.sort(key=lambda x: x["published"], reverse=True)

# 显示
st.success(f"共抓取到 {len(unique_news)} 条新闻，显示前 {TOTAL_SHOW} 条")

for i, news in enumerate(unique_news[:TOTAL_SHOW], 1):
    with st.expander(f"{i}. {news['title']}", expanded=False):
        st.markdown(f"**来源**：{news['source']}　|　**时间**：{news['published']}")
        st.write(news['summary'])
        st.markdown(f"[🔗 阅读全文]({news['link']})")

st.caption("数据来自公开 RSS 源 • 每小时自动更新缓存 • 可在手机浏览器添加至主屏幕")
