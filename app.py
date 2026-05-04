import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. إعداد الصفحة
st.set_page_config(page_title="Dubai Real Estate Dashboard", page_icon="🏢", layout="wide")

# 2. نظام الحماية (Password Protection)
st.sidebar.title("🛡️ Secure Access")
password = st.sidebar.text_input("Enter Password to Unlock", type="password")

if password != "AhmedDash2026":
    st.title("Dubai Luxury Real Estate Portfolio")
    st.markdown("---")
    if password == "":
        st.info("👋 Welcome! Please enter the access code provided by **Ahmed Dash**.")
    else:
        st.error("🚫 Invalid Password.")
    st.stop()

# 3. التنسيق الجمالي (Luxury Style)
st.markdown("""
<style>
    .stApp { background-color: #1A1A1A; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6 { color: #D4AF37 !important; font-family: 'Playfair Display', serif; }
    .gold-text { color: #D4AF37 !important; }
</style>
""", unsafe_allow_html=True)

# 4. محرك البحث الديناميكي عن البيانات (Dynamic Core Engine)
@st.cache_data
def load_data(file_path):
    xl = pd.ExcelFile(file_path)
    all_data = {}
    
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name, header=None).astype(str)
        # استبدال 'nan' بفراغ حقيقي لسهولة المعالجة
        df = df.replace('nan', '')
        
        project_info = {"name": sheet_name, "details": {}, "units": []}
        
        # أ) استخراج تفاصيل المشروع (العمود A و B عادة)
        for idx, row in df.iterrows():
            key = str(row.iloc[0]).strip()
            val = str(row.iloc[1]).strip()
            if key.lower() == "project name": project_info["name"] = val
            elif key and val and key.lower() not in ["field", "value"]:
                # التوقف عند الوصول لأقسام أخرى في العمود الأول
                if any(x in key.lower() for x in ["payment plan", "amenities", "location"]): break
                project_info["details"][key] = val

        # ب) البحث الديناميكي عن جدول الوحدات (البحث عن خلية Unit No.)
        unit_row_idx, unit_col_idx = -1, -1
        for r_idx, row in df.iterrows():
            for c_idx, cell in enumerate(row):
                if "unit no" in str(cell).lower():
                    unit_row_idx, unit_col_idx = r_idx, c_idx
                    break
            if unit_row_idx != -1: break

        # ج) قراءة جدول الوحدات إذا وجد
        if unit_row_idx != -1:
            # استخراج العناوين من صف "Unit No."
            headers = [str(h).strip() for h in df.iloc[unit_row_idx, unit_col_idx:] if str(h).strip()]
            
            # قراءة الصفوف التالية للرأس
            for r in range(unit_row_idx + 1, len(df)):
                current_row = df.iloc[r, unit_col_idx : unit_col_idx + len(headers)].tolist()
                
                # التحقق من أن الصف ليس فارغاً أو بداية قسم جديد
                first_cell = str(df.iloc[r, 0]).lower()
                if any(x in first_cell for x in ["payment plan", "location", "amenities", "features"]): break
                
                if any(str(c).strip() for c in current_row):
                    unit_dict = dict(zip(headers, current_row))
                    # تنظيف: استبعاد الصفوف التي هي مجرد عناوين فرعية (مثل "1 Bedroom Units")
                    u_no = str(unit_dict.get(headers[0], "")).lower()
                    if u_no and "bedroom" not in u_no and "studio" not in u_no and "units" not in u_no:
                        project_info["units"].append(unit_dict)
                        
        all_data[sheet_name] = [project_info]
    return all_data

# 5. واجهة العرض
st.sidebar.title("Dubai Real Estate")
st.sidebar.markdown("<p class='gold-text'>Luxury Portfolio</p>", unsafe_allow_html=True)

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "Project (1) - Copy.xlsx")

if not os.path.exists(file_path):
    file_path = r"d:\mr pual\Project (1) - Copy.xlsx"

try:
    data = load_data(file_path)
    regions = list(data.keys())
    selected_region = st.sidebar.selectbox("📍 Select Region/Sheet", regions)
    
    if selected_region:
        project = data[selected_region][0]
        st.title(f"{project['name']}")
        
        tab1, tab2 = st.tabs(["🏗️ Details & Amenities", "🔑 Inventory"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                for k, v in list(project["details"].items())[:8]: st.write(f"**{k}:** {v}")
            with col2:
                for k, v in list(project["details"].items())[8:]: st.write(f"**{k}:** {v}")
                
        with tab2:
            if project["units"]:
                df_units = pd.DataFrame(project["units"])
                # تنظيف الأرقام ديناميكياً
                for col in df_units.columns:
                    if any(x in col.lower() for x in ["price", "size"]):
                        df_units[col] = pd.to_numeric(df_units[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
                
                st.dataframe(df_units, use_container_width=True, hide_index=True)
            else:
                st.info("No unit data found using the dynamic scanner.")
except Exception as e:
    st.error(f"Error: {e}")