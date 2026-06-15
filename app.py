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

# ২. কাস্টম CSS (সামারি জুম করা, ডার্ক গ্রে টেক্সট এবং কালারড হেডিং)
st.markdown("""
    <style>
    /* টেক্সট কালার ডার্ক গ্রে */
    html, body, [class*="css"] { 
        color: #333333 !important; 
        font-family: 'Segoe UI', sans-serif; 
    }
    
    /* মেইন টাইটেল এবং স্লোগান */
    .main-title { text-align: center; color: #FF6600; font-size: 55px; font-weight: 800; margin-top: -80px; margin-bottom: 5px; }
    .developer-text { text-align: center; font-style: italic; font-size: 18px; color: #666; margin-bottom: 10px; }
    .slogan-text { text-align: center; font-size: 30px; font-weight: 800; color: #222; margin-top: 10px; }
    .vision-text { text-align: center; font-size: 20px; color: #777; margin-bottom: 30px; }
    
    /* সামারি সেকশন জুম করা (বিশাল কার্ড) */
    .metric-card { 
        background: #FFFFFF; 
        padding: 40px 15px; 
        border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); 
        text-align: center; 
        border-top: 8px solid #FF6600; 
        margin-bottom: 25px;
    }
    .metric-label { font-size: 22px; color: #555; margin-bottom: 15px; font-weight: 600; }
    .metric-value { font-size: 50px; color: #333; margin: 0; font-weight: 700; }

    /* প্রতিটি রিপোর্ট সেকশনের কালারড হেডিং */
    .section-header { 
        font-size: 28px; 
        color: #333; 
        background-color: #F0F2F6; 
        padding: 12px 20px; 
        border-radius: 8px; 
        border-left: 10px solid #FF6600; 
        margin-top: 45px; 
        margin-bottom: 25px; 
        font-weight: 700;
    }
    
    /* টেবিল স্টাইল */
    .stTable { color: #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

# ৩. ডাটা লোডিং
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDhr-rwKe88LKKludd74G766j1l4vbvoaHi1YwwkefcfjCCgDGkZL6Ty9ngNv3gVvd5ezElgXghOs3/pub?gid=81417&single=true&output=csv"
    df = pd.read_csv(url)
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])
    
    # সব সংখ্যা পূর্ণ সংখ্যায় রূপান্তর
    cols = ['Total Amount', 'Discount', 'Total Qty']
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    for i in range(1, 16):
        if f'Product QTY-{i}' in df.columns:
            df[f'Product QTY-{i}'] = pd.to_numeric(df[f'Product QTY-{i}'], errors='coerce').fillna(0).astype(int)
        if f'Product Price-{i}' in df.columns:
            df[f'Product Price-{i}'] = pd.to_numeric(df[f'Product Price-{i}'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df = load_data()

    # --- হেডার ও লোগো ---
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
    
    st.markdown('<div class="main-title">Tele Sales AI Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="developer-text">Web App Developed By-Shujoy Shaha</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan-text">ম্যানুয়েল কাজের দিন শেষ, বিজ্ঞানবাক্সে বাংলাদেশ</div>', unsafe_allow_html=True)
    st.markdown('<div class="vision-text">অন্যরকম বাংলাদেশের স্বপ্ন নিয়ে</div>', unsafe_allow_html=True)
    st.markdown("---")

    # --- সাইডবার ফিল্টার ---
    st.sidebar.header("📅 Select Date Range")
    today = datetime.date.today()
    start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=30), min_value=datetime.date(2024,1,1), max_value=datetime.date(2030,12,31))
    end_date = st.sidebar.date_input("End Date", today, min_value=datetime.date(2024,1,1), max_value=datetime.date(2030,12,31))
    f_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    # --- ১. সামারি রিপোর্ট (বিশাল বড় জুম করা) ---
    rev = int(f_df['Total Amount'].sum())
    ords = len(f_df)
    qty = int(f_df['Total Qty'].sum())
    dis = int(f_df['Discount'].sum())
    aov = int(rev/ords) if ords > 0 else 0
    dis_p = (dis/rev*100) if rev > 0 else 0

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    summaries = [
        ("Revenue", f"৳{rev:,}"), ("Orders", f"{ords}"), ("AOV", f"৳{aov:,}"),
        ("Product Qty", f"{qty:,}"), ("Discount", f"৳{dis:,}"), ("Discount %", f"{dis_p:.1f}%")
    ]
    for col, (label, value) in zip([m1, m2, m3, m4, m5, m6], summaries):
        col.markdown(f"<div class='metric-card'><p class='metric-label'>{label}</p><p class='metric-value'>{value}</p></div>", unsafe_allow_html=True)

    # --- ২. এজেন্ট রিপোর্ট সেকশন ---
    st.markdown('<div class="section-header">Agent Performance Report</div>', unsafe_allow_html=True)
    a_col1, a_col2 = st.columns(2)
    
    agent_data = f_df.groupby('Order Collector').agg(Revenue=('Total Amount', 'sum'), Orders=('Total Amount', 'count'), Qty=('Total Qty', 'sum')).sort_values(by='Revenue', ascending=False).reset_index()

    with a_col1:
        fig_a = px.bar(agent_data, x='Revenue', y='Order Collector', orientation='h', title="Revenue by Agent", color_discrete_sequence=['#FF6600'], text_auto=True)
        fig_a.update_traces(textangle=0, textposition='outside') # টেক্সট সোজা করার কমান্ড
        st.plotly_chart(fig_a, use_container_width=True)
    with a_col2:
        # টেবিল থেকে অতিরিক্ত শূন্য সরানো হয়েছে
        disp_agent = agent_data.copy()
        disp_agent['Revenue'] = disp_agent['Revenue'].map('৳{:,}'.format)
        st.table(disp_agent)

    # --- ৩. প্রোডাক্ট রিপোর্ট সেকশন ---
    st.markdown('<div class="section-header">Product Sales Analytics</div>', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)

    all_items = []
    for i in range(1, 16):
        if f'Product Name-{i}' in f_df.columns:
            temp = f_df[[f'Product Name-{i}', f'Product QTY-{i}']].copy().dropna().rename(columns={f'Product Name-{i}': 'Product', f'Product QTY-{i}': 'Qty'})
            all_items.append(temp)
    p_df = pd.concat(all_items)
    p_df = p_df[(p_df['Product'] != "0") & (p_df['Product'] != "")]
    p_summary = p_df.groupby('Product').agg(Qty=('Qty', 'sum')).sort_values(by='Qty', ascending=False).reset_index()

    with p_col1:
        fig_p = px.bar(p_summary.head(10), x='Qty', y='Product', orientation='h', title="Top 10 Products by Qty", color='Qty', color_continuous_scale='Oranges', text_auto=True)
        fig_p.update_traces(textangle=0, textposition='inside') # টেক্সট সোজা করা হয়েছে
        fig_p.update_layout(xaxis=dict(tickformat='d'))
        st.plotly_chart(fig_p, use_container_width=True)
    with p_col2:
        st.table(p_summary.head(10))

    # --- ৪. কাস্টমার রিপোর্ট সেকশন (ক্লাস, এজ, প্রফেশন, ডিসট্রিক্ট) ---
    st.markdown('<div class="section-header">Customer Demographics & Location Analytics</div>', unsafe_allow_html=True)
    
    # Row 1: Class and Age
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.markdown("#### Class-wise Order Distribution")
        class_stats = f_df['Class'].value_counts().reset_index()
        fig_cl = px.pie(class_stats, values='count', names='Class', hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_cl, use_container_width=True)
        
    with c_col2:
        st.markdown("#### Top Age Groups")
        age_stats = f_df['Age'].value_counts().reset_index().head(10)
        fig_ag = px.bar(age_stats, x='count', y='Age', orientation='h', color_discrete_sequence=['#333333'], text_auto=True)
        fig_ag.update_traces(textangle=0)
        st.plotly_chart(fig_ag, use_container_width=True)

    # Row 2: Profession and District
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.markdown("#### Guardian's Profession (Table)")
        prof_stats = f_df['Profession'].value_counts().reset_index().rename(columns={'count': 'Orders'})
        st.table(prof_stats.head(10))
        
    with d_col2:
        st.markdown("#### Top 15 Districts by Revenue")
        dist_stats = f_df.groupby('District')['Total Amount'].sum().reset_index().sort_values(by='Total Amount', ascending=False).head(15)
        fig_dt = px.bar(dist_stats, x='Total Amount', y='District', orientation='h', color='Total Amount', color_continuous_scale='Greens', text_auto='.2s')
        fig_dt.update_traces(textangle=0)
        st.plotly_chart(fig_dt, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
