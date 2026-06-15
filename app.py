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

# ২. কাস্টম CSS (ছবিগুলোর মতো প্রফেশনাল লুক দিতে)
st.markdown("""
    <style>
    .reportview-container { background: #F8F9FB; }
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 5px solid #FF6600; }
    .insight-box { background: #2D2E5F; color: white; padding: 20px; border-radius: 12px; margin: 10px 0px; }
    .section-header { font-size: 22px; font-weight: bold; color: #1E1E1E; margin-bottom: 15px; padding-left: 5px; border-left: 5px solid #FF6600; }
    .stTable { background: white; border-radius: 10px; }
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
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    for i in range(1, 16):
        if f'Product QTY-{i}' in df.columns:
            df[f'Product QTY-{i}'] = pd.to_numeric(df[f'Product QTY-{i}'], errors='coerce').fillna(0)
            df[f'Product Price-{i}'] = pd.to_numeric(df[f'Product Price-{i}'], errors='coerce').fillna(0)
    return df

try:
    df = load_data()

    # --- হেডার ও লোগো ---
    h_col1, h_col2 = st.columns([1, 6])
    with h_col1:
        if os.path.exists(logo_path): st.image(logo_path, width=100)
    with h_col2:
        st.markdown(f"<h1 style='color:#FF6600; margin-top:-10px;'>Tele Sales AI Analytics Dashboard</h1>", unsafe_allow_html=True)

    # --- সাইডবার ফিল্টার ---
    st.sidebar.header("📅 Date Selection")
    today = datetime.date.today()
    start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=30))
    end_date = st.sidebar.date_input("End Date", today)
    f_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    # --- ১. টপ মেট্রিক্স (KPIs) ---
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    rev = f_df['Total Amount'].sum()
    ords = len(f_df)
    aov = rev/ords if ords > 0 else 0
    qty = f_df['Total Qty'].sum()
    dis = f_df['Discount'].sum()
    dis_p = (dis/rev*100) if rev > 0 else 0

    m1.markdown(f"<div class='metric-card'><p style='color:grey;'>Revenue</p><h3>৳{rev:,.0f}</h3></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card'><p style='color:grey;'>Orders</p><h3>{ords}</h3></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card'><p style='color:grey;'>AOV</p><h3>৳{aov:,.0f}</h3></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-card'><p style='color:grey;'>Product Qty</p><h3>{int(qty)}</h3></div>", unsafe_allow_html=True)
    m5.markdown(f"<div class='metric-card'><p style='color:grey;'>Discount</p><h3>৳{dis:,.0f}</h3></div>", unsafe_allow_html=True)
    m6.markdown(f"<div class='metric-card'><p style='color:grey;'>Discount %</p><h3>{dis_p:.1f}%</h3></div>", unsafe_allow_html=True)

    # --- ২. AI COO Insight ---
    top_agent = f_df.groupby('Order Collector')['Total Amount'].sum().idxmax() if len(f_df)>0 else "N/A"
    st.markdown(f"""
    <div class='insight-box'>
        <h4>🤖 AI Business Insight</h4>
        <p><b>{top_agent}</b> is currently leading in revenue. Most orders are single product orders. 
        Focus on multi-product bundles to increase AOV (Average Order Value).</p>
    </div>
    """, unsafe_allow_html=True)

    # --- ৩. এজেন্ট সেগমেন্ট (Person-wise Analysis) ---
    st.markdown("<div class='section-header'>Agent Performance (Person-wise)</div>", unsafe_allow_html=True)
    a_col1, a_col2 = st.columns(2)

    with a_col1:
        agent_rev = f_df.groupby('Order Collector')['Total Amount'].sum().sort_values(ascending=False).reset_index()
        fig_a_rev = px.bar(agent_rev, x='Total Amount', y='Order Collector', orientation='h', title="Revenue Contribution by Person",
                          color='Total Amount', color_continuous_scale='Blues', text_auto='.2s')
        st.plotly_chart(fig_a_rev, use_container_width=True)

    with a_col2:
        agent_qty = f_df.groupby('Order Collector')['Total Qty'].sum().sort_values(ascending=False).reset_index()
        fig_a_qty = px.bar(agent_qty, x='Total Qty', y='Order Collector', orientation='h', title="Product Qty Contribution by Person",
                          color='Total Qty', color_continuous_scale='Greens', text_auto=True)
        st.plotly_chart(fig_a_qty, use_container_width=True)

    # Agent Ranking Table
    st.markdown("#### Team Ranking with Contribution %")
    agent_stats = f_df.groupby('Order Collector').agg(
        Revenue=('Total Amount', 'sum'),
        Orders=('Total Amount', 'count'),
        Qty=('Total Qty', 'sum')
    ).sort_values(by='Revenue', ascending=False).reset_index()
    agent_stats['Rev %'] = (agent_stats['Revenue'] / rev * 100).map('{:.1f}%'.format)
    agent_stats['AOV'] = (agent_stats['Revenue'] / agent_stats['Orders']).map('৳{:.0f}'.format)
    st.table(agent_stats)

    # --- ৪. প্রোডাক্ট সেগমেন্ট ---
    st.markdown("<div class='section-header'>Product Analytics</div>", unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)

    # মেल्टিং প্রোডাক্ট ডাটা (সবগুলো আইটেম এক করার জন্য)
    all_items = []
    for i in range(1, 16):
        if f'Product Name-{i}' in f_df.columns:
            temp = f_df[[f'Product Name-{i}', f'Product QTY-{i}', f'Product Price-{i}']].copy().dropna()
            temp.columns = ['Product', 'Qty', 'Price']
            all_items.append(temp)
    p_df = pd.concat(all_items)
    p_df = p_df[(p_df['Product'] != "0") & (p_df['Product'] != "")]
    p_df['Revenue'] = p_df['Qty'] * p_df['Price']
    p_summary = p_df.groupby('Product').agg({'Qty': 'sum', 'Revenue': 'sum'}).sort_values(by='Qty', ascending=False).reset_index()

    with p_col1:
        fig_p_qty = px.bar(p_summary.head(10), x='Qty', y='Product', orientation='h', title="Top 10 Products by Qty", color='Qty', color_continuous_scale='YlOrRd')
        st.plotly_chart(fig_p_qty, use_container_width=True)
    with p_col2:
        fig_p_rev = px.pie(p_summary.head(8), values='Revenue', names='Product', title="Revenue Share by Product", hole=0.4)
        st.plotly_chart(fig_p_rev, use_container_width=True)

    # --- ৫. এরিয়া ও ডেমোগ্রাফিক সেগমেন্ট ---
    st.markdown("<div class='section-header'>Area & Demographics</div>", unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)

    with d1:
        dist_rev = f_df.groupby('District')['Total Amount'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_dist = px.bar(dist_rev, x='Total Amount', y='District', orientation='h', title="Top 10 Districts (Revenue)", color_discrete_sequence=['#3B82F6'])
        st.plotly_chart(fig_dist, use_container_width=True)
    with d2:
        fig_class = px.pie(f_df, names='Class', title="Class-wise Contribution", hole=0.4)
        st.plotly_chart(fig_class, use_container_width=True)
    with d3:
        f_df['Order_Type'] = f_df['Total Qty'].apply(lambda x: "Single" if x==1 else ("Double" if x==2 else "Multi"))
        fig_type = px.pie(f_df, names='Order_Type', title="Order Complexity (Single/Double/Multi)", color_discrete_sequence=['#FF6600', '#2D2E5F', '#E5E7EB'])
        st.plotly_chart(fig_type, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
