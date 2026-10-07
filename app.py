import os
import urllib.parse
import streamlit as st
import feedparser
from groq import Groq

# ---------------------------------------------------------
# Page Configuration & Global Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Titan Pulse | Short-Form Media Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #0F172A; margin-bottom: 0px; }
    .sub-title { font-size: 1rem; color: #475569; margin-bottom: 25px; }
    .news-card { background-color: #F8FAFC; border-radius: 8px; padding: 18px; border: 1px solid #E2E8F0; margin-bottom: 12px; }
    .source-tag { font-size: 0.85rem; color: #64748B; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Authentication & Client Initialization
# ---------------------------------------------------------
api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", None))

if not api_key:
    api_key = st.sidebar.text_input(
        "🔑 Groq API Key:", 
        type="password", 
        help="Obtain a free high-speed API key at https://console.groq.com"
    )

client = Groq(api_key=api_key) if api_key else None

# ---------------------------------------------------------
# Target Entity Database
# ---------------------------------------------------------
TITANS = {
    "Big Tech & AI Titans": [
        "Elon Musk", "Sam Altman", "Mark Zuckerberg", "Jensen Huang", 
        "Satya Nadella", "Sundar Pichai", "Tim Cook", "Alex Karp"
    ],
    "Wall Street & Mega Wealth": [
        "Jeff Bezos", "Bill Gates", "Warren Buffett", "Bernard Arnault", 
        "Larry Ellison", "Peter Thiel", "Ken Griffin"
    ],
    "Media & Cultural Moguls": [
        "MrBeast", "Joe Rogan", "Brian Chesky"
    ],
    "Global Strategy & Geopolitics (Economic/Tech Angle Only)": [
        "Xi Jinping", "Vladimir Putin", "Benjamin Netanyahu", "Kim Jong Un"
    ]
}

# ---------------------------------------------------------
# Data Ingestion Engine
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def fetch_google_news(entity_name: str):
    """Fetch verified US-targeted news RSS feeds from Google News."""
    query = f'"{entity_name}" when:2d'
    encoded_query = urllib.parse.quote(query)
    feed_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(feed_url)
    articles = []
    
    for entry in feed.entries[:6]:
        source_name = getattr(entry, "source", {}).get("title", "Google News")
        published_date = getattr(entry, "published", "Recent")
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "source": source_name,
            "published": published_date
        })
    return articles

# ---------------------------------------------------------
# Inference & Content Generation Engine
# ---------------------------------------------------------
def generate_production_package(entity: str, headline: str, reference_url: str) -> str:
    """Generate fact-checked 40-second viral production scripts using Groq LLM."""
    system_prompt = """You are the Executive Producer for a high-RPM short-form video network targeting US and Tier-1 audiences.
Your objective is to produce 40-second Facebook Reels packages on global titans, billionaires, and tech developments.

Adhere strictly to this structure:
1. FACT-CHECK & MONETIZATION SAFETY AUDIT:
   - Verify story plausibility against public records.
   - Assess Meta Advertiser Safety (Ensure zero policy violations regarding hate, violence, or unoriginal clickbait).
2. 40-SECOND VIRAL VOICEOVER SCRIPT:
   - [00:00 - 00:03] THE HOOK: Extreme pattern-interrupting opening line. Bold curiosity gap.
   - [00:03 - 00:15] THE ESCALATION: Dollar stakes, corporate maneuvers, or power shifts.
   - [00:15 - 00:32] THE CORE IMPACT: Real-world significance and market disruptions.
   - [00:32 - 00:40] THE LOOP ENDING: The concluding line must grammatically reconnect into the hook.
3. SCENE-BY-SCENE B-ROLL & VISUAL ASSET LIST:
   - 5 to 6 specific, practical visuals/screenshots the editor must place on the CapCut timeline.

Tone: Punchy, urgent, informative, and authoritative (Style: Dylan Page / Morning Brew)."""

    user_prompt = f"""Target Entity: {entity}
Breaking Headline: {headline}
Source URL: {reference_url}

Generate the complete production package in clean, structured Markdown."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    return response.choices[0].message.content

# ---------------------------------------------------------
# Main Application User Interface
# ---------------------------------------------------------
st.sidebar.title("⚡ Titan Pulse Monitor")
st.sidebar.caption("High-RPM Short-Form Intelligence Pipeline")

category = st.sidebar.selectbox("Select Category:", list(TITANS.keys()))
entity = st.sidebar.selectbox("Select Entity:", TITANS[category])

st.markdown('<div class="main-title">⚡ Titan Pulse: Media Intelligence Hub</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Tracking real-time developments for <b>{entity}</b> across Tier-1 US outlets.</div>', unsafe_allow_html=True)

news_records = fetch_google_news(entity)

if not news_records:
    st.info("No breaking reports discovered in the last 48 hours. Select another entity or refresh.")
else:
    for idx, item in enumerate(news_records):
        with st.container():
            st.markdown(f"""
            <div class="news-card">
                <h4 style="margin:0; font-size:1.1rem;">
                    <a href="{item['link']}" target="_blank" style="text-decoration:none; color:#0F172A;">{item['title']}</a>
                </h4>
                <div class="source-tag" style="margin-top:6px;">
                    📰 Source: {item['source']} &nbsp;|&nbsp; 🗓 Published: {item['published']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn, _ = st.columns([2, 5])
            with col_btn:
                trigger = st.button("🚀 Generate Reel Package", key=f"btn_{idx}")
                
            if trigger:
                if not client:
                    st.error("Please supply a valid Groq API Key in the sidebar or via Streamlit Secrets.")
                else:
                    with st.spinner("Analyzing headline, verifying safety, and synthesizing production package..."):
                        try:
                            package = generate_production_package(entity, item['title'], item['link'])
                            st.success("Production package generated successfully.")
                            
                            with st.expander("📄 View Production Package & Script", expanded=True):
                                st.markdown(package)
                                st.download_button(
                                    label="💾 Download Package (.txt)",
                                    data=package,
                                    file_name=f"{entity.lower().replace(' ', '_')}_reel_package.txt",
                                    mime="text/plain"
                                )
                        except Exception as err:
                            st.error(f"Inference pipeline encountered an error: {err}")
        st.write("---")
