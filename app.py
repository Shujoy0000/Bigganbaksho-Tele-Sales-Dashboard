import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
import datetime

# লোগো চেক
logo_path = "logo.png"
if not os.path.exists(logo_path):
    logo_path = "logo.jpg"

# ১. পেজ সেটিংস
st.set_page_config(
    page_title="Tele Sales Analytics Dashboard", 
    layout="wide", 
    page_icon=logo_path if os.path.exists(logo_path) else "📊"
)

# ২. কাস্টম CSS (ডিজাইন আরও টাইট এবং লোগো পজিশনিং)
st.markdown("""
    <style>
    /* লোগো বামে সেট করা */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    .main-title { 
        text-align: center; 
        color: #FF6600; 
        font-size: 50px; 
        font-weight: 800; 
        margin-top: -80px; 
        margin-bottom: 5px;
        line-height: 1;
    }
    .developer-text { 
        text-align: center; 
        font-style: italic; 
        font-size: 16px; 
        color: #555; 
        margin-bottom: 5px;
    }
    .slogan-text { 
        text-align: center; 
        font-size: 24px; 
        font-weight: 700; 
        color: #000; 
        margin-top: 0px; 
        margin-bottom: 5px;
    }
    .vision-text { 
        text-align: center; 
        font-size: 16px; 
        color: #666; 
        margin-bottom: 10px; 
    }
    .stMetric { 
        background-color: #ffffff; 
        padding: 10px; 
        border-radius: 8px; 
        border: 1px solid #e0e0e0;
        border-left: 5px solid #FF6600; 
    }
    </style>
    """, unsafe_allow_html=True)

# লোগো প্রদর্শন (Top-Left)
if os.path.exists(logo_path):
    st.image(logo_path, width=100)

# টেক্সট সেকশন
st.markdown('<div class="main-title">Tele Sales Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="developer-text">Web App Developed By-Shujoy Shaha</div>', unsafe_allow_html=True)
st.markdown('<div class="slogan-text">ম্যানুয়েল কাজের দিন শেষ, বিজ্ঞানবাক্সে বাংলাদেশ</div>', unsafe_allow_html=True)
st.markdown('<div class="vision-text">অন্যরকম বাংলাদেশের স্বপ্ন নিয়ে</div>', unsafe_allow_html=True)
st.markdown("<hr style='margin:10px 0px;'>", unsafe_allow_html=True)

# ৩. ডাটা লোডিং ফাংশন
@st.cache_data(ttl=300)
def load_live_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDhr-rwKe88LKKludd74G766j1l4vbvoaHi1YwwkefcfjCCgDGkZL6Ty9ngNv3gVvd5ezElgXghOs3/pub?gid=81417&single=true&output=csv"
    df = pd.read_csv(url)
    
    # ডেট ঠিক করা
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])
    
    # নিউমেরিক ডাটা ঠিক করা
    numeric_cols = ['Total Amount', 'Discount', 'Total Qty', 'Shipping Charge']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    for i in range(1, 16):
        qty_col = f'Product QTY-{i}'
        if qty_col in df.columns:
            df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)
            
    return df

