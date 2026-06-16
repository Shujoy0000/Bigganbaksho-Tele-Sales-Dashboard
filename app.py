import streamlit as st
import pandas as pd
import io
import os
import re

# লোগো ফাইলের নাম চেক করা
logo_path = "logo.jpg"
if not os.path.exists(logo_path):
logo_path = "images (1).jpeg"
if not os.path.exists(logo_path):
logo_path = "logo.png"

# ১. পেজ সেটিংস
st.set_page_config(
page_title="Bigganbaksho Order Converter",
layout="wide",
page_icon=logo_path if os.path.exists(logo_path) else "🚀"
)

# ২. CSS ডিজাইন (বিশাল বোল্ড কমলা টাইটেল)
st.markdown("""
<style>
.main-title {
text-align: center; color: #FF6600; font-size: 65px; font-weight: 800;
margin-top: -100px; margin-bottom: 15px; line-height: 1.1;
}
.developer-text { text-align: center; font-style: italic; font-size: 19px; color: #555; }
.slogan-text { text-align: center; font-size: 32px; font-weight: 800; color: #000; margin-top: 20px; }
.vision-text { text-align: center; font-size: 22px; color: #444; margin-bottom: 40px; }
.upload-label { font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

if os.path.exists(logo_path):
    st.image(logo_path, width=130)

st.markdown('<div class=main-title"">Bigganbaksho Order Converter</div>', unsafe_allow_html=True)"
st.markdown('<div class="developer-text">Web App Developed By-Shujoy Shaha</div>', unsafe_allow_html=True)
st.markdown('<div class="slogan-text">ম্যানুয়েল কাজের দিন শেষ, বিজ্ঞানবাক্সে বাংলাদেশ</div>', unsafe_allow_html=True)
st.markdown('<div class="vision-text">অন্যরকম বাংলাদেশের স্বপ্ন নিয়ে</div>', unsafe_allow_html=True)
st.markdown("---")

# ৩. টেক্সট ক্লিন করার ফাংশন
def normalize_text(text):
if not text: return ""
text = str(text).strip()
text = re.sub(r'[\u200b-\u200d\uFEFF]', '', text) # অদৃশ্য ক্যারেক্টার রিমুভ
return text

# ৪. প্রোডাক্ট ও প্যাকেজ ম্যাপিং
MAPPING = {
আলোর ঝলক: "ALOR JHALAK",
চুম্বকের চমক: "CHUMBAKER CHAMAK",
তড়িৎ তাণ্ডব: "TARIT TANDOB",
রসায়ন রহস্য: "RASHAYON RAHOSSHO",
অদ্ভুত মাপজোখ: "ODVUT MAPJOKH",
ট্যানগ্রাম: "MAGNETIC TANGRAM",
পঞ্চম শ্রেণি: "CLASS FIVE Kit",
ফোকাস চ্যালেঞ্জ: "FOCUS CHALLENGE- BANGLA VERSION",
ফোকাস চ্যালেঞ্জ কিট: "FOCUS CHALLENGE- BANGLA VERSION",
মজার পেরিস্কোপ: "MOJAR PERISCOPE",
Mystery of Chemistry: "MYSTERY OF CHEMISTRY",
Amazing Electricity: "AMAZING ELECTRICITY",
Fun with Measurement: "FUN WITH MEASUREMENT",
Magic of Magnet: "MAGIC OF MAGNET",
Color of Light: "COLOR OF LIGHT",
Focus Challenge: "FOCUS CHALLENGE- ENGLISH VERSION",
মহাকাশের জগৎ: "MOHAKASHER JAGAT",
ব্রেইন বুস্টার: "Brain Booster",
Power Of Personality: "Power Of Personality"
}

# ৩টি প্যাকেজের লিস্ট
BUNDLES = {
ব্রেইন ডেভেলপমেন্ট প্যাকেজ: ["MAGNETIC TANGRAM", "FOCUS CHALLENGE- BANGLA VERSION", "Brain Booster"],
Little Genius Package: ["CHUMBAKER CHAMAK", "MOHAKASHER JAGAT", "MOJAR PERISCOPE"],
জুনিয়র সায়েন্টিস্ট প্যাকেজ: ["ALOR JHALAK", "CHUMBAKER CHAMAK", "TARIT TANDOB", "RASHAYON RAHOSSHO", "ODVUT MAPJOKH"]
}

def clean_phone(phone):
if not phone: return ""
p = str(phone).strip()
if p.endswith('.0'): p = p[:-2]
if p.startswith('880'): p = '0' + p[3:]
if p.startswith('+880'): p = '0' + p[4:]
if not p.startswith('0') and len(p) > 5: p = '0' + p
return p

# ৫. মেইন প্রসেসিং অংশ
st.markdown('<p class="upload-label">ওয়েবসাইটের এক্সেল ফাইলটি আপলোড করুন</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=['xlsx', 'csv'], label_visibility="collapsed")

if uploaded_file:
try:
if uploaded_file.name.endswith('.csv'):
df = pd.read_csv(uploaded_file, dtype={'Phone (Billing)': str, 'Order Number': str})
else:
df = pd.read_excel(uploaded_file, dtype={'Phone (Billing)': str, 'Order Number': str})

df = df.fillna("")
grouped = df.groupby('Order Number', sort=False)
final_data = []

for order_id, group in grouped:
first_row = group.iloc[0]
first_n = normalize_text(first_row.get('First Name (Billing)', ''))
last_n = normalize_text(first_row.get('Last Name (Billing)', ''))
full_name = f"{first_n} {last_n}".strip()
phone_num = clean_phone(first_row.get('Phone (Billing)', ''))

discount_val = first_row.get('Cart Discount Amount', "")
try:
if discount_val == "" or float(discount_val) == 0: discount_val = ""
except: discount_val = ""

row_dict = {
Name: full_name, "Contact Number": phone_num,
Address: first_row.get('Address 1&2 (Billing)', ''),
District: first_row.get('City (Billing)', ''),
Sub District: "", "Total Amount": "",
Shipping Charge: first_row.get('Order Shipping Amount', 0),
Discount: discount_val, "Invoice ID": order_id,
Order Collector: "", "Source": "Website Bigganbaksho.com",
AD ID: first_row.get('Customer Note', ''),
Profession: "", "Class": "", "Age": "", "User Name": "", "Birth Date": ""
}

slot = 1
for _, item in group.iterrows():
raw_name = normalize_text(item.get('Item Name', '')).replace('- additional', '').strip()
qty = item.get('Quantity (- Refund)', 0)

is_bundle = False
# যেকোনো প্যাকেজ ডিটেক্ট করার জন্য লুপ
for bundle_name, bundle_items in BUNDLES.items():
if bundle_name in raw_name or raw_name in bundle_name:
is_bundle = True
for b_item in bundle_items:
if slot <= 15:
row_dict[f"Product Name-{slot}"] = b_item
row_dict[f"Product Price-{slot}"] = ""
row_dict[f"Product QTY-{slot}"] = qty
slot += 1
break # একটি আইটেম একটি প্যাকেজ হিসেবে শনাক্ত হলে লুপ থেকে বের হবে

# যদি কোনো প্যাকেজ না হয়, সাধারণ প্রোডাক্ট হিসেবে বসবে
if not is_bundle:
if slot <= 15:
final_name = MAPPING.get(raw_name, raw_name)
row_dict[f"Product Name-{slot}"] = final_name
row_dict[f"Product Price-{slot}"] = ""
row_dict[f"Product QTY-{slot}"] = qty
slot += 1

final_data.append(row_dict)

output_columns = [
Name, "Contact Number", "Address", "District", "Sub District",
Total Amount, "Shipping Charge", "Discount", "Invoice ID",
Order Collector, "Source", "Product Name-1", "Product Price-1", "Product QTY-1",
Profession, "Class", "Age", "User Name", "Birth Date", "AD ID",
Product Name-2, "Product Price-2", "Product QTY-2",
Product Name-3, "Product Price-3", "Product QTY-3",
Product Name-4, "Product Price-4", "Product QTY-4",
Product Name-5, "Product Price-5", "Product QTY-5",
Product Name-6, "Product Price-6", "Product QTY-6",
Product Name-7, "Product Price-7", "Product QTY-7",
Product Name-8, "Product Price-8", "Product QTY-8",
Product Name-9, "Product Price-9", "Product QTY-9",
Product Name-10, "Product Price-10", "Product QTY-10",
Product Name-11, "Product Price-11", "Product QTY-11",
Product Name-12, "Product Price-12", "Product QTY-12",
Product Name-13, "Product Price-13", "Product QTY-13",
Product Name-14, "Product Price-14", "Product QTY-14",
Product Name-15, "Product Price-15", "Product QTY-15"
]

result_df = pd.DataFrame(final_data).reindex(columns=output_columns, fill_value="")
result_df.index = result_df.index + 1
st.success(f"সফলভাবে {len(result_df)} টি অর্ডার প্রসেস করা হয়েছে!")
st.dataframe(result_df)

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
result_df.to_excel(writer, index=False, sheet_name='Orders')
workbook  = writer.book
worksheet = writer.sheets['Orders']
text_format = workbook.add_format({'num_format': '@'})
worksheet.set_column('B:B', 20, text_format)

st.download_button(label="গুগল শীট ফাইল ডাউনলোড করুন", data=output.getvalue(),
file_name="Bigganbaksho_Final_Orders.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

except Exception as e:
st.error(f"Error: {e}")
