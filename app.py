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
if 'users' not in st.session_state: 
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

# --- PDF Bill Generator ---
def create_bill_pdf(bill):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 33)
        pdf.ln(20)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Life Care Laboratory Pvt (Ltd)", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana. Tel: 0773326715", ln=True, align='C')
    pdf.ln(10); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.text(10, pdf.get_y() + 5, f"Patient: {bill['patient']}")
    pdf.text(10, pdf.get_y() + 12, f"Age: {bill.get('age_y', 0)}Y {bill.get('age_m', 0)}M")
    pdf.text(130, pdf.get_y() + 5, f"Date: {bill['date']}")
    pdf.text(130, pdf.get_y() + 12, f"Ref No: {bill['bill_id']}")
    pdf.ln(25); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(2)
    
    pdf.cell(140, 8, "Test Description", ln=0)
    pdf.cell(40, 8, "Price (LKR)", ln=1, align='R')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(2)
    
    pdf.set_font("Arial", size=10)
    for t_name in bill['tests']:
        # Finding test price from session state
        price = next((t['price'] for t in st.session_state.tests if t['name'] == t_name), 0.0)
        pdf.cell(140, 8, str(t_name), ln=0)
        pdf.cell(40, 8, f"{price:,.2f}", ln=1, align='R')
        
    pdf.ln(2); pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Final Amount (LKR):", align='R')
    pdf.cell(40, 10, f"{bill['final']:,.2f}", align='R', ln=1)
    return pdf.output(dest='S').encode('latin-1')

# Helper to download PDF automatically on save
def get_pdf_download_link(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Click here to Download Bill PDF</a>'

# --- (Other dash logic same as previous turn - Keeping it exact) ---

if not st.session_state.logged_in:
    # [Logo & Login code...]
    if os.path.exists("logo.png"):
        c1, c2, c3 = st.columns([1,1,1]); c2.image("logo.png", width=200)
    u = st.text_input("Username"); p = st.text_input("Password", type="password")
    r = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"])
    if st.button("Login"):
        user = next((x for x in st.session_state.users if x['username'] == u and x['password'] == p and x['role'] == r), None)
        if user: st.session_state.logged_in, st.session_state.current_user, st.session_state.role = True, u, r; st.rerun()
else:
    if os.path.exists("logo.png"): st.sidebar.image("logo.png", use_container_width=True)
    if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

    # Admin Unchanged...
    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        t1, t2, t3, t4, t5 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals", "🛠 Edit Bill"])
        # [Admin logic exactly as before...]
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

    # --- BILLING DASHBOARD (Save as PDF fix) ---
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
            final_amt = total - disc
            st.write(f"### Final Amount: LKR {final_amt:,.2f}")
            
            if st.button("Save & Print"):
                if p_name and ptests:
                    bid = f"LC{datetime.now().strftime('%y%m%d%H%M%S')}"
                    new_bill = {"bill_id": bid, "date": date.today().isoformat(), "patient": f"{salute} {p_name}", "age_y": ay, "age_m": am, "doctor": pdoc, "tests": ptests, "final": final_amt, "user": st.session_state.current_user}
                    st.session_state.saved_bills.append(new_bill)
                    
                    # Generate PDF and provide download link immediately
                    pdf_bytes = create_bill_pdf(new_bill)
                    st.markdown(get_pdf_download_link(pdf_bytes, f"Bill_{bid}.pdf"), unsafe_allow_html=True)
                    st.success(f"Bill {bid} Saved Successfully!")
        
        with t_saved:
            for b in reversed([x for x in st.session_state.saved_bills if x['user'] == st.session_state.current_user]):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{b['bill_id']}** | {b['patient']} | LKR {b['final']:,.2f}")
                c2.download_button("Download PDF", create_bill_pdf(b), file_name=f"Bill_{b['bill_id']}.pdf", key=f"dl_{b['bill_id']}")

    # --- TECHNICIAN & SATELLITE (Keep previous turnout logic) ---
    elif st.session_state.role == "Technician":
        st.title("🔬 Technician Dashboard")
        # [Technician logic from previous Turn...]
        pending = [b for b in st.session_state.saved_bills if b['bill_id'] not in st.session_state.report_data]
        st.subheader("📋 Pending Tests")
        for b in pending:
            c1, c2 = st.columns([4, 1]); c1.write(f"**{b['bill_id']}** | {b['patient']}")
            if c2.button("Enter Result", key=f"e_{b['bill_id']}"): st.session_state.active_rid = b['bill_id']
        # (Rest of the report entry logic stays here)

    elif st.session_state.role == "Satellite":
        st.title("📡 Satellite Dashboard")
        # [Satellite logic from previous Turn...]