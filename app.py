import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import plotly.graph_objects as go
import json
import os

# ==========================================
# 0. 页面基础设置与 顶级 SaaS 视觉风格注入
# ==========================================
st.set_page_config(page_title="ES 业务全局看板", page_icon="✨", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    html, body, [class*="css"] { font-family: 'Poppins', 'Segoe UI', sans-serif !important; color: #2D235C !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #F1F5F9 !important; }
    [data-testid="stHeader"] { background-color: transparent !important; }

    .soft-card {
        background-color: #ffffff; border: 1px solid #E2E8F0; border-radius: 28px; padding: 30px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 4px 10px -2px rgba(15, 23, 42, 0.04);
        margin-bottom: 24px; transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .soft-card:hover { transform: translateY(-4px); box-shadow: 0 20px 40px -10px rgba(15, 23, 42, 0.12), 0 10px 15px -5px rgba(15, 23, 42, 0.08); }
    
    .welcome-banner {
        background: linear-gradient(135deg, #FFB000 0%, #FF9000 100%); border-radius: 28px; padding: 32px 40px; color: white; margin-bottom: 30px; box-shadow: 0 16px 32px -10px rgba(255, 160, 0, 0.4); position: relative; overflow: hidden;
    }
    .welcome-banner h1 { color: white !important; font-size: 36px; font-weight: 800; margin: 0 0 8px 0; }
    .welcome-banner p { color: rgba(255,255,255,0.9) !important; font-size: 16px; margin: 0; }
    
    .progress-track { background-color: #F0F1F6; border-radius: 999px; height: 18px; width: 100%; position: relative; }
    .progress-fill-red { background: linear-gradient(90deg, #FF8491 0%, #FF6475 100%); height: 100%; border-radius: 999px; transition: width 0.8s ease; box-shadow: 0 6px 16px -4px rgba(255, 100, 117, 0.6); }
    .progress-fill-blue { background: linear-gradient(90deg, #6BE1F0 0%, #42D2E6 100%); height: 100%; border-radius: 999px; transition: width 0.8s ease; box-shadow: 0 6px 16px -4px rgba(66, 210, 230, 0.6); }
    .rocket-icon { position: absolute; right: -12px; top: -6px; font-size: 22px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.15)); }
    
    .icon-square { display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 16px; margin-right: 16px; font-size: 22px; }
    .icon-small { width: 36px; height: 36px; border-radius: 12px; margin-right: 12px; font-size: 16px; }
    
    .bg-red { background-color: #FFF0F2; color: #FF6475; }
    .bg-blue { background-color: #E8F9FB; color: #42D2E6; }
    .bg-purple { background-color: #F1F0F7; color: #2D235C; }
    .bg-orange { background-color: #FFF6E5; color: #FFB000; }
    .bg-gray { background-color: #F6F8FA; color: #8E8CA7; }
    .bg-green { background-color: #F0FDF4; color: #22C55E; }
    
    .flex-center { display: flex; align-items: center; }

    div[data-testid="stButton"] button { background-color: #ffffff; border: 2px solid #F0F1F6; border-radius: 20px; color: #2D235C; font-weight: 600; padding: 6px 24px; box-shadow: 0 4px 10px rgba(45, 35, 92, 0.03); transition: all 0.3s ease; }
    div[data-testid="stButton"] button:hover { transform: scale(1.03); background-color: #2D235C; border-color: #2D235C; box-shadow: 0 10px 20px -6px rgba(45, 35, 92, 0.4); color: #ffffff; }
    
    .text-main { color: #2D235C !important; }
    .text-muted { color: #8E8CA7 !important; }
    
    .funnel-item { flex: 1; border-right: 2px solid #F0F1F6; padding-left: 20px; }
    .funnel-item:last-child { border-right: none; }
    .funnel-title { color: #8E8CA7; font-size: 13px; font-weight:500; margin: 0 0 8px 0; display: flex; align-items: center; }
    .funnel-dot { font-size: 10px; margin-right: 8px; }
    .funnel-value { color: #2D235C; font-size: 32px; font-weight: 700; margin: 0; display: flex; align-items: baseline;}
    
    .inner-box { padding: 20px 24px; border-radius: 20px; flex: 1; margin-right: 16px; }
    .inner-box:last-child { margin-right: 0; }
    .box-deep { background-color: #2D235C; border: none; color: white;}
    .box-light { background-color: #ffffff; border: 2px solid #F0F1F6; }
    .box-label { font-size: 13px; margin: 0 0 12px 0; display: flex; align-items: center; font-weight:500;}
    .box-value-dark { font-size: 30px; font-weight: 700; color: #2D235C; margin: 0; display: flex; align-items: baseline; justify-content: flex-start; } 
    .box-value-white { font-size: 30px; font-weight: 700; color: #ffffff; margin: 0; }
    .compare-date-str { font-size: 12px; color: #8E8CA7; font-weight: normal; margin-left: 8px; }
    
    .wk-table { width: 100%; border-collapse: collapse; font-family: 'Poppins', 'Segoe UI', sans-serif; background: #fff; border-radius: 12px; overflow: hidden; }
    .wk-table th { background-color: #F8FAFC; padding: 14px 16px; border: 1px solid #E2E8F0; text-align: center; color: #475569; font-weight: 600; font-size: 14px; }
    .wk-table td { padding: 14px 16px; border: 1px solid #E2E8F0; text-align: center; color: #1E293B; font-weight: 500; font-size: 14px; transition: background 0.2s; }
    .wk-table tr:hover td { background-color: #F8FAFC; }
    .wk-table td:first-child { text-align: left; color: #475569; font-weight: 600; background-color: #FAFAFA; width: 25%; }
    .text-green { color: #22C55E !important; }
    .text-red { color: #FF6475 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 0.1 SaaS 级密码保护模块
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_login, _ = st.columns([1.5, 2, 1.5])
    with col_login:
        st.markdown('<div class="soft-card" style="text-align: center; margin-top: 100px;">', unsafe_allow_html=True)
        st.markdown('<div class="icon-square bg-purple" style="margin: 0 auto 16px auto;"><i class="fa-solid fa-lock"></i></div>', unsafe_allow_html=True)
        st.markdown('<h3 class="text-main" style="margin-top: 0;">Restricted Access</h3>', unsafe_allow_html=True)
        st.caption("Please enter the passkey to access the ES Global Dashboard.")
        
        pwd = st.text_input("Passkey", type="password", label_visibility="collapsed", placeholder="Enter Passkey...")
        
        if st.button("Unlock Dashboard", use_container_width=True):
            if pwd == "escalate":
                st.session_state["authenticated"] = True
                st.rerun() 
            else:
                st.error("🔒 Incorrect passkey. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

from plotly.subplots import make_subplots

def hex_to_rgba(hex_color, alpha=0.1):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r}, {g}, {b}, {alpha})'

# ==========================================
# 1. 核心数据统一抓取区
# ==========================================
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4KTuYQtC6xsRIwgWLDK9aJUhqmKDmUg4XmMxbsKadyj4QSRM9GNvDjyYz7z8vzKj8nohA7a8ukiLz/pub?gid=0&single=true&output=csv"
GSC_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTzi-PSTqsbOE_3GmT9xOU-2UNiXhlUYeW118jPq4pFBY3arsMbVtIr1BAMbv5qYL3BFmKqzcb5vBAO/pub?gid=0&single=true&output=csv"
SUPERSET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTzi-PSTqsbOE_3GmT9xOU-2UNiXhlUYeW118jPq4pFBY3arsMbVtIr1BAMbv5qYL3BFmKqzcb5vBAO/pub?gid=1272454464&single=true&output=csv"
AI_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTzi-PSTqsbOE_3GmT9xOU-2UNiXhlUYeW118jPq4pFBY3arsMbVtIr1BAMbv5qYL3BFmKqzcb5vBAO/pub?gid=779297131&single=true&output=csv"

@st.cache_data(ttl=600)
def load_and_clean_data(url):
    bust_url = f"{url}&_t={int(datetime.now().timestamp())}"
    df_raw = pd.read_csv(bust_url, header=None)
    df_es = df_raw.iloc[44:62].copy()
    raw_columns = list(df_raw.iloc[43])
    
    clean_columns = []
    for i, col in enumerate(raw_columns):
        if i == 0: clean_columns.append("Metric")
        else:
            col_str = str(col)
            if pd.isna(col) or col_str.lower() == 'nan': clean_columns.append(f"空列_{i}")
            elif col_str in clean_columns: clean_columns.append(f"{col_str}_重复_{i}")
            else: clean_columns.append(col_str)
                
    df_es.columns = clean_columns
    df_es.reset_index(drop=True, inplace=True)
    df_es['Metric'] = df_es['Metric'].astype(str).str.strip()
    df_es['Metric_Norm'] = df_es['Metric'].str.replace(' ', '', regex=False).str.lower()
    df_es = df_es[df_es['Metric'].notna()]
    df_es = df_es[df_es['Metric'] != '']
    df_es = df_es[df_es['Metric'].str.lower() != 'nan']
    
    cols_to_keep = [c for c in df_es.columns if "空列_" not in c]
    return df_es[cols_to_keep]

@st.cache_data(ttl=600)
def load_gsc_data(url):
    bust_url = f"{url}&_t={int(datetime.now().timestamp())}"
    df_raw = pd.read_csv(bust_url, header=None)
    
    row0 = df_raw.iloc[0].replace(r'^\s*$', pd.NA, regex=True).ffill()
    row1 = df_raw.iloc[1] 
    
    clean_cols = []
    for cat, sub in zip(row0, row1):
        cat_str = str(cat).strip()
        sub_str = str(sub).strip()
        if sub_str.lower() in ['date', '时间', '日期']: clean_cols.append('Date')
        elif pd.notna(sub) and sub_str.lower() != 'nan': clean_cols.append(f"{cat_str} - {sub_str}")
        else: clean_cols.append("DropMe")
            
    df_gsc = df_raw.iloc[2:].copy()
    df_gsc.columns = clean_cols
    df_gsc = df_gsc.loc[:, ~df_gsc.columns.str.contains('DropMe')]
    df_gsc = df_gsc.dropna(subset=['Date'])
    
    df_gsc['Date'] = pd.to_datetime(df_gsc['Date']).dt.date
    for col in df_gsc.columns:
        if col != 'Date':
            df_gsc[col] = df_gsc[col].astype(str).str.replace('%', '', regex=False).str.replace(',', '', regex=False)
            df_gsc[col] = pd.to_numeric(df_gsc[col], errors='coerce').fillna(0)
            
    return df_gsc.sort_values('Date').reset_index(drop=True)

@st.cache_data(ttl=600)
def load_superset_data(url):
    bust_url = f"{url}&_t={int(datetime.now().timestamp())}"
    df_super = pd.read_csv(bust_url)
    df_super = df_super.dropna(subset=['时间']) 
    
    def parse_start_date(date_str):
        try: return pd.to_datetime(str(date_str).split('-')[0].strip()).date()
        except: return pd.to_datetime('1900-01-01').date()
        
    df_super['_Sort_Date'] = df_super['时间'].apply(parse_start_date)
    
    for col in df_super.columns:
        if col not in ['时间', '_Sort_Date']:
            df_super[col] = df_super[col].astype(str).str.replace('%', '', regex=False).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df_super[col] = pd.to_numeric(df_super[col], errors='coerce').fillna(0)
            
    return df_super.sort_values('_Sort_Date').reset_index(drop=True)

# 智能 AI Overview / AI Mode 数据解析引擎
@st.cache_data(ttl=600)
def load_ai_data(url):
    bust_url = f"{url}&_t={int(datetime.now().timestamp())}"
    df_raw = pd.read_csv(bust_url, header=None)
    
    first_row_str = " ".join([str(x) for x in df_raw.iloc[0].values]).lower()
    second_row_str = " ".join([str(x) for x in df_raw.iloc[1].values]).lower() if len(df_raw) > 1 else ""
    
    if 'date' in second_row_str or '时间' in second_row_str or 'clicks' in second_row_str or 'impressions' in second_row_str:
        row0 = df_raw.iloc[0].replace(r'^\s*$', pd.NA, regex=True).ffill()
        row1 = df_raw.iloc[1]
        clean_cols = []
        for cat, sub in zip(row0, row1):
            cat_str = str(cat).strip()
            sub_str = str(sub).strip()
            if sub_str.lower() in ['date', '时间', '日期']: clean_cols.append('Date')
            elif pd.notna(sub) and sub_str.lower() != 'nan': clean_cols.append(f"{cat_str} - {sub_str}")
            else: clean_cols.append("DropMe")
                
        df_ai = df_raw.iloc[2:].copy()
        df_ai.columns = clean_cols
        df_ai = df_ai.loc[:, ~df_ai.columns.str.contains('DropMe')]
    else:
        df_ai = pd.read_csv(bust_url)
        col_map = {}
        for c in df_ai.columns:
            if str(c).strip().lower() in ['date', '时间', '日期']: col_map[c] = 'Date'
        df_ai = df_ai.rename(columns=col_map)
        
    if 'Date' in df_ai.columns:
        df_ai['Date'] = df_ai['Date'].astype(str).apply(lambda x: str(x).split('-')[0].strip() if '-' in str(x) and len(str(x)) > 15 else str(x))
        df_ai['Date'] = pd.to_datetime(df_ai['Date'], errors='coerce').dt.date
        df_ai = df_ai.dropna(subset=['Date'])
        
    for col in df_ai.columns:
        if col != 'Date':
            df_ai[col] = df_ai[col].astype(str).str.replace('%', '', regex=False).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df_ai[col] = pd.to_numeric(df_ai[col], errors='coerce').fillna(0)
            
    return df_ai.sort_values('Date').reset_index(drop=True)

def norm_cat(s):
    return str(s).lower().replace(" ", "").replace("（", "(").replace("）", ")").strip()

try:
    with st.spinner('🚀 同步大盘、GSC 与 AI 监控数据引擎中...'):
        df_es = load_and_clean_data(sheet_url)
        try: df_gsc = load_gsc_data(GSC_CSV_URL)
        except: df_gsc = pd.DataFrame() 
        
        try: df_super = load_superset_data(SUPERSET_CSV_URL)
        except: df_super = pd.DataFrame()

        try: df_ai = load_ai_data(AI_CSV_URL)
        except: df_ai = pd.DataFrame()

        today = datetime.now().date()
        current_year, current_month = today.year, today.month

        # ==========================================
        # 2. 界面绘制 & 目标配置 
        # ==========================================
        st.markdown(f"""
        <div class="welcome-banner">
            <h1>Hola, SEO Team!</h1>
            <p>Welcome back to Spain (ES) Global Dashboard • Syncing to real-time Date: {today.strftime('%Y-%m-%d')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_btn, _ = st.columns([1, 5])
        with col_btn:
            if st.button("🔄 Sync All Data"):
                load_and_clean_data.clear()
                load_gsc_data.clear()
                load_superset_data.clear()
                load_ai_data.clear()
                st.rerun()

        # ==========================================
        # 3. 口径 A：大盘固定指标 
        # ==========================================
        date_mapping = {}
        for col in df_es.columns:
            if col not in ['Metric', 'Metric_Norm']:
                try:
                    dt = pd.to_datetime(col).date()
                    date_mapping[col] = dt
                except: pass
        
        mtd_cols = [col for col, dt in date_mapping.items() if dt.year == current_year and dt.month == current_month and dt <= today]
        curr_str = f"({current_month:02d}/01 - {current_month:02d}/{today.day:02d})"
        
        lm_year = current_year if current_month > 1 else current_year - 1
        lm_month = current_month - 1 if current_month > 1 else 12
        lm_day = min(today.day, calendar.monthrange(lm_year, lm_month)[1])
        lm_str = f"({lm_year}/{lm_month:02d}/01 - {lm_month:02d}/{lm_day:02d})"
        lm_start = date(lm_year, lm_month, 1)
        lm_end = date(lm_year, lm_month, lm_day)
        lm_cols = [col for col, dt in date_mapping.items() if lm_start <= dt <= lm_end]
        
        ly_year = current_year - 1
        ly_day = min(today.day, calendar.monthrange(ly_year, current_month)[1])
        ly_str = f"({ly_year}/{current_month:02d}/01 - {current_month:02d}/{ly_day:02d})"
        ly_start = date(ly_year, current_month, 1)
        ly_end = date(ly_year, current_month, ly_day)
        ly_cols = [col for col, dt in date_mapping.items() if ly_start <= dt <= ly_end]

        def get_sum(metric_name, cols, is_currency=False):
            target = metric_name.replace(' ', '').lower()
            data = df_es[df_es['Metric_Norm'] == target]
            if not data.empty and cols:
                vals = data[cols].iloc[0].astype(str).str.replace(',', '', regex=False)
                if is_currency: vals = vals.str.replace('$', '', regex=False)
                return pd.to_numeric(vals, errors='coerce').fillna(0).sum()
            return 0.0
            
        def get_latest(metric_name, cols):
            target = metric_name.replace(' ', '').lower()
            data = df_es[df_es['Metric_Norm'] == target]
            if not data.empty and cols:
                vals = data[cols].iloc[0].replace(['None', 'nan', '', '#DIV/0!'], pd.NA).dropna()
                if not vals.empty:
                    val = str(vals.iloc[-1]).replace(',', '').replace('$', '')
                    return pd.to_numeric(val, errors='coerce')
            return 0

        mtd_sales = get_sum('Superset SEO销售额', mtd_cols, True)
        mtd_traffic = get_sum('SEO流量', mtd_cols)

        real_lm_sales = get_sum('Superset SEO销售额', lm_cols, True)
        real_ly_sales = get_sum('Superset SEO销售额', ly_cols, True)
        real_lm_traffic = get_sum('SEO流量', lm_cols)
        real_ly_traffic = get_sum('SEO流量', ly_cols)

        # 3.1 目标达成 (URL 参数永久保存配置)
        st.markdown('<div class="flex-center" style="margin:20px 0;"><div class="icon-square bg-orange"><i class="fa-solid fa-bullseye"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">Target Achievement</h3></div>', unsafe_allow_html=True)
        st.caption("💡 设定目标后，数值会自动存入网页链接中。**请将设定好目标的网页加入收藏夹（书签）**，下次直接打开就不会丢失啦！")

        saved_sales = float(st.query_params.get("sales", 3000.0))
        saved_traffic = int(st.query_params.get("traffic", 6100))
        
        t_col1, t_col2, _ = st.columns([1, 1, 2])
        with t_col1:
            target_sales = st.number_input("🎯 Target Sales ($)", min_value=0.0, value=saved_sales, step=100.0)
        with t_col2:
            target_traffic = st.number_input("⚡ Target Traffic", min_value=0, value=saved_traffic, step=100)

        st.query_params["sales"] = target_sales
        st.query_params["traffic"] = target_traffic

        prog_sales = min(mtd_sales / target_sales, 1.0) if target_sales > 0 else 0
        prog_traffic = min(mtd_traffic / target_traffic, 1.0) if target_traffic > 0 else 0
        gap_sales = max(0, target_sales - mtd_sales)
        gap_traffic = max(0, target_traffic - mtd_traffic)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="soft-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                    <div class="flex-center text-muted" style="font-size: 15px; font-weight: 500;"><i class="fa-solid fa-sack-dollar" style="color:#FF6475; margin-right:8px;"></i> Sales Progress</div>
                    <div style="color: #FF6475; font-size: 14px; font-weight: 700;">Gap: $ {gap_sales:,.2f}</div>
                </div>
                <div style="margin-bottom: 28px; display: flex; align-items: baseline;">
                    <span class="text-main" style="font-size: 38px; font-weight: 700;">$ {mtd_sales:,.2f}</span>
                    <span class="text-muted" style="font-size: 16px; margin-left: 8px;">/ $ {target_sales:,.2f}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill-red" style="width: {prog_sales*100}%;"></div>
                    <span class="rocket-icon">🎯</span>
                </div>
                <div style="text-align: right; margin-top: 16px;">
                    <span style="color: #FF6475; font-weight: 800; font-size: 18px;">{prog_sales*100:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="soft-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                    <div class="flex-center text-muted" style="font-size: 15px; font-weight: 500;"><i class="fa-solid fa-users" style="color:#42D2E6; margin-right:8px;"></i> Traffic Progress</div>
                    <div style="color: #42D2E6; font-size: 14px; font-weight: 700;">Gap: {gap_traffic:,.0f}</div>
                </div>
                <div style="margin-bottom: 28px; display: flex; align-items: baseline;">
                    <span class="text-main" style="font-size: 38px; font-weight: 700;">{mtd_traffic:,.0f}</span>
                    <span class="text-muted" style="font-size: 16px; margin-left: 8px;">/ {target_traffic:,.0f}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill-blue" style="width: {prog_traffic*100}%;"></div>
                    <span class="rocket-icon">⚡</span>
                </div>
                <div style="text-align: right; margin-top: 16px;">
                    <span style="color: #42D2E6; font-weight: 800; font-size: 18px;">{prog_traffic*100:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="flex-center" style="margin:30px 0 20px 0;"><div class="icon-square bg-purple"><i class="fa-solid fa-chart-simple"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">MTD Monitoring</h3></div>', unsafe_allow_html=True)
        def get_trend_ui(pct): return ("#FF6475" if pct < 0 else "#22C55E", "#FFF0F2" if pct < 0 else "#F0FDF4", "↓" if pct < 0 else "↑")

        mom_sales_pct = ((mtd_sales - real_lm_sales) / real_lm_sales) * 100 if real_lm_sales else 0
        yoy_sales_pct = ((mtd_sales - real_ly_sales) / real_ly_sales) * 100 if real_ly_sales else 0
        mom_traf_pct = ((mtd_traffic - real_lm_traffic) / real_lm_traffic) * 100 if real_lm_traffic else 0
        yoy_traf_pct = ((mtd_traffic - real_ly_traffic) / real_ly_traffic) * 100 if real_ly_traffic else 0

        c1_m, bg1_m, arr1_m = get_trend_ui(mom_sales_pct)
        c1_y, bg1_y, arr1_y = get_trend_ui(yoy_sales_pct)
        c2_m, bg2_m, arr2_m = get_trend_ui(mom_traf_pct)
        c2_y, bg2_y, arr2_y = get_trend_ui(yoy_traf_pct)

        st.markdown(f"""
        <div class="soft-card" style="display: flex; justify-content: space-between; text-align: left; padding-bottom:30px;">
            <div style="flex: 1;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Sales MTD <span class="compare-date-str">{curr_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 32px;">$ {mtd_sales:,.2f}</h2>
            </div>
            <div style="flex: 1; border-left: 2px solid #F0F1F6; padding-left: 30px;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Last Month <span class="compare-date-str">{lm_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 26px; margin-bottom: 12px;">$ {real_lm_sales:,.2f}</h2>
                <span style="color: {c1_m}; font-weight: 600; background: {bg1_m}; padding: 4px 12px; border-radius: 8px; font-size: 13px;">{arr1_m} {abs(mom_sales_pct):.1f}% MoM</span>
            </div>
            <div style="flex: 1; border-left: 2px solid #F0F1F6; padding-left: 30px;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Last Year <span class="compare-date-str">{ly_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 26px; margin-bottom: 12px;">$ {real_ly_sales:,.2f}</h2>
                <span style="color: {c1_y}; font-weight: 600; background: {bg1_y}; padding: 4px 12px; border-radius: 8px; font-size: 13px;">{arr1_y} {abs(yoy_sales_pct):.1f}% YoY</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="soft-card" style="display: flex; justify-content: space-between; text-align: left; padding-bottom:30px;">
            <div style="flex: 1;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Traffic MTD <span class="compare-date-str">{curr_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 32px;">{mtd_traffic:,.0f}</h2>
            </div>
            <div style="flex: 1; border-left: 2px solid #F0F1F6; padding-left: 30px;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Last Month <span class="compare-date-str">{lm_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 26px; margin-bottom: 12px;">{real_lm_traffic:,.0f}</h2>
                <span style="color: {c2_m}; font-weight: 600; background: {bg2_m}; padding: 4px 12px; border-radius: 8px; font-size: 13px;">{arr2_m} {abs(mom_traf_pct):.1f}% MoM</span>
            </div>
            <div style="flex: 1; border-left: 2px solid #F0F1F6; padding-left: 30px;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Last Year <span class="compare-date-str">{ly_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 26px; margin-bottom: 12px;">{real_ly_traffic:,.0f}</h2>
                <span style="color: {c2_y}; font-weight: 600; background: {bg2_y}; padding: 4px 12px; border-radius: 8px; font-size: 13px;">{arr2_y} {abs(yoy_traf_pct):.1f}% YoY</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<br><hr style="border:1px solid #E2E8F0; margin: 20px 0;"><br>', unsafe_allow_html=True)

        # ==========================================
        # 4. & 5. 区间维度与计算
        # ==========================================
        valid_dates = list(date_mapping.values())
        min_date = min(valid_dates) if valid_dates else date.today()
        max_date = max(valid_dates) if valid_dates else date.today()

        header_col1, header_col2, header_col3 = st.columns([1.5, 1, 1])
        with header_col1:
            st.markdown('<div class="flex-center" style="margin-bottom:6px;"><div class="icon-square bg-blue"><i class="fa-regular fa-calendar"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">Interval Analysis</h3></div>', unsafe_allow_html=True)
            st.caption("Modules below are strictly bounded by your date selection.")
        
        mtd_default_start = date(current_year, current_month, 1)
        mtd_default_end = today

        with header_col2:
            primary_dates = st.date_input("🗓️ Primary Date Range", [mtd_default_start, mtd_default_end])
        with header_col3:
            enable_compare = st.checkbox("🔄 Enable Trend Comparison")
            if enable_compare: compare_dates = st.date_input("🗓️ Compare Date Range", [min_date, max_date])
            else: compare_dates = []

        if len(primary_dates) == 2: start_d1, end_d1 = primary_dates
        else: start_d1 = end_d1 = primary_dates[0]
        filtered_cols_1 = [col for col, dt in date_mapping.items() if start_d1 <= dt <= end_d1]

        if enable_compare and len(compare_dates) == 2:
            start_d2, end_d2 = compare_dates
            filtered_cols_2 = [col for col, dt in date_mapping.items() if start_d2 <= dt <= end_d2]
        else: filtered_cols_2 = []

        int_traffic = get_sum('SEO流量', filtered_cols_1)
        int_blog = get_sum('SEO Blog 流量', filtered_cols_1)
        int_insite = get_sum('SEO 站内流量', filtered_cols_1)
        int_site_total = get_sum('网站总流量', filtered_cols_1)
        
        def calc_bounce_rate(cols):
            bounce_data = df_es[df_es['Metric_Norm'] == '跳出率']
            if not bounce_data.empty and cols:
                br_vals = bounce_data[cols].iloc[0].astype(str).str.replace('%', '', regex=False)
                br_series = pd.to_numeric(br_vals, errors='coerce').dropna()
                if not br_series.empty: return br_series.mean()
            return 0.0
            
        int_bounce_rate = calc_bounce_rate(filtered_cols_1)
        int_super_sales = get_sum('Superset SEO销售额', filtered_cols_1, True)
        int_ga4_sales = get_sum('GA4 SEO销售额', filtered_cols_1, True)
        ai_sales = get_sum('AI Assistant 销售额', filtered_cols_1, True)
        ai_traffic = get_sum('AI Assistant 流量', filtered_cols_1)
        google_index = get_latest('收录', filtered_cols_1)
        google_backlinks = get_latest('外链', filtered_cols_1)
        google_domain = get_latest('外链域名广度', filtered_cols_1)

        cmp_traffic = get_sum('SEO流量', filtered_cols_2) if enable_compare else 0
        cmp_blog = get_sum('SEO Blog 流量', filtered_cols_2) if enable_compare else 0
        cmp_insite = get_sum('SEO 站内流量', filtered_cols_2) if enable_compare else 0
        cmp_site_total = get_sum('网站总流量', filtered_cols_2) if enable_compare else 0
        cmp_bounce_rate = calc_bounce_rate(filtered_cols_2) if enable_compare else 0
        cmp_super_sales = get_sum('Superset SEO销售额', filtered_cols_2, True) if enable_compare else 0
        cmp_ga4_sales = get_sum('GA4 SEO销售额', filtered_cols_2, True) if enable_compare else 0
        
        def render_delta(curr, prev, reverse_color=False, is_pct=False):
            if not enable_compare or len(filtered_cols_2) == 0: return ""
            if prev == 0: return '<span style="font-size:12px; color:#8E8CA7; margin-left:8px; font-weight: 500;">(vs. --)</span>'
            diff = curr - prev
            pct = diff if is_pct else (diff / prev) * 100
            if diff > 0: color, arrow = ("#FF6475" if reverse_color else "#22C55E", "↑")
            elif diff < 0: color, arrow = ("#22C55E" if reverse_color else "#FF6475", "↓")
            else: color, arrow = ("#8E8CA7", "-")
            val_str = f"{abs(pct):.1f}pp" if is_pct else f"{abs(pct):.1f}%"
            return f'<span style="color:{color}; font-size:13px; font-weight:700; margin-left:10px;">{arrow} {val_str}</span>'

        st.markdown(f"""
        <div class="soft-card">
            <h4 class="text-main" style="margin-top: 0; margin-bottom: 24px; display: flex; align-items: center; font-size:18px;">
                <div class="icon-small bg-blue flex-center" style="justify-content:center;"><i class="fa-solid fa-filter"></i></div> Traffic Funnel Health
            </h4>
            <div style="display: flex; justify-content: space-between; border-bottom: 2px dashed #F0F1F6; padding-bottom: 24px; margin-bottom: 18px;">
                <div class="funnel-item" style="padding-left: 0;"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#2D235C;"></i> SEO 流量</p><p class="funnel-value">{int_traffic:,.0f} {render_delta(int_traffic, cmp_traffic)}</p></div>
                <div class="funnel-item"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#42D2E6;"></i> SEO Blog 流量</p><p class="funnel-value">{int_blog:,.0f} {render_delta(int_blog, cmp_blog)}</p></div>
                <div class="funnel-item"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#FF6475;"></i> SEO 站内流量</p><p class="funnel-value">{int_insite:,.0f} {render_delta(int_insite, cmp_insite)}</p></div>
                <div class="funnel-item"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#FFB000;"></i> 网站总流量</p><p class="funnel-value">{int_site_total:,.0f} {render_delta(int_site_total, cmp_site_total)}</p></div>
                <div class="funnel-item"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#8E8CA7;"></i> 跳出率</p><p class="funnel-value">{int_bounce_rate:.2f}% {render_delta(int_bounce_rate, cmp_bounce_rate, reverse_color=True, is_pct=True)}</p></div>
            </div>
            <p class="text-muted" style="font-size: 12px; margin: 0;">✦ Traffic anomalies have been filtered. Cross-reference with bounce rate to assess channel quality.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="soft-card">
            <h4 class="text-main" style="margin-top: 0; margin-bottom: 24px; display: flex; align-items: center; font-size:18px;">
                <div class="icon-small bg-red flex-center" style="justify-content:center;"><i class="fa-solid fa-sack-dollar"></i></div> Sales Breakdown (Selected Interval)
            </h4>
            <div style="display: flex; gap: 20px;">
                <div class="inner-box box-light" style="flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                    <p class="box-label text-muted" style="justify-content: center; margin-bottom: 8px;"><i class="fa-solid fa-circle" style="color:#FF6475; font-size:8px; margin-right:8px;"></i> Superset SEO Sales</p>
                    <div class="box-value-dark" style="font-size: 36px; justify-content: center;">$ {int_super_sales:,.2f} {render_delta(int_super_sales, cmp_super_sales)}</div>
                </div>
                <div class="inner-box box-light" style="flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                    <p class="box-label text-muted" style="justify-content: center; margin-bottom: 8px;"><i class="fa-solid fa-circle" style="color:#FFB000; font-size:8px; margin-right:8px;"></i> GA4 SEO Sales</p>
                    <div class="box-value-dark" style="font-size: 36px; justify-content: center;">$ {int_ga4_sales:,.2f} {render_delta(int_ga4_sales, cmp_ga4_sales)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_ai, col_google = st.columns(2)
        with col_ai:
            st.markdown(f"""
            <div class="soft-card" style="height: 100%;">
                <p class="asset-card-title"><div class="icon-small bg-purple flex-center" style="display:inline-flex; justify-content:center; margin-bottom:-4px;"><i class="fa-solid fa-robot"></i></div> AI Assistant</p>
                <div style="display: flex; margin-top:24px;">
                    <div class="inner-box box-deep">
                        <p class="box-label" style="color:rgba(255,255,255,0.8);"><i class="fa-solid fa-circle" style="color:#FFB000; font-size:8px; margin-right:8px;"></i> AI Sales</p>
                        <p class="box-value-white">$ {ai_sales:,.2f}</p>
                    </div>
                    <div class="inner-box box-light">
                        <p class="box-label text-muted"><i class="fa-solid fa-circle" style="color:#2D235C; font-size:8px; margin-right:8px;"></i> AI Traffic</p>
                        <p class="box-value-dark">{ai_traffic:,.0f} {render_delta(ai_traffic, 0)}</p>
                    </div>
                </div>
                <p class="card-caption">Commercial value driven by AI Models.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_google:
            st.markdown(f"""
            <div class="soft-card" style="height: 100%;">
                <p class="asset-card-title"><div class="icon-small bg-orange flex-center" style="display:inline-flex; justify-content:center; margin-bottom:-4px;"><i class="fa-brands fa-google"></i></div> Google Assets</p>
                <div style="display: flex; margin-top:24px;">
                    <div class="inner-box box-light" style="flex: 1.2;">
                        <p class="box-label text-muted"><i class="fa-solid fa-circle" style="color:#FFB000; font-size:8px; margin-right:8px;"></i> Indexing</p>
                        <p class="box-value-dark">{google_index:,.0f}</p>
                    </div>
                    <div class="inner-box box-light">
                        <p class="box-label text-muted"><i class="fa-solid fa-circle" style="color:#FF6475; font-size:8px; margin-right:8px;"></i> Backlinks</p>
                        <p class="box-value-dark">{google_backlinks:,.0f}</p>
                    </div>
                    <div class="inner-box box-light">
                        <p class="box-label text-muted"><i class="fa-solid fa-circle" style="color:#42D2E6; font-size:8px; margin-right:8px;"></i> Domains</p>
                        <p class="box-value-dark">{google_domain:,.0f}</p>
                    </div>
                </div>
                <p class="card-caption">Long-term domain authority and credibility accumulation.</p>
            </div>
            """, unsafe_allow_html=True)

        # ==========================================
        # 5.3 Interval 维度的专属趋势图 (流量 + 销售)
        # ==========================================
        def get_trend_series(metric, cols, is_curr=False):
            target = metric.replace(' ', '').lower()
            data = df_es[df_es['Metric_Norm'] == target]
            if not data.empty and cols:
                vals = data[cols].iloc[0].astype(str).str.replace(',', '', regex=False)
                if is_curr: vals = vals.str.replace('$', '', regex=False)
                return pd.to_numeric(vals, errors='coerce').fillna(0).tolist()
            return []

        dates1 = [date_mapping[d].strftime('%Y-%m-%d') for d in filtered_cols_1]
        dates2 = [date_mapping[d].strftime('%Y-%m-%d') for d in filtered_cols_2] if filtered_cols_2 else []
        font_style = dict(family="Poppins, sans-serif", color="#8E8CA7")

        traffic_metrics_options = ['SEO流量', 'SEO Blog 流量', 'SEO 站内流量', '网站总流量']
        traffic_colors = {
            'SEO流量': '#2D235C', 'SEO Blog 流量': '#42D2E6', 
            'SEO 站内流量': '#FF6475', '网站总流量': '#FFB000'
        }

        st.markdown('<div class="soft-card" style="padding-bottom:10px; margin-top:24px;"><div class="flex-center" style="margin-bottom:20px; justify-content:space-between;"><div class="flex-center"><div class="icon-small bg-blue flex-center" style="justify-content:center;"><i class="fa-solid fa-chart-line"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">Traffic Breakdown (Selected Interval)</span></div></div>', unsafe_allow_html=True)
        selected_traffic_metrics = st.multiselect("Select Traffic Metrics", traffic_metrics_options, default=['SEO流量', 'SEO Blog 流量', 'SEO 站内流量'], label_visibility="collapsed", key="interval_traffic_sel")

        fig_traffic = go.Figure()
        if not selected_traffic_metrics:
            fig_traffic.update_layout(annotations=[dict(text="Select at least one metric to display", xref="paper", yref="paper", showarrow=False, font=dict(size=14, color="#8E8CA7"))])
        else:
            for metric in selected_traffic_metrics:
                color = traffic_colors.get(metric, '#2D235C')
                t_trend1 = get_trend_series(metric, filtered_cols_1)
                t_trend2 = get_trend_series(metric, filtered_cols_2) if filtered_cols_2 else []

                if not t_trend2:
                    fig_traffic.add_trace(go.Scatter(x=dates1, y=t_trend1, mode='lines+markers', name=metric, line=dict(color=color, width=3, shape='spline'), marker=dict(size=6), fill='tozeroy', fillcolor=hex_to_rgba(color, 0.06), hovertemplate=f'{metric}<br>Date: %{{x}}<br>Traffic: %{{y:,}}<extra></extra>'))
                else:
                    max_len = max(len(t_trend1), len(t_trend2))
                    x_axis = [f"Day {i+1}" for i in range(max_len)]
                    fig_traffic.add_trace(go.Scatter(x=x_axis[:len(t_trend1)], y=t_trend1, mode='lines+markers', name=f'{metric} (Pri)', customdata=dates1, hovertemplate=f'{metric} - Pri (%{{customdata}})<br>Traffic: %{{y:,}}<extra></extra>', fill='tozeroy', fillcolor=hex_to_rgba(color, 0.06), line=dict(color=color, width=3, shape='spline'), marker=dict(size=6)))
                    fig_traffic.add_trace(go.Scatter(x=x_axis[:len(t_trend2)], y=t_trend2, mode='lines', name=f'{metric} (Cmp)', customdata=dates2, hovertemplate=f'{metric} - Cmp (%{{customdata}})<br>Traffic: %{{y:,}}<extra></extra>', line=dict(color=color, width=2.5, dash='dash', shape='spline')))

            fig_traffic.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=font_style))

        fig_traffic.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, xaxis=dict(showgrid=True, gridcolor='#F0F1F6'), yaxis=dict(showgrid=True, gridcolor='#F0F1F6'))
        st.plotly_chart(fig_traffic, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        sales_metrics_options = ['Superset SEO销售额', 'GA4 SEO销售额']
        sales_colors = {'Superset SEO销售额': '#FF6475', 'GA4 SEO销售额': '#FFB000'}

        st.markdown('<div class="soft-card" style="padding-bottom:10px;"><div class="flex-center" style="margin-bottom:20px; justify-content:space-between;"><div class="flex-center"><div class="icon-small bg-red flex-center" style="justify-content:center;"><i class="fa-solid fa-chart-area"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">Sales Trend Breakdown (Selected Interval)</span></div></div>', unsafe_allow_html=True)
        selected_sales_metrics = st.multiselect("Select Sales Metrics", sales_metrics_options, default=['Superset SEO销售额', 'GA4 SEO销售额'], label_visibility="collapsed", key="interval_sales_sel")

        fig_sales = go.Figure()
        if not selected_sales_metrics:
            fig_sales.update_layout(annotations=[dict(text="Select at least one metric to display", xref="paper", yref="paper", showarrow=False, font=dict(size=14, color="#8E8CA7"))])
        else:
            for metric in selected_sales_metrics:
                color = sales_colors.get(metric, '#FF6475')
                s_trend1 = get_trend_series(metric, filtered_cols_1, True)
                s_trend2 = get_trend_series(metric, filtered_cols_2, True) if filtered_cols_2 else []

                if not s_trend2:
                    fig_sales.add_trace(go.Scatter(x=dates1, y=s_trend1, mode='lines+markers', name=metric, line=dict(color=color, width=3, shape='spline'), marker=dict(size=6), fill='tozeroy', fillcolor=hex_to_rgba(color, 0.08), hovertemplate=f'{metric}<br>Date: %{{x}}<br>Sales: $%{{y:,.2f}}<extra></extra>'))
                else:
                    max_len = max(len(s_trend1), len(s_trend2))
                    x_axis = [f"Day {i+1}" for i in range(max_len)]
                    fig_sales.add_trace(go.Scatter(x=x_axis[:len(s_trend1)], y=s_trend1, mode='lines+markers', name=f'{metric} (Pri)', customdata=dates1, hovertemplate=f'{metric} - Pri (%{{customdata}})<br>Sales: $%{{y:,.2f}}<extra></extra>', fill='tozeroy', fillcolor=hex_to_rgba(color, 0.08), line=dict(color=color, width=3, shape='spline'), marker=dict(size=6)))
                    fig_sales.add_trace(go.Scatter(x=x_axis[:len(s_trend2)], y=s_trend2, mode='lines', name=f'{metric} (Cmp)', customdata=dates2, hovertemplate=f'{metric} - Cmp (%{{customdata}})<br>Sales: $%{{y:,.2f}}<extra></extra>', line=dict(color=color, width=2.5, dash='dash', shape='spline')))

            fig_sales.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=font_style))

        fig_sales.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, xaxis=dict(showgrid=True, gridcolor='#F0F1F6'), yaxis=dict(showgrid=True, gridcolor='#F0F1F6', tickprefix="$"))
        st.plotly_chart(fig_sales, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<br><hr style="border:1px solid #E2E8F0; margin: 20px 0;"><br>', unsafe_allow_html=True)

        # ==========================================
        # 6. Weekly Performance Comparison (含 AI Overview 3 个维度)
        # ==========================================
        st.markdown('<div class="flex-center" style="margin-bottom:6px;"><div class="icon-square bg-green"><i class="fa-solid fa-table-columns"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">Weekly Performance Comparison</h3></div>', unsafe_allow_html=True)
        st.caption("✦ Data dynamically aggregated from both Dashboards to mirror your manual report.")
        
        col_w1, col_w2, _ = st.columns([1, 1, 2])
        
        default_w2_end = date.today()
        default_w2_start = default_w2_end - timedelta(days=6)
        default_w1_end = default_w2_start - timedelta(days=1)
        default_w1_start = default_w1_end - timedelta(days=6)
        
        with col_w1: wk_range1 = st.date_input("📅 Compare Date Range 1 (Previous)", [default_w1_start, default_w1_end])
        with col_w2: wk_range2 = st.date_input("📅 Compare Date Range 2 (Current)", [default_w2_start, default_w2_end])
            
        if len(wk_range1) == 2 and len(wk_range2) == 2:
            r1_start, r1_end = wk_range1
            r2_start, r2_end = wk_range2
            
            cols_r1 = [col for col, dt in date_mapping.items() if r1_start <= dt <= r1_end]
            cols_r2 = [col for col, dt in date_mapping.items() if r2_start <= dt <= r2_end]
            
            if not df_gsc.empty:
                df_gsc_r1 = df_gsc[(df_gsc['Date'] >= r1_start) & (df_gsc['Date'] <= r1_end)]
                df_gsc_r2 = df_gsc[(df_gsc['Date'] >= r2_start) & (df_gsc['Date'] <= r2_end)]
            else:
                df_gsc_r1 = pd.DataFrame()
                df_gsc_r2 = pd.DataFrame()

            if not df_ai.empty:
                df_ai_r1 = df_ai[(df_ai['Date'] >= r1_start) & (df_ai['Date'] <= r1_end)]
                df_ai_r2 = df_ai[(df_ai['Date'] >= r2_start) & (df_ai['Date'] <= r2_end)]
            else:
                df_ai_r1 = pd.DataFrame()
                df_ai_r2 = pd.DataFrame()
                
            def get_gsc_val(df, cat):
                if df.empty: return 0
                target_cat = norm_cat(cat)
                for col in df.columns:
                    if ' - ' in col:
                        c_cat, c_sub = col.split(' - ', 1)
                        if norm_cat(c_cat) == target_cat and c_sub.strip().lower() in ['clicks', '点击']:
                            return df[col].sum()
                    elif norm_cat(col) == target_cat:
                        return df[col].sum()
                return 0

            def get_ai_val(df, cat):
                if df.empty: return 0
                target_cat = norm_cat(cat)
                for col in df.columns:
                    if ' - ' in col:
                        c_cat, c_sub = col.split(' - ', 1)
                        if norm_cat(c_cat) == target_cat and c_sub.strip().lower() in ['clicks', '点击', '流量', 'value', '数值']:
                            return df[col].sum()
                    elif norm_cat(col) == target_cat:
                        return df[col].sum()
                matched_cols = [col for col in df.columns if norm_cat(cat) in norm_cat(col)]
                if matched_cols:
                    return df[matched_cols[0]].sum()
                return 0
                
            # 💡 核心更新：把 AI Performance 3 个维度加在 销售额 (AI assistant) 正下方
            metrics_list = [
                ("销售额 (Superset)", "currency", "es", "Superset SEO销售额"),
                ("销售额 (GA4)", "currency", "es", "GA4 SEO销售额"),
                ("流量 (GA4)", "number", "es", "SEO流量"),
                ("流量 (Blog)", "number", "es", "SEO Blog 流量"),
                ("流量 (站内)", "number", "es", "SEO 站内流量"),
                ("流量 (AI assistant)", "number", "es", "AI Assistant 流量"),
                ("销售额 (AI assistant)", "currency", "es", "AI Assistant 销售额"),
                ("AI Performance（总）", "number", "ai", "AI Performance（总）"),
                ("AI Performance（非Blog）", "number", "ai", "AI Performance（非Blog）"),
                ("AI Performance（Blog）", "number", "ai", "AI Performance（Blog）"),
                ("点击 (GSC)", "number", "gsc", "点击(GSC)"),
                ("点击 (非品牌词点击)", "number", "gsc", "点击(非品牌词点击)"),
                ("点击 (Blog)", "number", "gsc", "点击(Blog)"),
                ("点击 (非Blog)", "number", "gsc", "点击(非Blog)"),
                ("点击 (非品牌词非Blog)", "number", "gsc", "点击(非品牌词非Blog)"),
                ("点击 (非品牌词非Blog非utm)", "number", "gsc", "点击(非品牌词非Blog非utm)")
            ]
            
            raw_table_data = []
            for m_name, m_type, src, m_key in metrics_list:
                is_curr = (m_type == "currency")
                if src == "es":
                    v1 = get_sum(m_key, cols_r1, is_curr)
                    v2 = get_sum(m_key, cols_r2, is_curr)
                elif src == "ai":
                    v1 = get_ai_val(df_ai_r1, m_key)
                    v2 = get_ai_val(df_ai_r2, m_key)
                else:
                    v1 = get_gsc_val(df_gsc_r1, m_key)
                    v2 = get_gsc_val(df_gsc_r2, m_key)
                raw_table_data.append({"日期": m_name, "W1": v1, "W2": v2, "_type": m_type})
            
            df_compare_base = pd.DataFrame(raw_table_data)
            
            table_container = st.empty()
            
            with st.expander("⚙️ 发现异常想调整？点此展开底层数据进行手动微调 (Edit Raw Values)"):
                st.info("💡 提示：在此处修改 W1 或 W2 的数值，上方的精美表格会立即以您的新数据为准进行渲染，包括红绿变化与排版！")
                edited_df = st.data_editor(
                    df_compare_base[["日期", "W1", "W2"]],
                    column_config={
                        "日期": st.column_config.TextColumn("指标名称", disabled=True),
                        "W1": st.column_config.NumberColumn(f"{r1_start.strftime('%-m/%-d')}-{r1_end.strftime('%-m/%-d')}", format="%.2f"),
                        "W2": st.column_config.NumberColumn(f"{r2_start.strftime('%-m/%-d')}-{r2_end.strftime('%-m/%-d')}", format="%.2f"),
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
            table_html = f"""
            <table class="wk-table" style="margin-bottom: 24px;">
                <tr>
                    <th>日期</th>
                    <th>{r1_start.strftime('%-m/%-d')}-{r1_end.strftime('%-m/%-d')}</th>
                    <th>{r2_start.strftime('%-m/%-d')}-{r2_end.strftime('%-m/%-d')}</th>
                    <th>环比变化</th>
                </tr>
            """
            
            for i, row in edited_df.iterrows():
                m_name = row["日期"]
                v1 = row["W1"]
                v2 = row["W2"]
                m_type = df_compare_base.loc[i, "_type"]
                is_curr = (m_type == "currency")

                v1_str = f"${v1:,.2f}" if is_curr else f"{v1:,.0f}"
                v2_str = f"${v2:,.2f}" if is_curr else f"{v2:,.0f}"

                if v1 == 0 and v2 == 0:
                    pct_str, color_class = ("0.00%", "")
                elif v1 == 0:
                    pct_str, color_class = ("+100.00%", "text-green")
                else:
                    pct = ((v2 - v1) / v1) * 100
                    pct_str = f"{pct:+.2f}%"
                    color_class = "text-green" if pct > 0 else ("text-red" if pct < 0 else "")
                
                table_html += f"<tr><td>{m_name}</td><td>{v1_str}</td><td class='{color_class}'>{v2_str}</td><td class='{color_class}'>{pct_str}</td></tr>"

            table_html += "</table>"
            table_container.markdown(table_html, unsafe_allow_html=True)

        st.markdown('<br><hr style="border:1px solid #E2E8F0; margin: 20px 0;"><br>', unsafe_allow_html=True)

        # ==========================================
        # 6.5 Superset Performance Tracking
        # ==========================================
        if not df_super.empty:
            st.markdown('<div class="flex-center" style="margin-bottom:20px;"><div class="icon-square bg-red"><i class="fa-solid fa-cart-shopping"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">Superset Funnel Tracking</h3></div>', unsafe_allow_html=True)
            st.caption("✦ Analyze E-commerce funnel absolute volumes vs conversion rates simultaneously.")

            all_super_metrics = [c for c in df_super.columns if c not in ['时间', '_Sort_Date']]
            super_rate_metrics = [c for c in all_super_metrics if '率' in c]
            super_vol_metrics = [c for c in all_super_metrics if '率' not in c]

            col_s1, col_s2, col_s3 = st.columns([1.5, 1.5, 1])
            with col_s1:
                sel_super_vols = st.multiselect("📦 Select Volume Metrics (Bar / Line)", super_vol_metrics, default=["访问量", "订单数"])
            with col_s2:
                sel_super_rates = st.multiselect("📈 Select Rate Metrics (Area / Line)", super_rate_metrics, default=["转化率", "加购率"])
            with col_s3:
                super_date_range = st.date_input("🗓️ Filter Superset Dates", [])

            plot_sup_df = df_super.copy()
            if len(super_date_range) == 2:
                plot_sup_df = plot_sup_df[(plot_sup_df['_Sort_Date'] >= super_date_range[0]) & (plot_sup_df['_Sort_Date'] <= super_date_range[1])]

            def get_hover_format(m_name):
                if '额' in m_name or '美元' in m_name: return '$%{y:,.2f}'
                if '率' in m_name: return '%{y:.2f}%'
                return '%{y:,}'

            st.markdown('<div class="soft-card" style="padding-bottom:10px;"><div class="flex-center" style="margin-bottom:20px;"><div class="icon-small bg-blue flex-center" style="justify-content:center;"><i class="fa-solid fa-layer-group"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">Funnel Volume Breakdown</span></div>', unsafe_allow_html=True)
            fig_sup_vol = make_subplots(specs=[[{"secondary_y": True}]])
            
            if not sel_super_vols:
                fig_sup_vol.update_layout(annotations=[dict(text="Select metrics above", xref="paper", yref="paper", showarrow=False, font=dict(size=14, color="#8E8CA7"))])
            else:
                vol_colors = ["#42D2E6", "#2D235C", "#FF6475", "#FFB000"]
                for i, metric in enumerate(sel_super_vols):
                    color = vol_colors[i % len(vol_colors)]
                    fmt = get_hover_format(metric)
                    if i == 0:
                        fig_sup_vol.add_trace(go.Bar(x=plot_sup_df['时间'], y=plot_sup_df[metric], name=metric, marker_color=hex_to_rgba(color, 0.4), hovertemplate=f'Time: %{{x}}<br>{metric}: {fmt}<extra></extra>'), secondary_y=False)
                    else:
                        fig_sup_vol.add_trace(go.Scatter(x=plot_sup_df['时间'], y=plot_sup_df[metric], mode='lines+markers', name=metric, line=dict(color=color, width=3, shape='spline'), marker=dict(size=6), hovertemplate=f'Time: %{{x}}<br>{metric}: {fmt}<extra></extra>'), secondary_y=True)
            
            fig_sup_vol.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            fig_sup_vol.update_xaxes(showgrid=True, gridcolor='#F0F1F6')
            fig_sup_vol.update_yaxes(showgrid=True, gridcolor='#F0F1F6', secondary_y=False)
            fig_sup_vol.update_yaxes(showgrid=False, secondary_y=True)
            st.plotly_chart(fig_sup_vol, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="soft-card" style="padding-bottom:10px;"><div class="flex-center" style="margin-bottom:20px;"><div class="icon-small bg-green flex-center" style="justify-content:center;"><i class="fa-solid fa-bolt"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">Conversion Rate Health</span></div>', unsafe_allow_html=True)
            fig_sup_rate = make_subplots(specs=[[{"secondary_y": True}]])
            
            if not sel_super_rates:
                fig_sup_rate.update_layout(annotations=[dict(text="Select metrics above", xref="paper", yref="paper", showarrow=False, font=dict(size=14, color="#8E8CA7"))])
            else:
                rate_colors = ["#22C55E", "#FFB000", "#FF6475", "#42D2E6"]
                for i, metric in enumerate(sel_super_rates):
                    color = rate_colors[i % len(rate_colors)]
                    fmt = get_hover_format(metric)
                    if i == 0:
                        fig_sup_rate.add_trace(go.Scatter(x=plot_sup_df['时间'], y=plot_sup_df[metric], mode='lines', name=metric, line=dict(color=color, width=3, shape='spline'), fill='tozeroy', fillcolor=hex_to_rgba(color, 0.1), hovertemplate=f'Time: %{{x}}<br>{metric}: {fmt}<extra></extra>'), secondary_y=False)
                    else:
                        fig_sup_rate.add_trace(go.Scatter(x=plot_sup_df['时间'], y=plot_sup_df[metric], mode='lines+markers', name=metric, line=dict(color=color, width=3, shape='spline'), marker=dict(size=6), hovertemplate=f'Time: %{{x}}<br>{metric}: {fmt}<extra></extra>'), secondary_y=True)
            
            fig_sup_rate.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            fig_sup_rate.update_xaxes(showgrid=True, gridcolor='#F0F1F6')
            fig_sup_rate.update_yaxes(showgrid=True, gridcolor='#F0F1F6', secondary_y=False, ticksuffix="%")
            fig_sup_rate.update_yaxes(showgrid=False, secondary_y=True, ticksuffix="%")
            st.plotly_chart(fig_sup_rate, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<br><hr style="border:1px solid #E2E8F0; margin: 20px 0;"><br>', unsafe_allow_html=True)


        # ==========================================
        # 7. GSC Performance Tracking
        # ==========================================
        if not df_gsc.empty:
            st.markdown('<div class="flex-center" style="margin-bottom:20px;"><div class="icon-square bg-orange"><i class="fa-brands fa-google"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">GSC Performance Tracking</h3></div>', unsafe_allow_html=True)
            
            raw_cats = list(set([c.split(' - ')[0] for c in df_gsc.columns if ' - ' in c]))
            custom_order = [
                "点击(gsc)", 
                "点击(非品牌词点击)", 
                "点击(blog)", 
                "点击(非blog)", 
                "点击(非品牌词非blog)", 
                "点击(非品牌词非blog非utm)"
            ]
            
            def cat_sort_key(x):
                nx = norm_cat(x)
                return custom_order.index(nx) if nx in custom_order else 999
            
            gsc_categories = sorted(raw_cats, key=cat_sort_key)
            
            ctrl_col1, ctrl_col2 = st.columns([2, 1])
            with ctrl_col1:
                selected_gsc_cat = st.selectbox("🎯 Select Tracking Category for Deep Dive", gsc_categories)
            with ctrl_col2:
                gsc_mtd_start = date(current_year, current_month, 1)
                gsc_mtd_end = today
                gsc_date_range = st.date_input("🗓️ Filter Chart Date Range", [gsc_mtd_start, gsc_mtd_end])
            
            plot_gsc_df = df_gsc.copy()
            if len(gsc_date_range) == 2:
                plot_gsc_df = plot_gsc_df[(plot_gsc_df['Date'] >= gsc_date_range[0]) & (plot_gsc_df['Date'] <= gsc_date_range[1])]
            
            font_style = dict(family="Poppins, sans-serif", color="#8E8CA7")
            
            st.markdown(f'<div class="soft-card" style="padding-bottom:10px;"><div class="flex-center" style="margin-bottom:20px;"><div class="icon-small bg-blue flex-center" style="justify-content:center;"><i class="fa-solid fa-eye"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">Volume: Impressions vs Clicks ({selected_gsc_cat})</span></div>', unsafe_allow_html=True)
            
            fig_vol = make_subplots(specs=[[{"secondary_y": True}]])
            col_imp = f"{selected_gsc_cat} - Impressions"
            if col_imp in plot_gsc_df.columns:
                fig_vol.add_trace(go.Bar(x=plot_gsc_df['Date'], y=plot_gsc_df[col_imp], name="Impressions", marker_color=hex_to_rgba("#42D2E6", 0.4), hovertemplate='Date: %{x}<br>Impressions: %{y:,}<extra></extra>'), secondary_y=False)
            col_clk = f"{selected_gsc_cat} - Clicks"
            if col_clk in plot_gsc_df.columns:
                fig_vol.add_trace(go.Scatter(x=plot_gsc_df['Date'], y=plot_gsc_df[col_clk], mode='lines+markers', name="Clicks", line=dict(color="#2D235C", width=3, shape='spline'), marker=dict(size=6), hovertemplate='Date: %{x}<br>Clicks: %{y:,}<extra></extra>'), secondary_y=True)
            
            fig_vol.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            fig_vol.update_xaxes(showgrid=True, gridcolor='#F0F1F6')
            fig_vol.update_yaxes(showgrid=True, gridcolor='#F0F1F6', secondary_y=False)
            fig_vol.update_yaxes(showgrid=False, secondary_y=True)
            st.plotly_chart(fig_vol, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="soft-card" style="padding-bottom:10px;"><div class="flex-center" style="margin-bottom:20px;"><div class="icon-small bg-orange flex-center" style="justify-content:center;"><i class="fa-solid fa-trophy"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">Quality: CTR vs Position ({selected_gsc_cat})</span></div>', unsafe_allow_html=True)
            
            fig_qual = make_subplots(specs=[[{"secondary_y": True}]])
            col_ctr = f"{selected_gsc_cat} - CTR"
            if col_ctr in plot_gsc_df.columns:
                fig_qual.add_trace(go.Scatter(x=plot_gsc_df['Date'], y=plot_gsc_df[col_ctr], mode='lines', name="CTR (%)", line=dict(color="#22C55E", width=3, shape='spline'), fill='tozeroy', fillcolor=hex_to_rgba("#22C55E", 0.1), hovertemplate='Date: %{x}<br>CTR: %{y:.2f}%<extra></extra>'), secondary_y=False)
            col_pos = f"{selected_gsc_cat} - Position"
            if col_pos in plot_gsc_df.columns:
                fig_qual.add_trace(go.Scatter(x=plot_gsc_df['Date'], y=plot_gsc_df[col_pos], mode='lines+markers', name="Position", line=dict(color="#FFB000", width=3, shape='spline'), marker=dict(size=6), hovertemplate='Date: %{x}<br>Position: %{y:.1f}<extra></extra>'), secondary_y=True)
            
            fig_qual.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            fig_qual.update_xaxes(showgrid=True, gridcolor='#F0F1F6')
            fig_qual.update_yaxes(showgrid=True, gridcolor='#F0F1F6', secondary_y=False, ticks="outside")
            fig_qual.update_yaxes(showgrid=False, secondary_y=True, autorange="reversed", title_text="Rank Position (Lower is better)", title_font=dict(size=11, color="#8E8CA7"))
            st.plotly_chart(fig_qual, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<br><hr style="border:1px solid #E2E8F0; margin: 20px 0;"><br>', unsafe_allow_html=True)

        # ==========================================
        # 7.5 🚀 新增：AI Performance Tracking 模块 (包含 2 个专属趋势图)
        # ==========================================
        st.markdown('<div class="flex-center" style="margin-bottom:20px;"><div class="icon-square bg-purple"><i class="fa-solid fa-robot"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">AI Performance Tracking</h3></div>', unsafe_allow_html=True)
        
        # --- 图表 1：AI Assistant (日度趋势图，抓取自 df_es) ---
        st.markdown('<div class="soft-card" style="padding-bottom:10px;"><div class="flex-center" style="margin-bottom:20px; justify-content:space-between;"><div class="flex-center"><div class="icon-small bg-purple flex-center" style="justify-content:center;"><i class="fa-solid fa-chart-line"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">AI Assistant Trend (Daily)</span></div></div>', unsafe_allow_html=True)
        
        fig_ai_daily = make_subplots(specs=[[{"secondary_y": True}]])
        ai_daily_sales = get_trend_series('AI Assistant 销售额', filtered_cols_1, is_curr=True)
        ai_daily_traffic = get_trend_series('AI Assistant 流量', filtered_cols_1)
        
        if dates1:
            fig_ai_daily.add_trace(go.Bar(x=dates1, y=ai_daily_traffic, name="AI Assistant 流量", marker_color=hex_to_rgba("#2D235C", 0.4), hovertemplate='Date: %{x}<br>Traffic: %{y:,}<extra></extra>'), secondary_y=False)
            fig_ai_daily.add_trace(go.Scatter(x=dates1, y=ai_daily_sales, mode='lines+markers', name="AI Assistant 销售额 ($)", line=dict(color="#FFB000", width=3, shape='spline'), marker=dict(size=6), hovertemplate='Date: %{x}<br>Sales: $%{y:,.2f}<extra></extra>'), secondary_y=True)
            
        fig_ai_daily.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_ai_daily.update_xaxes(showgrid=True, gridcolor='#F0F1F6')
        fig_ai_daily.update_yaxes(showgrid=True, gridcolor='#F0F1F6', secondary_y=False)
        fig_ai_daily.update_yaxes(showgrid=False, secondary_y=True, tickprefix="$")
        st.plotly_chart(fig_ai_daily, use_container_width=True)
        st.caption("✦ 备注：不包括 AI Overview / AI Mode")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 图表 2：AI Mode / Overview Performance (抓取自 df_ai) ---
        if not df_ai.empty:
            st.markdown('<div class="soft-card" style="padding-bottom:10px;"><div class="flex-center" style="margin-bottom:20px; justify-content:space-between;"><div class="flex-center"><div class="icon-small bg-green flex-center" style="justify-content:center;"><i class="fa-solid fa-microchip"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">AI Overview / AI Mode Performance</span></div></div>', unsafe_allow_html=True)
            
            ai_cats = [c for c in df_ai.columns if c != 'Date']
            raw_ai_cats = list(set([c.split(' - ')[0] for c in ai_cats if ' - ' in c])) if any(' - ' in c for c in ai_cats) else ai_cats
            
            ai_ctrl_col1, ai_ctrl_col2 = st.columns([2, 1])
            with ai_ctrl_col1:
                selected_ai_cat = st.selectbox("🎯 Select AI Dimension for Deep Dive", raw_ai_cats if raw_ai_cats else ai_cats, key="ai_cat_sel")
            with ai_ctrl_col2:
                ai_mtd_start = date(current_year, current_month, 1)
                ai_date_range = st.date_input("🗓️ Filter AI Date Range", [ai_mtd_start, today], key="ai_date_range_picker")
                
            plot_ai_df = df_ai.copy()
            if len(ai_date_range) == 2:
                plot_ai_df = plot_ai_df[(plot_ai_df['Date'] >= ai_date_range[0]) & (plot_ai_df['Date'] <= ai_date_range[1])]
                
            fig_ai_overview = go.Figure()
            matched_cols = [c for c in plot_ai_df.columns if norm_cat(selected_ai_cat) in norm_cat(c)] if raw_ai_cats else [selected_ai_cat]
            if not matched_cols: matched_cols = [c for c in plot_ai_df.columns if c != 'Date']
            
            ai_colors = ["#22C55E", "#FFB000", "#FF6475", "#42D2E6", "#2D235C"]
            for idx, col in enumerate(matched_cols):
                color = ai_colors[idx % len(ai_colors)]
                fig_ai_overview.add_trace(go.Scatter(
                    x=plot_ai_df['Date'], y=plot_ai_df[col], mode='lines+markers', name=col,
                    line=dict(color=color, width=3, shape='spline'), marker=dict(size=6),
                    fill='tozeroy', fillcolor=hex_to_rgba(color, 0.05),
                    hovertemplate=f'{col}<br>Date: %{{x}}<br>Value: %{{y:,}}<extra></extra>'
                ))
                
            fig_ai_overview.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            fig_ai_overview.update_xaxes(showgrid=True, gridcolor='#F0F1F6')
            fig_ai_overview.update_yaxes(showgrid=True, gridcolor='#F0F1F6')
            st.plotly_chart(fig_ai_overview, use_container_width=True)
            st.caption("✦ 备注：只包括 AI Overview / AI Mode")
            st.markdown('</div>', unsafe_allow_html=True)


        # ==========================================
        # 8. 底层数据明细 (Raw Data Matrix)
        # ==========================================
        st.markdown('<div class="flex-center" style="margin:30px 0 20px 0;"><div class="icon-square bg-gray"><i class="fa-solid fa-table"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">Raw Data Matrix</h3></div>', unsafe_allow_html=True)
        
        tab_raw1, tab_raw2, tab_raw3, tab_raw4 = st.tabs(["📊 Primary Dashboard Matrix", "📈 GSC Matrix", "🛒 Superset Matrix", "🤖 AI Matrix"])
        
        with tab_raw1:
            dates1 = [date_mapping[d].strftime('%Y-%m-%d') for d in filtered_cols_1]
            df_display = df_es[['Metric'] + filtered_cols_1].copy()
            df_display.columns = ['Metric'] + dates1
            df_display = df_display.set_index('Metric')
            st.markdown('<div class="soft-card" style="padding: 16px;">', unsafe_allow_html=True)
            st.dataframe(df_display, use_container_width=True, height=450)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with tab_raw2:
            if 'df_gsc' in locals() and not df_gsc.empty:
                st.markdown('<div class="soft-card" style="padding: 16px;">', unsafe_allow_html=True)
                st.dataframe(df_gsc.set_index("Date"), use_container_width=True, height=450)
                st.markdown('</div>', unsafe_allow_html=True)
                
        with tab_raw3:
            if 'df_super' in locals() and not df_super.empty:
                st.markdown('<div class="soft-card" style="padding: 16px;">', unsafe_allow_html=True)
                st.dataframe(df_super.set_index("时间").drop(columns=["_Sort_Date"], errors="ignore"), use_container_width=True, height=450)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab_raw4:
            if 'df_ai' in locals() and not df_ai.empty:
                st.markdown('<div class="soft-card" style="padding: 16px;">', unsafe_allow_html=True)
                st.dataframe(df_ai.set_index("Date"), use_container_width=True, height=450)
                st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("Error occurred during rendering:")
    st.write(e)