try:
    df = load_live_data()

    # --- সাইডবার ফিল্টার (ডেট রেঞ্জ ফিক্সড) ---
    st.sidebar.header("Filter by Date")
    
    # বর্তমান ডেট এবং রেঞ্জ ঠিক করা
    today = datetime.date.today()
    start_of_range = datetime.date(2024, 1, 1)
    end_of_range = datetime.date(2030, 12, 31)

    start_date = st.sidebar.date_input("Start Date", today, min_value=start_of_range, max_value=end_of_range)
    end_date = st.sidebar.date_input("End Date", today, min_value=start_of_range, max_value=end_of_range)

    # ফিল্টারিং
    f_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    # --- KPI Metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Revenue", f"৳{f_df['Total Amount'].sum():,.0f}")
    m2.metric("Total Orders", f"{len(f_df)}")
    m3.metric("Items Sold", f"{int(f_df['Total Qty'].sum())}")
    m4.metric("Total Discount", f"৳{f_df['Discount'].sum():,.0f}")

    # --- Row 1: Charts ---
    st.markdown("#### 📈 Sales Trends & Types")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        trend = f_df.groupby(f_df['Order Date'].dt.date)['Total Amount'].sum().reset_index()
        fig_trend = px.area(trend, x='Order Date', y='Total Amount', title="Daily Revenue Trend", color_discrete_sequence=['#FF6600'])
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with c2:
        f_df['Order_Type'] = f_df['Total Qty'].apply(lambda x: "Single Item" if x == 1 else "Multiple Items")
        complexity = f_df['Order_Type'].value_counts().reset_index()
        fig_comp = px.pie(complexity, values='count', names='Order_Type', title="Order Distribution (%)", hole=0.4, color_discrete_sequence=['#FF6600', '#333'])
        st.plotly_chart(fig_comp, use_container_width=True)

    # --- Row 2: Performance ---
    st.markdown("<hr style='margin:10px 0px;'>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        prod_list = []
        for i in range(1, 16):
            if f'Product Name-{i}' in f_df.columns:
                temp = f_df[[f'Product Name-{i}', f'Product QTY-{i}']].copy().rename(columns={f'Product Name-{i}': 'Product', f'Product QTY-{i}': 'Qty'})
                prod_list.append(temp)
        all_p = pd.concat(prod_list)
        all_p = all_p[(all_p['Product'] != "0") & (all_p['Product'].notna()) & (all_p['Product'] != "")]
        p_stats = all_p.groupby('Product')['Qty'].sum().reset_index().sort_values('Qty', ascending=False)
        fig_p = px.bar(p_stats.head(10), x='Qty', y='Product', orientation='h', color='Qty', color_continuous_scale='Oranges', title="Top 10 Products by Qty")
        st.plotly_chart(fig_p, use_container_width=True)

    with c4:
        agent_s = f_df.groupby('Order Collector')['Total Amount'].sum().reset_index().sort_values('Total Amount', ascending=False)
        fig_a = px.bar(agent_s, x='Order Collector', y='Total Amount', color='Total Amount', color_continuous_scale='YlOrBr', title="Revenue per Agent")
        st.plotly_chart(fig_a, use_container_width=True)

    # --- Row 3: Demographics ---
    st.markdown("<hr style='margin:10px 0px;'>", unsafe_allow_html=True)
    st.markdown("#### 👤 Customer Profile Analysis")
    c5, c6, c7 = st.columns(3)
    with c5:
        fig_cl = px.pie(f_df, names='Class', title="Class Distribution", hole=0.3)
        st.plotly_chart(fig_cl, use_container_width=True)
    with c6:
        age_data = f_df['Age'].value_counts().reset_index().head(10)
        fig_ag = px.bar(age_data, x='Age', y='count', title="Sales by Age Group", color_discrete_sequence=['#FF6600'])
        st.plotly_chart(fig_ag, use_container_width=True)
    with c7:
        fig_pr = px.pie(f_df, names='Profession', title="Profession Distribution")
        st.plotly_chart(fig_pr, use_container_width=True)

    # --- Row 4: Geography ---
    st.markdown("<hr style='margin:10px 0px;'>", unsafe_allow_html=True)
    st.markdown("#### 📍 Geographical Analysis")
    c8, c9 = st.columns(2)
    with c8:
        dist_data = f_df['District'].value_counts().reset_index().head(15)
        fig_dt = px.bar(dist_data, x='count', y='District', orientation='h', title="Top 15 Districts", color_discrete_sequence=['#333'])
        st.plotly_chart(fig_dt, use_container_width=True)
    with c9:
        sub_data = f_df['Sub District'].value_counts().reset_index().head(15)
        fig_sd = px.bar(sub_data, x='count', y='Sub District', orientation='h', title="Top 15 Sub Districts", color_discrete_sequence=['#FF6600'])
        st.plotly_chart(fig_sd, use_container_width=True)

except Exception as e:
    st.error(f"Something went wrong: {e}")
