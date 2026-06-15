import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime

# ১. পেজ সেটিংস ও লোগো
logo_path = "logo.png"
if not os.path.exists(logo_path): logo_path = "logo.jpg"

st.set_page_config(page_title="Bigganbaksho Analytics", layout="wide", page_icon="📊")

# ২. কাস্টম প্রফেশনাল CSS (গাঢ় কালো লিখা এবং বোল্ড মেট্রিক্স)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #000000 !important; }
    
    /* হেডিং পজিশন */
    .main-title { text-align: center; color: #FF6600; font-size: 52px; font-weight: 900; margin-top: -100px; margin-bottom: 2px; }
    .developer-text { text-align: center; font-style: italic; font-size: 18px; color: #333; margin-bottom: 5px; }
    .slogan-text { text-align: center; font-size: 28px; font-weight: 800; color: #000; margin-top: 5px; margin-bottom: 2px; }
    .vision-text { text-align: center; font-size: 18px; color: #444; margin-bottom: 20px; }
    
    /* মেট্রিক কার্ড ডিজাইন */
    .metric-box {
        background: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 6px solid #FF6600;
        margin-bottom: 20px;
    }
    .metric-label { font-size: 14px; color: #555; font-weight: 700; text-transform: uppercase; }
    .metric-value { font-size: 32px; color: #000; font-weight: 900; margin: 5px 0; }

    /* টেবিল ডিজাইন - গাঢ় কালো */
    .stTable, table { color: #000000 !important; font-weight: 600 !important; }
    th { background-color: #f8f9fa !important; color: #000 !important; font-weight: 900 !important; }
    
    .section-header { font-size: 24px; font-weight: 900; color: #000; margin-top: 30px; margin-bottom: 15px; border-left: 6px solid #FF6600; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ৩. ডাটা লোডিং
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDhr-rwKe88LKKludd74G766j1l4vbvoaHi1YwwkefcfjCCgDGkZL6Ty9ngNv3gVvd5ezElgXghOs3/pub?gid=81417&single=true&output=csv"
    df = pd.read_csv(url)
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])
    for col in ['Total Amount', 'Discount', 'Total Qty']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    for i in range(1, 16):
        if f'Product QTY-{i}' in df.columns:
            df[f'Product QTY-{i}'] = pd.to_numeric(df[f'Product QTY-{i}'], errors='coerce').fillna(0).astype(int)
            df[f'Product Price-{i}'] = pd.to_numeric(df[f'Product Price-{i}'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df = load_data()

    # --- লোগো ও হেডার ---
    if os.path.exists(logo_path):
        st.image(logo_path, width=110)
    
    st.markdown('<div class="main-title">Tele Sales AI Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="developer-text">Web App Developed By-Shujoy Shaha</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan-text">ম্যানুয়েল কাজের দিন শেষ, বিজ্ঞানবাক্সে বাংলাদেশ</div>', unsafe_allow_html=True)
    st.markdown('<div class="vision-text">অন্যরকম বাংলাদেশের স্বপ্ন নিয়ে</div>', unsafe_allow_html=True)
    st.markdown("<hr style='margin:10px 0px; border: 1px solid #eee;'>", unsafe_allow_html=True)

    # --- সাইডবার ডেট ফিল্টার ---
    st.sidebar.header("📅 Date Range")
    today = datetime.date.today()
    start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=30), min_value=datetime.date(2024, 1, 1), max_value=datetime.date(2030, 12, 31))
    end_date = st.sidebar.date_input("End Date", today, min_value=datetime.date(2024, 1, 1), max_value=datetime.date(2030, 12, 31))
    f_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    # --- ১. মেট্রিক্স সেকশন ---
    rev = int(f_df['Total Amount'].sum())
    ords = len(f_df)
    aov = int(rev/ords) if ords > 0 else 0
    qty = int(f_df['Total Qty'].sum())
    dis = int(f_df['Discount'].sum())
    dis_p = (dis/rev*100) if rev > 0 else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    metrics = [
        ("Revenue", f"৳{rev:,}"), ("Orders", f"{ords}"), ("AOV", f"৳{aov:,}"),
        ("Product Qty", f"{qty:,}"), ("Discount", f"৳{dis:,}"), ("Discount %", f"{dis_p:.1f}%")
    ]
    for col, (label, value) in zip([c1, c2, c3, c4, c5, c6], metrics):
        col.markdown(f"""<div class='metric-box'><p class='metric-label'>{label}</p><p class='metric-value'>{value}</p></div>""", unsafe_allow_html=True)

    # --- ২. এজেন্ট সেকশন ---
    st.markdown("<div class='section-header'>Agent Performance (Person-wise)</div>", unsafe_allow_html=True)
    
    agent_data = f_df.groupby('Order Collector').agg(
        Revenue=('Total Amount', 'sum'),
        Orders=('Total Amount', 'count'),
        Qty=('Total Qty', 'sum')
    ).sort_values(by='Revenue', ascending=False).reset_index()
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        fig_rev = px.bar(agent_data, x='Revenue', y='Order Collector', orientation='h', title="Revenue Contribution",
                         color='Revenue', color_continuous_scale='Blues', text_auto=True)
        fig_rev.update_traces(textfont=dict(size=14, color='black', family='Arial Black'), textangle=0)
        st.plotly_chart(fig_rev, use_container_width=True)
    with col_a2:
        fig_qty = px.bar(agent_data, x='Qty', y='Order Collector', orientation='h', title="Product Qty Contribution",
                         color='Qty', color_continuous_scale='Greens', text_auto=True)
        fig_qty.update_traces(textfont=dict(size=14, color='black', family='Arial Black'), textangle=0)
        fig_qty.update_layout(xaxis=dict(showticklabels=False, title="")) # কিউটি এক্সিস অস্পষ্টতা ফিক্স
        st.plotly_chart(fig_qty, use_container_width=True)

    # র‍্যাঙ্কিং টেবিল
    st.markdown("#### Team Ranking with Contribution %")
    table_df = agent_data.copy()
    table_df['Rev %'] = (table_df['Revenue'] / rev * 100).map('{:.1f}%'.format)
    table_df['AOV'] = (table_df['Revenue'] / table_df['Orders']).astype(int).map('৳{:,}'.format)
    table_df['Revenue'] = table_df['Revenue'].map('৳{:,}'.format)
    st.table(table_df)

    # --- ৩. প্রোডাক্ট অ্যানালিটিক্স ---
    st.markdown("<div class='section-header'>Product Analytics</div>", unsafe_allow_html=True)
    
    all_items = []
    for i in range(1, 16):
        if f'Product Name-{i}' in f_df.columns:
            temp = f_df[[f'Product Name-{i}', f'Product QTY-{i}', f'Product Price-{i}']].copy().dropna()
            temp.columns = ['Product', 'Qty', 'Price']
            all_items.append(temp)
    p_df = pd.concat(all_items)
    p_df = p_df[(p_df['Product'] != "0") & (p_df['Product'] != "")]
    p_summary = p_df.groupby('Product').agg(Qty=('Qty', 'sum')).sort_values(by='Qty', ascending=False).reset_index()

    fig_p = px.bar(p_summary.head(10), x='Qty', y='Product', orientation='h', title="Top 10 Products by Qty",
                   color='Qty', color_continuous_scale='Oranges', text_auto=True)
    fig_p.update_traces(textfont=dict(size=14, color='black', family='Arial Black'), textangle=0)
    fig_p.update_layout(xaxis=dict(showticklabels=False, title="")) # ৫০, ১০০ অস্পষ্টতা ফিক্স
    st.plotly_chart(fig_p, use_container_width=True)

    # --- ৪. কাস্টমার ও এরিয়া ---
    st.markdown("<div class='section-header'>Customer Profile & District</div>", unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1:
        st.plotly_chart(px.pie(f_df, names='Class', title="Class Distribution", hole=0.4), use_container_width=True)
    with d2:
        st.plotly_chart(px.pie(f_df, names='Profession', title="Profession Distribution", hole=0.4), use_container_width=True)
    with d3:
        dist_data = f_df['District'].value_counts().reset_index().head(10)
        fig_d = px.bar(dist_data, x='count', y='District', orientation='h', title="Top 10 Districts", color_discrete_sequence=['#FF6600'], text_auto=True)
        fig_d.update_layout(xaxis=dict(showticklabels=False))
        st.plotly_chart(fig_d, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
