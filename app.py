import streamlit as st
import os
from datetime import datetime, date
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# Session State Initialize
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'saved_bills' not in st.session_state: st.session_state.saved_bills = []
if 'tests' not in st.session_state: st.session_state.tests = []
if 'doctors' not in st.session_state: st.session_state.doctors = ["Self"]
if 'cancel_requests' not in st.session_state: st.session_state.cancel_requests = []
if 'report_data' not in st.session_state: st.session_state.report_data = {}
if 'users' not in st.session_state: 
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

# --- Comprehensive FBC Reference Ranges ---
FBC_RANGES = {
    "Baby": {
        "WBC": "5,000 - 13,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01",
        "RBC": "4.0 - 5.2", "HB": "11.5 - 15.5", "HCT": "35.0 - 45.0", "MCV": "77.0 - 95.0", "MCH": "25.0 - 33.0", "MCHC": "31.0 - 37.0", "RDW": "11.5 - 14.5", "PLT": "150,000 - 450,000"
    },
    "Male": {
        "WBC": "4,000 - 11,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01",
        "RBC": "4.5 - 5.6", "HB": "13.0 - 17.0", "HCT": "40.0 - 50.0", "MCV": "82.0 - 98.0", "MCH": "27.0 - 32.0", "MCHC": "32.0 - 36.0", "RDW": "11.5 - 14.5", "PLT": "150,000 - 400,000"
    },
    "Female": {
        "WBC": "4,000 - 11,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01",
        "RBC": "3.9 - 4.5", "HB": "11.5 - 15.5", "HCT": "35.0 - 45.0", "MCV": "82.0 - 98.0", "MCH": "27.0 - 32.0", "MCHC": "32.0 - 36.0", "RDW": "11.5 - 14.5", "PLT": "150,000 - 400,000"
    }
}

# --- PDF Generation Function (Full FBC) ---
def create_report_pdf(bill, res, abs_counts, fmt, comment):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "LIFE CARE LABORATORY", ln=True, align='C')
    pdf.set_font("Arial", '', 9); pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana. Tel: 0773326715", ln=True, align='C')
    pdf.ln(5); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)
    
    # Patient Data
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 6, "Patient Name:"); pdf.set_font("Arial", '', 10); pdf.cell(80, 6, bill['patient'])
    pdf.set_font("Arial", 'B', 10); pdf.cell(30, 6, "Date:"); pdf.set_font("Arial", '', 10); pdf.cell(0, 6, bill['date'], ln=True)
    pdf.set_font("Arial", 'B', 10); pdf.cell(30, 6, "Ref. Doctor:"); pdf.set_font("Arial", '', 10); pdf.cell(80, 6, bill.get('doctor', 'Self'))
    pdf.set_font("Arial", 'B', 10); pdf.cell(30, 6, "Ref. No:"); pdf.set_font("Arial", '', 10); pdf.cell(0, 6, bill['bill_id'], ln=True)
    
    pdf.ln(8); pdf.set_font("Arial", 'BU', 12); pdf.cell(0, 10, "FULL BLOOD COUNT", ln=True, align='C'); pdf.ln(5)
    
    # Header
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(65, 8, "TEST DESCRIPTION", 1); pdf.cell(25, 8, "RESULT", 1, 0, 'C'); pdf.cell(25, 8, "UNIT", 1, 0, 'C'); pdf.cell(30, 8, "ABS. COUNT", 1, 0, 'C'); pdf.cell(45, 8, "REF. RANGE", 1, 1, 'C')
    
    ranges = FBC_RANGES[fmt]
    pdf.set_font("Arial", '', 9)
    
    def add_row(label, key, unit, is_abs=False):
        pdf.cell(65, 7, label, 1)
        pdf.cell(25, 7, str(res.get(key, '-')), 1, 0, 'C')
        pdf.cell(25, 7, unit, 1, 0, 'C')
        abs_val = str(abs_counts.get(key, '-')) if is_abs else ""
        pdf.cell(30, 7, abs_val, 1, 0, 'C')
        pdf.cell(45, 7, ranges.get(key, ''), 1, 1, 'C')

    # Rows
    add_row("WHITE BLOOD CELLS", "WBC", "cells/cu.mm")
    pdf.set_font("Arial", 'B', 8); pdf.cell(190, 6, "DIFFERENTIAL COUNT", 1, 1, 'L'); pdf.set_font("Arial", '', 9)
    add_row("NEUTROPHILS", "NEU", "%", True)
    add_row("LYMPHOCYTES", "LYM", "%", True)
    add_row("MONOCYTES", "MON", "%", True)
    add_row("EOSINOPHILS", "EOS", "%", True)
    add_row("BASOPHILS", "BAS", "%", True)
    pdf.set_font("Arial", 'B', 8); pdf.cell(190, 6, "Hb AND RBC INDICES", 1, 1, 'L'); pdf.set_font("Arial", '', 9)
    add_row("RED BLOOD CELLS", "RBC", "mill/cu.mm")
    add_row("HAEMOGLOBIN", "HB", "g/dl")
    add_row("PACKED CELL VOLUME (HCT)", "HCT", "%")
    add_row("MCV", "MCV", "fl")
    add_row("MCH", "MCH", "pg")
    add_row("MCHC", "MCHC", "g/dl")
    add_row("RDW", "RDW", "%")
    add_row("PLATELET COUNT", "PLT", "/cu.mm")

    if comment:
        pdf.ln(5); pdf.set_font("Arial", 'B', 9); pdf.cell(0, 6, "Comments:", ln=True)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, comment)

    return pdf.output(dest='S').encode('latin-1')

