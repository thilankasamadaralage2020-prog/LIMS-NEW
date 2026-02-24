import streamlit as st
import os
from datetime import datetime, date
from fpdf import FPDF
import base64

# 1. Page Configuration
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

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

# --- PDF Generation Functions ---
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
    for t in bill['tests']: pdf.cell(140, 8, t, 1); pdf.cell(40, 8, "Included", 1, 1, 'R')
    pdf.set_font("Arial", 'B', 12); pdf.cell(140, 10, "Total (LKR):", 0, 0, 'R'); pdf.cell(40, 10, f"{bill['final']:,.2f}", 0, 1, 'R')
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
        # Requirement: Double digits for WBC and Diff Count
        if key in ["WBC", "NEU", "LYM", "MON", "EOS", "BAS"] and val != '-':
            try: formatted_val = f"{int(float(val)):02d}"
            except: formatted_val = str(val)
        else:
            formatted_val = str(val)
            
        pdf.cell(25, 7, formatted_val, 0, 0, 'C')
        pdf.cell(35, 7, str(abs_c.get(key, '')) if is_abs else "", 0, 0, 'C')
        pdf.cell(25, 7, unit, 0, 0, 'C')
        pdf.cell(45, 7, ranges.get(key, ''), 0, 1, 'C')

    if comment:
        pdf.ln(10); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 6, "Comments:"); pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 5, comment)
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
    if os.path.exists("logo.png"): st.sidebar.image("logo.png", use_container_width=True)
    if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

    # Admin Dashboard (Untouched)
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

    # Billing Dashboard (Untouched)
    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        t_new, t_saved = st.tabs(["📝 New Bill", "📂 Saved Bills"])
        with t_new:
            salute = st.selectbox("Salute", ["Mr.", "Mrs.", "Miss", "Baby", "Rev."])
            p_name = st.text_input("Patient Name")
            ay = st.number_input("Years", 0); am = st.number_input("Months", 0)
            pdoc = st.selectbox("Doctor", options=st.session_state.doctors)
            ptests = st.multiselect("Tests", options=[t['name'] for t in st.session_state.tests])
            total = sum(t['price'] for t in st.session_state.tests if t['name'] in ptests)
            disc = st.number_input("Discount", 0.0)
            if st.button("Save & Print"):
                bid = f"LC{datetime.now().strftime('%y%m%d%H%M%S')}"
                new_b = {"bill_id": bid, "date": date.today().isoformat(), "patient": f"{salute} {p_name}", "age_y": ay, "age_m": am, "doctor": pdoc, "tests": ptests, "final": total-disc, "user": st.session_state.current_user}
                st.session_state.saved_bills.append(new_b)
                st.markdown(get_pdf_download_link(create_bill_pdf(new_b), f"Bill_{bid}.pdf"), unsafe_allow_html=True)
                st.success("Saved!")
        with t_saved:
            for b in reversed(st.session_state.saved_bills): 
                st.write(f"{b['bill_id']} - {b['patient']}"); st.download_button("PDF", create_bill_pdf(b), file_name=f"Bill_{b['bill_id']}.pdf", key=f"b_{b['bill_id']}")

    # Technician Dashboard (Modified)
    elif st.session_state.role == "Technician":
        st.title("🔬 Technician Dashboard")
        pending = [b for b in st.session_state.saved_bills if b['bill_id'] not in st.session_state.report_data]
        st.subheader("📋 Pending Tests")
        for b in pending:
            c1, c2 = st.columns([4, 1]); c1.write(f"**{b['bill_id']}** | {b['patient']}")
            if c2.button("Enter Result", key=f"btn_{b['bill_id']}"):
                st.session_state.active_rid = b['bill_id']; st.rerun()

        if st.session_state.active_rid:
            bill = next(x for x in pending if x['bill_id'] == st.session_state.active_rid)
            fmt = "Baby" if bill['age_y'] < 5 else ("Male" if "Mr." in bill['patient'] or "Baby" in bill['patient'] else "Female")
            ranges = FBC_RANGES[fmt]
            
            st.divider()
            st.subheader(f"📝 Result Entry - {bill['patient']} ({fmt})")
            
            with st.form("fbc_full_form"):
                h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 3])
                h1.write("**PARAMETER**"); h2.write("**RESULT**"); h3.write("**ABS. COUNT**"); h4.write("**UNIT**"); h5.write("**REF. RANGE**")
                
                # WBC & Diff Counts (Formatting logic handled during save/pdf)
                def get_row(label, key, unit, step_val, is_abs=False):
                    cols = st.columns([3, 2, 2, 2, 3])
                    cols[0].write(label)
                    val = cols[1].number_input(key, label_visibility="collapsed", step=step_val)
                    abs_val = ""
                    if is_abs:
                        # Calculation logic
                        wbc_val = st.session_state.get('wbc_temp', 0) if key != "WBC" else val
                        calc_abs = round((wbc_val * val) / 100) if wbc_val and val else 0
                        abs_val = str(calc_abs)
                        cols[2].write(abs_val)
                    cols[3].write(unit)
                    cols[4].write(ranges.get(key, ''))
                    return val, abs_val

                # Data Entry Rows
                wbc, _ = get_row("WBC", "WBC", "cells/cu.mm", 1)
                st.session_state.wbc_temp = wbc # Helper for live abs calc
                neu, a_neu = get_row("Neutrophils", "NEU", "%", 0.1, True)
                lym, a_lym = get_row("Lymphocytes", "LYM", "%", 0.1, True)
                mon, a_mon = get_row("Monocytes", "MON", "%", 0.1, True)
                eos, a_eos = get_row("Eosinophils", "EOS", "%", 0.1, True)
                bas, a_bas = get_row("Basophils", "BAS", "%", 0.1, True)
                st.write("**Red Cells Indices**"); st.divider()
                rbc, _ = get_row("RBC", "RBC", "mill/cu.mm", 0.01)
                hb, _ = get_row("Haemoglobin", "HB", "g/dl", 0.1)
                mcv, _ = get_row("MCV", "MCV", "fl", 0.1)
                mch, _ = get_row("MCH", "MCH", "pg", 0.1)
                mchc, _ = get_row("MCHC", "MCHC", "g/dl", 0.1)
                rdw, _ = get_row("RDW", "RDW", "%", 0.1)
                plt, _ = get_row("PLATELETS", "PLT", "/cu.mm", 1000)
                
                comment = st.text_area("Comments")
                if st.form_submit_button("Authorize & View Report"):
                    res = {"WBC": wbc, "NEU": neu, "LYM": lym, "MON": mon, "EOS": eos, "BAS": bas, "RBC": rbc, "HB": hb, "MCV": mcv, "MCH": mch, "MCHC": mchc, "RDW": rdw, "PLT": plt}
                    abs_dict = {"NEU": a_neu, "LYM": a_lym, "MON": a_mon, "EOS": a_eos, "BAS": a_bas}
                    st.session_state.report_data[bill['bill_id']] = {"res": res, "abs": abs_dict, "fmt": fmt, "comment": comment}
                    st.session_state.last_authorized = bill['bill_id']
                    st.session_state.active_rid = None; st.rerun()

        # View Full Report after Authorization
        if 'last_authorized' in st.session_state:
            rid = st.session_state.last_authorized
            b_orig = next((x for x in st.session_state.saved_bills if x['bill_id'] == rid), None)
            if b_orig:
                data = st.session_state.report_data[rid]
                st.divider(); st.success(f"Report Authorized for {b_orig['patient']}!")
                # Download Button
                pdf_bytes = create_report_pdf(b_orig, data['res'], data['abs'], data['fmt'], data['comment'])
                st.download_button("⬇️ Download Full Report (PDF)", pdf_bytes, file_name=f"Report_{rid}.pdf", type="primary")
                # Visual Preview
                st.subheader("Preview:")
                st.json(data['res'])

    elif st.session_state.role == "Satellite":
        st.title("📡 Satellite Dashboard")
        sval = st.text_input("Search Patient")
        if sval:
            for r in [b for b in st.session_state.saved_bills if sval.lower() in b['patient'].lower()]:
                st.write(f"**{r['bill_id']}** | {r['patient']}")
                if r['bill_id'] in st.session_state.report_data:
                    rep = st.session_state.report_data[r['bill_id']]
                    st.download_button("Report", create_report_pdf(r, rep['res'], rep['abs'], rep['fmt'], rep['comment']), key=f"s_{r['bill_id']}")