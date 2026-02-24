import streamlit as st
import os
from datetime import datetime, date
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# Session State Initialize (Keeping all previous states intact)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'saved_bills' not in st.session_state: st.session_state.saved_bills = []
if 'tests' not in st.session_state: st.session_state.tests = []
if 'doctors' not in st.session_state: st.session_state.doctors = ["Self"]
if 'cancel_requests' not in st.session_state: st.session_state.cancel_requests = []
if 'report_data' not in st.session_state: st.session_state.report_data = {}
if 'users' not in st.session_state: 
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

# --- FBC Reference Ranges ---
FBC_RANGES = {
    "Baby": {"WBC": "5,000 - 13,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01", "RBC": "4.0 - 5.2", "HB": "11.5 - 15.5", "HCT": "35.0 - 45.0", "MCV": "77.0 - 95.0", "MCH": "25.0 - 33.0", "MCHC": "31.0 - 37.0", "RDW": "11.5 - 14.5", "PLT": "150,000 - 450,000"},
    "Male": {"WBC": "4,000 - 11,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01", "RBC": "4.5 - 5.6", "HB": "13.0 - 17.0", "HCT": "40.0 - 50.0", "MCV": "82.0 - 98.0", "MCH": "27.0 - 32.0", "MCHC": "32.0 - 36.0", "RDW": "11.5 - 14.5", "PLT": "150,000 - 400,000"},
    "Female": {"WBC": "4,000 - 11,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01", "RBC": "3.9 - 4.5", "HB": "11.5 - 15.5", "HCT": "35.0 - 45.0", "MCV": "82.0 - 98.0", "MCH": "27.0 - 32.0", "MCHC": "32.0 - 36.0", "RDW": "11.5 - 14.5", "PLT": "150,000 - 400,000"}
}

# --- PDF Report Generator (Clean Style) ---
def create_report_pdf(bill, res, abs_counts, fmt, comment):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 40)
        pdf.ln(15)

    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 8, "LIFE CARE LABORATORY", ln=True, align='C')
    pdf.set_font("Arial", '', 9); pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana. Tel: 0773326715", ln=True, align='C')
    pdf.ln(4); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)
    
    # Header Information (Left and Right)
    gender = "Male" if "Mr." in bill['patient'] or "Baby" in bill['patient'] else "Female"
    pdf.set_font("Arial", 'B', 10)
    
    # Left Side
    pdf.text(10, pdf.get_y() + 5, f"Patient Name: {bill['patient']}")
    pdf.text(10, pdf.get_y() + 11, f"Age: {bill.get('age_y', 0)}Y {bill.get('age_m', 0)}M")
    pdf.text(10, pdf.get_y() + 17, f"Gender: {gender}")
    pdf.text(10, pdf.get_y() + 23, f"Ref. Doctor: {bill.get('doctor', 'Self')}")
    
    # Right Side
    pdf.text(130, pdf.get_y() + 5, f"Billed Date: {bill['date']}")
    pdf.text(130, pdf.get_y() + 11, f"Reported Date: {date.today().isoformat()}")
    pdf.text(130, pdf.get_y() + 17, f"Ref. Number: {bill['bill_id']}")
    
    pdf.ln(30); pdf.set_font("Arial", 'BU', 12); pdf.cell(0, 10, "FULL BLOOD COUNT", ln=True, align='C'); pdf.ln(5)
    
    # Column Headers (No internal lines)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(70, 8, "TEST DESCRIPTION", 0); pdf.cell(30, 8, "RESULT", 0, 0, 'C'); pdf.cell(30, 8, "UNIT", 0, 0, 'C'); pdf.cell(30, 8, "ABS. COUNT", 0, 0, 'C'); pdf.cell(0, 8, "REF. RANGE", 0, 1, 'C')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(2)
    
    ranges = FBC_RANGES[fmt]
    pdf.set_font("Arial", '', 10)
    
    params = [
        ("WHITE BLOOD CELLS", "WBC", "cells/cu.mm", False),
        ("NEUTROPHILS", "NEU", "%", True), ("LYMPHOCYTES", "LYM", "%", True),
        ("MONOCYTES", "MON", "%", True), ("EOSINOPHILS", "EOS", "%", True), ("BASOPHILS", "BAS", "%", True),
        ("RED BLOOD CELLS", "RBC", "mill/cu.mm", False), ("HAEMOGLOBIN", "HB", "g/dl", False),
        ("HCT", "HCT", "%", False), ("MCV", "MCV", "fl", False), ("MCH", "MCH", "pg", False),
        ("MCHC", "MCHC", "g/dl", False), ("RDW", "RDW", "%", False), ("PLATELET COUNT", "PLT", "/cu.mm", False)
    ]

    for label, key, unit, is_abs in params:
        pdf.cell(70, 7, label, 0)
        pdf.cell(30, 7, str(res.get(key, '-')), 0, 0, 'C')
        pdf.cell(30, 7, unit, 0, 0, 'C')
        abs_val = str(abs_counts.get(key, '-')) if is_abs else ""
        pdf.cell(30, 7, abs_val, 0, 0, 'C')
        pdf.cell(0, 7, ranges.get(key, ''), 0, 1, 'C')

    if comment:
        pdf.ln(10); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 6, "Comments:", ln=True)
        pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 5, comment)

    return pdf.output(dest='S').encode('latin-1')

