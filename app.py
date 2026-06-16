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
    
    /* মেট্রিক কার্ডের নতুন ডিজাইন */
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
        min-height: 140px; /* সব বক্সের উচ্চতা সমান রাখার জন্য */
        overflow: hidden; /* বাইরে যেন না যায় */
    }
    .metric-label { 
        font-size: 24px; /* লেবেল বড় করা হয়েছে */
        color: #555; 
        margin-bottom: 5px; 
        font-weight: 800; 
        text-transform: uppercase; 
        white-space: nowrap; /* এক লাইনে রাখার জন্য */
    }
    .metric-value { 
        font-size: 58px; /* ভ্যালু অনেক বড় করা হয়েছে */
        color: #000; 
        font-weight: 900; 
        margin: 0; 
        line-height: 1.1; 
        white-space: nowrap; /* এক লাইনে রাখার জন্য */
    }

    .section-header { 
        font-size: 28px; color: #333; background-color: #F0F2F6; 
        padding: 12px 20px; border-radius: 8px; border-left: 10px solid #FF6600; 
        margin-top: 45px; margin-bottom: 25px; font-weight: 700;
    }
    .stTable { color: #333333 !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)
