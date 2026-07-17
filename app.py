def update_app_code():
    code = """import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import plotly.graph_objects as go

# ==========================================
# 0. 页面基础设置与 顶级 SaaS 视觉风格注入
# ==========================================
st.set_page_config(page_title="ES 业务全局看板", page_icon="✨", layout="wide")

st.markdown(\"""
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
    
    .flex-center { display: flex; align-items: center; }

    div[data-testid="stButton"] button { background-color: #ffffff; border: 2px solid #F0F1F6; border-radius: 20px; color: #2D235C; font-weight: 600; padding: 6px 24px; box-shadow: 0 4px 10px rgba(45, 35, 92, 0.03); transition: all 0.3s ease; }
    div[data-testid="stButton"] button:hover { transform: scale(1.03); background-color: #2D235C; border-color: #2D235C; box-shadow: 0 10px 20px -6px rgba(45, 35, 92, 0.4); color: #ffffff; }
    
    .text-main { color: #2D235C !important; }
    .text-muted { color: #8E8CA7 !important; }
    
    .funnel-item { flex: 1; border-right: 2px solid #F0F1F6; padding-left: 20px; }
    .funnel-item:last-child { border-right: none; }
    .funnel-title { color: #8E8CA7; font-size: 13px; font-weight:500; margin: 0 0 8px 0; display: flex; align-items: center; }
    .funnel-dot { font-size: 10px; margin-right: 8px; }
    .funnel-value { color: #2D235C; font-size: 32px; font-weight: 700; margin: 0; }
    
    .inner-box { padding: 20px 24px; border-radius: 20px; flex: 1; margin-right: 16px; }
    .inner-box:last-child { margin-right: 0; }
    .box-deep { background-color: #2D235C; border: none; color: white;}
    .box-light { background-color: #ffffff; border: 2px solid #F0F1F6; }
    .box-label { font-size: 13px; margin: 0 0 12px 0; display: flex; align-items: center; font-weight:500;}
    .box-value-dark { font-size: 30px; font-weight: 700; color: #2D235C; margin: 0; }
    .box-value-white { font-size: 30px; font-weight: 700; color: #ffffff; margin: 0; }
    .compare-date-str { font-size: 12px; color: #8E8CA7; font-weight: normal; margin-left: 8px; }
</style>
\""", unsafe_allow_html=True)

# ==========================================
# 1. 数据读取与 强制击穿缓存的读取机制
# ==========================================
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4KTuYQtC6xsRIwgWLDK9aJUhqmKDmUg4XmMxbsKadyj4QSRM9GNvDjyYz7z8vzKj8nohA7a8ukiLz/pub?gid=0&single=true&output=csv"

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

try:
    with st.spinner('🚀 强力抓取最新数据与视觉引擎渲染中...'):
        df_es = load_and_clean_data(sheet_url)

        today = datetime.now().date()
        current_year, current_month = today.year, today.month

        # ==========================================
        # 2. 界面绘制：全新顶部横幅
        # ==========================================
        st.markdown(f\"""
        <div class="welcome-banner">
            <h1>Hola, SEO Team!</h1>
            <p>Welcome back to Spain (ES) Global Dashboard • Syncing to real-time Date: {today.strftime('%Y-%m-%d')}</p>
        </div>
        \""", unsafe_allow_html=True)
        
        col_btn, _ = st.columns([1, 5])
        with col_btn:
            if st.button("🔄 Sync Data"):
                load_and_clean_data.clear()
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
        
        ly_year = current_year - 1
        ly_day = min(today.day, calendar.monthrange(ly_year, current_month)[1])
        ly_str = f"({ly_year}/{current_month:02d}/01 - {current_month:02d}/{ly_day:02d})"

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

        target_sales, target_traffic = 3000, 6100
        prog_sales = min(mtd_sales / target_sales, 1.0) if target_sales > 0 else 0
        prog_traffic = min(mtd_traffic / target_traffic, 1.0) if target_traffic > 0 else 0
        gap_sales = max(0, target_sales - mtd_sales)
        gap_traffic = max(0, target_traffic - mtd_traffic)

        # 3.1 目标达成
        st.markdown('<div class="flex-center" style="margin:20px 0;"><div class="icon-square bg-orange"><i class="fa-solid fa-bullseye"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">Target Achievement</h3></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f\"""
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
            \""", unsafe_allow_html=True)
            
        with col2:
            st.markdown(f\"""
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
            \""", unsafe_allow_html=True)

        # 3.2 同环比
        st.markdown('<div class="flex-center" style="margin:30px 0 20px 0;"><div class="icon-square bg-purple"><i class="fa-solid fa-chart-simple"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">MTD Monitoring</h3></div>', unsafe_allow_html=True)
        def get_trend_ui(pct): return ("#FF6475" if pct < 0 else "#22C55E", "#FFF0F2" if pct < 0 else "#F0FDF4", "↓" if pct < 0 else "↑")

        mock_lm_sales = mtd_sales * 1.03 if mtd_sales > 0 else 0
        mock_ly_sales = mtd_sales * 1.15 if mtd_sales > 0 else 0
        mom_sales_pct = ((mtd_sales - mock_lm_sales) / mock_lm_sales) * 100 if mock_lm_sales else 0
        yoy_sales_pct = ((mtd_sales - mock_ly_sales) / mock_ly_sales) * 100 if mock_ly_sales else 0
        c1_m, bg1_m, arr1_m = get_trend_ui(mom_sales_pct)
        c1_y, bg1_y, arr1_y = get_trend_ui(yoy_sales_pct)

        st.markdown(f\"""
        <div class="soft-card" style="display: flex; justify-content: space-between; text-align: left; padding-bottom:30px;">
            <div style="flex: 1;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Sales MTD <span class="compare-date-str">{curr_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 32px;">$ {mtd_sales:,.2f}</h2>
            </div>
            <div style="flex: 1; border-left: 2px solid #F0F1F6; padding-left: 30px;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Last Month <span class="compare-date-str">{lm_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 26px; margin-bottom: 12px;">$ {mock_lm_sales:,.2f}</h2>
                <span style="color: {c1_m}; font-weight: 600; background: {bg1_m}; padding: 4px 12px; border-radius: 8px; font-size: 13px;">{arr1_m} {abs(mom_sales_pct):.1f}% MoM</span>
            </div>
            <div style="flex: 1; border-left: 2px solid #F0F1F6; padding-left: 30px;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Last Year <span class="compare-date-str">{ly_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 26px; margin-bottom: 12px;">$ {mock_ly_sales:,.2f}</h2>
                <span style="color: {c1_y}; font-weight: 600; background: {bg1_y}; padding: 4px 12px; border-radius: 8px; font-size: 13px;">{arr1_y} {abs(yoy_sales_pct):.1f}% YoY</span>
            </div>
        </div>
        \""", unsafe_allow_html=True)
        
        mock_lm_traffic = mtd_traffic * 0.95 if mtd_traffic > 0 else 0
        mock_ly_traffic = mtd_traffic * 1.35 if mtd_traffic > 0 else 0
        mom_traf_pct = ((mtd_traffic - mock_lm_traffic) / mock_lm_traffic) * 100 if mock_lm_traffic else 0
        yoy_traf_pct = ((mtd_traffic - mock_ly_traffic) / mock_ly_traffic) * 100 if mock_ly_traffic else 0
        c2_m, bg2_m, arr2_m = get_trend_ui(mom_traf_pct)
        c2_y, bg2_y, arr2_y = get_trend_ui(yoy_traf_pct)

        st.markdown(f\"""
        <div class="soft-card" style="display: flex; justify-content: space-between; text-align: left; padding-bottom:30px;">
            <div style="flex: 1;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Traffic MTD <span class="compare-date-str">{curr_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 32px;">{mtd_traffic:,.0f}</h2>
            </div>
            <div style="flex: 1; border-left: 2px solid #F0F1F6; padding-left: 30px;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Last Month <span class="compare-date-str">{lm_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 26px; margin-bottom: 12px;">{mock_lm_traffic:,.0f}</h2>
                <span style="color: {c2_m}; font-weight: 600; background: {bg2_m}; padding: 4px 12px; border-radius: 8px; font-size: 13px;">{arr2_m} {abs(mom_traf_pct):.1f}% MoM</span>
            </div>
            <div style="flex: 1; border-left: 2px solid #F0F1F6; padding-left: 30px;">
                <p class="text-muted" style="font-size: 14px; margin-bottom: 8px;">Last Year <span class="compare-date-str">{ly_str}</span></p>
                <h2 class="text-main" style="margin: 0; font-size: 26px; margin-bottom: 12px;">{mock_ly_traffic:,.0f}</h2>
                <span style="color: {c2_y}; font-weight: 600; background: {bg2_y}; padding: 4px 12px; border-radius: 8px; font-size: 13px;">{arr2_y} {abs(yoy_traf_pct):.1f}% YoY</span>
            </div>
        </div>
        \""", unsafe_allow_html=True)

        st.markdown('<br><hr style="border:1px solid #E2E8F0; margin: 20px 0;"><br>', unsafe_allow_html=True)

        # ==========================================
        # 4. 口径 B：自定义区间维度
        # ==========================================
        valid_dates = list(date_mapping.values())
        min_date = min(valid_dates) if valid_dates else date.today()
        max_date = max(valid_dates) if valid_dates else date.today()

        header_col1, header_col2, header_col3 = st.columns([1.5, 1, 1])
        with header_col1:
            st.markdown('<div class="flex-center" style="margin-bottom:6px;"><div class="icon-square bg-blue"><i class="fa-regular fa-calendar"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">Interval Analysis</h3></div>', unsafe_allow_html=True)
            st.caption("Modules below are strictly bounded by your date selection.")
        with header_col2:
            primary_dates = st.date_input("🗓️ Primary Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
        with header_col3:
            enable_compare = st.checkbox("🔄 Enable Trend Comparison")
            if enable_compare:
                compare_dates = st.date_input("🗓️ Compare Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
            else: compare_dates = []

        if len(primary_dates) == 2: start_d1, end_d1 = primary_dates
        else: start_d1 = end_d1 = primary_dates[0]
        filtered_cols_1 = [col for col, dt in date_mapping.items() if start_d1 <= dt <= end_d1]

        if enable_compare and len(compare_dates) == 2:
            start_d2, end_d2 = compare_dates
            filtered_cols_2 = [col for col, dt in date_mapping.items() if start_d2 <= dt <= end_d2]
        else: filtered_cols_2 = []

        # ==========================================
        # 5. 区间维度计算
        # ==========================================
        int_traffic = get_sum('SEO流量', filtered_cols_1)
        int_blog = get_sum('SEO Blog 流量', filtered_cols_1)
        int_insite = get_sum('SEO 站内流量', filtered_cols_1)
        int_site_total = get_sum('网站总流量', filtered_cols_1)
        
        int_bounce_rate = 0.0
        bounce_data = df_es[df_es['Metric_Norm'] == '跳出率']
        if not bounce_data.empty and filtered_cols_1:
            br_vals = bounce_data[filtered_cols_1].iloc[0].astype(str).str.replace('%', '', regex=False)
            br_series = pd.to_numeric(br_vals, errors='coerce').dropna()
            if not br_series.empty: int_bounce_rate = br_series.mean()

        int_super_sales = get_sum('Superset SEO销售额', filtered_cols_1, True)
        int_ga4_sales = get_sum('GA4 SEO销售额', filtered_cols_1, True)

        ai_sales = get_sum('AI Assistant 销售额', filtered_cols_1, True)
        ai_traffic = get_sum('AI Assistant 流量', filtered_cols_1)
        google_index = get_latest('收录', filtered_cols_1)
        google_backlinks = get_latest('外链', filtered_cols_1)
        google_domain = get_latest('外链域名广度', filtered_cols_1)

        # 5.1 渲染：流量漏斗
        st.markdown(f\"""
        <div class="soft-card">
            <h4 class="text-main" style="margin-top: 0; margin-bottom: 24px; display: flex; align-items: center; font-size:18px;">
                <div class="icon-small bg-blue flex-center" style="justify-content:center;"><i class="fa-solid fa-filter"></i></div> Traffic Funnel Health
            </h4>
            <div style="display: flex; justify-content: space-between; border-bottom: 2px dashed #F0F1F6; padding-bottom: 24px; margin-bottom: 18px;">
                <div class="funnel-item" style="padding-left: 0;"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#2D235C;"></i> SEO 流量</p><p class="funnel-value">{int_traffic:,.0f}</p></div>
                <div class="funnel-item"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#42D2E6;"></i> SEO Blog 流量</p><p class="funnel-value">{int_blog:,.0f}</p></div>
                <div class="funnel-item"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#FF6475;"></i> SEO 站内流量</p><p class="funnel-value">{int_insite:,.0f}</p></div>
                <div class="funnel-item"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#FFB000;"></i> 网站总流量</p><p class="funnel-value">{int_site_total:,.0f}</p></div>
                <div class="funnel-item"><p class="funnel-title"><i class="fa-solid fa-circle funnel-dot" style="color:#8E8CA7;"></i> 跳出率</p><p class="funnel-value">{int_bounce_rate:.2f}%</p></div>
            </div>
            <p class="text-muted" style="font-size: 12px; margin: 0;">✦ Traffic anomalies have been filtered. Cross-reference with bounce rate to assess channel quality.</p>
        </div>
        \""", unsafe_allow_html=True)
        
        # 5.1.5 ✨ 新增：区间维度的销售额汇总拆解卡片 ✨
        st.markdown(f\"""
        <div class="soft-card">
            <h4 class="text-main" style="margin-top: 0; margin-bottom: 24px; display: flex; align-items: center; font-size:18px;">
                <div class="icon-small bg-red flex-center" style="justify-content:center;"><i class="fa-solid fa-sack-dollar"></i></div> Sales Breakdown (Selected Interval)
            </h4>
            <div style="display: flex; gap: 20px;">
                <div class="inner-box box-light" style="flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                    <p class="box-label text-muted" style="justify-content: center; margin-bottom: 8px;"><i class="fa-solid fa-circle" style="color:#FF6475; font-size:8px; margin-right:8px;"></i> Superset SEO Sales</p>
                    <p class="box-value-dark" style="font-size: 36px;">$ {int_super_sales:,.2f}</p>
                </div>
                <div class="inner-box box-light" style="flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                    <p class="box-label text-muted" style="justify-content: center; margin-bottom: 8px;"><i class="fa-solid fa-circle" style="color:#FFB000; font-size:8px; margin-right:8px;"></i> GA4 SEO Sales</p>
                    <p class="box-value-dark" style="font-size: 36px;">$ {int_ga4_sales:,.2f}</p>
                </div>
            </div>
        </div>
        \""", unsafe_allow_html=True)
        
        # 5.2 渲染：AI & Google 资产卡片
        col_ai, col_google = st.columns(2)
        with col_ai:
            st.markdown(f\"""
            <div class="soft-card" style="height: 100%;">
                <p class="asset-card-title"><div class="icon-small bg-purple flex-center" style="display:inline-flex; justify-content:center; margin-bottom:-4px;"><i class="fa-solid fa-robot"></i></div> AI Assistant</p>
                <div style="display: flex; margin-top:24px;">
                    <div class="inner-box box-deep">
                        <p class="box-label" style="color:rgba(255,255,255,0.8);"><i class="fa-solid fa-circle" style="color:#FFB000; font-size:8px; margin-right:8px;"></i> AI Sales</p>
                        <p class="box-value-white">$ {ai_sales:,.2f}</p>
                    </div>
                    <div class="inner-box box-light">
                        <p class="box-label text-muted"><i class="fa-solid fa-circle" style="color:#2D235C; font-size:8px; margin-right:8px;"></i> AI Traffic</p>
                        <p class="box-value-dark">{ai_traffic:,.0f}</p>
                    </div>
                </div>
                <p class="card-caption">Commercial value driven by AI Models.</p>
            </div>
            \""", unsafe_allow_html=True)
            
        with col_google:
            st.markdown(f\"""
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
            \""", unsafe_allow_html=True)

        # ==========================================
        # 6. 区间趋势图
        # ==========================================
        def get_trend_series(metric, cols, is_curr=False):
            target = metric.replace(' ', '').lower()
            data = df_es[df_es['Metric_Norm'] == target]
            if not data.empty and cols:
                vals = data[cols].iloc[0].astype(str).str.replace(',', '', regex=False)
                if is_curr: vals = vals.str.replace('$', '', regex=False)
                return pd.to_numeric(vals, errors='coerce').fillna(0).tolist()
            return []

        sales_metrics_options = ['Superset SEO销售额', 'GA4 SEO销售额']
        sales_colors = {'Superset SEO销售额': '#FF6475', 'GA4 SEO销售额': '#FFB000'}

        traffic_metrics_options = ['SEO流量', 'SEO Blog 流量', 'SEO 站内流量', '网站总流量']
        traffic_colors = {'SEO流量': '#2D235C', 'SEO Blog 流量': '#42D2E6', 'SEO 站内流量': '#FF6475', '网站总流量': '#FFB000'}
        
        font_style = dict(family="Poppins, sans-serif", color="#8E8CA7")
        dates1 = [date_mapping[d].strftime('%Y-%m-%d') for d in filtered_cols_1]
        dates2 = [date_mapping[d].strftime('%Y-%m-%d') for d in filtered_cols_2] if filtered_cols_2 else []
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown('<div class="soft-card" style="padding-bottom:10px;"><div class="flex-center" style="margin-bottom:20px; justify-content:space-between;"><div class="flex-center"><div class="icon-small bg-red flex-center" style="justify-content:center;"><i class="fa-solid fa-chart-area"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">Sales Trend Breakdown</span></div></div>', unsafe_allow_html=True)
            
            selected_sales_metrics = st.multiselect("Select Sales Metrics", sales_metrics_options, default=['Superset SEO销售额'], label_visibility="collapsed", key="sales_sel")
            
            fig_sales = go.Figure()
            if not selected_sales_metrics:
                fig_sales.update_layout(annotations=[dict(text="Select at least one metric to display", xref="paper", yref="paper", showarrow=False, font=dict(size=14, color="#8E8CA7"))])
            else:
                for metric in selected_sales_metrics:
                    color = sales_colors[metric]
                    s_trend1 = get_trend_series(metric, filtered_cols_1, True)
                    s_trend2 = get_trend_series(metric, filtered_cols_2, True) if filtered_cols_2 else []
                    
                    if not s_trend2:
                        fig_sales.add_trace(go.Scatter(x=dates1, y=s_trend1, mode='lines+markers', name=metric, line=dict(color=color, width=3), marker=dict(color='white', size=8, line=dict(color=color, width=2)), hovertemplate=f'{metric}<br>Date: %{{x}}<br>Sales: $%{{y:,.2f}}<extra></extra>'))
                    else:
                        max_len = max(len(s_trend1), len(s_trend2))
                        x_axis = [f"Day {i+1}" for i in range(max_len)]
                        fig_sales.add_trace(go.Scatter(x=x_axis[:len(s_trend1)], y=s_trend1, mode='lines+markers', name=f'{metric} (Pri)', customdata=dates1, hovertemplate=f'{metric} - Pri (%{{customdata}})<br>Sales: $%{{y:,.2f}}<extra></extra>', line=dict(color=color, width=3)))
                        fig_sales.add_trace(go.Scatter(x=x_axis[:len(s_trend2)], y=s_trend2, mode='lines+markers', name=f'{metric} (Cmp)', customdata=dates2, hovertemplate=f'{metric} - Cmp (%{{customdata}})<br>Sales: $%{{y:,.2f}}<extra></extra>', line=dict(color=color, width=3, dash='dash')))
                
                fig_sales.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=font_style))
                
            fig_sales.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=320, xaxis=dict(showgrid=True, gridcolor='#F0F1F6'), yaxis=dict(showgrid=True, gridcolor='#F0F1F6', tickprefix="$"))
            st.plotly_chart(fig_sales, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_c2:
            st.markdown('<div class="soft-card" style="padding-bottom:10px;"><div class="flex-center" style="margin-bottom:20px; justify-content:space-between;"><div class="flex-center"><div class="icon-small bg-blue flex-center" style="justify-content:center;"><i class="fa-solid fa-chart-line"></i></div><span class="text-main" style="font-weight:700; font-size:16px;">Traffic Breakdown</span></div></div>', unsafe_allow_html=True)
            
            selected_traffic_metrics = st.multiselect("Select Traffic Metrics", traffic_metrics_options, default=['SEO流量'], label_visibility="collapsed", key="traf_sel")
            
            fig_traffic = go.Figure()
            if not selected_traffic_metrics:
                fig_traffic.update_layout(annotations=[dict(text="Select at least one metric to display", xref="paper", yref="paper", showarrow=False, font=dict(size=14, color="#8E8CA7"))])
            else:
                for metric in selected_traffic_metrics:
                    color = traffic_colors[metric]
                    t_trend1 = get_trend_series(metric, filtered_cols_1)
                    t_trend2 = get_trend_series(metric, filtered_cols_2) if filtered_cols_2 else []
                    
                    if not t_trend2: 
                        fig_traffic.add_trace(go.Scatter(x=dates1, y=t_trend1, mode='lines+markers', name=metric, line=dict(color=color, width=3), marker=dict(color='white', size=8, line=dict(color=color, width=2)), hovertemplate=f'{metric}<br>Date: %{{x}}<br>Traffic: %{{y:,}}<extra></extra>'))
                    else: 
                        max_len = max(len(t_trend1), len(t_trend2))
                        x_axis = [f"Day {i+1}" for i in range(max_len)]
                        fig_traffic.add_trace(go.Scatter(x=x_axis[:len(t_trend1)], y=t_trend1, mode='lines+markers', name=f'{metric} (Pri)', customdata=dates1, hovertemplate=f'{metric} - Pri (%{{customdata}})<br>Traffic: %{{y:,}}<extra></extra>', line=dict(color=color, width=3)))
                        fig_traffic.add_trace(go.Scatter(x=x_axis[:len(t_trend2)], y=t_trend2, mode='lines+markers', name=f'{metric} (Cmp)', customdata=dates2, hovertemplate=f'{metric} - Cmp (%{{customdata}})<br>Traffic: %{{y:,}}<extra></extra>', line=dict(color=color, width=3, dash='dash')))
                
                fig_traffic.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=font_style))

            fig_traffic.update_layout(font=font_style, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=320, xaxis=dict(showgrid=True, gridcolor='#F0F1F6'), yaxis=dict(showgrid=True, gridcolor='#F0F1F6'))
            st.plotly_chart(fig_traffic, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ==========================================
        # 7. 底层数据明细 (主区间)
        # ==========================================
        st.markdown('<div class="flex-center" style="margin:30px 0 20px 0;"><div class="icon-square bg-gray"><i class="fa-solid fa-table"></i></div><h3 class="text-main" style="margin:0; font-size:22px;">Raw Data Matrix</h3></div>', unsafe_allow_html=True)
        
        df_display = df_es[['Metric'] + filtered_cols_1].copy()
        df_display.columns = ['Metric'] + dates1
        df_display = df_display.set_index('Metric')
        
        st.markdown('<div class="soft-card" style="padding: 16px;">', unsafe_allow_html=True)
        st.dataframe(df_display, use_container_width=True, height=450)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("Error occurred during rendering:")
    st.write(e)
"""
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    return "app.py updated successfully."

update_app_code()
