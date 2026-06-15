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

# ২. কাস্টম CSS (লিখা বড়, বোল্ড এবং সামারি কার্ড ইমপ্রুভমেন্ট)
st.markdown("""
    <style>
    /* পুরো পেজের টেক্সট গাঢ় কালো */
    html, body, [class*="css"] { color: #000000 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* হেডিং স্টাইল */
    .main-title { text-align: center; color: #FF6600; font-size: 55px; font-weight: 900; margin-top: -80px; margin-bottom: 5px; }
    .developer-text { text-align: center; font-style: italic; font-size: 20px; color: #333; font-weight: 600; }
    .slogan-text { text-align: center; font-size: 30px; font-weight: 800; color: #000; margin-top: 10px; }
    .vision-text { text-align: center; font-size: 20px; color: #444; font-weight: 600; margin-bottom: 30px; }
    
    /* সামারি কার্ড - কিছুটা বড় এবং বোল্ড */
    .metric-card { 
        background: white; 
        padding: 25px; /* আগের চেয়ে বড় প্যাডিং */
        border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        text-align: center; 
        border-top: 8px solid #FF6600; 
        margin-bottom: 20px;
    }
    .metric-label { font-size: 18px; color: #555; font-weight: 800; text-transform: uppercase; }
    .metric-value { font-size: 38px; color: #000; font-weight: 900; margin: 10px 0; }

    /* টেবিল ডাটা গাঢ় কালো এবং বোল্ড */
    .stTable, table { color: #000000 !important; font-weight: 700 !important; }
    
    .section-header { 
        font-size: 28px; font-weight: 900; color: #000; margin-top: 40px; margin-bottom: 20px; 
        border-left: 10px solid #FF6600; padding-left: 15px; background: #FFF5EE; padding-top: 10px; padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ৩. ডাটা লোডিং
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDhr-rwKe88LKKludd74G766j1l4vbvoaHi1YwwkefcfjCCgDGkZL6Ty9ngNv3gVvd5ezElgXghOs3/pub?gid=81417&single=true&output=csv"
    df = pd.read_csv(url)
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])
    
    # সব সংখ্যা পূর্ণ সংখ্যায় (Integer) রূপান্তর
    for col in ['Total Amount', 'Discount', 'Total Qty']:
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
    if os.path.exists(logo_path): st.image(logo_path, width=120)
    st.markdown('<div class="main-title">Tele Sales AI Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="developer-text">Web App Developed By-Shujoy Shaha</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan-text">ম্যানুয়েল কাজের দিন শেষ, বিজ্ঞানবাক্সে বাংলাদেশ</div>', unsafe_allow_html=True)
    st.markdown('<div class="vision-text">অন্যরকম বাংলাদেশের স্বপ্ন নিয়ে</div>', unsafe_allow_html=True)

    # --- সাইডবার ফিল্টার ---
    st.sidebar.header("📅 Select Reporting Period")
    today = datetime.date.today()
    start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=30), min_value=datetime.date(2024,1,1), max_value=datetime.date(2030,12,31))
    end_date = st.sidebar.date_input("End Date", today, min_value=datetime.date(2024,1,1), max_value=datetime.date(2030,12,31))
    f_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    # --- ১. টপ সামারি রিপোর্ট (বড় এবং বোল্ড) ---
    rev = int(f_df['Total Amount'].sum())
    ords = len(f_df)
    qty = int(f_df['Total Qty'].sum())
    dis = int(f_df['Discount'].sum())
    aov = int(rev/ords) if ords > 0 else 0
    dis_p = (dis/rev*100) if rev > 0 else 0

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    summary_data = [
        ("Revenue", f"৳{rev:,}"), ("Orders", f"{ords}"), ("AOV", f"৳{aov:,}"), 
        ("Total Qty", f"{qty:,}"), ("Discount", f"৳{dis:,}"), ("Discount %", f"{dis_p:.1f}%")
    ]
    for col, (label, value) in zip([m1, m2, m3, m4, m5, m6], summary_data):
        col.markdown(f"<div class='metric-card'><p class='metric-label'>{label}</p><p class='metric-value'>{value}</p></div>", unsafe_allow_html=True)

    # --- ২. এজেন্ট পারফরম্যান্স ---
    st.markdown("<div class='section-header'>Agent Performance (Person-wise)</div>", unsafe_allow_html=True)
    a_col1, a_col2 = st.columns(2)

    with a_col1:
        agent_rev = f_df.groupby('Order Collector')['Total Amount'].sum().sort_values(ascending=False).reset_index()
        fig_a_rev = px.bar(agent_rev, x='Total Amount', y='Order Collector', orientation='h', title="Revenue by Agent",
                          color='Total Amount', color_continuous_scale='Oranges', text_auto=True)
        fig_a_rev.update_traces(textfont=dict(size=14, color='black', family='Arial Black'), textangle=0)
        st.plotly_chart(fig_a_rev, use_container_width=True)

    with a_col2:
        agent_qty = f_df.groupby('Order Collector')['Total Qty'].sum().sort_values(ascending=False).reset_index()
        fig_a_qty = px.bar(agent_qty, x='Total Qty', y='Order Collector', orientation='h', title="Product Qty by Agent",
                          color='Total Qty', color_continuous_scale='Greens', text_auto=True)
        fig_a_qty.update_traces(textfont=dict(size=14, color='black', family='Arial Black'))
        fig_a_qty.update_layout(xaxis=dict(tickformat='d'))
        st.plotly_chart(fig_a_qty, use_container_width=True)

    # র‍্যাঙ্কিং টেবিল
    st.markdown("#### Team Ranking Table")
    agent_stats = f_df.groupby('Order Collector').agg(Revenue=('Total Amount', 'sum'), Orders=('Total Amount', 'count'), Qty=('Total Qty', 'sum')).sort_values(by='Revenue', ascending=False).reset_index()
    agent_stats['Rev %'] = (agent_stats['Revenue'] / rev * 100).map('{:.1f}%'.format)
    agent_stats['AOV'] = (agent_stats['Revenue'] / agent_stats['Orders']).fillna(0).astype(int).map('৳{:,}'.format)
    agent_stats['Revenue'] = agent_stats['Revenue'].map('৳{:,}'.format)
    st.table(agent_stats)

    # --- ৩. প্রোডাক্ট অ্যানালিটিক্স ---
    st.markdown("<div class='section-header'>Product Analytics</div>", unsafe_allow_html=True)
    
    all_items = []
    for i in range(1, 16):
        if f'Product Name-{i}' in f_df.columns:
            temp = f_df[[f'Product Name-{i}', f'Product QTY-{i}']].copy().dropna().rename(columns={f'Product Name-{i}': 'Product', f'Product QTY-{i}': 'Qty'})
            all_items.append(temp)
    p_df = pd.concat(all_items)
    p_df = p_df[(p_df['Product'] != "0") & (p_df['Product'] != "") & (p_df['Product'].notna())]
    p_summary = p_df.groupby('Product').agg(Qty=('Qty', 'sum')).sort_values(by='Qty', ascending=False).reset_index()

    fig_p_qty = px.bar(p_summary.head(10), x='Qty', y='Product', orientation='h', title="Top 10 Products by Qty", color='Qty', color_continuous_scale='YlOrRd', text_auto=True)
    fig_p_qty.update_traces(textfont=dict(size=14, color='black', family='Arial Black'))
    fig_p_qty.update_layout(xaxis=dict(tickformat='d'))
    st.plotly_chart(fig_p_qty, use_container_width=True)

    # --- ৪. কাস্টমার প্রোফাইল (ক্লাস, এজ, প্রফেশন, ডিস্ট্রিক্ট) ---
    st.markdown("<div class='section-header'>Customer Profile & Geographical Report</div>", unsafe_allow_html=True)
    
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        # ক্লাস ভিত্তিক রিপোর্ট
        class_stats = f_df['Class'].value_counts().reset_index().rename(columns={'count': 'Orders', 'Class': 'Student Class'})
        fig_class = px.bar(class_stats, x='Orders', y='Student Class', orientation='h', title="Class-wise Distribution", color='Orders', color_continuous_scale='Blues', text_auto=True)
        st.plotly_chart(fig_class, use_container_width=True)
        
    with c_col2:
        # বয়স ভিত্তিক রিপোর্ট
        age_stats = f_df['Age'].value_counts().reset_index().head(10).rename(columns={'count': 'Orders', 'Age': 'Age Group'})
        fig_age = px.bar(age_stats, x='Orders', y='Age Group', orientation='h', title="Age-wise Distribution", color='Orders', color_continuous_scale='Purples', text_auto=True)
        st.plotly_chart(fig_age, use_container_width=True)

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        # প্রফেশন ভিত্তিক রিপোর্ট
        prof_stats = f_df['Profession'].value_counts().reset_index().rename(columns={'count': 'Orders', 'Profession': 'Guardian Profession'})
        fig_prof = px.pie(prof_stats, values='Orders', names='Guardian Profession', title="Profession Distribution (%)", hole=0.4)
        st.plotly_chart(fig_prof, use_container_width=True)
        
    with d_col2:
        # জেলা ভিত্তিক রিপোর্ট
        dist_stats = f_df['District'].value_counts().reset_index().head(15).rename(columns={'count': 'Orders', 'District': 'District Name'})
        fig_dist = px.bar(dist_stats, x='Orders', y='District Name', orientation='h', title="Top 15 Districts by Orders", color='Orders', color_continuous_scale='Reds', text_auto=True)
        st.plotly_chart(fig_dist, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
