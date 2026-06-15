import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime

# ১. পেজ সেটিংস ও লোগো
logo_path = "logo.png"
if not os.path.exists(logo_path): logo_path = "logo.jpg"

st.set_page_config(page_title="Bigganbaksho Analytics", layout="wide", page_icon="📊")

# ২. কাস্টম প্রফেশনাল CSS (গাঢ় কালো লিখা এবং বোল্ড ডিজাইন)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #000000 !important; }
    
    .main-title { text-align: center; color: #FF6600; font-size: 52px; font-weight: 900; margin-top: -100px; margin-bottom: 2px; }
    .developer-text { text-align: center; font-style: italic; font-size: 18px; color: #333; margin-bottom: 5px; }
    .slogan-text { text-align: center; font-size: 28px; font-weight: 800; color: #000; margin-top: 5px; }
    .vision-text { text-align: center; font-size: 18px; color: #444; margin-bottom: 20px; }
    
    .metric-box { background: #FFFFFF; padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; border-top: 6px solid #FF6600; margin-bottom: 20px; }
    .metric-label { font-size: 14px; color: #555; font-weight: 700; text-transform: uppercase; }
    .metric-value { font-size: 32px; color: #000; font-weight: 900; margin: 5px 0; }

    .stTable, table { color: #000000 !important; font-weight: 600 !important; width: 100%; }
    th { background-color: #f8f9fa !important; color: #000 !important; font-weight: 900 !important; font-size: 16px; }
    
    .section-header { font-size: 26px; font-weight: 900; color: #000; margin-top: 40px; margin-bottom: 20px; border-left: 8px solid #FF6600; padding-left: 15px; background: #fdf2e9; padding-top: 5px; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ৩. ডাটা লোডিং
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDhr-rwKe88LKKludd74G766j1l4vbvoaHi1YwwkefcfjCCgDGkZL6Ty9ngNv3gVvd5ezElgXghOs3/pub?gid=81417&single=true&output=csv"
    df = pd.read_csv(url)
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])
    
    # ফাঁকা ঘর পূরণ
    cols_to_fill = ['Class', 'Age', 'Profession', 'District']
    for col in cols_to_fill:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").replace("", "Unknown")
            
    # নম্বর ফরম্যাট ফিক্স
    for col in ['Total Amount', 'Discount', 'Total Qty']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return df

# সাহায্যকারী ফাংশন কন্ট্রিবিউশন টেবিল তৈরির জন্য
def get_contribution_table(df, group_col, total_rev):
    stats = df.groupby(group_col).agg(
        Revenue=('Total Amount', 'sum'),
        Orders=('Total Amount', 'count'),
        Qty=('Total Qty', 'sum')
    ).sort_values(by='Revenue', ascending=False).reset_index()
    stats['Rev %'] = (stats['Revenue'] / total_rev * 100).map('{:.1f}%'.format)
    stats['Revenue'] = stats['Revenue'].map('৳{:,}'.format)
    return stats

try:
    df = load_data()

    # --- হেডার ---
    if os.path.exists(logo_path): st.image(logo_path, width=110)
    st.markdown('<div class="main-title">Tele Sales AI Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="developer-text">Web App Developed By-Shujoy Shaha</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan-text">ম্যানুয়েল কাজের দিন শেষ, বিজ্ঞানবাক্সে বাংলাদেশ</div>', unsafe_allow_html=True)
    st.markdown('<div class="vision-text">অন্যরকম বাংলাদেশের স্বপ্ন নিয়ে</div>', unsafe_allow_html=True)

    # --- সাইডবার ফিল্টার ---
    st.sidebar.header("📅 Date Range")
    today = datetime.date.today()
    start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=30))
    end_date = st.sidebar.date_input("End Date", today)
    f_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    # --- KPI মেট্রিক্স ---
    rev = int(f_df['Total Amount'].sum())
    ords = len(f_df)
    qty = int(f_df['Total Qty'].sum())
    dis = int(f_df['Discount'].sum())
    aov = int(rev/ords) if ords > 0 else 0
    dis_p = (dis/rev*100) if rev > 0 else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    metrics = [("Revenue", f"৳{rev:,}"), ("Orders", f"{ords}"), ("AOV", f"৳{aov:,}"), 
               ("Product Qty", f"{qty:,}"), ("Discount", f"৳{dis:,}"), ("Discount %", f"{dis_p:.1f}%")]
    for col, (label, value) in zip([c1, c2, c3, c4, c5, c6], metrics):
        col.markdown(f"<div class='metric-box'><p class='metric-label'>{label}</p><p class='metric-value'>{value}</p></div>", unsafe_allow_html=True)

    # --- ১. এজেন্ট পারফরম্যান্স (Person Wise) ---
    st.markdown("<div class='section-header'>Agent Performance (Person-wise)</div>", unsafe_allow_html=True)
    col_a1, col_a2 = st.columns([1, 1])
    with col_a1:
        fig_agent = px.bar(f_df.groupby('Order Collector')['Total Amount'].sum().reset_index(), 
                           x='Total Amount', y='Order Collector', orientation='h', 
                           title="Revenue by Agent", color_discrete_sequence=['#FF6600'], text_auto='.2s')
        fig_agent.update_traces(textfont=dict(size=14, color='black', family='Arial Black'))
        st.plotly_chart(fig_agent, use_container_width=True)
    with col_a2:
        st.table(get_contribution_table(f_df, 'Order Collector', rev))

    # --- ২. ক্লাস এবং বয়স ভিত্তিক (Class & Age Wise) ---
    st.markdown("<div class='section-header'>Customer Wise: Class & Age Report</div>", unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("#### Class-wise Revenue Contribution")
        st.table(get_contribution_table(f_df, 'Class', rev))
    with col_c2:
        st.markdown("#### Age-wise Revenue Contribution")
        st.table(get_contribution_table(f_df, 'Age', rev))

    # --- ৩. প্রফেশন এবং জেলা ভিত্তিক (Profession & District Wise) ---
    st.markdown("<div class='section-header'>Customer Wise: Profession & District Report</div>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("#### Profession-wise Revenue Contribution")
        st.table(get_contribution_table(f_df, 'Profession', rev))
    with col_d2:
        st.markdown("#### Top 15 Districts (Revenue)")
        st.table(get_contribution_table(f_df, 'District', rev).head(15))

    # --- ৪. প্রোডাক্ট অ্যানালিটিক্স ---
    st.markdown("<div class='section-header'>Product Analytics (Top Selling)</div>", unsafe_allow_html=True)
    all_items = []
    for i in range(1, 16):
        if f'Product Name-{i}' in f_df.columns:
            temp = f_df[[f'Product Name-{i}', f'Product QTY-{i}']].copy().dropna().rename(columns={f'Product Name-{i}': 'Product', f'Product QTY-{i}': 'Qty'})
            all_items.append(temp)
    p_df = pd.concat(all_items)
    p_df = p_df[(p_df['Product'] != "0") & (p_df['Product'] != "")]
    p_summary = p_df.groupby('Product').agg(Qty=('Qty', 'sum')).sort_values(by='Qty', ascending=False).reset_index()

    fig_p = px.bar(p_summary.head(10), x='Qty', y='Product', orientation='h', title="Top 10 Products by Qty",
                   color='Qty', color_continuous_scale='Oranges', text_auto=True)
    fig_p.update_layout(xaxis=dict(showticklabels=False, title=""))
    st.plotly_chart(fig_p, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
