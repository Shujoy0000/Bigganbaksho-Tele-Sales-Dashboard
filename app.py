import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime

# ১. পেজ সেটিংস ও লোগো
logo_path = "logo.png"
if not os.path.exists(logo_path): logo_path = "logo.jpg"

st.set_page_config(page_title="Bigganbaksho AI Dashboard", layout="wide", page_icon="📊")

# ২. কাস্টম CSS
st.markdown("""
    <style>
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 5px solid #FF6600; }
    .insight-box { background: #2D2E5F; color: white; padding: 20px; border-radius: 12px; margin: 10px 0px; }
    .section-header { font-size: 22px; font-weight: bold; color: #1E1E1E; margin-bottom: 15px; padding-left: 5px; border-left: 5px solid #FF6600; }
    </style>
    """, unsafe_allow_html=True)

# ৩. ডাটা লোডিং
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDhr-rwKe88LKKludd74G766j1l4vbvoaHi1YwwkefcfjCCgDGkZL6Ty9ngNv3gVvd5ezElgXghOs3/pub?gid=81417&single=true&output=csv"
    df = pd.read_csv(url)
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])
    
    # ডাটা টাইপ ফিক্স (শুরুতেই ইনটিজার করে নেওয়া)
    cols_to_fix = ['Total Amount', 'Discount', 'Total Qty']
    for col in cols_to_fix:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    for i in range(1, 16):
        if f'Product QTY-{i}' in df.columns:
            df[f'Product QTY-{i}'] = pd.to_numeric(df[f'Product QTY-{i}'], errors='coerce').fillna(0).astype(int)
        if f'Product Price-{i}' in df.columns:
            df[f'Product Price-{i}'] = pd.to_numeric(df[f'Product Price-{i}'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df = load_data()

    # --- হেডার ---
    h_col1, h_col2 = st.columns([1, 6])
    with h_col1:
        if os.path.exists(logo_path): st.image(logo_path, width=100)
    with h_col2:
        st.markdown(f"<h1 style='color:#FF6600; margin-top:-10px; font-size:45px;'>Tele Sales AI Analytics Dashboard</h1>", unsafe_allow_html=True)

    # --- সাইডবার ফিল্টার ---
    st.sidebar.header("📅 Date Selection")
    today = datetime.date.today()
    start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=30))
    end_date = st.sidebar.date_input("End Date", today)
    f_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    # --- ১. টপ মেট্রিক্স ---
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    rev = int(f_df['Total Amount'].sum())
    ords = len(f_df)
    qty = int(f_df['Total Qty'].sum())
    dis = int(f_df['Discount'].sum())
    aov = int(rev/ords) if ords > 0 else 0
    dis_p = (dis/rev*100) if rev > 0 else 0

    m1.markdown(f"<div class='metric-card'><p style='color:grey;font-size:14px;'>Revenue</p><h3>৳{rev:,}</h3></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card'><p style='color:grey;font-size:14px;'>Orders</p><h3>{ords}</h3></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card'><p style='color:grey;font-size:14px;'>AOV</p><h3>৳{aov:,}</h3></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-card'><p style='color:grey;font-size:14px;'>Product Qty</p><h3>{qty:,}</h3></div>", unsafe_allow_html=True)
    m5.markdown(f"<div class='metric-card'><p style='color:grey;font-size:14px;'>Discount</p><h3>৳{dis:,}</h3></div>", unsafe_allow_html=True)
    m6.markdown(f"<div class='metric-card'><p style='color:grey;font-size:14px;'>Discount %</p><h3>{dis_p:.1f}%</h3></div>", unsafe_allow_html=True)

    # --- ২. এজেন্ট সেগমেন্ট (Ranking Table Fix) ---
    st.markdown("<div class='section-header'>Agent Performance (Person-wise)</div>", unsafe_allow_html=True)
    
    # গ্রাফ
    a_col1, a_col2 = st.columns(2)
    with a_col1:
        agent_rev = f_df.groupby('Order Collector')['Total Amount'].sum().sort_values(ascending=False).reset_index()
        fig_a_rev = px.bar(agent_rev, x='Total Amount', y='Order Collector', orientation='h', title="Revenue by Person",
                          color='Total Amount', color_continuous_scale='Blues', text_auto=True)
        st.plotly_chart(fig_a_rev, use_container_width=True)
    with a_col2:
        agent_qty = f_df.groupby('Order Collector')['Total Qty'].sum().sort_values(ascending=False).reset_index()
        fig_a_qty = px.bar(agent_qty, x='Total Qty', y='Order Collector', orientation='h', title="Product Qty by Person",
                          color='Total Qty', color_continuous_scale='Greens', text_auto=True)
        fig_a_qty.update_layout(xaxis=dict(tickformat='d'))
        st.plotly_chart(fig_a_qty, use_container_width=True)

    # টেবিল সেকশন (দশমিক এবং অতিরিক্ত শূন্য ফিক্স)
    st.markdown("#### Team Ranking with Contribution %")
    agent_stats = f_df.groupby('Order Collector').agg(
        Revenue=('Total Amount', 'sum'),
        Orders=('Total Amount', 'count'),
        Qty=('Total Qty', 'sum')
    ).sort_values(by='Revenue', ascending=False).reset_index()
    
    # স্ট্রিং ফরম্যাটিং এর মাধ্যমে দশমিক সম্পূর্ণ বাদ দেওয়া
    display_stats = agent_stats.copy()
    display_stats['Rev %'] = (display_stats['Revenue'] / rev * 100).map('{:.1f}%'.format)
    display_stats['AOV'] = (display_stats['Revenue'] / display_stats['Orders']).fillna(0).astype(int).map('৳{:,}'.format)
    display_stats['Revenue'] = display_stats['Revenue'].astype(int).map('৳{:,}'.format)
    display_stats['Qty'] = display_stats['Qty'].astype(int) # কিউটি পূর্ণ সংখ্যা
    display_stats['Orders'] = display_stats['Orders'].astype(int)
    
    st.table(display_stats)

    # --- ৩. প্রোডাক্ট সেগমেন্ট ---
    st.markdown("<div class='section-header'>Product Analytics</div>", unsafe_allow_html=True)
    
    all_items = []
    for i in range(1, 16):
        if f'Product Name-{i}' in f_df.columns:
            temp = f_df[[f'Product Name-{i}', f'Product QTY-{i}', f'Product Price-{i}']].copy().dropna()
            temp.columns = ['Product', 'Qty', 'Price']
            all_items.append(temp)
    p_df = pd.concat(all_items)
    p_df = p_df[(p_df['Product'] != "0") & (p_df['Product'] != "") & (p_df['Product'].notna())]
    
    p_summary = p_df.groupby('Product').agg(
        Qty=('Qty', 'sum'),
        Revenue=('Qty', lambda x: (x * p_df.loc[x.index, 'Price']).sum())
    ).sort_values(by='Qty', ascending=False).reset_index()

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        fig_p_qty = px.bar(p_summary.head(10), x='Qty', y='Product', orientation='h', title="Top 10 Products by Qty", color='Qty', color_continuous_scale='YlOrRd', text_auto=True)
        fig_p_qty.update_layout(xaxis=dict(tickformat='d'))
        st.plotly_chart(fig_p_qty, use_container_width=True)
    with p_col2:
        fig_p_rev = px.pie(p_summary.head(8), values='Revenue', names='Product', title="Revenue Share by Product", hole=0.4)
        st.plotly_chart(fig_p_rev, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
