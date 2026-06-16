import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime

# ১. পেজ সেটিংস ও লোগো
logo_path = "logo.png"
if not os.path.exists(logo_path): logo_path = "logo.jpg"

st.set_page_config(page_title="Tele Sales Analytics", layout="wide", page_icon="📊")

# ২. কাস্টম CSS
st.markdown("""
    <style>
    html, body, [class*="css"] { 
        color: #333333 !important; 
        font-family: 'Segoe UI', sans-serif; 
    }
    
    .main-title { text-align: center; color: #FF6600; font-size: 55px; font-weight: 800; margin-top: -100px; margin-bottom: 5px; }
    .developer-text { text-align: center; font-style: italic; font-size: 18px; color: #666; margin-bottom: 10px; }
    .slogan-text { text-align: center; font-size: 30px; font-weight: 800; color: #222; margin-top: 10px; }
    .vision-text { text-align: center; font-size: 20px; color: #777; margin-bottom: 30px; }
    
    .metric-card { 
        background: #FFFFFF; 
        padding: 20px 5px; 
        border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        text-align: center; 
        border-top: 8px solid #FF6600; 
        margin-bottom: 10px;
        display: flex; 
        flex-direction: column; 
        justify-content: center;
        min-height: 140px; 
        overflow: hidden; 
    }
    .metric-label { 
        font-size: 20px; 
        color: #555; 
        margin-bottom: 5px; 
        font-weight: 800; 
        text-transform: uppercase; 
        white-space: nowrap; 
    }
    .metric-value { 
        font-size: 42px; 
        color: #000; 
        font-weight: 900; 
        margin: 0; 
        line-height: 1.1; 
        white-space: nowrap; 
    }

    .section-header { 
        font-size: 28px; color: #333; background-color: #F0F2F6; 
        padding: 12px 20px; border-radius: 8px; border-left: 10px solid #FF6600; 
        margin-top: 45px; margin-bottom: 25px; font-weight: 700;
    }
    .stTable { color: #333333 !important; font-weight: 600 !important; }
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
        qty_col = f'Product QTY-{i}'
        price_col = f'Product Price-{i}'
        if qty_col in df.columns: df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0).astype(int)
        if price_col in df.columns: df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0).astype(int)
    return df

# সাহায্যকারী ফাংশন: টেবিল প্রসেসিং এবং দশমিক ফিক্স
def process_table_data(df, label_col, val_col, total_val, is_currency=False, limit_15=True):
    if df.empty: return df
    df = df.copy()
    
    # শুধু সংখ্যার কলামগুলো নেওয়া হচ্ছে
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if label_col in numeric_cols:
        numeric_cols.remove(label_col)

    if limit_15 and len(df) > 15:
        top_df = df.head(14).copy()
        others_dict = {label_col: 'Others'}
        for col in numeric_cols:
            others_dict[col] = df.iloc[14:][col].sum()
        others_row = pd.DataFrame([others_dict])
        final_df = pd.concat([top_df, others_row], ignore_index=True)
    else:
        final_df = df.copy()

    final_df['%'] = (final_df[val_col] / (total_val if total_val > 0 else 1) * 100).map('{:.1f}%'.format)
    
    total_dict = {label_col: "**Total**", '%': "100.0%"}
    for col in numeric_cols:
        if col == val_col:
            total_dict[col] = total_val
        else:
            total_dict[col] = final_df[col].sum()
            
    final_df = pd.concat([final_df, pd.DataFrame([total_dict])], ignore_index=True)
    
    # দশমিক রিমুভ করার নিশ্চিত লজিক
    for col in numeric_cols:
        if col == val_col and is_currency:
            final_df[col] = final_df[col].apply(lambda x: f"৳{int(float(x)):,}" if pd.notna(x) else "")
        else:
            final_df[col] = final_df[col].apply(lambda x: f"{int(float(x)):,}" if pd.notna(x) else "")
            
    return final_df

try:
    df = load_data()

    # --- হেডার ---
    if os.path.exists(logo_path): st.image(logo_path, width=120)
    st.markdown('<div class="main-title">Tele Sales Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="developer-text">Web App Developed By-Shujoy Shaha</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan-text">ম্যানুয়েল কাজের দিন শেষ, বিজ্ঞানবাক্সে বাংলাদেশ</div>', unsafe_allow_html=True)
    st.markdown('<div class="vision-text">অন্যরকম বাংলাদেশের স্বপ্ন নিয়ে</div>', unsafe_allow_html=True)

    # --- ফিল্টার ---
    st.sidebar.header("📅 Select Date Range")
    today = datetime.date.today()
    start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=30))
    end_date = st.sidebar.date_input("End Date", today)
    f_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    # --- ১. সামারি ---
    rev = int(f_df['Total Amount'].sum())
    ords, qty, dis = len(f_df), int(f_df['Total Qty'].sum()), int(f_df['Discount'].sum())
    aov = int(rev/ords) if ords > 0 else 0
    dis_p = (dis/rev*100) if rev > 0 else 0

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    summaries = [("Revenue", f"৳{rev:,}"), ("Orders", f"{ords:,}"), ("AOV", f"৳{aov:,}"), ("Product Qty", f"{qty:,}"), ("Discount", f"৳{dis:,}"), ("Discount %", f"{dis_p:.1f}%")]
    for col, (label, value) in zip([m1, m2, m3, m4, m5, m6], summaries):
        col.markdown(f"<div class='metric-card'><p class='metric-label'>{label}</p><p class='metric-value'>{value}</p></div>", unsafe_allow_html=True)

    # --- ২. এজেন্ট পারফরম্যান্স ---
    st.markdown('<div class="section-header">Agent Performance (Person-wise)</div>', unsafe_allow_html=True)
    agent_data = f_df.groupby('Order Collector').agg(Revenue=('Total Amount', 'sum'), Orders=('Total Amount', 'count'), Qty=('Total Qty', 'sum')).reset_index()
    agent_data = agent_data.sort_values('Revenue', ascending=False)
    
    fig_a = px.bar(agent_data, x='Revenue', y='Order Collector', orientation='h', color='Order Collector', color_discrete_sequence=px.colors.qualitative.Vivid, text_auto=True)
    fig_a.update_traces(textfont=dict(size=14, color='black'), textangle=0, textposition='outside', texttemplate='৳%{x:,}')
    
    # বারের থিকনেস ফিক্সড করার জন্য হাইট এবং মার্জিন কন্ট্রোল
    agent_fig_height = len(agent_data) * 45 + 70
    fig_a.update_layout(
        height=agent_fig_height, 
        margin=dict(t=20, b=40, l=10, r=80), # মার্জিন ফিক্সড করে দেওয়া হয়েছে
        yaxis={'categoryorder': 'array', 'categoryarray': agent_data['Order Collector'].tolist()}, 
        xaxis=dict(tickformat=',d', title="Total Revenue"), 
        showlegend=False
    ) 
    
    st.plotly_chart(fig_a, use_container_width=True)
    st.table(process_table_data(agent_data, 'Order Collector', 'Revenue', rev, is_currency=True, limit_15=False))

    # --- ৩. বিস্তারিত অ্যানালিটিক্স ড্রপডাউন ---
    st.markdown('<div class="section-header">Detailed Category Analytics</div>', unsafe_allow_html=True)
    sel_agent = st.selectbox("Filter Reports by Agent:", ["All Agents"] + sorted(list(f_df['Order Collector'].unique())))
    p_df_f = f_df if sel_agent == "All Agents" else f_df[f_df['Order Collector'] == sel_agent]
    curr_rev, curr_qty, curr_ords = p_df_f['Total Amount'].sum(), p_df_f['Total Qty'].sum(), len(p_df_f)

    # ডাইনামিক রিপোর্ট ফাংশন 
    def render_report_dynamic(title, df_in, group_col, val_col, grand_total, is_currency=False, chart_top_10=True, table_limit_15=True):
        st.markdown(f"### {title}")
        if df_in.empty: return
        
        df_work = df_in.copy()
        df_work[group_col] = df_work[group_col].astype(str).str.replace(r'\.0$', '', regex=True)
            
        stats = df_work.groupby(group_col).agg(Value=(val_col, 'sum' if group_col == 'Product' else 'count' if not is_currency else 'sum')).reset_index()
        
        stats = stats.sort_values('Value', ascending=False)
        cat_array = stats[group_col].tolist() 
            
        c1, c2 = st.columns([2, 1])
        with c1:
            if chart_top_10:
                plot_data = stats.head(10).copy()
            else:
                plot_data = stats.copy()
                
            fig = px.bar(plot_data, x='Value', y=group_col, orientation='h', color=group_col,
                         color_discrete_sequence=px.colors.qualitative.Vivid, text_auto=True)
            fig.update_traces(textangle=0, textposition='outside', texttemplate='৳%{x:,}' if is_currency else '%{x:,}')
            
            # বারের থিকনেস ফিক্সড করার জন্য হাইট এবং মার্জিন কন্ট্রোল
            dynamic_height = len(plot_data) * 45 + 50
            fig.update_layout(
                height=dynamic_height, 
                margin=dict(t=20, b=20, l=10, r=80), # মার্জিন ফিক্সড করে দেওয়া হয়েছে
                yaxis={'type': 'category', 'categoryorder': 'array', 'categoryarray': cat_array}, 
                xaxis=dict(showticklabels=False, title=""), 
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.table(process_table_data(stats, group_col, 'Value', grand_total, is_currency, limit_15=table_limit_15))

    # ৩. প্রোডাক্ট
    all_i = []
    for i in range(1, 16):
        if f'Product Name-{i}' in p_df_f.columns:
            temp = p_df_f[[f'Product Name-{i}', f'Product QTY-{i}']].copy().dropna().rename(columns={f'Product Name-{i}': 'Product', f'Product QTY-{i}': 'Qty'})
            all_i.append(temp)
    if all_i:
        p_data = pd.concat(all_i)
        p_data = p_data[(p_data['Product'] != "0") & (p_data['Product'] != "")]
        render_report_dynamic("Product Sales Analytics", p_data, 'Product', 'Qty', curr_qty, chart_top_10=True, table_limit_15=True)

    # অন্যান্য কাস্টমার রিপোর্ট
    render_report_dynamic("Class-wise Distribution", p_df_f, 'Class', 'Total Amount', curr_ords, chart_top_10=True, table_limit_15=True) 
    render_report_dynamic("Age-wise Distribution", p_df_f, 'Age', 'Total Amount', curr_ords, chart_top_10=True, table_limit_15=True) 
    render_report_dynamic("Guardian Profession", p_df_f, 'Profession', 'Total Amount', curr_ords, chart_top_10=True, table_limit_15=True)
    render_report_dynamic("District-wise Revenue", p_df_f, 'District', 'Total Amount', curr_rev, is_currency=True, chart_top_10=True, table_limit_15=True)

except Exception as e:
    st.error(f"Error: {e}")
