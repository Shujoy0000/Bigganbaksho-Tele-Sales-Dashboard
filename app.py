import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os

# লোগো ফাইলের নাম চেক করা (ব্রাউজার আইকনের জন্য)
logo_path = "logo.png"
if not os.path.exists(logo_path):
    logo_path = "logo.jpg"

# ১. পেজ সেটিংস
st.set_page_config(
    page_title="Tele Sales Analytics Dashboard", 
    layout="wide", 
    page_icon=logo_path if os.path.exists(logo_path) else "📊"
)

# ২. CSS দিয়ে প্রফেশনাল ডিজাইন
st.markdown("""
    <style>
    .main-title { 
        text-align: center; 
        color: #FF6600; 
        font-size: 65px; 
        font-weight: 800; 
        margin-top: -30px; 
        margin-bottom: 10px; 
        line-height: 1.1;
        font-family: 'Source Sans Pro', sans-serif;
    }
    .developer-text { 
        text-align: center; 
        font-style: italic; 
        font-size: 20px; 
        color: #555; 
        margin-top: 0px; 
        margin-bottom: 30px;
    }
    .slogan-text { 
        text-align: center; 
        font-size: 34px; 
        font-weight: 800; 
        color: #000; 
        margin-top: 10px; 
    }
    .vision-text { 
        text-align: center; 
        font-size: 24px; 
        color: #666; 
        margin-bottom: 40px; 
    }
    .stMetric { background-color: #fff5eb; padding: 15px; border-radius: 10px; border-left: 5px solid #FF6600; }
    </style>
    """, unsafe_allow_html=True)

# ৩. লোগো প্রদর্শন (মাঝখানে)
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)

# ৪. টেক্সট সেকশন
st.markdown('<div class="main-title">Tele Sales Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="developer-text">Web App Developed By-Shujoy Shaha</div>', unsafe_allow_html=True)
st.markdown('<div class="slogan-text">ম্যানুয়েল কাজের দিন শেষ, বিজ্ঞানবাক্সে বাংলাদেশ</div>', unsafe_allow_html=True)
st.markdown('<div class="vision-text">অন্যরকম বাংলাদেশের স্বপ্ন নিয়ে</div>', unsafe_allow_html=True)

st.markdown("---")

# ৫. ডাটা লোডিং ফাংশন
@st.cache_data(ttl=300)
def load_live_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDhr-rwKe88LKKludd74G766j1l4vbvoaHi1YwwkefcfjCCgDGkZL6Ty9ngNv3gVvd5ezElgXghOs3/pub?gid=81417&single=true&output=csv"
    df = pd.read_csv(url)
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])
    numeric_cols = ['Total Amount', 'Discount', 'Total Qty', 'Shipping Charge']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

