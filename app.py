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

# --- FBC Reference Ranges (Based on your formats) ---
FBC_RANGES = {
    "Baby": {
        "WBC": "5,000 - 13,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01",
        "RBC": "4.0 - 5.2", "HB": "11.5 - 15.5", "PCV": "35.0 - 45.0", "MCV": "77.0 - 95.0", "MCH": "25.0 - 33.0", "MCHC": "31.0 - 37.0", "PLT": "150,000 - 450,000"
    },
    "Male": {
        "WBC": "4,000 - 11,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01",
        "RBC": "4.5 - 5.6", "HB": "13.0 - 17.0", "PCV": "40.0 - 50.0", "MCV": "82.0 - 98.0", "MCH": "27.0 - 32.0", "MCHC": "32.0 - 36.0", "PLT": "150,000 - 400,000"
    },
    "Female": {
        "WBC": "4,000 - 11,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01",
        "RBC": "3.9 - 4.5", "HB": "11.5 - 15.5", "PCV": "35.0 - 45.0", "MCV": "82.0 - 98.0", "MCH": "27.0 - 32.0", "MCHC": "32.0 - 36.0", "PLT": "150,000 - 400,000"
    }
}

# --- PDF Generation Functions (A4 Format) ---
def create_report_pdf(bill, res, fmt):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "LIFE CARE LABORATORY", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana. Tel: 0773326715", ln=True, align='C')
    pdf.ln(5); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)
    
    # Patient Info Header
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 7, "Patient Name:", 0); pdf.set_font("Arial", '', 10); pdf.cell(80, 7, bill['patient'], 0)
    pdf.set_font("Arial", 'B', 10); pdf.cell(30, 7, "Date:", 0); pdf.set_font("Arial", '', 10); pdf.cell(0, 7, bill['date'], ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 7, "Age / Sex:", 0); pdf.set_font("Arial", '', 10)
    sex = "Male" if "Mr." in bill['patient'] or "Baby" in bill['patient'] else "Female"
    pdf.cell(80, 7, f"{bill['age_y']}Y {bill['age_m']}M / {sex}", 0)
    pdf.set_font("Arial", 'B', 10); pdf.cell(30, 7, "Ref. No:", 0); pdf.set_font("Arial", '', 10); pdf.cell(0, 7, bill['bill_id'], ln=True)
    
    pdf.ln(10); pdf.set_font("Arial", 'BU', 12); pdf.cell(0, 10, "FULL BLOOD COUNT", ln=True, align='C'); pdf.ln(5)
    
    # Table Header
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(70, 8, "TEST DESCRIPTION", 1); pdf.cell(30, 8, "RESULT", 1, 0, 'C'); pdf.cell(40, 8, "UNIT", 1, 0, 'C'); pdf.cell(50, 8, "REF. RANGE", 1, 1, 'C')
    
    # FBC Results Rows
    ranges = FBC_RANGES[fmt]
    params = [
        ("WHITE BLOOD CELLS", "WBC", "cells/cu.mm"), ("NEUTROPHILS", "NEU", "%"), ("LYMPHOCYTES", "LYM", "%"),
        ("MONOCYTES", "MON", "%"), ("EOSINOPHILS", "EOS", "%"), ("BASOPHILS", "BAS", "%"),
        ("RED BLOOD CELLS", "RBC", "mill/ cu.mm"), ("HAEMOGLOBIN", "HB", "g/dl"), ("PACKED CELL VOLUME", "PCV", "%"),
        ("PLATELET COUNT", "PLT", "/cu.mm")
    ]
    
    pdf.set_font("Arial", '', 10)
    for label, key, unit in params:
        pdf.cell(70, 8, label, 1)
        pdf.cell(30, 8, str(res.get(key, '')), 1, 0, 'C')
        pdf.cell(40, 8, unit, 1, 0, 'C')
        pdf.cell(50, 8, ranges[key], 1, 1, 'C')
    
    pdf.ln(20); pdf.set_font("Arial", 'I', 9); pdf.cell(0, 10, "--- Authorized by Life Care LIMS ---", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- Main App ---
if not st.session_state.logged_in:
    # (Login code same as before - Admin/Billing/Technician/Satellite)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    r = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"])
    if st.button("Login"):
        user = next((x for x in st.session_state.users if x['username'] == u and x['password'] == p and x['role'] == r), None)
        if user:
            st.session_state.logged_in, st.session_state.current_user, st.session_state.role = True, u, r
            st.rerun()
else:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- TECHNICIAN DASHBOARD ---
    if st.session_state.role == "Technician":
        st.title("🔬 Technician Dashboard")
        
        # 1. Pending Tests View
        st.subheader("📋 Pending Tests")
        pending_fbc = [b for b in st.session_state.saved_bills if "FBC" in b['tests'] and b['bill_id'] not in st.session_state.report_data]
        
        if pending_fbc:
            for b in pending_fbc:
                col_info, col_btn = st.columns([4, 1])
                col_info.write(f"**ID:** {b['bill_id']} | **Patient:** {b['patient']} | **Age:** {b['age_y']}Y")
                if col_btn.button("Enter Result", key=f"btn_{b['bill_id']}"):
                    st.session_state.active_report_id = b['bill_id']
            
            # 2. Result Entry Form (Loads when "Enter Result" is clicked)
            if 'active_report_id' in st.session_state:
                st.divider()
                bill = next(b for b in pending_fbc if b['bill_id'] == st.session_state.active_report_id)
                
                # Auto format detection
                fmt = "Baby" if bill['age_y'] < 5 else ("Male" if "Mr." in bill['patient'] or "Baby" in bill['patient'] else "Female")
                st.subheader(f"Entering Results: {bill['patient']} ({fmt} Format)")
                
                with st.form("fbc_entry"):
                    c1, c2, c3 = st.columns(3)
                    wbc = c1.text_input("WBC (cells/cu.mm)")
                    neu = c2.text_input("Neutrophils %")
                    lym = c3.text_input("Lymphocytes %")
                    mon = c1.text_input("Monocytes %")
                    eos = c2.text_input("Eosinophils %")
                    bas = c3.text_input("Basophils %")
                    rbc = c1.text_input("Red Cells (mill/cu.mm)")
                    hb = c2.text_input("Haemoglobin (g/dl)")
                    pcv = c3.text_input("PCV %")
                    plt = c1.text_input("Platelets (/cu.mm)")
                    
                    if st.form_submit_button("Authorize & Save"):
                        res_dict = {"WBC": wbc, "NEU": neu, "LYM": lym, "MON": mon, "EOS": eos, "BAS": bas, "RBC": rbc, "HB": hb, "PCV": pcv, "PLT": plt}
                        st.session_state.report_data[bill['bill_id']] = {"res": res_dict, "fmt": fmt, "auth": True}
                        del st.session_state.active_report_id
                        st.success("Report Saved Successfully!")
                        st.rerun()
        else:
            st.info("No pending FBC tests.")

        # 3. Print Authorized Reports
        st.divider()
        st.subheader("🖨 Authorized Reports")
        auth_reports = [b for b in st.session_state.saved_bills if b['bill_id'] in st.session_state.report_data]
        for r in auth_reports:
            c1, c2 = st.columns([4, 1])
            c1.write(f"✅ {r['bill_id']} - {r['patient']}")
            rep_info = st.session_state.report_data[r['bill_id']]
            c2.download_button("Print PDF", create_report_pdf(r, rep_info['res'], rep_info['fmt']), file_name=f"FBC_{r['bill_id']}.pdf", key=f"pr_{r['bill_id']}")

    # --- Other Dashboards (Rest of the code remains UNCHANGED) ---
    elif st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        # [Admin logic here...]
        
    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        # [Billing logic here - Final Amount and Save issues fixed in previous turn...]
        
    elif st.session_state.role == "Satellite":
        st.title("📡 Satellite Dashboard")
        # [Satellite logic here...]