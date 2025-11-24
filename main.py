import streamlit as st
from scrape import scrape_webiste, split_dom_content, clean_body_content, extract_body_content
from parse import parse_with_external_ai
import time

# Page config
st.set_page_config(
    page_title="AI Web Crawler",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "dom_content" not in st.session_state:
    st.session_state.dom_content = None
if "parsed_result" not in st.session_state:
    st.session_state.parsed_result = None
if "scrape_status" not in st.session_state:
    st.session_state.scrape_status = None

# Theme colors
themes = {
    "dark": {
        "bg": "#0f0f1a",
        "card": "#1a1a2e",
        "card_hover": "#252542",
        "text": "#e4e4e7",
        "text_muted": "#a1a1aa",
        "primary": "#8b5cf6",
        "primary_hover": "#a78bfa",
        "accent": "#06b6d4",
        "border": "#2d2d44",
        "success": "#10b981",
        "input_bg": "#252542",
    },
}

t = themes[st.session_state.theme]

# CSS Styles
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background: {t['bg']};
    }}
    
    /* Hide default elements */
    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{
        padding: 2rem 3rem !important;
        max-width: 1200px;
    }}
    
    /* Header */
    .header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 1px solid {t['border']};
        margin-bottom: 2rem;
    }}
    
    .logo {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom:10px;
    }}
    
    .logo-icon {{
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, {t['primary']} 0%, {t['accent']} 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }}
    
    .logo-text {{
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, {t['primary']} 0%, {t['accent']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Theme Toggle (currently not used) */
    .theme-toggle {{
        position: relative;
        width: 60px;
        height: 30px;
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .toggle-slider {{
        position: absolute;
        top: 3px;
        left: 3px;
        width: 22px;
        height: 22px;
        background: linear-gradient(135deg, {t['primary']} 0%, {t['accent']} 100%);
        border-radius: 50%;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }}
    
    /* Cards */
    .card {{
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }}
    
    .card:hover {{
        border-color: {t['primary']}40;
        box-shadow: 0 8px 32px {t['primary']}10;
    }}
    
    .card-title {{
        color: {t['text']};
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    
    .card-icon {{
        width: 32px;
        height: 32px;
        background: {t['primary']}20;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    /* Input styling */
    .stTextInput > div > div > input {{
        background: {t['input_bg']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 12px !important;
        color: {t['text']} !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {t['primary']} !important;
        box-shadow: 0 0 0 3px {t['primary']}30 !important;
    }}
    
    .stTextInput > div > div > input::placeholder {{
        color: {t['text_muted']} !important;
    }}
    
    .stTextArea > div > div > textarea {{
        background: {t['input_bg']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 12px !important;
        color: {t['text']} !important;
        font-size: 0.95rem !important;
    }}
    
    .stTextArea > div > div > textarea:focus {{
        border-color: {t['primary']} !important;
        box-shadow: 0 0 0 3px {t['primary']}30 !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {t['primary']} 0%, {t['accent']} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px {t['primary']}40 !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px {t['primary']}50 !important;
    }}
    
    .stDownloadButton > button {{
        background: {t['success']} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }}
    
    .stDownloadButton > button:hover {{
        background: {t['success']}dd !important;
        transform: translateY(-2px) !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background: {t['input_bg']} !important;
        border-radius: 12px !important;
        color: {t['text']} !important;
        font-weight: 500 !important;
    }}
    
    .streamlit-expanderContent {{
        background: {t['card']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 0 0 12px 12px !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }}
    .streamlit-expanderContent .stTextArea > div > div > textarea {{
        background: {t['card']} !important;
        color: {t['text']} !important;
        font-size: 0.9rem !important;
        border-radius: 8px !important;
    }}
    
    /* Status indicators */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }}
    
    .status-success {{
        background: {t['success']}20;
        color: {t['success']};
    }}
    
    .status-pending {{
        background: {t['primary']}20;
        color: {t['primary']};
    }}
    
    /* Stats */
    .stats-container {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }}
    
    .stat-card {{
        background: {t['input_bg']};
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }}
    
    .stat-value {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {t['primary']};
    }}
    
    .stat-label {{
        font-size: 0.8rem;
        color: {t['text_muted']};
        margin-top: 4px;
    }}
    
    /* Result card */
    .result-card {{
        background: {t['input_bg']};
        border-radius: 12px;
        padding: 0.5rem 0.75rem;
        color: {t['text']};
        font-size: 0.95rem;
        line-height: 1.3;
        white-space: normal;
        max-height: 400px;
        overflow-y: auto;
    }}
    .result-card table {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        border-collapse: collapse;
        width: 100%;
    }}

    .result-card th, .result-card td {{
        padding: 4px 6px;
    }}

    .result-card p:first-child {{
        margin-top: 0 !important;
    }}

    .result-card p:last-child {{
        margin-bottom: 0 !important;
    }}
 
    /* Labels */
    .stTextInput label, .stTextArea label {{
        color: {t['text']} !important;
        font-weight: 500 !important;
    }}
    
    /* Spinner */
    .stSpinner > div {{
        border-color: {t['primary']} transparent transparent transparent !important;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: {t['text_muted']};
        font-size: 0.85rem;
        border-top: 1px solid {t['border']};
        margin-top: 2rem;
    }}
    
    /* Animations */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    .pulse {{
        animation: pulse 2s infinite;
    }}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {t['bg']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {t['border']};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {t['text_muted']};
    }}
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([6, 1])

with col1:
    st.markdown(f"""
    <div class="logo">
        <div class="logo-icon">🕷️</div>
        <span class="logo-text">AI Web Crawler</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<p style="color: {t['text_muted']}; margin-top: -0.5rem; margin-bottom: 2rem;">
    Extract and analyze web content with AI-powered intelligence
</p>
""", unsafe_allow_html=True)

# Main content
col_main, col_side = st.columns([2, 1])

with col_main:
    # URL Input Card
    st.markdown(f"""
    <div class="card">
        <div class="card-title">
            <div class="card-icon">🔗</div>
            Enter Website URL below
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    url = st.text_input(
        "URL",
        placeholder="https://example.com",
        label_visibility="collapsed"
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        scrape_clicked = st.button("🚀 Scrape Site", use_container_width=True)
    
    with col_btn2:
        if st.session_state.dom_content:
            st.download_button(
                "📥 Download DOM",
                st.session_state.dom_content,
                file_name="scraped_content.txt",
                mime="text/plain",
                use_container_width=True
            )

    # Scraping logic
    # Scraping logic
if scrape_clicked and url:
    with st.spinner("🔄 Scraping website (this may take a while for protected sites)..."):
        try:
            result = scrape_webiste(url)
            body_content = extract_body_content(result)
            cleaned_content = clean_body_content(body_content)
            
            # Check if we got blocked or got limited content
            if len(cleaned_content.strip()) < 500:
                st.warning("⚠️ Limited content retrieved - site may have anti-bot protection")
            elif any(blocked_indicator in cleaned_content.lower() for blocked_indicator in ['cloudflare', 'enable javascript', 'verification', 'security check', 'please complete the security check']):
                st.warning("⚠️ Website has anti-bot protection. Content may be limited.")
            
            st.session_state.dom_content = cleaned_content
            st.session_state.scrape_status = "success"
            st.success("✅ Website scraped successfully!")
            
        except Exception as e:
            st.session_state.scrape_status = "error"
            error_msg = str(e)
            if "cloudflare" in error_msg.lower() or "challenge" in error_msg.lower() or "bot" in error_msg.lower():
                st.error("❌ Website blocked the request with anti-bot protection")
                st.info("💡 Try a different website or check if the site allows scraping")
            else:
                st.error(f"❌ Error: {error_msg}")
    # DOM Content Display
    if st.session_state.dom_content:
        st.markdown(f"""
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-title">
                <div class="card-icon">📄</div>
                Scraped Content
                <span class="status-badge status-success">✓ Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats
        content = st.session_state.dom_content
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-value">{len(content):,}</div>
                <div class="stat-label">Characters</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(content.split()):,}</div>
                <div class="stat-label">Words</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(content.splitlines()):,}</div>
                <div class="stat-label">Lines</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("👁️ View DOM Content", expanded=False):
            st.text_area("content", content, height=300, label_visibility="collapsed")

    # ======================
    # Parse Section with Model Dropdown
    # ======================
    if st.session_state.dom_content:
        st.markdown(f"""
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-title">
                <div class="card-icon">🤖</div>
                AI Parser
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Groq Free Tier Models + Limits
        groq_models_info = {
        "groq/compound": {"RPM":30,"RPD":250,"TPM":70000,"TPD":None},
        "groq/compound-mini": {"RPM":30,"RPD":250,"TPM":70000,"TPD":None},
        "llama-3.1-8b-instant": {"RPM":30,"RPD":14400,"TPM":6000,"TPD":500000},
        "llama-3.3-70b-versatile": {"RPM":30,"RPD":1000,"TPM":12000,"TPD":100000},
        "meta-llama/llama-4-maverick-17b-128e-instruct": {"RPM":30,"RPD":1000,"TPM":6000,"TPD":500000},
        "meta-llama/llama-4-scout-17b-16e-instruct": {"RPM":30,"RPD":1000,"TPM":30000,"TPD":500000},
        "meta-llama/llama-guard-4-12b": {"RPM":30,"RPD":14400,"TPM":15000,"TPD":500000},
        "meta-llama/llama-prompt-guard-2-22m": {"RPM":30,"RPD":14400,"TPM":15000,"TPD":500000},
        "meta-llama/llama-prompt-guard-2-86m": {"RPM":30,"RPD":14400,"TPM":15000,"TPD":500000},
        "moonshotai/kimi-k2-instruct": {"RPM":60,"RPD":1000,"TPM":10000,"TPD":300000},
        "moonshotai/kimi-k2-instruct-0905": {"RPM":60,"RPD":1000,"TPM":10000,"TPD":300000},
        "openai/gpt-oss-120b": {"RPM":30,"RPD":1000,"TPM":8000,"TPD":200000},
        "openai/gpt-oss-20b": {"RPM":30,"RPD":1000,"TPM":8000,"TPD":200000},
        "openai/gpt-oss-safeguard-20b": {"RPM":30,"RPD":1000,"TPM":8000,"TPD":200000},
        "qwen/qwen3-32b": {"RPM":60,"RPD":1000,"TPM":6000,"TPD":500000},
    }

        model_names = list(groq_models_info.keys())

        selected_model = st.selectbox(
            "Choose AI Model (Groq Free Tier)",
            model_names,
            index=model_names.index("llama-3.1-8b-instant") if "llama-3.1-8b-instant" in model_names else 0,
            help="Pick which Groq model you want the parser to use."
        )

        limits = groq_models_info[selected_model]
        rpm = limits.get("RPM")
        rpd = limits.get("RPD")
        tpm = limits.get("TPM")
        tpd = limits.get("TPD")
        ash = limits.get("ASH")
        asd = limits.get("ASD")

        st.markdown(f"""
        <div class="card" style="margin-top: 0.5rem; margin-bottom: 0.5rem;">
            <div class="card-title" style="font-size:0.95rem;">
                <div class="card-icon">📊</div>
                Free Tier Limits for <code style="font-size:0.8rem;">{selected_model}</code>
            </div>
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-value">{rpm}</div>
                    <div class="stat-label">RPM (Requests / min)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{rpd}</div>
                    <div class="stat-label">RPD (Requests / day)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{tpm if tpm is not None else '-'}</div>
                    <div class="stat-label">TPM (Tokens / min)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        extra_limits = []
        if tpd is not None:
            extra_limits.append(f"<b>TPD</b>: {tpd} tokens/day")
        if ash is not None:
            extra_limits.append(f"<b>ASH</b>: {ash} sec/hour")
        if asd is not None:
            extra_limits.append(f"<b>ASD</b>: {asd} sec/day")

        if extra_limits:
            st.markdown(
                f"<p style='color:{t['text_muted']}; font-size:0.8rem; margin-top:-0.5rem;'>"
                + " | ".join(extra_limits) +
                "</p>",
                unsafe_allow_html=True
            )

        parse_description = st.text_area(
            "What would you like to extract?",
            placeholder="e.g., Extract all product names and prices as a markdown table with columns Item Name and Price...",
            height=100
        )
        
        col_parse1, col_parse2, col_parse3 = st.columns([1, 1, 2])
        
        with col_parse1:
            parse_clicked = st.button("✨ Parse Content", use_container_width=True)
        
        with col_parse2:
            if st.session_state.parsed_result:
                st.download_button(
                    "📥 Download Result",
                    st.session_state.parsed_result,
                    file_name="parsed_result.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        if parse_clicked and parse_description:
            with st.spinner(f"🧠 AI ({selected_model}) is analyzing content..."):
                try:
                    dom_chunks = split_dom_content(st.session_state.dom_content)
                    result = parse_with_external_ai(dom_chunks, parse_description, selected_model)
                    st.session_state.parsed_result = result
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.parsed_result:
            st.markdown(f"""
            <div class="card" style="margin-top: 1rem;">
                <div class="card-title">
                    <div class="card-icon">📊</div>
                    Parsed Results
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Let Streamlit render markdown tables nicely
            st.markdown(st.session_state.parsed_result)

with col_side:
    # Info Card
    st.markdown(f"""
    <div class="card">
        <div class="card-title">
            <div class="card-icon">💡</div>
            How it works
        </div>
        <div style="color: {t['text_muted']}; font-size: 0.9rem; line-height: 1.7;">
            <p><strong style="color: {t['text']};">1. Enter URL</strong><br>
            Paste the website URL you want to scrape</p>
            <p><strong style="color: {t['text']};">2. Scrape</strong><br>
            Click to extract the DOM content</p>
            <p><strong style="color: {t['text']};">3. Parse with AI</strong><br>
            Describe what data you need</p>
            <p><strong style="color: {t['text']};">4. Download</strong><br>
            Save your results locally</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tips Card
    st.markdown(f"""
    <div class="card">
        <div class="card-title">
            <div class="card-icon">⚡</div>
            Pro Tips
        </div>
        <div style="color: {t['text_muted']}; font-size: 0.85rem; line-height: 1.7;">
            <p>• Be specific with your parsing instructions</p>
            <p>• Use keywords like "extract", "find", "list"</p>
            <p>• Specify the format you want (JSON, list, table)</p>
            <p>• Include examples if possible</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="footer">
    <p>Built by Pavithra </p>
    <p style="font-size: 0.75rem; margin-top: 0.5rem;">
        Connect with me 
        <a href="https://www.linkedin.com/in/pavithra-m-b557002bb/" target="_blank" style="color:#60a5fa; text-decoration:none;">
            on LinkedIn
        </a>
    </p>
</div>
""", unsafe_allow_html=True)

