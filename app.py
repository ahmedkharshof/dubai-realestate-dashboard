import streamlit as st
import pandas as pd
import os
import re

# ==========================================
# 1. إعداد الصفحة ونظام الحماية (Security)
# ==========================================
st.set_page_config(page_title="Dubai Real Estate Dashboard", page_icon="🏢", layout="wide")

st.sidebar.title("🛡️ Secure Access")
password = st.sidebar.text_input("Enter Password", type="password")
if password != "hhhhhblshfa":
    st.title("Dubai Luxury Real Estate Portfolio")
    st.markdown("---")
    st.info("👋 Welcome! Please enter the access code provided by **Ahmed Dash** to unlock the dashboard.")
    st.stop()

# ==========================================
# 2. تصميم الواجهة (Luxury Aesthetic)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Playfair Display', serif; }
    .gold-text { color: #D4AF37 !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #D4AF37 !important; border-bottom-color: #D4AF37 !important; }
    .metric-card { background-color: #1A1C23; padding: 15px; border-radius: 8px; border-left: 4px solid #D4AF37; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. محرك استخراج المربعات (Anchor-Based Parser)
# ==========================================
@st.cache_data
def load_data(file_path):
    xl = pd.ExcelFile(file_path)
    all_data = {}
    
    for sheet in xl.sheet_names:
        # قراءة الشيت كشبكة (Grid) بالكامل وتحويل الفراغات لنصوص فارغة
        df = xl.parse(sheet, header=None).fillna('')
        df = df.astype(str).map(lambda x: x.strip())
        
        sheet_data = {
            "Overview": {}, "Location": {}, "Developer Info": {}, 
            "Partnership Terms": {}, "Amenities": [], "Payment Plan": [], 
            "Inventory_Detailed": [], "Inventory_Summary": []
        }
        
        # دالة مساعدة لجلب قيمة الخلية بأمان
        def get_val(r, c):
            if 0 <= r < len(df) and 0 <= c < len(df.columns): return df.iloc[r, c]
            return ""
        
        visited_rows = set() # لمنع قراءة نفس الجدول مرتين
        
        # البحث في كل خلية عن "نقاط الارتكاز" (التي حددتها أنت في المربعات)
        for r in range(len(df)):
            for c in range(len(df.columns)):
                cell = get_val(r, c).lower()
                
                # أ) المربعات التي تحتوي على (Field | Value)
                if cell == "field" and get_val(r, c+1).lower() == "value":
                    section = "Overview"
                    # فحص العنوان الذي يسبق الجدول لمعرفة نوعه
                    title1 = get_val(r-1, c).lower() if r > 0 else ""
                    title2 = get_val(r-2, c).lower() if r > 1 else ""
                    
                    if "location" in title1 or "location" in title2: section = "Location"
                    elif "developer" in title1 or "developer" in title2: section = "Developer Info"
                    elif "partnership" in title1 or "partnership" in title2: section = "Partnership Terms"
                    
                    for curr_r in range(r+1, len(df)):
                        k, v = get_val(curr_r, c), get_val(curr_r, c+1)
                        if not k and not v: break # توقف عند الصف الفارغ
                        if k.lower() in ["field", "location", "amenities", "payment plan", "stage", "developer information"]: break
                        if k: sheet_data[section][k] = v

                # ب) مربع خطة الدفع (Stage | Percentage)
                elif cell == "stage" and get_val(r, c+1).lower() == "percentage":
                    for curr_r in range(r+1, len(df)):
                        stage, perc = get_val(curr_r, c), get_val(curr_r, c+1)
                        if not stage and not perc: break
                        if stage.lower() in ["location", "amenities", "field"]: break
                        if stage: sheet_data["Payment Plan"].append({"Stage": stage, "Percentage": perc})

                # ج) مربع المميزات (Amenities)
                elif cell == "amenities":
                    for curr_r in range(r+1, len(df)):
                        am = get_val(curr_r, c)
                        if not am: break
                        if am.lower() in ["field", "location", "developer information", "stage"]: break
                        sheet_data["Amenities"].append(am)

                # د) مربع الوحدات التفصيلي (Unit No.)
                elif cell in ["unit no.", "unit no"]:
                    if r in visited_rows: continue
                    headers = []
                    hc = c
                    while get_val(r, hc):
                        headers.append(get_val(r, hc))
                        hc += 1
                        
                    for curr_r in range(r+1, len(df)):
                        visited_rows.add(curr_r)
                        row_vals = [get_val(curr_r, c+i) for i in range(len(headers))]
                        if not any(row_vals): break
                        if row_vals[0].lower() in ["unit type", "payment plan", "location"]: break
                        if row_vals[0] and not row_vals[1] and not row_vals[2]: continue # تجاهل العناوين الفرعية
                        
                        row_dict = dict(zip(headers, row_vals))
                        if row_dict.get(headers[0]): sheet_data["Inventory_Detailed"].append(row_dict)

                # هـ) مربع ملخص الوحدات (Unit Type)
                elif cell == "unit type":
                    if r in visited_rows: continue
                    headers = []
                    hc = c
                    while get_val(r, hc):
                        headers.append(get_val(r, hc))
                        hc += 1
                        
                    for curr_r in range(r+1, len(df)):
                        visited_rows.add(curr_r)
                        row_vals = [get_val(curr_r, c+i) for i in range(len(headers))]
                        if not any(row_vals): break
                        if row_vals[0].lower() in ["unit no.", "payment plan", "location"]: break
                        if row_vals[0] and not row_vals[1]: continue
                        
                        row_dict = dict(zip(headers, row_vals))
                        if row_dict.get(headers[0]): sheet_data["Inventory_Summary"].append(row_dict)

        all_data[sheet] = sheet_data
    return all_data

# ==========================================
# 4. بناء لوحة التحكم (Dashboard Layout)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.title("Dubai Real Estate")
st.sidebar.markdown("<p class='gold-text'>Luxury Portfolio</p>", unsafe_allow_html=True)

file_path = os.path.join(os.path.dirname(__file__), "Project (1) - Copy.xlsx")
if not os.path.exists(file_path): file_path = r"d:\mr pual\Project (1) - Copy.xlsx"

try:
    data = load_data(file_path)
    regions = list(data.keys())
    selected_region = st.sidebar.selectbox("📍 Select Region", regions)
    
    if selected_region:
        project = data[selected_region]
        
        # استخراج اسم المشروع وعرضه
        p_name = project["Overview"].get("Project Name", selected_region)
        st.title(f"🏙️ {p_name}")
        st.markdown("---")
        
        # تقسيم الواجهة إلى 3 ألسنة (Tabs) احترافية
        tab1, tab2, tab3 = st.tabs(["📋 Overview & Info", "🔑 Availability & Inventory", "💳 Payment & Features"])
        
        # ---- Tab 1: تفاصيل المشروع بالكامل ----
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Project Overview")
                for k, v in project["Overview"].items():
                    if k != "Project Name": st.markdown(f"**{k}:** <span style='color:#CCC'>{v}</span>", unsafe_allow_html=True)
                
                if project["Developer Info"]:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("Developer Information")
                    for k, v in project["Developer Info"].items():
                        st.markdown(f"**{k}:** <span style='color:#CCC'>{v}</span>", unsafe_allow_html=True)
                        
            with col2:
                if project["Location"]:
                    st.subheader("Location")
                    for k, v in project["Location"].items():
                        st.markdown(f"**{k}:** <span style='color:#CCC'>{v}</span>", unsafe_allow_html=True)
                
                if project["Partnership Terms"]:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("Partnership Terms")
                    for k, v in project["Partnership Terms"].items():
                        st.markdown(f"**{k}:** <span style='color:#CCC'>{v}</span>", unsafe_allow_html=True)

        # ---- Tab 2: جداول المخزون المنسقة ----
        with tab2:
            # 1. عرض التفصيلي إذا وجد
            if project["Inventory_Detailed"]:
                st.subheader("Detailed Units Inventory")
                df_inv = pd.DataFrame(project["Inventory_Detailed"])
                # تنظيف الأرقام للترتيب
                for col in df_inv.columns:
                    if any(x in col.lower() for x in ["price", "size"]):
                        df_inv[col] = pd.to_numeric(df_inv[col].str.replace(r'[^\d.]', '', regex=True), errors='coerce')
                st.dataframe(df_inv, use_container_width=True, hide_index=True)
            
            # 2. عرض الملخص إذا وجد
            if project["Inventory_Summary"]:
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("Units Summary")
                df_sum = pd.DataFrame(project["Inventory_Summary"])
                st.table(df_sum)
                
            if not project["Inventory_Detailed"] and not project["Inventory_Summary"]:
                st.info("No inventory data found for this project.")

        # ---- Tab 3: الدفع والمميزات ----
        with tab3:
            col_p, col_a = st.columns([1.5, 1])
            with col_p:
                st.subheader("Payment Plan")
                if project["Payment Plan"]:
                    st.table(pd.DataFrame(project["Payment Plan"]))
                else:
                    st.write("Not specified.")
            with col_a:
                st.subheader("Features & Amenities")
                if project["Amenities"]:
                    for item in project["Amenities"]:
                        st.markdown(f"🔹 {item}")
                else:
                    st.write("Not specified.")

except Exception as e:
    st.error(f"Error loading dashboard data: {e}")