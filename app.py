import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
import re
from deep_translator import GoogleTranslator 

st.set_page_config(page_title="每日全球财经简报", layout="wide", page_icon="📈")

st.title("📈 每日全球经济与宏观新闻简报")
st.markdown(f"**⏰ 今日更新时间：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")

# 🛠 换成绝对稳定且完全免费的国内外权威新闻源
DOMESTIC_FEEDS = {
    "中国政府网-经济要闻": "https://www.gov.cn/rss/zhengce.xml", # 国务院宏观政策，绝对稳定不封锁
    "环球网-财经快讯": "https://finance.huanqiu.com/api/rss"     # 环球网财经，内容完全公开
}

FOREIGN_FEEDS = {
    "路透社-全球宏观经济": "https://www.reutersagency.com/feed/?best-types=global-economy&post_type=best", # 国际通讯社，信息极全且无付费墙
    "联合早报-国际财经": "https://www.zaobao.com/external/rss/finance/global" # 全中文，直接提供无限制的海外财经视野
}

def translate_to_chinese(text):
    if not text or text.strip() == "":
        return ""
    try:
        # 清理可能导致翻译报错的特殊 HTML 标签
        clean_text = re.sub(r'<[^>]+>', '', text)
        translated = GoogleTranslator(source='auto', target='zh-CN').translate(clean_text)
        return translated
    except Exception:
        return text

@st.cache_data(ttl=1800)
def fetch_and_process_rss(feeds_dict, max_items_per_feed=3, is_foreign=False):
    news_list = []
    # 模拟真实浏览器，防止有些服务器拦截
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for name, url in feeds_dict.items():
        try:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code != 200:
                continue
            
            # 解决中文乱码问题
            response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'
            
            root = ET.fromstring(response.content)
            count = 0
            
            for item in root.findall('.//item'):
                if count >= max_items_per_feed:
                    break
                    
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                desc = item.find('description').text if item.find('description') is not None else ''
                
                # 清洗描述文本中的 HTML 标签
                if desc:
                    desc = re.sub(r'<[^>]+>', '', desc).strip()
                    desc = desc[:250] # 截取足够长的摘要
                
                if not title:
                    continue
                    
                if is_foreign:
                    with st.spinner(f"正在智能翻译海外头条: {title[:15]}..."):
                        title_translated = translate_to_chinese(title)
                        desc_translated = translate_to_chinese(desc) if desc else "点击链接可阅读外媒完整内文。"
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
                        "summary": desc if desc else "点击下方链接直接阅读国内新闻原文。",
                        "source": name
                    })
                count += 1
        except Exception:
            continue
            
    return news_list

# 4. 抓取与组合
with st.spinner("🚀 正在为您穿透网络屏障，捕捉全球宏观经济动态..."):
    domestic_news = fetch_and_process_rss(DOMESTIC_FEEDS, max_items_per_feed=3, is_foreign=False)[:5]
    foreign_news = fetch_and_process_rss(FOREIGN_FEEDS, max_items_per_feed=3, is_foreign=True)[:5]

# 5. 双栏排版
col1, col2 = st.columns(2)

with col1:
    st.subheader("🇨🇳 国内宏观经济要闻 (5条)")
    if domestic_news:
        for idx, news in enumerate(domestic_news, 1):
            with st.expander(f"{idx}. {news['title']}", expanded=True):
                st.caption(f"来源：{news['source']}")
                st.write(news['summary'])
                if news['link']:
                    st.markdown(f"[🔗 阅读全文]({news['link']})")
    else:
        st.info("💡 暂未捕获到国内财经更新，请尝试点击右上角 R 键强制刷新。")

with col2:
    st.subheader("🌐 国际财经开放视界 (5条)")
    if foreign_news:
        for idx, news in enumerate(foreign_news, 1):
            with st.expander(f"{idx}. {news['title']}", expanded=True):
                st.caption(f"来源：{news['source']} | 英文原题：*{news['original_title']}*")
                st.write(news['summary'])
                if news['link']:
                    st.markdown(f"[🔗 免费外媒原文]({news['link']})")
    else:
        st.info("💡 暂未捕获到国际财经更新，请稍后刷新重试。")

st.markdown("---")
st.caption("💡 提示：本页面每天全自动实时过滤、聚合、翻译，彻底告别媒体付费墙干扰。")
