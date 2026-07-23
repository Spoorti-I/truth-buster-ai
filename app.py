import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import time
import json
from datetime import datetime

from detector import FakeNewsDetector
from image_forensics import ImageForensicsAnalyzer
from scraper import ArticleScraper

# Page Configuration
st.set_page_config(
    page_title="Truth Buster AI",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════ PREMIUM DARK GLASSMORPHISM CSS ═══════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

    /* ─── Core Dark Theme ─── */
    .stApp {
        background: linear-gradient(160deg, #0a0c12 0%, #111520 40%, #0d1017 100%);
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ─── Sidebar ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #11141d 0%, #0d1017 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #ffffff; font-weight: 800; letter-spacing: -0.03em;
    }

    /* ─── Custom Headers ─── */
    h1 { color: #ffffff !important; font-size: 2.6rem !important; font-weight: 900 !important; letter-spacing: -0.03em !important; }
    h2 { color: #e2e8f0 !important; font-weight: 700 !important; }
    h3 { color: #cbd5e1 !important; font-weight: 600 !important; }

    /* ─── Glassmorphism Cards ─── */
    .glass-card {
        background: rgba(17, 20, 30, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 40px rgba(99, 102, 241, 0.08);
        transform: translateY(-2px);
    }

    /* ─── Metric Cards ─── */
    .metric-card-v2 {
        background: linear-gradient(135deg, rgba(17, 20, 30, 0.8), rgba(25, 30, 45, 0.6));
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .metric-card-v2::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 14px 14px 0 0;
    }
    .metric-card-v2:hover { transform: translateY(-3px); border-color: rgba(255,255,255,0.12); }
    .metric-card-v2 .mc-icon  { font-size: 1.5rem; margin-bottom: 4px; }
    .metric-card-v2 .mc-label { color: #94a3b8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-card-v2 .mc-val   { font-size: 2rem; font-weight: 800; margin: 4px 0; font-family: 'JetBrains Mono', monospace; }

    /* ─── Pipeline / Stage Indicators ─── */
    .pipeline-container { display: flex; gap: 6px; margin: 1rem 0 1.5rem; }
    .pipeline-step {
        flex: 1;
        text-align: center;
        padding: 10px 6px;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        transition: all 0.4s ease;
    }
    .pipeline-active  { background: rgba(99, 102, 241, 0.25); border: 1px solid rgba(99, 102, 241, 0.5); color: #a5b4fc; }
    .pipeline-done    { background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); color: #86efac; }
    .pipeline-waiting { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); color: #64748b; }

    /* ─── Flag / Finding Items ─── */
    .finding-item {
        display: flex; align-items: flex-start; gap: 10px;
        background: rgba(15, 18, 28, 0.6);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 3px solid;
        font-size: 0.92rem;
        transition: background 0.2s;
    }
    .finding-item:hover { background: rgba(20, 24, 38, 0.8); }
    .finding-danger  { border-color: #ef4444; }
    .finding-warning { border-color: #f59e0b; }
    .finding-success { border-color: #22c55e; }
    .finding-info    { border-color: #6366f1; }

    /* ─── Inputs ─── */
    .stTextArea textarea, .stTextInput input {
        background: rgba(15, 18, 28, 0.8) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15) !important;
    }

    /* ─── File Uploader ─── */
    [data-testid="stFileUploader"] {
        background: rgba(15, 18, 28, 0.5);
        border: 2px dashed rgba(99, 102, 241, 0.2);
        border-radius: 14px;
        padding: 1rem;
    }

    /* ─── 🔥 BUST THIS NEWS! Button ─── */
    div.stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 50%, #b91c1c 100%) !important;
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        padding: 1rem 2rem !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 6px 25px rgba(239, 68, 68, 0.35), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow: 0 10px 35px rgba(239, 68, 68, 0.5), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    }
    div.stButton > button:active { transform: translateY(0) scale(0.99) !important; }

    /* ─── Verdict Banner ─── */
    .verdict-banner {
        text-align: center;
        padding: 18px 24px;
        border-radius: 14px;
        font-weight: 800;
        font-size: 1.15rem;
        letter-spacing: 0.04em;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }

    /* ─── History Item ─── */
    .history-item {
        background: rgba(15, 18, 28, 0.5);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        font-size: 0.82rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s;
    }
    .history-item:hover { border-color: rgba(99, 102, 241, 0.25); }

    /* ─── Animated Separator ─── */
    .glow-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), rgba(236,72,153,0.3), transparent);
        margin: 1.5rem 0;
        border-radius: 2px;
    }

    /* ─── Tabs & Expanders ─── */
    .stTabs [data-baseweb="tab-list"] { background: transparent; gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(15, 18, 28, 0.6) !important;
        border-radius: 10px !important;
        color: #94a3b8 !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.15) !important;
        color: #a5b4fc !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ═══════════════ Initialize Engines ═══════════════
detector = FakeNewsDetector()
forensics = ImageForensicsAnalyzer()
scraper = ArticleScraper()

# Session State
if "history" not in st.session_state:
    st.session_state.history = []

# ═══════════════ SIDEBAR ═══════════════
st.sidebar.markdown("## 🕵️ Mode Selection")
st.sidebar.caption("Choose Input Type:")
input_type = st.sidebar.radio(
    "Input Mode",
    options=["Raw Text", "Article Link (URL)"],
    index=0,
    label_visibility="collapsed"
)

st.sidebar.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)
st.sidebar.markdown("### ⚡ Quick Test Samples")
sample_choice = st.sidebar.selectbox(
    "Load preset:",
    ["-- None --", "🚨 Fake: Miracle Cure Hoax", "✅ Real: NASA Artemis (Reuters)", "⚠️ Clickbait: Viral Headline"],
    label_visibility="collapsed"
)

sample_texts = {
    "🚨 Fake: Miracle Cure Hoax": "SHOCKING SECRET! Doctors hate this 100% natural miracle cure that ELIMINATES diabetes in 24 HOURS! Banned by big pharma, unbelievable discovery they don't want you to know! Share before it's deleted!!!",
    "✅ Real: NASA Artemis (Reuters)": "REUTERS - NASA announced today that the Artemis III lunar mission has completed its flight readiness review. Space agency officials confirmed the launch timeline remains on schedule for Q1 next year following rigorous telemetry testing and payload integration. \"We are confident in the readiness of the launch vehicle,\" said the mission director.",
    "⚠️ Clickbait: Viral Headline": "You Won't Believe What This Celebrity Did Yesterday! Number 4 Will Absolutely Blow Your Mind! Experts are SHOCKED and everyone is talking about it!"
}

st.sidebar.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)

# Analysis History
st.sidebar.markdown("### 📜 Recent Analyses")
if st.session_state.history:
    for idx, h in enumerate(reversed(st.session_state.history[-5:])):
        color = h.get("badge_color", "#ffc107")
        st.sidebar.markdown(f"""
        <div class="history-item">
            <span style="color: #cbd5e1; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block;">{h['preview']}</span>
            <span style="color: {color}; font-weight: 800; font-family: 'JetBrains Mono', monospace;">{h['score']}%</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.sidebar.caption("No analyses performed yet.")

st.sidebar.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)
st.sidebar.markdown("### 🧬 Engine")
st.sidebar.caption("NLP Linguistic v3.2 • ELA Forensic v2 • Source Index v1.5")
st.sidebar.caption(f"Session @ {datetime.now().strftime('%H:%M:%S')}")

# ═══════════════ MAIN HEADER ═══════════════
col_h1, col_h2 = st.columns([3, 1])

with col_h1:
    st.markdown("""
    <div style="margin-bottom: 0;">
        <h1 style="margin-bottom: 4px !important;">🕵️ Truth Buster AI</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.3rem; font-weight: 700; background: linear-gradient(135deg, #ef4444, #ec4899, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px;">
        Spot the Fake. Uncover the Truth. Zero Hassle. 🚀
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="color: #94a3b8; font-size: 1rem; margin-bottom: 1.5rem;">
        Paste an article, a news URL, or upload media to calculate its exact <span style="color: #a5b4fc; font-weight: 700;">Truth Percentage!</span>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown("""
    <div style="text-align: right; padding-top: 8px;">
        <div style="display: inline-block; background: linear-gradient(135deg, #1e1b4b, #312e81); border: 2px solid rgba(99, 102, 241, 0.5); border-radius: 50%; width: 85px; height: 85px; line-height: 85px; text-align: center; font-size: 40px; box-shadow: 0 0 30px rgba(99, 102, 241, 0.3), 0 0 60px rgba(99, 102, 241, 0.1);">
            🔍
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════ INPUT SECTION ═══════════════
col_left, col_right = st.columns([1.5, 1])

article_headline = ""
article_body = ""
scraped_domain = ""

with col_left:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if input_type == "Raw Text":
        st.markdown("""
        <div style="font-weight: 700; font-size: 0.95rem; color: #cbd5e1; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
            <span>📝</span> Paste Headline or Article Body
        </div>
        """, unsafe_allow_html=True)
        default_val = sample_texts.get(sample_choice, "")
        raw_input_text = st.text_area(
            label="input_text",
            value=default_val,
            placeholder="Paste suspicious claims or stories here...",
            height=190,
            label_visibility="collapsed"
        )
        article_body = raw_input_text
    else:
        st.markdown("""
        <div style="font-weight: 700; font-size: 0.95rem; color: #cbd5e1; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
            <span>🔗</span> Paste Article URL
        </div>
        """, unsafe_allow_html=True)
        url_input = st.text_input(
            label="url_input",
            placeholder="https://www.example-news-site.com/article...",
            label_visibility="collapsed"
        )
        if url_input:
            with st.spinner("🔍 Fetching & scraping URL..."):
                scrape_res = scraper.fetch_article(url_input)
                if scrape_res["success"]:
                    st.success(f"Scraped: **{scrape_res['domain']}**")
                    article_headline = scrape_res["headline"]
                    article_body = scrape_res["text"]
                    scraped_domain = scrape_res["domain"]
                    st.info(f"**Headline:** {article_headline[:100]}...")
                else:
                    st.warning(f"⚠️ {scrape_res['error']}")
                    scraped_domain = scrape_res["domain"]
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-weight: 700; font-size: 0.95rem; color: #cbd5e1; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
        <span>🖼️</span> Upload Visual Evidence <span style="color: #64748b; font-weight: 400;">(Optional)</span>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="img_upload",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.caption(f"📁 `{uploaded_file.name}` ({round(uploaded_file.size / 1024, 1)} KB)")
        try:
            img_preview = Image.open(uploaded_file)
            st.image(img_preview, caption="Evidence Preview", use_container_width=True)
        except Exception:
            pass
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ═══════════════ ACTION BUTTON ═══════════════
bust_clicked = st.button("🔥 BUST THIS NEWS!", type="primary", use_container_width=True)

# ═══════════════ ANALYSIS & RESULTS ═══════════════
if bust_clicked:
    if not article_body and not uploaded_file:
        st.error("⚠️ Please paste text, provide a URL, or upload visual evidence to analyze!")
    else:
        # ─── Animated Pipeline Progress ───
        pipeline_placeholder = st.empty()

        stages = [
            ("🔤 NLP Tokenizer", "Tokenizing input & extracting entities..."),
            ("🧠 Linguistic Model", "Running sensationalism & clickbait heuristics..."),
            ("🌐 Source Checker", "Cross-referencing domain authority index..."),
            ("🔬 Visual Forensics", "Analyzing image authenticity (ELA, EXIF)...") if uploaded_file else ("📊 Score Engine", "Computing weighted truth scores..."),
            ("✅ Report Builder", "Generating forensic verification report...")
        ]

        for i, (stage_name, stage_desc) in enumerate(stages):
            steps_html = ""
            for j, (sn, _) in enumerate(stages):
                if j < i:
                    cls = "pipeline-done"
                    icon = "✅"
                elif j == i:
                    cls = "pipeline-active"
                    icon = "⏳"
                else:
                    cls = "pipeline-waiting"
                    icon = "⬜"
                steps_html += f'<div class="pipeline-step {cls}">{icon} {sn}</div>'

            pipeline_placeholder.markdown(f"""
            <div style="margin: 10px 0;">
                <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 6px;">⚡ {stage_desc}</div>
                <div class="pipeline-container">{steps_html}</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.4)

        # Run actual analysis
        text_result = detector.analyze_text(
            text=article_body,
            headline=article_headline,
            domain=scraped_domain
        )

        image_result = None
        if uploaded_file:
            bytes_data = uploaded_file.getvalue()
            image_result = forensics.analyze_image(bytes_data, uploaded_file.name)

        # Mark pipeline complete
        final_steps = ""
        for j, (sn, _) in enumerate(stages):
            final_steps += f'<div class="pipeline-step pipeline-done">✅ {sn}</div>'
        pipeline_placeholder.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="color: #22c55e; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">✅ All analysis stages completed successfully</div>
            <div class="pipeline-container">{final_steps}</div>
        </div>
        """, unsafe_allow_html=True)

        # Overall Truth Score
        overall_truth = text_result["truth_score"]
        if image_result:
            overall_truth = round((text_result["truth_score"] * 0.65) + (image_result["authenticity_score"] * 0.35), 1)

        # Save to history
        preview_text = (article_body or article_headline)[:30] + "..." if (article_body or article_headline) else "Image Only"
        st.session_state.history.append({
            "preview": preview_text,
            "score": overall_truth,
            "badge_color": text_result["badge_color"],
            "time": datetime.now().strftime("%H:%M:%S")
        })

        # ─── Separator ───
        st.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)

        # ═══════════════ RESULTS DASHBOARD ═══════════════
        st.markdown("## 📊 Verification Intelligence Dashboard")

        # ─── Verdict Banner ───
        if overall_truth >= 75:
            banner_bg = "linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(16, 185, 129, 0.1))"
            banner_border = "rgba(34, 197, 94, 0.4)"
            verdict_icon = "🛡️"
        elif overall_truth >= 50:
            banner_bg = "linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(234, 179, 8, 0.1))"
            banner_border = "rgba(245, 158, 11, 0.4)"
            verdict_icon = "⚠️"
        else:
            banner_bg = "linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.1))"
            banner_border = "rgba(239, 68, 68, 0.4)"
            verdict_icon = "🚨"

        st.markdown(f"""
        <div class="verdict-banner" style="background: {banner_bg}; border: 1px solid {banner_border};">
            {verdict_icon} VERDICT: {text_result['status']}
        </div>
        """, unsafe_allow_html=True)

        # ─── Main Score + Radar + Metrics Row ───
        dash_c1, dash_c2, dash_c3 = st.columns([1, 1.2, 1.3])

        with dash_c1:
            # Gauge Chart
            if overall_truth >= 75:
                gauge_colors = ['#22c55e', '#16a34a']
            elif overall_truth >= 50:
                gauge_colors = ['#f59e0b', '#d97706']
            else:
                gauge_colors = ['#ef4444', '#dc2626']

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=overall_truth,
                number={'suffix': "%", 'font': {'color': "#ffffff", 'size': 48, 'family': "JetBrains Mono"}},
                title={'text': "TRUTH SCORE", 'font': {'size': 14, 'color': "#94a3b8", 'family': "Inter"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#334155", 'dtick': 25},
                    'bar': {'color': gauge_colors[0], 'thickness': 0.3},
                    'bgcolor': "rgba(15, 18, 28, 0.6)",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 30], 'color': 'rgba(239, 68, 68, 0.15)'},
                        {'range': [30, 50], 'color': 'rgba(249, 115, 22, 0.1)'},
                        {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                        {'range': [75, 100], 'color': 'rgba(34, 197, 94, 0.1)'}
                    ],
                    'threshold': {
                        'line': {'color': "#ffffff", 'width': 2},
                        'thickness': 0.8,
                        'value': overall_truth
                    }
                }
            ))
            fig_gauge.update_layout(
                height=240, margin=dict(l=20, r=20, t=35, b=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Inter'}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with dash_c2:
            # Radar Chart
            categories = ['Sensationalism', 'Clickbait', 'Syntax Quality', 'Source Trust']
            values = [
                text_result['sensationalism_score'],
                text_result['clickbait_score'],
                text_result['linguistic_score'],
                text_result['source_credibility']
            ]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(99, 102, 241, 0.2)',
                line=dict(color='#6366f1', width=2),
                marker=dict(size=6, color='#a5b4fc')
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.06)', tickfont=dict(color='#64748b', size=9)),
                    angularaxis=dict(gridcolor='rgba(255,255,255,0.06)', tickfont=dict(color='#94a3b8', size=11, family='Inter'))
                ),
                showlegend=False,
                height=260,
                margin=dict(l=40, r=40, t=25, b=25),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with dash_c3:
            # 4 Metric Cards
            metrics = [
                ("🔥", "Sensationalism", text_result['sensationalism_score'], '#ef4444' if text_result['sensationalism_score'] > 50 else '#22c55e'),
                ("🎣", "Clickbait Risk", text_result['clickbait_score'], '#ef4444' if text_result['clickbait_score'] > 40 else '#22c55e'),
                ("📖", "Syntax Quality", text_result['linguistic_score'], '#22c55e' if text_result['linguistic_score'] >= 60 else '#f59e0b'),
                ("🏛️", "Source Trust", text_result['source_credibility'], '#22c55e' if text_result['source_credibility'] >= 70 else '#f59e0b'),
            ]

            mc1, mc2 = st.columns(2)
            for idx, (icon, label, val, color) in enumerate(metrics):
                col = mc1 if idx % 2 == 0 else mc2
                with col:
                    st.markdown(f"""
                    <div class="metric-card-v2" style="margin-bottom: 10px;">
                        <div class="mc-icon">{icon}</div>
                        <div class="mc-label">{label}</div>
                        <div class="mc-val" style="color: {color};">{val}%</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)

        # ═══════════════ DETAILED FINDINGS (Tabs) ═══════════════
        tab_list = ["🔍 Forensic Flags", "📊 Score Breakdown"]
        if image_result:
            tab_list.append("🖼️ Visual Forensics")
        tab_list.append("📥 Export")

        tabs = st.tabs(tab_list)

        # ─── Tab 1: Forensic Flags ───
        with tabs[0]:
            st.markdown("### Key Forensic Flags & Findings")
            for reason in text_result["reasons"]:
                is_danger = any(k in reason.lower() for k in ["trigger", "clickbait", "unreliable", "stripped"])
                is_warning = any(k in reason.lower() for k in ["lacks", "question", "short"])
                if is_danger:
                    cls, icon = "finding-danger", "🚨"
                elif is_warning:
                    cls, icon = "finding-warning", "⚠️"
                else:
                    cls, icon = "finding-success", "✅"
                st.markdown(f'<div class="finding-item {cls}">{icon}&nbsp;&nbsp;{reason}</div>', unsafe_allow_html=True)

        # ─── Tab 2: Score Breakdown ───
        with tabs[1]:
            st.markdown("### Weighted Score Calculation")
            categories_bar = ['Sensationalism (35%)', 'Clickbait (30%)', 'Linguistic (15%)', 'Source (20%)']
            vals_bar = [text_result['sensationalism_score'], text_result['clickbait_score'], text_result['linguistic_score'], text_result['source_credibility']]
            colors_bar = ['#ef4444', '#f59e0b', '#6366f1', '#22c55e']

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=vals_bar, y=categories_bar, orientation='h',
                marker=dict(color=colors_bar, line=dict(width=0)),
                text=[f"{v}%" for v in vals_bar], textposition='auto',
                textfont=dict(color='white', size=13, family='JetBrains Mono')
            ))
            fig_bar.update_layout(
                height=220, margin=dict(l=10, r=20, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, 100], gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#64748b')),
                yaxis=dict(tickfont=dict(color='#cbd5e1', size=12, family='Inter')),
                font=dict(family='Inter')
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # ─── Tab 3: Visual Forensics (if image) ───
        if image_result:
            with tabs[2]:
                st.markdown("### 🔬 Visual Evidence & AI Detection Analysis")
                
                img_c1, img_c2 = st.columns([1, 1.5])
                with img_c1:
                    # Main authenticity card
                    ai_risk = image_result.get('ai_risk_score', 0)
                    ai_risk_color = '#dc3545' if ai_risk > 60 else '#fd7e14' if ai_risk > 35 else '#22c55e'
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 4px solid {image_result['status_color']};">
                        <div style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: 600;">Media Authenticity</div>
                        <div style="font-size: 2.5rem; font-weight: 900; color: {image_result['status_color']}; font-family: 'JetBrains Mono';">{image_result['authenticity_score']}%</div>
                        <div style="color: #cbd5e1; font-weight: 600; margin-top: 4px;">{image_result['status']}</div>
                        <div style="color: #64748b; font-size: 0.85rem; margin-top: 8px;">Resolution: {image_result['resolution']}<br/>Format: {image_result['format']}<br/>ELA Score: {image_result['ela_score']}/100</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # AI Risk Score card
                    st.markdown(f"""
                    <div class="metric-card-v2" style="margin-top: 10px; border-left: 4px solid {ai_risk_color};">
                        <div class="mc-icon">🤖</div>
                        <div class="mc-label">AI Generation Risk</div>
                        <div class="mc-val" style="color: {ai_risk_color};">{ai_risk}%</div>
                    </div>
                    """, unsafe_allow_html=True)

                with img_c2:
                    # New metric cards row
                    vm1, vm2, vm3 = st.columns(3)
                    smoothness = image_result.get('smoothness', 0)
                    noise_uni = image_result.get('noise_uniformity', 0)
                    entropy = image_result.get('entropy', 0)
                    
                    with vm1:
                        sm_color = '#dc3545' if smoothness > 60 else '#22c55e'
                        st.markdown(f"""
                        <div class="metric-card-v2">
                            <div class="mc-icon">✨</div>
                            <div class="mc-label">Smoothness</div>
                            <div class="mc-val" style="color: {sm_color};">{smoothness}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with vm2:
                        nu_color = '#dc3545' if noise_uni > 65 else '#22c55e'
                        st.markdown(f"""
                        <div class="metric-card-v2">
                            <div class="mc-icon">📡</div>
                            <div class="mc-label">Noise Uniform.</div>
                            <div class="mc-val" style="color: {nu_color};">{noise_uni}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with vm3:
                        en_color = '#22c55e' if entropy > 55 else '#dc3545'
                        st.markdown(f"""
                        <div class="metric-card-v2">
                            <div class="mc-icon">🧮</div>
                            <div class="mc-label">Entropy</div>
                            <div class="mc-val" style="color: {en_color};">{entropy}%</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.write("")
                    # Detection flags with proper classification
                    for f in image_result["flags"]:
                        if "🤖" in f:
                            cls = "finding-danger"
                        elif "⚠️" in f:
                            cls = "finding-warning"
                        elif "✅" in f:
                            cls = "finding-success"
                        else:
                            cls = "finding-info"
                        st.markdown(f'<div class="finding-item {cls}">{f}</div>', unsafe_allow_html=True)

        # ─── Tab: Export ───
        with tabs[-1]:
            st.markdown("### 📥 Download Verification Report")
            report_content = f"""TRUTH BUSTER AI - FORENSIC VERIFICATION REPORT
{'='*50}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Target: {scraped_domain or 'Raw Text Input'}

TRUTH SCORE: {overall_truth}%
VERDICT: {text_result['status']}

METRIC BREAKDOWN:
  - Sensationalism Score: {text_result['sensationalism_score']}%
  - Clickbait Risk: {text_result['clickbait_score']}%
  - Linguistic Quality: {text_result['linguistic_score']}%
  - Source Credibility: {text_result['source_credibility']}%

KEY FLAGS:
""" + "\n".join(f"  • {r}" for r in text_result["reasons"])

            if image_result:
                report_content += f"""

VISUAL FORENSICS:
  - Authenticity Score: {image_result['authenticity_score']}%
  - Status: {image_result['status']}
  - Resolution: {image_result['resolution']}
  - ELA Score: {image_result['ela_score']}/100
""" + "\n".join(f"  • {f}" for f in image_result["flags"])

            st.download_button(
                label="📥 Download Full Report (.txt)",
                data=report_content,
                file_name=f"TruthBuster_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

            # JSON export
            export_json = {
                "truth_score": overall_truth,
                "verdict": text_result["status"],
                "sensationalism": text_result["sensationalism_score"],
                "clickbait": text_result["clickbait_score"],
                "linguistic": text_result["linguistic_score"],
                "source": text_result["source_credibility"],
                "flags": text_result["reasons"]
            }
            st.download_button(
                label="📥 Download Structured Data (.json)",
                data=json.dumps(export_json, indent=2),
                file_name=f"TruthBuster_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        # ─── Summary ───
        st.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)
        st.markdown("### 📜 Automated Intelligence Summary")
        assessment = (
            "High levels of sensationalism, clickbait phrasing, or unverified language were detected, indicating significant potential for media manipulation or unverified claim propagation."
            if overall_truth < 60
            else "The text demonstrates consistent neutral reporting style, proper attribution, and absence of overt sensationalist manipulation triggers."
        )
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 8px;">Analysis Summary</div>
            <div style="font-size: 0.95rem; line-height: 1.7; color: #cbd5e1;">
                <b>Target:</b> <code>{scraped_domain or 'Text Input'}</code> &nbsp;•&nbsp;
                <b>Score:</b> <code style="color: {text_result['badge_color']}; font-weight: 800;">{overall_truth}%</code> &nbsp;•&nbsp;
                <b>Verdict:</b> <code>{text_result['status']}</code>
                <br/><br/>
                {assessment}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Footer ───
st.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #475569; font-size: 0.8rem; padding: 0.5rem 0;">
    Truth Buster AI Engine v2.0 • NLP Linguistic + Visual Forensic Multi-Vector Analysis
</div>
""", unsafe_allow_html=True)
