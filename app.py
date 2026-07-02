import streamlit as st
import requests
import datetime
from deep_translator import GoogleTranslator 

st.set_page_config(page_title="全球宏观财经简报", layout="wide", page_icon="📈")

st.title("📈 每日全球经济与宏观新闻简报")
st.markdown(f"**⏰ 今日更新时间：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")

def translate_to_chinese(text):
    if not text or text.strip() == "":
        return ""
    try:
        translated = GoogleTranslator(source='auto', target='zh-CN').translate(text)
        return translated
    except Exception:
        return text

# 核心函数：直接调用大厂最稳定的手机端财经快讯接口
@st.cache_data(ttl=600) # 缓存10分钟
def get_global_finance_news():
    domestic = []
    foreign = []
    
    # 新浪财经手机端高频快讯 API（涵盖国内外宏观、外汇、商品、政策）
    url = "https://feed.mix.sina.com.cn/api/roll/get?page_id=155&lid=1686&num=30"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("result", {}).get("data", [])
            
            for item in items:
                title = item.get("title", "")
                summary = item.get("summary", "") or item.get("intro", "")
                link = item.get("url", "")
                
                # 简单的关键词过滤逻辑，把包含美联储、非农、欧美、国际、美股等归为国外
                is_intl = any(k in title or k in summary for k in ["美联储", "美国", "拜登", "欧洲", "央行", "国际", "美股", "日元", "欧元", "外汇", "海外"])
                
                if is_intl and len(foreign) < 5:
                    # 如果原本包含部分英文，或者为了确保翻译逻辑运行
                    if any(ord(c) < 128 for c in title[:10]): # 含有英文
                        with st.spinner("正在翻译海外宏观讯息..."):
                            title = translate_to_chinese(title)
                            summary = translate_to_chinese(summary)
                    
                    foreign.append({
                        "title": f"[国际宏观] {title}",
                        "summary": summary if summary else "点击链接查看完整快讯详情。",
                        "link": link,
                        "source": "新浪财经国际"
                    })
                elif not is_intl and len(domestic) < 5:
                    domestic.append({
                        "title": title,
                        "summary": summary if summary else "点击链接查看完整快讯详情。",
                        "link": link,
                        "source": "新浪财经国内"
                    })
                    
                if len(domestic) >= 5 and len(foreign) >= 5:
                    break
    except Exception as e:
        st.error(f"数据加载异常，请稍后刷新。")
        
    return domestic, foreign

# 抓取数据
with st.spinner("🚀 正在接入全天候财经快讯流..."):
    domestic_news, foreign_news = get_global_finance_news()

# 双栏排版
col1, col2 = st.columns(2)

with col1:
    st.subheader("🇨🇳 国内宏观经济 (5条)")
    if domestic_news:
        for idx, news in enumerate(domestic_news, 1):
            with st.expander(f"{idx}. {news['title']}", expanded=True):
                st.caption(f"来源：{news['source']}")
                st.write(news['summary'])
                if news['link']:
                    st.markdown(f"[🔗 阅读全文]({news['link']})")
    else:
        st.info("💡 正在等待国内财经流更新...")

with col2:
    st.subheader("🌐 国际财经视野 (5条)")
    if foreign_news:
        for idx, news in enumerate(foreign_news, 1):
            with st.expander(f"{idx}. {news['title']}", expanded=True):
                st.caption(f"来源：{news['source']}")
                st.write(news['summary'])
                if news['link']:
                    st.markdown(f"[🔗 阅读全文]({news['link']})")
    else:
        st.info("💡 正在等待国际财经流更新...")

st.markdown("---")
st.caption("💡 提示：本页面采用全天候极速滚动快讯接口，彻底避开了传统 RSS 容易失效的弊端。")
