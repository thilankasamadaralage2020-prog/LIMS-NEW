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

# --- FBC Reference Ranges (Based on your excel files) ---
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

# --- PDF Generation Functions ---
def create_bill_pdf(bill):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"): pdf.image("logo.png", 10, 8, 33); pdf.ln(20)
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "Life Care Laboratory Pvt (Ltd)", ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana. Tel: 0773326715", ln=True, align='C')
    pdf.ln(10); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.text(10, pdf.get_y() + 5, f"Patient: {bill['patient']}")
    pdf.text(10, pdf.get_y() + 12, f"Age: {bill.get('age_y', 0)}Y {bill.get('age_m', 0)}M")
    pdf.text(130, pdf.get_y() + 5, f"Date: {bill['date']}")
    pdf.text(130, pdf.get_y() + 12, f"Ref No: {bill['bill_id']}")
    pdf.ln(25); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(2)
    pdf.cell(140, 8, "Test Description", ln=0); pdf.cell(40, 8, "Price (LKR)", ln=1, align='R')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(2); pdf.set_font("Arial", size=10)
    for t_name in bill['tests']:
        price = next((t['price'] for t in st.session_state.tests if t['name'] == t_name), 0)
        pdf.cell(140, 8, str(t_name), ln=0); pdf.cell(40, 8, f"{price:,.2f}", ln=1, align='R')
    pdf.ln(2); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Final Amount (LKR):", align='R'); pdf.cell(40, 10, f"{bill['final']:,.2f}", align='R', ln=1)
    return pdf.output(dest='S').encode('latin-1')

