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

# ২. কাস্টম CSS (বিশাল বড় সামারি এবং প্রফেশনাল ডিজাইন)
st.markdown("""
    <style>
    /* টেক্সট কালার ডার্ক গ্রে */
    html, body, [class*="css"] { 
        color: #333333 !important; 
        font-family: 'Segoe UI', sans-serif; 
    }
    
    /* হেডিং পজিশন */
    .main-title { text-align: center; color: #FF6600; font-size: 55px; font-weight: 800; margin-top: -80px; margin-bottom: 5px; }
    .developer-text { text-align: center; font-style: italic; font-size: 20px; color: #666; margin-bottom: 10px; }
    .slogan-text { text-align: center; font-size: 30px; font-weight: 800; color: #222; margin-top: 10px; }
    .vision-text { text-align: center; font-size: 20px; color: #777; margin-bottom: 30px; }
    
    /* বিশাল বড় সামারি কার্ড (১৫০ পিক্সেল সংখ্যা) */
    .metric-card { 
        background: #FFFFFF; 
        padding: 20px; 
        border-radius: 20px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); 
        text-align: center; 
        border-top: 10px solid #FF6600; 
        margin-bottom: 25px;
    }
    .metric-label { font-size: 30px; color: #555; margin-bottom: 0px; font-weight: 700; text-transform: uppercase; }
    .metric-value { 
        font-size: 150px; /* আপনার রিকোয়ারমেন্ট অনুযায়ী */
        color: #000; 
        font-weight: 900; 
        margin: 0; 
        line-height: 1.1;
        letter-spacing: -5px;
    }

    /* কালারড সেকশন হেডিং */
    .section-header { 
        font-size: 30px; 
        color: #333; 
        background-color: #F0F2F6; 
        padding: 15px 25px; 
        border-radius: 10px; 
        border-left: 12px solid #FF6600; 
        margin-top: 50px; 
        margin-bottom: 30px; 
        font-weight: 800;
    }
    
    /* টেবিল স্টাইল */
    .stTable { color: #333333 !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# ৩. ডাটা লোডিং ফাংশন
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
        if f'Product Price-{i}' in df.columns:
            df[f'Product Price-{i}'] = pd.to_numeric(df[f'Product Price-{i}'], errors='coerce').fillna(0).astype(int)
    return df

# সাহায্যকারী ফাংশন: টেবিলের নিচে Total যোগ করা
def add_total_row(df, numeric_cols, label_col):
    df_sum = df[numeric_cols].sum()
    total_row = {col: "" for col in df.columns}
    total_row[label_col] = "**Total**"
    for col in numeric_cols:
        total_row[col] = df_sum[col]
    return pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

try:
    df = load_data()

    # --- হেডার ও লোগো ---
    if os.path.exists(logo_path): st.image(logo_path, width=130)
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

    # --- ১. বিশাল বড় সামারি রিপোর্ট (৩টি করে ২ লাইনে) ---
    rev = int(f_df['Total Amount'].sum())
    ords = len(f_df)
    qty = int(f_df['Total Qty'].sum())
    dis = int(f_df['Discount'].sum())
    aov = int(rev/ords) if ords > 0 else 0
    dis_p = (dis/rev*100) if rev > 0 else 0

    # ১ম লাইন
    m1, m2, m3 = st.columns(3)
    m1.markdown(f"<div class='metric-card'><p class='metric-label'>Revenue</p><p class='metric-value'>৳{rev:,}</p></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card'><p class='metric-label'>Orders</p><p class='metric-value'>{ords:,}</p></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card'><p class='metric-label'>AOV</p><p class='metric-value'>৳{aov:,}</p></div>", unsafe_allow_html=True)
    
    # ২য় লাইন
    m4, m5, m6 = st.columns(3)
    m4.markdown(f"<div class='metric-card'><p class='metric-label'>Product Qty</p><p class='metric-value'>{qty:,}</p></div>", unsafe_allow_html=True)
    m5.markdown(f"<div class='metric-card'><p class='metric-label'>Discount</p><p class='metric-value'>৳{dis:,}</p></div>", unsafe_allow_html=True)
    m6.markdown(f"<div class='metric-card'><p class='metric-label'>Discount %</p><p class='metric-value'>{dis_p:.1f}%</p></div>", unsafe_allow_html=True)

    # --- ২. এজেন্ট পারফরম্যান্স (সবুজ চার্ট, সংখ্যা বাইরে) ---
    st.markdown('<div class="section-header">Agent Performance (Person-wise)</div>', unsafe_allow_html=True)
    agent_data = f_df.groupby('Order Collector').agg(Revenue=('Total Amount', 'sum'), Orders=('Total Amount', 'count'), Qty=('Total Qty', 'sum')).sort_values(by='Revenue', ascending=False).reset_index()
    agent_data['Rev %'] = (agent_data['Revenue'] / rev * 100).map('{:.1f}%'.format)

    fig_a = px.bar(agent_data, x='Revenue', y='Order Collector', orientation='h', title="Revenue by Person", color_discrete_sequence=['#2E7D32'], text_auto=True)
    fig_a.update_traces(textfont=dict(size=18, color='black', family='Arial Black'), textangle=0, textposition='outside', texttemplate='৳%{x:,}')
    fig_a.update_layout(xaxis=dict(tickformat=',d', showticklabels=True, title="Total Revenue"))
    st.plotly_chart(fig_a, use_container_width=True)

    table_a = add_total_row(agent_data, ['Revenue', 'Orders', 'Qty'], 'Order Collector')
    table_a['Revenue'] = table_a['Revenue'].apply(lambda x: f"৳{x:,}" if isinstance(x, (int, float)) else x)
    st.table(table_a)

    # ড্রপডাউন ফিল্টার (নিচের সব রিপোর্টের জন্য)
    st.markdown('<div class="section-header">Category-wise Detailed Analytics</div>', unsafe_allow_html=True)
    agent_list = ["All Agents"] + sorted(list(f_df['Order Collector'].unique()))
    sel_agent = st.selectbox("Filter Following Reports by Agent:", agent_list)
    p_df_f = f_df if sel_agent == "All Agents" else f_df[f_df['Order Collector'] == sel_agent]
    current_rev = p_df_f['Total Amount'].sum()
    current_qty = p_df_f['Total Qty'].sum()

    # রিপোর্ট ফাংশন (Chart-Table Layout)
    def render_report(title, df_input, group_col, val_col, total_val, is_currency=False):
        st.markdown(f"### {title}")
        if group_col == 'Product':
            stats = df_input.groupby('Product').agg(Value=(val_col, 'sum')).sort_values(by='Value', ascending=False).reset_index()
        else:
            stats = df_input.groupby(group_col).agg(Value=('Total Amount', 'count' if not is_currency else 'sum')).sort_values(by='Value', ascending=False).reset_index()
        
        stats['%'] = (stats['Value'] / total_val * 100).fillna(0).map('{:.1f}%'.format)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = px.bar(stats.head(10), x='Value', y=group_col, orientation='h', color='Value', color_continuous_scale='Oranges', text_auto=True)
            fig.update_traces(textfont=dict(size=14, color='black'), textangle=0, textposition='outside', texttemplate='৳%{x:,}' if is_currency else '%{x:,}')
            fig.update_layout(xaxis=dict(showticklabels=False, title=""))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.table(add_total_row(stats.head(15), ['Value'], group_col))

    # --- ৩. প্রোডাক্ট অ্যানালিটিক্স ---
    all_i = []
    for i in range(1, 16):
        if f'Product Name-{i}' in p_df_f.columns:
            temp = p_df_f[[f'Product Name-{i}', f'Product QTY-{i}']].copy().dropna().rename(columns={f'Product Name-{i}': 'Product', f'Product QTY-{i}': 'Qty'})
            all_i.append(temp)
    if all_i:
        p_data = pd.concat(all_i)
        p_data = p_data[(p_data['Product'] != "0") & (p_data['Product'] != "")]
        render_report("Product Sales Analytics", p_data, 'Product', 'Qty', current_qty)

    # --- ৪. কাস্টমার ও জিওগ্রাফিক্যাল ---
    render_report("Class-wise Distribution", p_df_f, 'Class', 'Total Amount', len(p_df_f))
    render_report("Age-wise Distribution", p_df_f, 'Age', 'Total Amount', len(p_df_f))
    render_report("Guardian Profession", p_df_f, 'Profession', 'Total Amount', len(p_df_f))
    render_report("District-wise Revenue", p_df_f, 'District', 'Total Amount', current_rev, is_currency=True)

except Exception as e:
    st.error(f"Error: {e}")