try:
    df = load_live_data()

    # --- ডেট ফিল্টার (সহজ করা হয়েছে) ---
    st.sidebar.title("📅 সময়কাল নির্বাচন করুন")
    min_d = df['Order Date'].min().date()
    max_d = df['Order Date'].max().date()
    
    start_date = st.sidebar.date_input("শুরু (Start Date)", min_d)
    end_date = st.sidebar.date_input("শেষ (End Date)", max_d)

    # ফিল্টারিং লজিক
    f_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    # --- KPI মেট্রিক্স ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("মোট রেভিনিউ", f"৳{f_df['Total Amount'].sum():,.0f}")
    m2.metric("মোট অর্ডার", f"{len(f_df)}")
    m3.metric("বিক্রিত পণ্য", f"{int(f_df['Total Qty'].sum())}")
    m4.metric("মোট ডিসকাউন্ট", f"৳{f_df['Discount'].sum():,.0f}")

    # --- চার্টস Row 1 ---
    st.markdown("### 📈 সেলস ট্রেন্ড এবং অর্ডারের ধরণ")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        trend = f_df.groupby(f_df['Order Date'].dt.date)['Total Amount'].sum().reset_index()
        fig_trend = px.area(trend, x='Order Date', y='Total Amount', title="প্রতিদিনের সেলস গ্রাফ", color_discrete_sequence=['#FF6600'])
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with c2:
        f_df['Order_Type'] = f_df['Total Qty'].apply(lambda x: "সিঙ্গেল প্রোডাক্ট" if x == 1 else "মাল্টিপল প্রোডাক্ট")
        complexity = f_df['Order_Type'].value_counts().reset_index()
        fig_comp = px.pie(complexity, values='count', names='Order_Type', title="সিঙ্গেল বনাম ডাবল অর্ডার (%)", hole=0.4, color_discrete_sequence=['#FF6600', '#333'])
        st.plotly_chart(fig_comp, use_container_width=True)

    # --- চার্টস Row 2 ---
    st.markdown("---")
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### 📦 টপ ১০ প্রোডাক্ট (পরিমাণ অনুযায়ী)")
        prod_list = []
        for i in range(1, 16):
            if f'Product Name-{i}' in f_df.columns:
                temp = f_df[[f'Product Name-{i}', f'Product QTY-{i}']].copy().rename(columns={f'Product Name-{i}': 'Product', f'Product QTY-{i}': 'Qty'})
                prod_list.append(temp)
        all_p = pd.concat(prod_list)
        all_p = all_p[(all_p['Product'] != "0") & (all_p['Product'].notna()) & (all_p['Product'] != "")]
        p_stats = all_p.groupby('Product')['Qty'].sum().reset_index().sort_values('Qty', ascending=False)
        fig_p = px.bar(p_stats.head(10), x='Qty', y='Product', orientation='h', color='Qty', color_continuous_scale='Oranges')
        st.plotly_chart(fig_p, use_container_width=True)

    with c4:
        st.markdown("#### 👥 এজেন্ট ভিত্তিক সেলস (Person Wise Total)")
        agent_s = f_df.groupby('Order Collector')['Total Amount'].sum().reset_index().sort_values('Total Amount', ascending=False)
        fig_a = px.bar(agent_s, x='Order Collector', y='Total Amount', color='Total Amount', color_continuous_scale='YlOrBr')
        st.plotly_chart(fig_a, use_container_width=True)

    # --- চার্টস Row 3 ---
    st.markdown("---")
    st.markdown("### 👤 কাস্টমার প্রোফাইল এবং জেলা ভিত্তিক রিপোর্ট")
    c5, c6, c7 = st.columns(3)
    with c5:
        fig_cl = px.pie(f_df, names='Class', title="ক্লাস ভিত্তিক সেলস (%)", hole=0.3)
        st.plotly_chart(fig_cl, use_container_width=True)
    with c6:
        age_data = f_df['Age'].value_counts().reset_index().head(10)
        fig_ag = px.bar(age_data, x='Age', y='count', title="বয়স ভিত্তিক সেলস", color_discrete_sequence=['#FF6600'])
        st.plotly_chart(fig_ag, use_container_width=True)
    with c7:
        fig_pr = px.pie(f_df, names='Profession', title="পেশা ভিত্তিক ডিস্ট্রিবিউশন (%)")
        st.plotly_chart(fig_pr, use_container_width=True)

    # জেলা ভিত্তিক
    st.markdown("---")
    c8, c9 = st.columns(2)
    with c8:
        dist_data = f_df['District'].value_counts().reset_index().head(15)
        fig_dt = px.bar(dist_data, x='count', y='District', orientation='h', title="টপ ১৫ জেলা", color_discrete_sequence=['#333'])
        st.plotly_chart(fig_dt, use_container_width=True)
    with c9:
        sub_data = f_df['Sub District'].value_counts().reset_index().head(15)
        fig_sd = px.bar(sub_data, x='count', y='Sub District', orientation='h', title="টপ ১৫ উপজেলা", color_discrete_sequence=['#FF6600'])
        st.plotly_chart(fig_sd, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
