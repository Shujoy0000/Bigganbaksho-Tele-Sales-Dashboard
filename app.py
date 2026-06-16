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
    html, body, [class*="css"] { color: #333333 !important; font-family: 'Segoe UI', sans-serif; }
    .main-title { text-align: center; color: #FF6600; font-size: 55px; font-weight: 800; margin-top: -100px; margin-bottom: 5px; }
    .developer-text { text-align: center; font-style: italic; font-size: 18px; color: #666; margin-bottom: 10px; }
    .slogan-text { text-align: center; font-size: 30px; font-weight: 800; color: #222; margin-top: 10px; }
    .vision-text { text-align: center; font-size: 20px; color: #777; margin-bottom: 30px; }
    
    .metric-card { 
        background: #FFFFFF; padding: 15px 0px; border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; 
        border-top: 8px solid #FF6600; margin-bottom: 10px;
    }
    .metric-label { font-size: 18px; color: #555; margin-bottom: 5px; font-weight: 700; text-transform: uppercase; }
    .metric-value { font-size: 52px; color: #000; font-weight: 900; margin: 0; line-height: 1.2; }

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

# সাহায্যকারী ফাংশন: Others এবং Total লজিক
def process_table_with_others(df, label_col, val_col, total_val, is_currency=False):
    if df.empty: return df
    df = df.sort_values(by=val_col, ascending=False).reset_index(drop=True)
    if len(df) > 15:
        top_df = df.head(14).copy()
        others_val = int(df.iloc[14:][val_col].sum())
        others_row = pd.DataFrame({label_col: ['Others'], val_col: [others_val]})
        final_df = pd.concat([top_df, others_row], ignore_index=True)
    else:
        final_df = df.copy()
    final_df['%'] = (final_df[val_col] / (total_val if total_val > 0 else 1) * 100).map('{:.1f}%'.format)
    total_row = {label_col: "**Total**", val_col: int(total_val), '%': "100.0%"}
    final_df = pd.concat([final_df, pd.DataFrame([total_row])], ignore_index=True)
    if is_currency: final_df[val_col] = final_df[val_col].apply(lambda x: f"৳{int(x):,}" if isinstance(x, (int, float)) else x)
    else: final_df[val_col] = final_df[val_col].apply(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)
    return final_df

try:
    df = load_data()

    # --- হেডার ---
    if os.path.exists(logo_path): st.image(logo_path, width=120)
    st.markdown('<div class="main-title">Tele Sales Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="developer-text">Web App Developed By-Shujoy Shaha</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan-text">ম্যানুয়েল কাজের দিন শেষ, বিজ্ঞানবাক্সে বাংলাদেশ</div>', unsafe_allow_html=True)
    st.markdown('<div class="vision-text">অন্যরকম বাংলাদেশের স্বপ্ন নিয়ে</div>', unsafe_allow_html=True)

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

    # --- ২. এজেন্ট পারফরম্যান্স (Sorting: Small on Top, Large on Bottom) ---
    st.markdown('<div class="section-header">Agent Performance (Person-wise)</div>', unsafe_allow_html=True)
    agent_data = f_df.groupby('Order Collector').agg(Revenue=('Total Amount', 'sum'), Orders=('Total Amount', 'count'), Qty=('Total Qty', 'sum')).reset_index()
    
    # সর্টিং ফিক্স: Small (Top) to Large (Bottom) করার জন্য categoryorder='total descending'
    fig_a = px.bar(agent_data, x='Revenue', y='Order Collector', orientation='h', color_discrete_sequence=['#2E7D32'], text_auto=True)
    fig_a.update_traces(textfont=dict(size=14, color='black'), textangle=0, textposition='outside', texttemplate='৳%{x:,}')
    fig_a.update_layout(yaxis={'categoryorder':'total descending'}, xaxis=dict(tickformat=',d', title="Total Revenue"))
    st.plotly_chart(fig_a, use_container_width=True)
    st.table(process_table_with_others(agent_data, 'Order Collector', 'Revenue', rev, is_currency=True))

    # --- ৩. ক্যাটাগরি ফিল্টার ---
    st.markdown('<div class="section-header">Detailed Category Analytics</div>', unsafe_allow_html=True)
    sel_agent = st.selectbox("Filter Following Reports by Agent:", ["All Agents"] + sorted(list(f_df['Order Collector'].unique())))
    p_df_f = f_df if sel_agent == "All Agents" else f_df[f_df['Order Collector'] == sel_agent]
    curr_rev, curr_qty, curr_ords = p_df_f['Total Amount'].sum(), p_df_f['Total Qty'].sum(), len(p_df_f)

    def render_final_report(title, df_in, group_col, val_col, grand_total, is_currency=False, color_scheme='Oranges'):
        st.markdown(f"### {title}")
        if df_in.empty: return
        stats = df_in.groupby(group_col).agg(Value=(val_col, 'sum' if group_col == 'Product' else 'count' if not is_currency else 'sum')).reset_index()
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = px.bar(stats.sort_values('Value', ascending=True).tail(10), x='Value', y=group_col, orientation='h', 
                         color='Value', color_continuous_scale=color_scheme, text_auto=True)
            fig.update_traces(textangle=0, textposition='outside', texttemplate='৳%{x:,}' if is_currency else '%{x:,}')
            fig.update_layout(yaxis={'categoryorder':'total descending'}, xaxis=dict(showticklabels=False, title=""), coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.table(process_table_with_others(stats, group_col, 'Value', grand_total, is_currency))

    # ৩. প্রোডাক্ট (Multi-color like Image 2)
    all_i = []
    for i in range(1, 16):
        if f'Product Name-{i}' in p_df_f.columns:
            temp = p_df_f[[f'Product Name-{i}', f'Product QTY-{i}']].copy().dropna().rename(columns={f'Product Name-{i}': 'Product', f'Product QTY-{i}': 'Qty'})
            all_i.append(temp)
    if all_i:
        p_data = pd.concat(all_i)
        p_data = p_data[(p_data['Product'] != "0") & (p_data['Product'] != "")]
        # কালার প্যালেট ঠিক করার জন্য px.colors.qualitative.Plotly ব্যবহার
        render_final_report("Product Sales Analytics", p_data, 'Product', 'Qty', curr_qty, color_scheme='Plotly')

    # ৪. কাস্টমার ও এরিয়া (Small to Large)
    render_final_report("Class-wise Distribution", p_df_f, 'Class', 'Total Amount', curr_ords, color_scheme='Viridis')
    render_final_report("Age-wise Distribution", p_df_f, 'Age', 'Total Amount', curr_ords, color_scheme='Plasma')
    render_final_report("Guardian Profession", p_df_f, 'Profession', 'Total Amount', curr_ords, color_scheme='Inferno')
    render_report_district = render_final_report("District-wise Revenue", p_df_f, 'District', 'Total Amount', curr_rev, is_currency=True, color_scheme='Greens')

except Exception as e:
    st.error(f"Error: {e}")
