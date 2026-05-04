import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. إعداد الصفحة الأساسي (Page Configuration)
st.set_page_config(page_title="Dubai Real Estate Dashboard", page_icon="🏢", layout="wide")

# 2. نظام حماية وأمان أحمد داش (Password Protection)
st.sidebar.title("🛡️ Secure Access")
password = st.sidebar.text_input("Enter Password to Unlock", type="password")

# التحقق من كلمة المرور قبل تحميل أي بيانات أو عرض الواجهة
if password != "AhmedDash2026":
    st.title("Dubai Luxury Real Estate Portfolio")
    st.markdown("---")
    if password == "":
        st.info("👋 Welcome! Please enter the access code provided by **Ahmed Dash** to view the portfolio.")
    else:
        st.error("🚫 Access Denied: Invalid Password.")
    st.stop() # إيقاف البرنامج تماماً لمنع تسريب البيانات

# 3. تصميم الواجهة الفاخرة (Luxury Dubai Aesthetic)
st.markdown("""
<style>
    .stApp { background-color: #1A1A1A; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6 { color: #D4AF37 !important; font-family: 'Playfair Display', serif; }
    .stTabs [aria-selected="true"] { color: #D4AF37 !important; border-bottom-color: #D4AF37 !important; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333333; }
    .gold-text { color: #D4AF37 !important; }
    .stDataFrame { border: 1px solid #333333; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 4. وظيفة تحميل ومعالجة بيانات الإكسيل (Data Core)
@st.cache_data
def load_data(file_path):
    xl = pd.ExcelFile(file_path)
    data = {}
    
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name, header=None).astype(str)
        projects = []
        current_project = {"name": sheet_name, "details": {}, "units": []}
        
        unit_start_col_idx = -1
        unit_headers = []
        in_units_section = False
        
        for index, row in df.iterrows():
            key = str(row.iloc[0]).strip()
            val = str(row.iloc[1]).strip()
            
            # التقاط اسم المشروع وبيانات الـ Overview
            if "project name" in key.lower():
                current_project["name"] = val
            elif key.lower() not in ["", "nan", "field", "value"]:
                if val.lower() not in ["", "nan"]:
                    current_project["details"][key] = val
            
            # تحديد بداية جدول الوحدات (Inventory)
            if not in_units_section:
                for i, cell in enumerate(row):
                    c_text = str(cell).strip().lower()
                    if "unit no" in c_text or "inventory" in c_text:
                        unit_start_col_idx = i
                        in_units_section = True
                        unit_headers = [str(x).strip() for x in row.iloc[i:] if str(x).lower() not in ["", "nan"]]
                        break
                continue 
            
            # جمع بيانات الوحدات السكنية
            if in_units_section:
                unit_row = [str(x).strip() for x in row.iloc[unit_start_col_idx:]]
                # التوقف عند نهاية الجدول
                if "unit type" in str(row.iloc[0]).lower() or "payment plan" in str(row.iloc[0]).lower():
                    in_units_section = False
                    continue
                
                if not all(x.lower() in ["", "nan"] for x in unit_row):
                    unit_data = dict(zip(unit_headers, unit_row[:len(unit_headers)]))
                    if unit_headers and unit_data.get(unit_headers[0]) and unit_data[unit_headers[0]].lower() not in ["", "nan"]:
                        current_project["units"].append(unit_data)
        
        projects.append(current_project)
        data[sheet_name] = projects
    return data

# 5. منطق واجهة المستخدم (User Interface Logic)
st.sidebar.markdown("---")
st.sidebar.title("Dubai Real Estate")
st.sidebar.markdown("<p class='gold-text'>Luxury Portfolio</p>", unsafe_allow_html=True)

# تحديد مسار الملف (قاعدة البيانات)
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "Project (1) - Copy.xlsx")

# محاولة تحميل البيانات
try:
    data = load_data(file_path)
except Exception as e:
    st.error(f"⚠️ Error: Excel file not found or corrupted. Please ensure 'Project (1) - Copy.xlsx' is in the repository. {e}")
    st.stop()

# اختيار المنطقة والمشروع
regions = list(data.keys())
selected_region = st.sidebar.selectbox("📍 Select Region", regions)

if selected_region:
    projects = data[selected_region]
    selected_p_name = st.sidebar.selectbox("🏢 Select Project", [p["name"] for p in projects])
    project = next((p for p in projects if p["name"] == selected_p_name), None)
    
    if project:
        st.title(f"{project['name']}")
        tab1, tab2, tab3 = st.tabs(["🏗️ Stage & Status", "📍 Location", "✨ Features"])
        
        det = project["details"]
        with tab1:
            st.subheader("Development Details")
            for k in ["Developer", "Status", "Construction Status", "Handover"]:
                if k in det: st.markdown(f"**{k}:** {det[k]}")
        with tab2:
            st.subheader("Location")
            if "District" in det: st.markdown(f"**District:** {det['District']}")
            elif "Location" in det: st.markdown(f"**Location:** {det['Location']}")
        with tab3:
            st.subheader("Amenities & Notes")
            for k, v in det.items():
                if k not in ["Developer", "Status", "Location", "District"] and v:
                    st.markdown(f"🔹 **{k}:** {v}")

        st.markdown("---")
        st.header("🔑 Available Inventory Filter")
        
        # عرض وجدولة الوحدات المتاحة
        if project["units"]:
            df_units = pd.DataFrame(project["units"])
            # البحث عن عمود "نوع الغرف"
            type_col = next((c for c in df_units.columns if any(x in c.lower() for x in ["type", "bedroom"])), None)
            
            if type_col:
                # تنظيف القائمة المنسدلة من "الضوضاء"
                valid_keywords = ['bedroom', 'studio', 'br', 'penthouse', 'duplex']
                mask = df_units[type_col].str.lower().apply(lambda x: any(k in str(x) for k in valid_keywords))
                df_units = df_units[mask]
                
                u_types = ["All"] + sorted(df_units[type_col].unique().tolist())
                sel_type = st.selectbox("Select Bedroom Type", u_types)
                if sel_type != "All":
                    df_units = df_units[df_units[type_col] == sel_type]

            # --- التعديل الجوهري لمعالجة أرقام الأسعار والمساحات (Fixing ValueError) ---
            for col in df_units.columns:
                if any(x in col.lower() for x in ["price", "size"]):
                    try:
                        # تنظيف البيانات من الكلمات التي تسبب عطل مثل "from" أو "AED" أو الفواصل
                        clean_col = df_units[col].astype(str).str.replace(',', '', regex=False)
                        clean_col = clean_col.str.replace('AED', '', regex=False)
                        clean_col = clean_col.str.replace('from', '', regex=False).str.strip()
                        
                        # تحويل القيم لأرقام حقيقية (مع تجاهل الأخطاء بتحويلها لـ NaN)
                        df_units[col] = pd.to_numeric(clean_col, errors='coerce')
                    except Exception:
                        pass
            
            # عرض الجدول النهائي
            st.dataframe(df_units, use_container_width=True, hide_index=True)
        else:
            st.info("No units available for this project at the moment.")