def create_report_pdf(bill, res, fmt):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "LIFE CARE LABORATORY", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "Katuwana. Tel: 0773326715", ln=True, align='C')
    pdf.ln(5); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)
    pdf.set_font("Arial", 'B', 10); pdf.cell(30, 7, "Patient Name:", 0); pdf.set_font("Arial", '', 10); pdf.cell(80, 7, bill['patient'], 0)
    pdf.set_font("Arial", 'B', 10); pdf.cell(30, 7, "Date:", 0); pdf.set_font("Arial", '', 10); pdf.cell(0, 7, bill['date'], ln=True)
    pdf.ln(10); pdf.set_font("Arial", 'BU', 12); pdf.cell(0, 10, "FULL BLOOD COUNT", ln=True, align='C'); pdf.ln(5)
    pdf.set_font("Arial", 'B', 10); pdf.cell(70, 8, "TEST DESCRIPTION", 1); pdf.cell(30, 8, "RESULT", 1, 0, 'C'); pdf.cell(40, 8, "UNIT", 1, 0, 'C'); pdf.cell(50, 8, "REF. RANGE", 1, 1, 'C')
    ranges = FBC_RANGES[fmt]
    params = [
        ("WHITE BLOOD CELLS", "WBC", "cells/cu.mm"), ("NEUTROPHILS", "NEU", "%"), 
        ("LYMPHOCYTES", "LYM", "%"), ("MONOCYTES", "MON", "%"), ("EOSINOPHILS", "EOS", "%"),
        ("RED BLOOD CELLS", "RBC", "mill/ cu.mm"), ("HAEMOGLOBIN", "HB", "g/dl"), 
        ("PACKED CELL VOLUME", "PCV", "%"), ("PLATELET COUNT", "PLT", "/cu.mm")
    ]
    pdf.set_font("Arial", '', 10)
    for label, key, unit in params:
        pdf.cell(70, 8, label, 1); pdf.cell(30, 8, str(res.get(key, '')), 1, 0, 'C'); pdf.cell(40, 8, unit, 1, 0, 'C'); pdf.cell(50, 8, ranges[key], 1, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# --- Login & Main Layout ---
if not st.session_state.logged_in:
    u = st.text_input("Username"); p = st.text_input("Password", type="password")
    r = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"])
    if st.button("Login"):
        user = next((x for x in st.session_state.users if x['username'] == u and x['password'] == p and x['role'] == r), None)
        if user: st.session_state.logged_in, st.session_state.current_user, st.session_state.role = True, u, r; st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

    # --- ADMIN DASHBOARD (Unchanged) ---
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
                c1, c2 = st.columns([4, 1]); c1.write(f"**{b['bill_id']}** | {b['patient']}"); c2.download_button("PDF", create_bill_pdf(b), file_name=f"{b['bill_id']}.pdf", key=f"s_{b['bill_id']}")

    # --- TECHNICIAN DASHBOARD (Updated Logic) ---
    elif st.session_state.role == "Technician":
        st.title("🔬 Technician Dashboard")
        
        # Display ALL bills that have at least one test pending (not in report_data)
        st.subheader("📋 Pending Tests")
        pending_bills = [b for b in st.session_state.saved_bills if b['bill_id'] not in st.session_state.report_data]
        
        if pending_bills:
            for b in pending_bills:
                with st.container():
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**ID:** {b['bill_id']} | **Patient:** {b['patient']} | **Tests:** {', '.join(b['tests'])}")
                    if c2.button("Enter Result", key=f"e_{b['bill_id']}"):
                        st.session_state.active_rid = b['bill_id']
            
            # Result Entry Form
            if 'active_rid' in st.session_state:
                st.divider()
                bill = next(x for x in pending_bills if x['bill_id'] == st.session_state.active_rid)
                # Auto-Format detection based on age and salute
                is_baby = bill['age_y'] < 5
                is_male = "Mr." in bill['patient'] or "Baby" in bill['patient']
                fmt = "Baby" if is_baby else ("Male" if is_male else "Female")
                
                st.subheader(f"📝 Result Entry: {bill['patient']} ({fmt} Format)")
                with st.form("fbc_form"):
                    c1, c2, c3 = st.columns(3)
                    wbc = c1.text_input("WBC (cells/cu.mm)")
                    neu = c2.text_input("NEU %")
                    lym = c3.text_input("LYM %")
                    mon = c1.text_input("MON %")
                    eos = c2.text_input("EOS %")
                    bas = c3.text_input("BAS %")
                    rbc = c1.text_input("RBC (mill/cu.mm)")
                    hb = c2.text_input("HB (g/dl)")
                    pcv = c3.text_input("PCV %")
                    plt = c1.text_input("PLT (/cu.mm)")
                    
                    if st.form_submit_button("Authorize Report"):
                        res_dict = {"WBC": wbc, "NEU": neu, "LYM": lym, "MON": mon, "EOS": eos, "BAS": bas, "RBC": rbc, "HB": hb, "PCV": pcv, "PLT": plt}
                        st.session_state.report_data[bill['bill_id']] = {"res": res_dict, "fmt": fmt}
                        del st.session_state.active_rid
                        st.success("Report Authorized!"); st.rerun()
        else:
            st.info("No pending tests found.")

        # Authorized reports section
        st.divider()
        st.subheader("🖨 Authorized Reports")
        for rid, data in st.session_state.report_data.items():
            b_orig = next((x for x in st.session_state.saved_bills if x['bill_id'] == rid), None)
            if b_orig:
                c1, c2 = st.columns([4, 1])
                c1.write(f"✅ {rid} - {b_orig['patient']}")
                c2.download_button("Print PDF", create_report_pdf(b_orig, data['res'], data['fmt']), file_name=f"Report_{rid}.pdf", key=f"p_{rid}")

    # --- SATELLITE DASHBOARD (Unchanged) ---
    elif st.session_state.role == "Satellite":
        st.title("📡 Satellite Dashboard")
        sval = st.text_input("Search Patient Name or Ref No")
        if sval:
            res = [b for b in st.session_state.saved_bills if sval.lower() in b['patient'].lower() or sval.upper() in b['bill_id']]
            for r in res:
                c1, c2 = st.columns([4, 1]); c1.write(f"**{r['bill_id']}** | {r['patient']}")
                if r['bill_id'] in st.session_state.report_data:
                    rep = st.session_state.report_data[r['bill_id']]
                    c2.download_button("Report", create_report_pdf(r, rep['res'], rep['fmt']), key=f"sat_{r['bill_id']}")
                else: c2.warning("Pending")