import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os
import datetime
import json
import re

# ১. পেজ সেটিংস ও লোগো
logo_path = "logo.png"
if not os.path.exists(logo_path):
    logo_path = "logo.jpg"

st.set_page_config(page_title="Tele Sales Analytics", layout="wide", page_icon="📊")

# ২. কাস্টম CSS
st.markdown("""
    <style>
    html, body, [class*="css"] { 
        color: #333333 !important; 
        font-family: 'Segoe UI', sans-serif; 
    }
    
    .main-title { 
        text-align: center; 
        color: #FF6600; 
        font-size: 55px; 
        font-weight: 800; 
        margin-top: -100px; 
        margin-bottom: 5px; 
    }

    .developer-text { 
        text-align: center; 
        font-style: italic; 
        font-size: 18px; 
        color: #666; 
        margin-bottom: 10px; 
    }

    .slogan-text { 
        text-align: center; 
        font-size: 30px; 
        font-weight: 800; 
        color: #222; 
        margin-top: 10px; 
    }

    .vision-text { 
        text-align: center; 
        font-size: 20px; 
        color: #777; 
        margin-bottom: 30px; 
    }
    
    .metric-card { 
        background: #FFFFFF; 
        padding: 0px 2px; 
        border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        text-align: center; 
        border-top: 8px solid #FF6600; 
        margin-bottom: 10px;
        display: flex; 
        align-items: center;
        justify-content: center;
        height: 152px;
        min-height: 152px; 
        overflow: hidden; 
    }

    .metric-content {
        transform: scale(1.42);
        transform-origin: center;
        width: 100%;
    }

    .metric-label { 
        font-size: 20px; 
        color: #444444; 
        margin: 0 0 10px 0; 
        font-weight: 900; 
        text-transform: uppercase; 
        white-space: nowrap; 
        line-height: 1;
    }

    .metric-value { 
        font-size: 40px; 
        color: #2b2b2b; 
        font-weight: 900; 
        margin: 0; 
        line-height: 1; 
        white-space: nowrap; 
        letter-spacing: -0.5px;
    }

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

    .copy-note {
        font-size: 13px;
        color: #666;
        margin-top: -4px;
        margin-bottom: 6px;
    }

    .stDataFrame {
        font-weight: 600 !important;
    }

    /* সব table header bold করার জন্য */
    [data-testid="stDataFrame"] div[role="columnheader"],
    [data-testid="stDataFrame"] div[role="columnheader"] * {
        font-weight: 900 !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# Copyable table helper
def clean_key(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')


def show_copyable_table(df_display, key_name):
    if df_display.empty:
        st.info("No data found.")
        return

    table_height = min(600, max(180, 38 * (len(df_display) + 1)))

    st.markdown(
        '<div class="copy-note">Table থেকে cell, column বা multiple column select করে copy করা যাবে। নিচের button দিয়ে full table copy হবে।</div>',
        unsafe_allow_html=True
    )

    # Total row পুরোটা bold করার জন্য
    def bold_total_row(row):
        first_cell = str(row.iloc[0]).replace("*", "").strip().lower()

        if first_cell == "total":
            return [
                "font-weight: 900; color: #000000;"
                for _ in row
            ]

        return ["" for _ in row]

    styled_df = (
        df_display.style
        .apply(bold_total_row, axis=1)
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("font-weight", "900"),
                    ("color", "#000000")
                ]
            }
        ])
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=table_height
    )

    table_text = df_display.to_csv(sep="\t", index=False)
    table_json = json.dumps(table_text, ensure_ascii=False)
    button_id = f"copy_btn_{clean_key(key_name)}"

    components.html(f"""
        <button id="{button_id}" style="
            background:#FF6600;
            color:white;
            border:none;
            border-radius:7px;
            padding:8px 14px;
            font-weight:700;
            cursor:pointer;
            font-size:14px;
            margin-top:4px;
        ">📋 Copy full table</button>

        <script>
        const btn = document.getElementById("{button_id}");
        const tableText = {table_json};

        btn.onclick = async function() {{
            try {{
                await navigator.clipboard.writeText(tableText);
                btn.innerText = "✅ Copied!";
                setTimeout(() => btn.innerText = "📋 Copy full table", 1300);
            }} catch (err) {{
                btn.innerText = "Copy failed";
                setTimeout(() => btn.innerText = "📋 Copy full table", 1300);
            }}
        }};
        </script>
    """, height=48)


# ৩. ডাটা লোডিং
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDhr-rwKe88LKKludd74G766j1l4vbvoaHi1YwwkefcfjCCgDGkZL6Ty9ngNv3gVvd5ezElgXghOs3/pub?gid=81417&single=true&output=csv"
    df = pd.read_csv(url)

    # কলাম clean
    df.columns = df.columns.astype(str).str.strip()

    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])

    # প্রয়োজনীয় numeric column
    needed_numeric_cols = ['Total Amount', 'Shipping Charge', 'Discount', 'Total Qty', 'Product Price']
    for col in needed_numeric_cols:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Product QTY এবং Product Price-1 to 15 clean
    for i in range(1, 16):
        qty_col = f'Product QTY-{i}'
        price_col = f'Product Price-{i}'

        if qty_col in df.columns:
            df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0).astype(int)

        if price_col in df.columns:
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0).astype(int)

    # Revenue = শেষের Product Price column
    # Fallback: যদি Product Price blank/0 হয়, তাহলে Total Amount - Shipping Charge
    fallback_revenue = df['Total Amount'] - df['Shipping Charge']
    df['Revenue'] = df['Product Price'].where(df['Product Price'] > 0, fallback_revenue)
    df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0).astype(int)
    df['Revenue'] = df['Revenue'].clip(lower=0)

    # Total Sales = Revenue + Discount
    df['Total Sales'] = df['Revenue'] + df['Discount']
    df['Total Sales'] = pd.to_numeric(df['Total Sales'], errors='coerce').fillna(0).astype(int)
    df['Total Sales'] = df['Total Sales'].clip(lower=0)

    return df


# সাহায্যকারী ফাংশন: টেবিল প্রসেসিং এবং দশমিক ফিক্স
def process_table_data(df, label_col, val_col, total_val, is_currency=False, limit_15=True):
    if df.empty:
        return df

    df = df.copy()

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

    total_dict = {label_col: "Total", '%': "100.0%"}
    for col in numeric_cols:
        if col == val_col:
            total_dict[col] = total_val
        else:
            total_dict[col] = final_df[col].sum()

    final_df = pd.concat([final_df, pd.DataFrame([total_dict])], ignore_index=True)

    for col in numeric_cols:
        if col == val_col and is_currency:
            final_df[col] = final_df[col].apply(lambda x: f"৳{int(float(x)):,}" if pd.notna(x) else "")
        else:
            final_df[col] = final_df[col].apply(lambda x: f"{int(float(x)):,}" if pd.notna(x) else "")

    return final_df


try:
    df = load_data()

    # --- হেডার ---
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

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
    total_sales = int(f_df['Total Sales'].sum())
    revenue = int(f_df['Revenue'].sum())
    ords = len(f_df)
    qty = int(f_df['Total Qty'].sum())
    dis = int(f_df['Discount'].sum())

    aov = int(revenue / ords) if ords > 0 else 0
    dis_p = (dis / total_sales * 100) if total_sales > 0 else 0

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

    summaries = [
        ("Total Sales", f"৳{total_sales:,}"),
        ("Revenue", f"৳{revenue:,}"),
        ("Orders", f"{ords:,}"),
        ("AOV", f"৳{aov:,}"),
        ("Product Qty", f"{qty:,}"),
        ("Discount", f"৳{dis:,}"),
        ("Discount %", f"{dis_p:.1f}%")
    ]

    for col, (label, value) in zip([c1, c2, c3, c4, c5, c6, c7], summaries):
        col.markdown(
            f"<div class='metric-card'><div class='metric-content'><p class='metric-label'>{label}</p><p class='metric-value'>{value}</p></div></div>",
            unsafe_allow_html=True
        )

    # --- ২. এজেন্ট পারফরম্যান্স ---
    st.markdown('<div class="section-header">Agent Performance (Person-wise)</div>', unsafe_allow_html=True)

    agent_data = f_df.groupby('Order Collector').agg(
        Revenue=('Revenue', 'sum'),
        Orders=('Revenue', 'count'),
        Qty=('Total Qty', 'sum')
    ).reset_index()

    agent_data = agent_data.sort_values('Revenue', ascending=False)

    fig_a = px.bar(
        agent_data,
        x='Revenue',
        y='Order Collector',
        orientation='h',
        color='Order Collector',
        color_discrete_sequence=px.colors.qualitative.Vivid,
        text_auto=True
    )

    fig_a.update_traces(
        textfont=dict(size=14, color='black'),
        textangle=0,
        textposition='outside',
        texttemplate='৳%{x:,}'
    )

    agent_fig_height = len(agent_data) * 45 + 70
    fig_a.update_layout(
        height=agent_fig_height,
        margin=dict(t=20, b=40, l=10, r=80),
        yaxis={'categoryorder': 'array', 'categoryarray': agent_data['Order Collector'].tolist()},
        xaxis=dict(tickformat=',d', title="Revenue"),
        showlegend=False
    )

    st.plotly_chart(fig_a, use_container_width=True)

    agent_table = process_table_data(
        agent_data,
        'Order Collector',
        'Revenue',
        revenue,
        is_currency=True,
        limit_15=False
    )

    show_copyable_table(agent_table, "agent_performance_table")

    # --- ৩. বিস্তারিত অ্যানালিটিক্স ড্রপডাউন ---
    st.markdown('<div class="section-header">Detailed Category Analytics</div>', unsafe_allow_html=True)

    sel_agent = st.selectbox(
        "Filter Reports by Agent:",
        ["All Agents"] + sorted(list(f_df['Order Collector'].dropna().unique()))
    )

    p_df_f = f_df if sel_agent == "All Agents" else f_df[f_df['Order Collector'] == sel_agent]

    curr_revenue = p_df_f['Revenue'].sum()
    curr_qty = p_df_f['Total Qty'].sum()
    curr_ords = len(p_df_f)

    # ডাইনামিক রিপোর্ট ফাংশন
    def render_report_dynamic(title, df_in, group_col, val_col, grand_total, is_currency=False, chart_top_10=True, table_limit_15=True):
        st.markdown(f"### {title}")

        if df_in.empty:
            return

        df_work = df_in.copy()

        if group_col not in df_work.columns:
            st.warning(f"{group_col} column not found.")
            return

        df_work[group_col] = df_work[group_col].astype(str).str.replace(r'\.0$', '', regex=True)
        df_work = df_work[(df_work[group_col] != "nan") & (df_work[group_col] != "") & (df_work[group_col] != "0")]

        if df_work.empty:
            return

        stats = df_work.groupby(group_col).agg(
            Value=(val_col, 'sum' if group_col == 'Product' else 'count' if not is_currency else 'sum')
        ).reset_index()

        stats = stats.sort_values('Value', ascending=False)
        cat_array = stats[group_col].tolist()

        c1, c2 = st.columns([2, 1])

        with c1:
            plot_data = stats.head(10).copy() if chart_top_10 else stats.copy()

            fig = px.bar(
                plot_data,
                x='Value',
                y=group_col,
                orientation='h',
                color=group_col,
                color_discrete_sequence=px.colors.qualitative.Vivid,
                text_auto=True
            )

            fig.update_traces(
                textangle=0,
                textposition='outside',
                texttemplate='৳%{x:,}' if is_currency else '%{x:,}'
            )

            dynamic_height = len(plot_data) * 45 + 50
            fig.update_layout(
                height=dynamic_height,
                margin=dict(t=20, b=20, l=10, r=80),
                yaxis={'type': 'category', 'categoryorder': 'array', 'categoryarray': cat_array},
                xaxis=dict(showticklabels=False, title=""),
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        with c2:
            table_df = process_table_data(
                stats,
                group_col,
                'Value',
                grand_total,
                is_currency,
                limit_15=table_limit_15
            )

            show_copyable_table(table_df, title)

    # ৩. প্রোডাক্ট
    all_i = []
    for i in range(1, 16):
        name_col = f'Product Name-{i}'
        qty_col = f'Product QTY-{i}'

        if name_col in p_df_f.columns and qty_col in p_df_f.columns:
            temp = p_df_f[[name_col, qty_col]].copy().dropna()
            temp = temp.rename(columns={name_col: 'Product', qty_col: 'Qty'})
            all_i.append(temp)

    if all_i:
        p_data = pd.concat(all_i)
        p_data['Product'] = p_data['Product'].astype(str).str.strip()
        p_data = p_data[
            (p_data['Product'] != "0") &
            (p_data['Product'] != "") &
            (p_data['Product'] != "nan")
        ]

        # Product chart Top 10, table full
        render_report_dynamic(
            "Product Sales Analytics",
            p_data,
            'Product',
            'Qty',
            curr_qty,
            chart_top_10=True,
            table_limit_15=False
        )

    # অন্যান্য কাস্টমার রিপোর্ট: chart Top 10, table full
    render_report_dynamic(
        "Class-wise Distribution",
        p_df_f,
        'Class',
        'Revenue',
        curr_ords,
        chart_top_10=True,
        table_limit_15=False
    )

    render_report_dynamic(
        "Age-wise Distribution",
        p_df_f,
        'Age',
        'Revenue',
        curr_ords,
        chart_top_10=True,
        table_limit_15=False
    )

    render_report_dynamic(
        "Guardian Profession",
        p_df_f,
        'Profession',
        'Revenue',
        curr_ords,
        chart_top_10=True,
        table_limit_15=False
    )

    render_report_dynamic(
        "District-wise Revenue",
        p_df_f,
        'District',
        'Revenue',
        curr_revenue,
        is_currency=True,
        chart_top_10=True,
        table_limit_15=False
    )

except Exception as e:
    st.error(f"Error: {e}")
