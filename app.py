import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
from urllib.parse import urlparse
# 需要在终端运行: pip install deep_translator
from deep_translator import GoogleTranslator 

st.set_page_config(page_title="每日全球财经简报", layout="wide", page_icon="📈")

# 优雅的 UI 头部
st.title("📈 每日全球经济与宏观新闻简报")
st.markdown(f"**⏰ 今日更新时间：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")

# 1. 重新规划更稳定的 RSS 订阅源
DOMESTIC_FEEDS = {
    "华尔街见闻-快讯": "https://wallstreetcn.com/rss/news",               # 国内极速宏观财经快讯
    "财新网-经济": "https://www.caixin.com/rss/finance_macro.xml",     # 权威宏观经济媒体
    "联合早报-中国财经": "https://www.zaobao.com/external/rss/finance/china" # 全中文，高频率更新中国经济动态
}


FOREIGN_FEEDS = {
    "路透社-宏观经济": "https://www.reutersagency.com/feed/?best-types=global-economy&post_type=best",
    "FT 金融时报": "https://www.ft.com/global-economy?format=rss"
}

# 2. 翻译函数（默认使用免费无需Key的Google翻译，可平替为AI大模型API）
def translate_to_chinese(text):
    if not text or text.strip() == "":
        return ""
    try:
        # 自动识别语言并翻译为中文(简体)
        translated = GoogleTranslator(source='auto', target='zh-CN').translate(text)
        return translated
    except Exception as e:
        return f"[翻译失败]: {text}"

# 3. 核心抓取函数
@st.cache_data(ttl=3600) # 缓存1小时，避免频繁刷新导致被RSS源封IP
def fetch_and_process_rss(feeds_dict, max_items_per_feed=3, is_foreign=False):
    news_list = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for name, url in feeds_dict.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            
            count = 0
            for item in root.findall('.//item'):
                if count >= max_items_per_feed:
                    break
                    
                title = item.find('title').text if item.find('title') is not None else '无标题'
                link = item.find('link').text if item.find('link') is not None else ''
                desc = item.find('description').text if item.find('description') is not None else ''
                
                # 清洗描述文本中的 HTML 标签
                if desc:
                    desc = ET.fromstring(f"<p>{desc}</p>").itertext()
                    desc = "".join(desc)[:200] # 截取前200字摘要
                
                # 如果是国外源，进行翻译
                if is_foreign:
                    with st.spinner(f"正在翻译海外头条: {title[:20]}..."):
                        title_translated = translate_to_chinese(title)
                        desc_translated = translate_to_chinese(desc)
                    news_list.append({
                        "title": f"[海外译讯] {title_translated}",
                        "original_title": title,
                        "link": link,
                        "summary": desc_translated,
                        "source": name
                    })
                else:
                    news_list.append({
                        "title": title,
                        "original_title": "",
                        "link": link,
                        "summary": desc,
                        "source": name
                    })
                count += 1
        except Exception as e:
            # 某个源失败时优雅跳过，不影响整体运行
            continue
            
    return news_list

# 4. 数据加载与精准控量（5条国内 + 5条国外 = 10条）
with st.spinner("正在捕捉全球宏观经济动态..."):
    domestic_news = fetch_and_process_rss(DOMESTIC_FEEDS, max_items_per_feed=3, is_foreign=False)[:5]
    foreign_news = fetch_and_process_rss(FOREIGN_FEEDS, max_items_per_feed=3, is_foreign=True)[:5]
    
    # 合并成每日10条
    final_10_news = domestic_news + foreign_news

# 5. UI 渲染呈现
col1, col2 = st.columns(2)

with col1:
    st.subheader("🇨🇳 国内财经要闻 (5条)")
    if domestic_news:
        for idx, news in enumerate(domestic_news, 1):
            with st.expander(f"{idx}. {news['title']}", expanded=True):
                st.caption(f"来源：{news['source']}")
                st.write(news['summary'] if news['summary'] else "点击查看全文")
                if news['link']:
                    st.markdown(f"[🔗 阅读全文]({news['link']})")
    else:
        st.info("暂未获取到国内新闻，请刷新重试。")

with col2:
    st.subheader("🌐 国际宏观动态 (5条)")
    if foreign_news:
        for idx, news in enumerate(foreign_news, 1):
            with st.expander(f"{idx}. {news['title']}", expanded=True):
                st.caption(f"来源：{news['source']} | 英文原题：*{news['original_title']}*")
                st.write(news['summary'])
                if news['link']:
                    st.markdown(f"[🔗 查看外媒原文]({news['link']})")
    else:
        st.info("暂未获取到国际新闻，可能是网络波动，请刷新重试。")

st.markdown("---")
st.caption("💡 提示：本页面每1小时自动缓存更新，你也可以点击右上角的 R 键强制刷新。")