# --- Main App ---
if not st.session_state.logged_in:
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: st.image("logo.png", width=200)
    u = st.text_input("Username"); p = st.text_input("Password", type="password")
    r = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"])
    if st.button("Login"):
        user = next((x for x in st.session_state.users if x['username'] == u and x['password'] == p and x['role'] == r), None)
        if user: st.session_state.logged_in, st.session_state.current_user, st.session_state.role = True, u, r; st.rerun()
else:
    # Sidebar
    if os.path.exists("logo.png"): st.sidebar.image("logo.png", use_container_width=True)
    if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

    # --- ADMIN DASHBOARD (Completely Restored) ---
    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        t1, t2, t3, t4, t5 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals", "🛠 Edit Bill"])
        with t1:
            nu, np = st.text_input("New User"), st.text_input("New Pass", type="password")
            nr = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"], key="arole")
            if st.button("Create User"):
                if nu and np: st.session_state.users.append({"username": nu, "password": np, "role": nr}); st.rerun()
            for u_obj in st.session_state.users: st.write(f"{u_obj['username']} ({u_obj['role']})")
        with t2:
            nd = st.text_input("Add Doctor")
            if st.button("Save Doctor"): st.session_state.doctors.append(nd); st.rerun()
            for d in st.session_state.doctors: st.write(d)
        with t3:
            nt = st.text_input("Add Test")
            npr = st.number_input("Test Price", min_value=0.0)
            if st.button("Save Test"): st.session_state.tests.append({"name": nt, "price": npr}); st.rerun()
            for t in st.session_state.tests: st.write(f"{t['name']} - {t['price']}")
        with t4:
            for i, req in enumerate(st.session_state.cancel_requests):
                st.warning(f"Request: {req['bill_id']}")
                if st.button("Approve", key=f"ac_{i}"):
                    st.session_state.saved_bills = [b for b in st.session_state.saved_bills if b['bill_id'] != req['bill_id']]
                    st.session_state.cancel_requests.pop(i); st.rerun()
        with t5:
            if st.session_state.saved_bills:
                b_map = {f"{b['bill_id']} - {b['patient']}": b for b in st.session_state.saved_bills}
                sel_b = st.selectbox("Select Bill", options=list(b_map.keys()))
                if sel_b:
                    target = b_map[sel_b]
                    en = st.text_input("Edit Name", value=target['patient'])
                    if st.button("Update Bill"): target.update({"patient": en}); st.success("Updated!"); st.rerun()

    # --- BILLING DASHBOARD (Unchanged) ---
    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        t_new, t_saved, t_recall, t_summary = st.tabs(["📝 New Bill", "📂 Saved Bills", "🔍 RECALL", "📊 Summary"])
        with t_new:
            c1, c2 = st.columns([1, 3])
            salute = c1.selectbox("Salute", ["Mr.", "Mrs.", "Miss", "Baby", "Rev."])
            p_name = c2.text_input("Patient Name", key="pname")
            a1, a2 = st.columns(2); ay = a1.number_input("Years", 0, key="agey"); am = a2.number_input("Months", 0, key="agem")
            pdoc = st.selectbox("Doctor", options=st.session_state.doctors, key="pdoc")
            ptests = st.multiselect("Tests", options=[t['name'] for t in st.session_state.tests], key="ptests")
            total = sum(t['price'] for t in st.session_state.tests if t['name'] in ptests)
            disc = st.number_input("Discount", 0.0, key="pdisc")
            st.write(f"### Final Amount: LKR {total - disc:,.2f}")
            if st.button("Save & Print"):
                if p_name and ptests:
                    bid = f"LC{datetime.now().strftime('%y%m%d%H%M%S')}"
                    st.session_state.saved_bills.append({"bill_id": bid, "date": date.today().isoformat(), "patient": f"{salute} {p_name}", "age_y": ay, "age_m": am, "doctor": pdoc, "tests": ptests, "final": total - disc, "user": st.session_state.current_user})
                    st.success("Saved!"); st.rerun()
        with t_saved:
            for b in reversed([x for x in st.session_state.saved_bills if x['user'] == st.session_state.current_user]):
                st.write(f"**{b['bill_id']}** | {b['patient']}"); st.download_button("Print Bill PDF", create_report_pdf(b, {}, {}, "Male", ""), key=f"s_{b['bill_id']}")

    # --- TECHNICIAN DASHBOARD (Optimized Tab Order) ---
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
            
            with st.form("fbc_form"):
                st.subheader(f"📝 Result Entry - {bill['patient']}")
                c1, c2, c3 = st.columns(3)
                wbc = c1.number_input("WBC (Total)", step=1)
                neu = c2.number_input("Neutrophils %", step=0.1)
                lym = c3.number_input("Lymphocytes %", step=0.1)
                eos = c1.number_input("Eosinophils %", step=0.1)
                mon = c2.number_input("Monocytes %", step=0.1)
                bas = c3.number_input("Basophils %", step=0.1)
                rbc = c1.number_input("RBC (mill/cu.mm)", step=0.01)
                hb = c2.number_input("Haemoglobin (g/dl)", step=0.1)
                hct = c3.number_input("HCT/PCV %", step=0.1)
                mcv = c1.number_input("MCV (fl)", step=0.1)
                mch = c2.number_input("MCH (pg)", step=0.1)
                mchc = c3.number_input("MCHC (g/dl)", step=0.1)
                rdw = c1.number_input("RDW %", step=0.1)
                plt = c2.number_input("Platelets (/cu.mm)", step=1000)
                comment = st.text_area("Comment Box")
                
                if st.form_submit_button("Authorize Report"):
                    abs_c = {k: round((wbc * v) / 100) for k, v in {"NEU": neu, "LYM": lym, "MON": mon, "EOS": eos, "BAS": bas}.items()}
                    res = {"WBC": wbc, "NEU": neu, "LYM": lym, "MON": mon, "EOS": eos, "BAS": bas, "RBC": rbc, "HB": hb, "HCT": hct, "MCV": mcv, "MCH": mch, "MCHC": mchc, "RDW": rdw, "PLT": plt}
                    st.session_state.report_data[bill['bill_id']] = {"res": res, "abs": abs_c, "fmt": fmt, "comment": comment}
                    del st.session_state.active_rid; st.rerun()

    # --- SATELLITE DASHBOARD (Unchanged) ---
    elif st.session_state.role == "Satellite":
        st.title("📡 Satellite Dashboard")
        sval = st.text_input("Search Patient")
        if sval:
            res = [b for b in st.session_state.saved_bills if sval.lower() in b['patient'].lower() or sval.upper() in b['bill_id']]
            for r in res:
                c1, c2 = st.columns([4, 1]); c1.write(f"**{r['bill_id']}** | {r['patient']}")
                if r['bill_id'] in st.session_state.report_data:
                    rep = st.session_state.report_data[r['bill_id']]
                    c2.download_button("Print Report", create_report_pdf(r, rep['res'], rep['abs'], rep['fmt'], rep['comment']), key=f"sat_{r['bill_id']}")