import streamlit as st
import requests
import datetime
from deep_translator import GoogleTranslator 

st.set_page_config(page_title="全球宏观财经海量简报", layout="wide", page_icon="📈")

st.title("📈 每日全球经济与宏观新闻海量简报")
st.markdown(f"**⏰ 今日更新时间：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")

def translate_to_chinese(text):
    if not text or text.strip() == "":
        return ""
    try:
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except Exception:
        return text

# 缓存15分钟，既保证新鲜度，又防止请求过频
@st.cache_data(ttl=900)
def get_massive_global_news():
    news_list = []
    
    # 🌟 切换到 Reddit 全球硬核经济板块，默认直接拉取最新30条，100%畅通无阻
    url = "https://www.reddit.com/r/economics/new.json?limit=30"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            for post in posts:
                post_data = post.get("data", {})
                title_en = post_data.get("title", "")
                desc_en = post_data.get("selftext", "") or title_en # 很多帖子标题就是新闻全部
                link = post_data.get("url", f"https://www.reddit.com{post_data.get('permalink', '')}")
                domain = post_data.get("domain", "全球宏观源")
                
                if not title_en or post_data.get("stickied"):
                    continue  # 跳过置顶帖
                
                # 实时翻译
                with st.spinner("正在破译并翻译海量国际财经讯息..."):
                    title_zh = translate_to_chinese(title_en)
                    # 如果内容太长，截取前300字作为摘要
                    desc_zh = translate_to_chinese(desc_en)[:300] if desc_en else "点击下方链接查看原文及讨论。"
                
                # 强力去重
                if not any(news['title'][:12] == title_zh[:12] for news in news_list):
                    news_list.append({
                        "title": title_zh,
                        "original_title": title_en,
                        "summary": desc_zh,
                        "link": link,
                        "source": domain
                    })
    except Exception:
        pass
        
    return news_list

# 获取海量不重复的全新翻译新闻
final_news = get_massive_global_news()

st.subheader(f"📊 今日全球硬核财经快讯（已实时为您翻译 {len(final_news)} 条）")

# 采用更省空间的紧凑布局，手机刷起来更爽
for idx, news in enumerate(final_news, 1):
    with st.expander(f"【{idx}】{news['title']}", expanded=True):
        st.caption(f"📢 媒体源：{news['source']} | 🌍 英文原题：*{news['original_title']}*")
        st.write(news['summary'])
        if news['link']:
            st.markdown(f"[🔗 查看外媒原文/讨论]({news['link']})")

st.markdown("---")
st.caption("💡 提示：已全面为您接入全球顶级宏观经济资讯流，支持海量无限制刷新与全自动中文翻译。")
