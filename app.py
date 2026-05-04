import streamlit as st
import pandas as pd
import os
import re

# 1. إعداد الصفحة
st.set_page_config(page_title="Dubai Real Estate Dashboard", page_icon="🏢", layout="wide")

# 2. نظام الحماية (Password Protection)
st.sidebar.title("🛡️ Secure Access")
password = st.sidebar.text_input("Enter Password", type="password")
if password != "AhmedDash2026":
    st.info("👋 Welcome! Please enter the access code to unlock the portfolio.")
    st.stop()

# 3. التنسيق الجمالي المحسن (Luxury Aesthetic)
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Playfair Display', serif; }
    .gold-text { color: #D4AF37 !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #D4AF37 !important; border-bottom-color: #D4AF37 !important; }
    div[data-testid="stExpander"] { border: 1px solid #333; background-color: #1A1C23; }
</style>
""", unsafe_allow_html=True)

# 4. محرك استخراج البيانات المطور
@st.cache_data
def load_data(file_path):
    xl = pd.ExcelFile(file_path)
    all_data = {}
    
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name, header=None).astype(str).replace('nan', '')
        
        project = {
            "name": sheet_name,
            "details": {},
            "summary_table": [],
            "inventory": [],
            "amenities": []
        }
        
        # أ) استخراج التفاصيل العامة (العمود A و B)
        for idx, row in df.iterrows():
            key, val = str(row.iloc[0]).strip(), str(row.iloc[1]).strip()
            if not key: continue
            
            # التوقف عند بداية الجداول الفرعية
            if any(x in key.lower() for x in ["unit type", "payment plan", "amenities", "location"]): break
            
            if key.lower() == "project name": project["name"] = val
            elif val:
                # تنسيق التاريخ والنسب المئوية
                if "date" in key.lower() or "added" in key.lower():
                    val = val.split(' ')[0] # حذف الوقت من التاريخ
                if "progress" in key.lower() and val == "1": val = "100%"
                project["details"][key] = val

        # ب) استخراج جدول ملخص الوحدات (Unit Type, Count, etc.)
        summary_idx = df[df.iloc[:, 0].str.lower().str.contains("unit type", na=False)].index
        if not summary_idx.empty:
            start_r = summary_idx[0]
            headers = [h for h in df.iloc[start_r] if h]
            for r in range(start_r + 1, start_r + 5):
                row_vals = df.iloc[r, :len(headers)].tolist()
                if row_vals[0] and "bedroom" in row_vals[0].lower():
                    project["summary_table"].append(dict(zip(headers, row_vals)))

        # ج) استخراج جدول المخزون الكامل (Unit No.) ديناميكياً
        unit_row_idx, unit_col_idx = -1, -1
        for r_idx, row in df.iterrows():
            for c_idx, cell in enumerate(row):
                if "unit no" in str(cell).lower():
                    unit_row_idx, unit_col_idx = r_idx, c_idx
                    break
            if unit_row_idx != -1: break

        if unit_row_idx != -1:
            headers = [str(h).strip() for h in df.iloc[unit_row_idx, unit_col_idx:] if str(h).strip()]
            for r in range(unit_row_idx + 1, len(df)):
                row_data = df.iloc[r, unit_col_idx : unit_col_idx + len(headers)].tolist()
                u_no = str(row_data[0]).strip()
                if u_no and not any(x in u_no.lower() for x in ["bedroom", "unit", "summary"]):
                    project["inventory"].append(dict(zip(headers, row_data)))
                elif u_no == "" and r > unit_row_idx + 5: break # توقف إذا زادت الصفوف الفارغة

        all_data[sheet_name] = project
    return all_data

# 5. واجهة العرض (Ahmed Dash Luxury UI)
st.sidebar.title("Dubai Real Estate")
st.sidebar.markdown("<p class='gold-text'>Luxury Portfolio</p>", unsafe_allow_html=True)

file_path = os.path.join(os.path.dirname(__file__), "Project (1) - Copy.xlsx")
if not os.path.exists(file_path): file_path = r"d:\mr pual\Project (1) - Copy.xlsx"

try:
    data = load_data(file_path)
    selected_region = st.sidebar.selectbox("📍 Select Region", list(data.keys()))
    
    if selected_region:
        project = data[selected_region]
        st.title(f"🏙️ {project['name']}")
        
        tab1, tab2, tab3 = st.tabs(["📋 Project Overview", "📊 Inventory Summary", "🔑 Detailed Inventory"])
        
        with tab1:
            st.subheader("Development Details")
            cols = st.columns(2)
            items = list(project["details"].items())
            mid = (len(items) + 1) // 2
            for i, (k, v) in enumerate(items):
                cols[0 if i < mid else 1].markdown(f"**{k}:** <span style='color:#DDD'>{v}</span>", unsafe_allow_html=True)
        
        with tab2:
            if project["summary_table"]:
                st.subheader("Inventory Snapshot")
                st.table(pd.DataFrame(project["summary_table"]))
            else: st.info("No summary table available.")

        with tab3:
            if project["inventory"]:
                df_inv = pd.DataFrame(project["inventory"])
                # تنظيف الأرقام للترتيب (Sorting)
                for col in df_inv.columns:
                    if any(x in col.lower() for x in ["price", "size"]):
                        df_inv[col] = pd.to_numeric(df_inv[col].str.replace(r'[^\d.]', '', regex=True), errors='coerce')
                
                st.subheader("Available Units")
                st.dataframe(df_inv, use_container_width=True, hide_index=True)
            else: st.info("Inventory table not detected.")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")