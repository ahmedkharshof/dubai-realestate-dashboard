import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. إعداد الصفحة الأساسي
st.set_page_config(page_title="Dubai Real Estate Dashboard", page_icon="🏢", layout="wide")

# 2. واجهة الدخول والأمان (Ahmed Dash Protection)
st.sidebar.title("🛡️ Secure Access")
password = st.sidebar.text_input("Enter Password to Unlock", type="password")

if password != "AhmedDash2026":
    st.title("Welcome to Dubai Luxury Real Estate Portfolio")
    st.markdown("---")
    if password == "":
        st.info("Please enter the access code provided by **Ahmed Dash** in the sidebar to view the data.")
    else:
        st.error("Invalid password. Access to the portfolio is restricted.")
    
    st.stop() # توقف كامل للبرنامج ومنع قراءة ملف الإكسيل

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

# 4. وظيفة تحميل ومعالجة البيانات
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
            
            if "project name" in key.lower():
                current_project["name"] = val
            elif key.lower() not in ["", "nan", "field", "value"]:
                if val.lower() not in ["", "nan"]:
                    current_project["details"][key] = val
            
            if not in_units_section:
                for i, cell in enumerate(row):
                    c_text = str(cell).strip().lower()
                    if "unit no" in c_text or "inventory" in c_text:
                        unit_start_col_idx = i
                        in_units_section = True
                        unit_headers = [str(x).strip() for x in row.iloc[i:] if str(x).lower() not in ["", "nan"]]
                        break
                continue 
            
            if in_units_section:
                unit_row = [str(x).strip() for x in row.iloc[unit_start_col_idx:]]
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

# ---- منطق واجهة المستخدم المتقدمة ----
st.sidebar.markdown("---")
st.sidebar.title("Dubai Real Estate")
st.sidebar.markdown("<p class='gold-text'>Luxury Portfolio</p>", unsafe_allow_html=True)

# مسار الملف (يبحث في المجلد الحالي لسهولة التشغيل عند العميل)
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "Project (1) - Copy.xlsx")

if not os.path.exists(file_path):
    file_path = r"d:\mr pual\Project (1) - Copy.xlsx"

try:
    data = load_data(file_path)
except Exception as e:
    st.error(f"Error: Could not find or read the Excel file. {e}")
    st.stop()

selected_region = st.sidebar.selectbox("📍 Select Region", list(data.keys()))

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
        with tab3:
            st.subheader("Amenities & Notes")
            for k, v in det.items():
                if k not in ["Developer", "Status", "Location", "District"] and v:
                    st.markdown(f"🔹 **{k}:** {v}")

        st.markdown("---")
        st.header("🔑 Available Inventory Filter")
        
        if project["units"]:
            df_units = pd.DataFrame(project["units"])
            type_col = next((c for c in df_units.columns if any(x in c.lower() for x in ["type", "bedroom"])), None)
            
            if type_col:
                valid_keywords = ['bedroom', 'studio', 'br', 'penthouse', 'duplex']
                mask = df_units[type_col].str.lower().apply(lambda x: any(k in str(x) for k in valid_keywords))
                df_units = df_units[mask]
                
                u_types = ["All"] + sorted(df_units[type_col].unique().tolist())
                sel_type = st.selectbox("Select Bedroom Type", u_types)
                if sel_type != "All":
                    df_units = df_units[df_units[type_col] == sel_type]

            # تنسيق العملة والمساحة
            for col in df_units.columns:
                if any(x in col.lower() for x in ["price", "size"]):
                    df_units[col] = pd.to_numeric(df_units[col].str.replace(',', '').str.replace('AED', '').str.strip(), errors='ignore')
            
            st.dataframe(df_units, use_container_width=True, hide_index=True)
        else:
            st.info("No units available for this project.")