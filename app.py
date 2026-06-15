import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os

# পেজ সেটিংস
st.set_page_config(page_title="Bigganbaksho Tele Sales Analytics", layout="wide", page_icon="📊")

# ৩. লোগো চেক (যদি রিপোজিটরিতে থাকে)
logo_path = "logo.jpg"

# ২. ডাটা লোডিং ফাংশন (আপনার লাইভ লিঙ্কের সাথে কানেক্ট করা)
@st.cache_data(ttl=300)
def load_live_data():
    # আপনার দেওয়া নির্দিষ্ট ট্যাবের লিঙ্ক
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDhr-rwKe88LKKludd74G766j1l4vbvoaHi1YwwkefcfjCCgDGkZL6Ty9ngNv3gVvd5ezElgXghOs3/pub?gid=81417&single=true&output=csv"
    df = pd.read_csv(url)
    
    # ডাটা ক্লিনআপ
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])
    
    numeric_cols = ['Total Amount', 'Discount', 'Total Qty', 'Shipping Charge']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

# অ্যাপ ইন্টারফেস ডিজাইন
st.markdown("""
    <style>
    .main-title { text-align: center; color: #FF6600; font-size: 50px; font-weight: bold; margin-bottom: 10px; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #FF6600; }
    </style>
    """, unsafe_allow_html=True)

try:
    df = load_live_data()

    # সাইডবার ফিল্টার
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=120)
    
    st.sidebar.title("🔍 Report Filters")
    min_date = df['Order Date'].min().date()
    max_date = df['Order Date'].max().date()
    
    date_range = st.sidebar.date_input("সিলেক্ট সময়কাল", [min_date, max_date])

    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        f_df = df[(df['Order Date'] >= start_date) & (df['Order Date'] <= end_date)]
    else:
        f_df = df

    # ড্যাশবোর্ড টাইটেল
    st.markdown('<p class="main-title">Tele Sales Analytics Dashboard</p>', unsafe_allow_html=True)
    st.write(f"সব ডাটা সরাসরি **'টেলি সেলস'** ট্যাব থেকে আপডেট হচ্ছে। সময়কাল: **{date_range[0]}** থেকে **{date_range[1]}**")
    st.markdown("---")

    # --- KPI Section ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Revenue", f"৳{f_df['Total Amount'].sum():,.0f}")
    k2.metric("Total Orders", f"{len(f_df)}")
    k3.metric("Items Sold", f"{int(f_df['Total Qty'].sum())}")
    k4.metric("Total Discount", f"৳{f_df['Discount'].sum():,.0f}")

    # --- Row 1: Sales Trend & Order Complexity ---
    st.markdown("### 📈 Sales Performance")
    r1_c1, r1_c2 = st.columns([2, 1])
    
    with r1_c1:
        trend = f_df.groupby(f_df['Order Date'].dt.date)['Total Amount'].sum().reset_index()
        fig_trend = px.line(trend, x='Order Date', y='Total Amount', title="Daily Revenue Trend", markers=True, color_discrete_sequence=['#FF6600'])
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with r1_c2:
        f_df['Order_Complexity'] = f_df['Total Qty'].apply(lambda x: "Single Product" if x == 1 else "Double/Multiple")
        complexity = f_df['Order_Complexity'].value_counts().reset_index()
        fig_comp = px.pie(complexity, values='count', names='Order_Complexity', title="Single vs Double Order (%)", hole=0.4, color_discrete_sequence=['#FF6600', '#333'])
        st.plotly_chart(fig_comp, use_container_width=True)

    # --- Row 2: Product & Agent (Person Wise) ---
    st.markdown("---")
    r2_c1, r2_c2 = st.columns(2)

    with r2_c1:
        st.markdown("### 📦 Product Wise Qty")
        prod_data = []
        for i in range(1, 16):
            if f'Product Name-{i}' in f_df.columns:
                temp = f_df[[f'Product Name-{i}', f'Product QTY-{i}']].copy().rename(columns={f'Product Name-{i}': 'Product', f'Product QTY-{i}': 'Qty'})
                prod_data.append(temp)
        all_prods = pd.concat(prod_data)
        all_prods = all_prods[(all_prods['Product'] != "0") & (all_prods['Product'].notna()) & (all_prods['Product'] != "")]
        all_prods['Qty'] = pd.to_numeric(all_prods['Qty'], errors='coerce').fillna(0)
        p_stats = all_prods.groupby('Product')['Qty'].sum().reset_index().sort_values('Qty', ascending=False)
        
        fig_p = px.bar(p_stats.head(10), x='Qty', y='Product', orientation='h', title="Top 10 Products by Qty", color='Qty', color_continuous_scale='Oranges')
        st.plotly_chart(fig_p, use_container_width=True)

    with r2_c2:
        st.markdown("### 👥 Agent Wise Total (Person Wise)")
        agent_stats = f_df.groupby('Order Collector')['Total Amount'].sum().reset_index().sort_values('Total Amount', ascending=False)
        fig_a = px.bar(agent_stats, x='Order Collector', y='Total Amount', title="Revenue by Agent", color='Total Amount', color_continuous_scale='YlOrBr')
        st.plotly_chart(fig_a, use_container_width=True)

    # --- Row 3: Demographics (Age, Class, Profession) ---
    st.markdown("---")
    st.markdown("### 👤 Customer Profile Analysis")
    r3_c1, r3_c2, r3_c3 = st.columns(3)

    with r3_c1:
        fig_class = px.pie(f_df, names='Class', title="Class-wise Distribution (%)", hole=0.3)
        st.plotly_chart(fig_class, use_container_width=True)
    with r3_c2:
        age_s = f_df['Age'].value_counts().reset_index().head(10)
        fig_age = px.bar(age_s, x='Age', y='count', title="Age-wise Sales", color_discrete_sequence=['#FF6600'])
        st.plotly_chart(fig_age, use_container_width=True)
    with r3_c3:
        fig_prof = px.pie(f_df, names='Profession', title="Profession-wise (%)")
        st.plotly_chart(fig_prof, use_container_width=True)

    # --- Row 4: Geography (District & Sub-District) ---
    st.markdown("---")
    st.markdown("### 📍 Geographical Performance")
    r4_c1, r4_c2 = st.columns(2)

    with r4_c1:
        dist_s = f_df['District'].value_counts().reset_index().head(15)
        fig_dist = px.bar(dist_s, x='count', y='District', orientation='h', title="Top 15 Districts", color_discrete_sequence=['#333'])
        st.plotly_chart(fig_dist, use_container_width=True)
    with r4_c2:
        sub_s = f_df['Sub District'].value_counts().reset_index().head(15)
        fig_sub = px.bar(sub_s, x='count', y='Sub District', orientation='h', title="Top 15 Sub-Districts", color_discrete_sequence=['#FF6600'])
        st.plotly_chart(fig_sub, use_container_width=True)

    # Raw Data Check
    if st.sidebar.checkbox("Show Raw Data Table"):
        st.markdown("### 📄 Filtered Data Details")
        st.dataframe(f_df)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("আপনার গুগল শীটটি CSV হিসেবে পাবলিশ করা হয়েছে কি না নিশ্চিত করুন।")
