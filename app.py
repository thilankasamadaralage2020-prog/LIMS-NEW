import streamlit as st
import os
from datetime import datetime, date
from fpdf import FPDF
import base64

# 1. Page Configuration
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# Custom CSS to fix input box alignment
st.markdown("""
    <style>
    div[data-testid="stColumn"] {
        padding: 0px 5px;
    }
    input {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialize
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'saved_bills' not in st.session_state: st.session_state.saved_bills = []
if 'tests' not in st.session_state: st.session_state.tests = []
if 'doctors' not in st.session_state: st.session_state.doctors = ["Self"]
if 'cancel_requests' not in st.session_state: st.session_state.cancel_requests = []
if 'report_data' not in st.session_state: st.session_state.report_data = {}
if 'active_rid' not in st.session_state: st.session_state.active_rid = None
if 'users' not in st.session_state: 
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

# --- Reference Ranges ---
FBC_RANGES = {
    "Baby": {"WBC": "5,000 – 13,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01", "RBC": "4.0 - 5.2", "HB": "11.5 - 15.5", "HCT": "35.0 - 45.0", "MCV": "77.0 - 95.0", "MCH": "25.0 - 33.0", "MCHC": "31.0 - 37.0", "RDW": "11.5 - 14.5", "PLT": "150,000 - 450,000"},
    "Male": {"WBC": "4,000 – 11,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01", "RBC": "4.5 - 5.6", "HB": "13.0 - 17.0", "HCT": "40.0 - 50.0", "MCV": "82.0 - 98.0", "MCH": "27.0 - 32.0", "MCHC": "32.0 - 36.0", "RDW": "11.5 - 14.5", "PLT": "150,000 - 400,000"},
    "Female": {"WBC": "4,000 – 11,000", "NEU": "45 - 75", "LYM": "25 - 45", "MON": "01 - 10", "EOS": "01 - 06", "BAS": "00 - 01", "RBC": "3.9 - 4.5", "HB": "11.5 - 15.5", "HCT": "35.0 - 45.0", "MCV": "82.0 - 98.0", "MCH": "27.0 - 32.0", "MCHC": "32.0 - 36.0", "RDW": "11.5 - 14.5", "PLT": "150,000 - 400,000"}
}

# --- PDF Functions ---
def create_bill_pdf(bill):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"): pdf.image("logo.png", 10, 8, 33); pdf.ln(20)
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "Life Care Laboratory Pvt (Ltd)", ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 5, "Katuwana. Tel: 0773326715", ln=True, align='C')
    pdf.ln(10); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.text(10, pdf.get_y() + 5, f"Patient: {bill['patient']}")
    pdf.text(130, pdf.get_y() + 5, f"Ref No: {bill['bill_id']}")
    pdf.ln(20); pdf.cell(140, 8, "Test Description", 1); pdf.cell(40, 8, "Price", 1, 1, 'R')
    pdf.set_font("Arial", size=10)
    subtotal = bill['final'] + bill.get('discount', 0)
    for t in bill['tests']:
        pdf.cell(140, 8, t, 1); pdf.cell(40, 8, "Included", 1, 1, 'R')
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 10)
    if bill.get('discount', 0) > 0:
        pdf.cell(140, 8, "Sub Total (LKR):", 0, 0, 'R'); pdf.cell(40, 8, f"{subtotal:,.2f}", 0, 1, 'R')
        pdf.cell(140, 8, f"Discount (LKR):", 0, 0, 'R'); pdf.cell(40, 8, f"-{bill['discount']:,.2f}", 0, 1, 'R')
    pdf.set_font("Arial", 'B', 12); pdf.cell(140, 10, "Total Amount (LKR):", 0, 0, 'R'); pdf.cell(40, 10, f"{bill['final']:,.2f}", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

def create_report_pdf(bill, res, abs_c, fmt, comment):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"): pdf.image("logo.png", 10, 8, 40); pdf.ln(15)
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 8, "LIFE CARE LABORATORY", ln=True, align='C')
    pdf.set_font("Arial", '', 9); pdf.cell(0, 5, "Katuwana. Tel: 0773326715", ln=True, align='C')
    pdf.ln(4); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    gender = "Male" if "Mr." in bill['patient'] or "Baby" in bill['patient'] else "Female"
    pdf.text(10, pdf.get_y()+5, f"Patient Name: {bill['patient']}")
    pdf.text(10, pdf.get_y()+11, f"Age: {bill['age_y']}Y {bill['age_m']}M / Gender: {gender}")
    pdf.text(10, pdf.get_y()+17, f"Ref. Doctor: {bill.get('doctor', 'Self')}")
    pdf.text(130, pdf.get_y()+5, f"Billed Date: {bill['date']}")
    pdf.text(130, pdf.get_y()+11, f"Reported Date: {date.today().isoformat()}")
    pdf.text(130, pdf.get_y()+17, f"Ref No: {bill['bill_id']}")
    pdf.ln(25); pdf.set_font("Arial", 'BU', 12); pdf.cell(0, 10, "FULL BLOOD COUNT", ln=True, align='C'); pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 8, "TEST DESCRIPTION"); pdf.cell(25, 8, "RESULT", 0, 0, 'C'); pdf.cell(35, 8, "ABS. COUNT", 0, 0, 'C'); pdf.cell(25, 8, "UNIT", 0, 0, 'C'); pdf.cell(45, 8, "REF. RANGE", 0, 1, 'C')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(2)
    ranges = FBC_RANGES[fmt]
    pdf.set_font("Arial", '', 10)
    params = [
        ("WHITE BLOOD CELLS", "WBC", "cells/cu.mm", False),
        ("NEUTROPHILS", "NEU", "%", True), ("LYMPHOCYTES", "LYM", "%", True),
        ("MONOCYTES", "MON", "%", True), ("EOSINOPHILS", "EOS", "%", True), ("BASOPHILS", "BAS", "%", True),
        ("RED BLOOD CELLS", "RBC", "mill/cu.mm", False), ("HAEMOGLOBIN", "HB", "g/dl", False),
        ("MCV", "MCV", "fl", False), ("MCH", "MCH", "pg", False), ("MCHC", "MCHC", "g/dl", False),
        ("RDW", "RDW", "%", False), ("PLATELET COUNT", "PLT", "/cu.mm", False)
    ]
    for label, key, unit, is_abs in params:
        pdf.cell(60, 7, label)
        val = res.get(key, '-')
        f_val = f"{int(float(val)):02d}" if key in ["WBC", "NEU", "LYM", "MON", "EOS", "BAS"] and val != '-' else str(val)
        pdf.cell(25, 7, f_val, 0, 0, 'C')
        pdf.cell(35, 7, str(abs_c.get(key, '')) if is_abs else "", 0, 0, 'C')
        pdf.cell(25, 7, unit, 0, 0, 'C')
        pdf.cell(45, 7, ranges.get(key, ''), 0, 1, 'C')
    if comment: pdf.ln(10); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 6, "Comments:"); pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 5, comment)
    return pdf.output(dest='S').encode('latin-1')

def get_pdf_download_link(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode(); return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Click here to Download PDF</a>'

# --- App Logic ---
if not st.session_state.logged_in:
    if os.path.exists("logo.png"): st.image("logo.png", width=200)
    u = st.text_input("Username"); p = st.text_input("Password", type="password")
    r = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"])
    if st.button("Login"):
        user = next((x for x in st.session_state.users if x['username'] == u and x['password'] == p and x['role'] == r), None)
        if user: st.session_state.logged_in, st.session_state.current_user, st.session_state.role = True, u, r; st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        t1, t2, t3, t4 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals"])
        with t1:
            st.subheader("Create New User")
            nu = st.text_input("Username", key="new_u")
            np = st.text_input("Password", type="password", key="new_p")
            nr = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"], key="new_r")
            if st.button("Create User"):
                if nu and np:
                    st.session_state.users.append({"username": nu, "password": np, "role": nr})
                    st.success(f"User {nu} created!")
                    st.rerun()
            st.divider()
            st.subheader("Existing Users")
            for user in st.session_state.users:
                st.write(f"👤 **{user['username']}** | 🔑 {user['role']}")

        with t2:
            st.subheader("Manage Doctors")
            nd = st.text_input("Add Doctor Name")
            if st.button("Save Doctor"): 
                if nd:
                    st.session_state.doctors.append(nd)
                    st.success(f"Doctor {nd} added!")
                    st.rerun()
            st.divider()
            st.subheader("Doctor List")
            for doc in st.session_state.doctors:
                st.write(f"👨‍⚕️ {doc}")

        with t3:
            st.subheader("Manage Tests")
            nt = st.text_input("Add Test Name")
            npr = st.number_input("Test Price (LKR)", min_value=0.0)
            if st.button("Save Test"): 
                if nt:
                    st.session_state.tests.append({"name": nt, "price": npr})
                    st.success(f"Test {nt} added!")
                    st.rerun()
            st.divider()
            st.subheader("Available Tests")
            for tst in st.session_state.tests:
                st.write(f"🔬 {tst['name']} - LKR {tst['price']:,.2f}")

        with t4:
            for i, req in enumerate(st.session_state.cancel_requests):
                st.warning(f"Request: {req['bill_id']}")
                if st.button("Approve", key=f"ac_{i}"):
                    st.session_state.saved_bills = [b for b in st.session_state.saved_bills if b['bill_id'] != req['bill_id']]
                    st.session_state.cancel_requests.pop(i); st.rerun()

    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        salute = st.selectbox("Salute", ["Mr.", "Mrs.", "Miss", "Baby", "Rev."])
        p_name = st.text_input("Patient Name")
        ay = st.number_input("Years", 0); am = st.number_input("Months", 0)
        pdoc = st.selectbox("Doctor", options=st.session_state.doctors)
        ptests = st.multiselect("Tests", options=[t['name'] for t in st.session_state.tests])
        total = sum(t['price'] for t in st.session_state.tests if t['name'] in ptests)
        disc = st.number_input("Discount", 0.0)
        if st.button("Save & Print"):
            bid = f"LC{datetime.now().strftime('%y%m%d%H%M%S')}"
            new_b = {"bill_id": bid, "date": date.today().isoformat(), "patient": f"{salute} {p_name}", "age_y": ay, "age_m": am, "doctor": pdoc, "tests": ptests, "final": total-disc, "discount": disc}
            st.session_state.saved_bills.append(new_b)
            st.markdown(get_pdf_download_link(create_bill_pdf(new_b), f"Bill_{bid}.pdf"), unsafe_allow_html=True)

    elif st.session_state.role == "Technician":
        st.title("🔬 Technician Dashboard")
        pending = [b for b in st.session_state.saved_bills if b['bill_id'] not in st.session_state.report_data]
        for b in pending:
            if st.button(f"Enter Result: {b['bill_id']} - {b['patient']}"): 
                st.session_state.active_rid = b['bill_id']
                st.rerun()

        if st.session_state.active_rid:
            bill = next(x for x in pending if x['bill_id'] == st.session_state.active_rid)
            fmt = "Baby" if bill['age_y'] < 5 else ("Male" if "Mr." in bill['patient'] or "Baby" in bill['patient'] else "Female")
            ranges = FBC_RANGES[fmt]
            
            with st.form("fbc_entry"):
                st.subheader(f"FBC Entry: {bill['patient']} ({fmt})")
                def fbc_row(label, key, unit, step_val=1.0):
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 3])
                    c1.write(f"**{label}**")
                    val = c2.number_input("", key=f"in_{key}", label_visibility="collapsed", step=step_val)
                    c3.write("") 
                    c4.write(unit); c5.write(ranges.get(key, ''))
                    return val
                wbc = fbc_row("WBC", "WBC", "cells/cu.mm")
                neu = fbc_row("Neutrophils", "NEU", "%")
                lym = fbc_row("Lymphocytes", "LYM", "%")
                mon = fbc_row("Monocytes", "MON", "%")
                eos = fbc_row("Eosinophils", "EOS", "%")
                bas = fbc_row("Basophils", "BAS", "%")
                st.write("---")
                rbc = fbc_row("RBC", "RBC", "mill/cu.mm", 0.01)
                hb = fbc_row("Haemoglobin", "HB", "g/dl", 0.1)
                mcv = fbc_row("MCV", "MCV", "fl", 0.1)
                mch = fbc_row("MCH", "MCH", "pg", 0.1)
                mchc = fbc_row("MCHC", "MCHC", "g/dl", 0.1)
                rdw = fbc_row("RDW", "RDW", "%", 0.1)
                plt = fbc_row("PLATELETS", "PLT", "/cu.mm", 1000.0)
                comment = st.text_area("Comments")
                if st.form_submit_button("Authorize Report"):
                    abs_dict = {"NEU": round((wbc * neu) / 100), "LYM": round((wbc * lym) / 100), "MON": round((wbc * mon) / 100), "EOS": round((wbc * eos) / 100), "BAS": round((wbc * bas) / 100)}
                    res = {"WBC": wbc, "NEU": neu, "LYM": lym, "MON": mon, "EOS": eos, "BAS": bas, "RBC": rbc, "HB": hb, "MCV": mcv, "MCH": mch, "MCHC": mchc, "RDW": rdw, "PLT": plt}
                    st.session_state.report_data[bill['bill_id']] = {"res": res, "abs": abs_dict, "fmt": fmt, "comment": comment}
                    st.session_state.last_authorized = bill['bill_id']
                    st.session_state.active_rid = None; st.rerun()

        if 'last_authorized' in st.session_state:
            rid = st.session_state.last_authorized
            b_orig = next((x for x in st.session_state.saved_bills if x['bill_id'] == rid), None)
            if b_orig:
                data = st.session_state.report_data[rid]
                st.success(f"Authorized: {b_orig['patient']}")
                pdf_b = create_report_pdf(b_orig, data['res'], data['abs'], data['fmt'], data['comment'])
                st.download_button("⬇️ Download PDF Report", pdf_b, file_name=f"Report_{rid}.pdf")

    elif st.session_state.role == "Satellite":
        st.title("📡 Satellite Dashboard")
        sval = st.text_input("Search Patient")
        if sval:
            for b in [x for x in st.session_state.saved_bills if sval.lower() in x['patient'].lower()]:
                if b['bill_id'] in st.session_state.report_data:
                    data = st.session_state.report_data[b['bill_id']]
                    st.write(f"**{b['patient']}** ({b['bill_id']})")
                    st.download_button("Download Report", create_report_pdf(b, data['res'], data['abs'], data['fmt'], data['comment']), key=b['bill_id'])