# --- Main App (Login & Admin/Billing Unchanged) ---
if not st.session_state.logged_in:
    u = st.text_input("Username"); p = st.text_input("Password", type="password")
    r = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"])
    if st.button("Login"):
        user = next((x for x in st.session_state.users if x['username'] == u and x['password'] == p and x['role'] == r), None)
        if user: st.session_state.logged_in, st.session_state.current_user, st.session_state.role = True, u, r; st.rerun()
else:
    # (Existing Logout/Dashboard logic)
    if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

    # Admin & Billing Sections remain untouched...
    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        # [Existing Admin Tabs...]

    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        # [Existing Billing Tabs...]

    # --- TECHNICIAN DASHBOARD ---
    elif st.session_state.role == "Technician":
        st.title("🔬 Technician Dashboard")
        pending = [b for b in st.session_state.saved_bills if b['bill_id'] not in st.session_state.report_data]
        
        st.subheader("📋 Pending Tests")
        for b in pending:
            c1, c2 = st.columns([4, 1]); c1.write(f"**{b['bill_id']}** | {b['patient']}")
            if c2.button("Enter Result", key=f"e_{b['bill_id']}"): st.session_state.active_rid = b['bill_id']
        
        if 'active_rid' in st.session_state:
            bill = next(x for x in pending if x['bill_id'] == st.session_state.active_rid)
            fmt = "Baby" if bill['age_y'] < 5 else ("Male" if "Mr." in bill['patient'] or "Baby" in bill['patient'] else "Female")
            
            st.divider(); st.subheader(f"📝 FBC Result Entry - {bill['patient']} ({fmt})")
            
            with st.form("fbc_full_form"):
                # Data Entry in Tab Order
                c1, c2, c3 = st.columns(3)
                wbc = c1.number_input("WBC (Total)", min_value=0, step=1)
                neu = c2.number_input("Neutrophils %", min_value=0.0, step=0.1)
                lym = c3.number_input("Lymphocytes %", min_value=0.0, step=0.1)
                mon = c1.number_input("Monocytes %", min_value=0.0, step=0.1)
                eos = c2.number_input("Eosinophils %", min_value=0.0, step=0.1)
                bas = c3.number_input("Basophils %", min_value=0.0, step=0.1)
                rbc = c1.number_input("RBC (mill/cu.mm)", min_value=0.0, step=0.01)
                hb = c2.number_input("Hb (g/dl)", min_value=0.0, step=0.1)
                hct = c3.number_input("PCV/HCT %", min_value=0.0, step=0.1)
                mcv = c1.number_input("MCV (fl)", min_value=0.0, step=0.1)
                mch = c2.number_input("MCH (pg)", min_value=0.0, step=0.1)
                mchc = c3.number_input("MCHC (g/dl)", min_value=0.0, step=0.1)
                rdw = c1.number_input("RDW %", min_value=0.0, step=0.1)
                plt = c2.number_input("Platelets", min_value=0, step=1000)
                
                comment = st.text_area("Doctor's Comments / Notes")
                
                if st.form_submit_button("Authorize & Save Report"):
                    # Calculate Absolute Counts: WBC / 100 * Percentage
                    abs_c = {
                        "NEU": round((wbc * neu) / 100) if wbc and neu else 0,
                        "LYM": round((wbc * lym) / 100) if wbc and lym else 0,
                        "MON": round((wbc * mon) / 100) if wbc and mon else 0,
                        "EOS": round((wbc * eos) / 100) if wbc and eos else 0,
                        "BAS": round((wbc * bas) / 100) if wbc and bas else 0,
                    }
                    res_dict = {
                        "WBC": wbc, "NEU": neu, "LYM": lym, "MON": mon, "EOS": eos, "BAS": bas,
                        "RBC": rbc, "HB": hb, "HCT": hct, "MCV": mcv, "MCH": mch, "MCHC": mchc, "RDW": rdw, "PLT": plt
                    }
                    st.session_state.report_data[bill['bill_id']] = {"res": res_dict, "abs": abs_c, "fmt": fmt, "comment": comment}
                    del st.session_state.active_rid; st.success("Report Authorized!"); st.rerun()

        st.divider(); st.subheader("🖨 Authorized Reports")
        for rid, data in st.session_state.report_data.items():
            b_orig = next((x for x in st.session_state.saved_bills if x['bill_id'] == rid), None)
            if b_orig:
                c1, c2 = st.columns([4, 1]); c1.write(f"✅ {rid} - {b_orig['patient']}")
                c2.download_button("Print PDF", create_report_pdf(b_orig, data['res'], data['abs'], data['fmt'], data['comment']), file_name=f"FBC_{rid}.pdf", key=f"p_{rid}")

    # Satellite Unchanged...
    elif st.session_state.role == "Satellite":
        st.title("📡 Satellite Dashboard")
        # [Existing Satellite Logic...]