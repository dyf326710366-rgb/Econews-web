import streamlit as st
import feedparser
import datetime

st.set_page_config(page_title="每日经济新闻", layout="wide")
st.title("📈 每日经济与宏观新闻")
st.markdown(f"**更新时间：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

RSS_FEEDS = {
    "新浪财经要闻": "http://rss.sina.com.cn/roll/finance/hot_roll.xml",
    "新浪财经焦点": "http://rss.sina.com.cn/news/allnews/finance.xml",
    "WSJ Economy": "https://feeds.content.dowjones.io/public/rss/socialeconomyfeed",
    "Financial Times": "https://www.ft.com/global-economy?format=rss",
}

@st.cache_data(ttl=3600)
def fetch_news():
    all_news = []
    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                summary = entry.get("summary", entry.get("description", "无摘要"))
                # 简单清理
                summary = summary.replace("<p>", "").replace("</p>", "")[:280]
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": summary + "..." if len(summary) > 280 else summary,
                    "published": entry.get("published", "未知"),
                    "source": name
                })
        except:
            pass
    return all_news

news_list = fetch_news()

# 去重并显示
seen = set()
for i, news in enumerate(news_list, 1):
    if news["title"] not in seen and i <= 20:
        seen.add(news["title"])
        with st.expander(f"{i}. {news['title'][:80]}...", expanded=False):
            st.markdown(f"**来源**：{news['source']} | **时间**：{news['published']}")
            st.write(news['summary'])
            st.markdown(f"[阅读全文]({news['link']})")

st.caption("数据来自公开 RSS • 刷新页面可更新")
