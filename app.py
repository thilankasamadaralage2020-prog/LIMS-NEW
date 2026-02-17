import streamlit as st
import os
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF

# Page Configuration - මෙය සැමවිටම පළමු පේළිය විය යුතුය
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# Session State පිරිසිදු ලෙස ආරම්භ කිරීම
def init_state():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'saved_bills' not in st.session_state: st.session_state.saved_bills = []
    if 'tests' not in st.session_state: st.session_state.tests = []
    if 'doctors' not in st.session_state: st.session_state.doctors = ["Self"]
    if 'cancel_requests' not in st.session_state: st.session_state.cancel_requests = []
    if 'users' not in st.session_state: 
        st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

init_state()

# --- PDF Generator ---
def create_pdf(bill):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Life Care Laboratory Pvt (Ltd)", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana. Tel: 0773326715", ln=True, align='C')
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        pdf.text(10, pdf.get_y() + 5, f"Patient: {bill['patient']}")
        pdf.text(10, pdf.get_y() + 12, f"Age: {bill.get('age_y', 0)}Y {bill.get('age_m', 0)}M")
        pdf.text(130, pdf.get_y() + 5, f"Date: {bill['date']}")
        pdf.text(130, pdf.get_y() + 12, f"Ref No: {bill['bill_id']}")
        pdf.ln(25)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        for t_name in bill['tests']:
            pdf.cell(140, 8, str(t_name))
            pdf.cell(40, 8, "-", align='R')
            pdf.ln(7)
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.cell(140, 10, "Total (LKR):", align='R')
        pdf.cell(40, 10, f"{bill['final']:,.2f}", align='R')
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        return b""

# --- Login ---
def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔬 Life Care LIMS</h1>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        r = st.selectbox("Role", ["Admin", "Billing", "Technician"])
        if st.button("Login", use_container_width=True):
            user = next((x for x in st.session_state.users if x['username']==u and x['password']==p and x['role']==r), None)
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.session_state.role = r
                st.rerun()
            else: st.error("වැරදි පරිශීලක නාමයක් හෝ මුරපදයක්!")

if not st.session_state.logged_in:
    login_screen()
else:
    if st.sidebar.button("⬅️ Home"): st.rerun()
    if st.sidebar.button("Logout"): 
        st.session_state.logged_in = False
        st.rerun()

    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        t1, t2, t3, t4, t5 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals", "🛠 Edit Bill"])
        
        with t1:
            nu = st.text_input("New Username")
            np = st.text_input("New Password")
            if st.button("Create User"):
                st.session_state.users.append({"username": nu, "password": np, "role": "Billing"})
                st.success("User Created!"); st.rerun()
        
        with t2:
            nd = st.text_input("Doctor Name")
            if st.button("Add Doctor"):
                st.session_state.doctors.append(nd); st.rerun()
            st.write(st.session_state.doctors)

        with t3:
            nt = st.text_input("Test Name")
            npr = st.number_input("Price", min_value=0.0)
            if st.button("Add Test"):
                st.session_state.tests.append({"name": nt, "price": npr}); st.rerun()

        with t4:
            for i, req in enumerate(st.session_state.cancel_requests):
                st.write(f"Request for: {req['bill_id']}")
                if st.button("Approve", key=f"ap_{i}"):
                    st.session_state.saved_bills = [b for b in st.session_state.saved_bills if b['bill_id'] != req['bill_id']]
                    st.session_state.cancel_requests.pop(i)
                    st.rerun()

    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        t_new, t_saved, t_recall, t_summary = st.tabs(["📝 New Bill", "📂 Saved Bills", "🔍 RECALL", "📊 Summary"])

        with t_new:
            c1, c2 = st.columns([1, 3])
            sal = c1.selectbox("Salute", ["Mr.", "Mrs.", "Miss", "Baby"])
            name = c2.text_input("Patient Name")
            a1, a2, a3 = st.columns(3)
            ay = a1.number_input("Years", 0, 120)
            am = a2.number_input("Months", 0, 11)
            mob = a3.text_input("Mobile")
            doc = st.selectbox("Doctor", st.session_state.doctors)
            tests = st.multiselect("Select Tests", [t['name'] for t in st.session_state.tests])
            total = sum(t['price'] for t in st.session_state.tests if t['name'] in tests)
            disc = st.number_input("Discount")
            final = total - disc
            st.write(f"### Total: LKR {final:,.2f}")
            if st.button("Save & Print"):
                bid = f"LC{datetime.now().strftime('%M%S')}"
                st.session_state.saved_bills.append({"bill_id": bid, "patient": f"{sal} {name}", "age_y": ay, "age_m": am, "mobile": mob, "doctor": doc, "tests": tests, "final": final, "user": st.session_state.current_user, "date": date.today().isoformat()})
                st.success("Saved!"); st.rerun()

        with t_recall:
            mode = st.radio("Search By", ["Name", "Mobile", "Date"], horizontal=True)
            results = []
            if mode == "Name":
                s = st.text_input("Search Name")
                results = [b for b in st.session_state.saved_bills if s.lower() in b['patient'].lower()]
            elif mode == "Mobile":
                s = st.text_input("Search Mobile")
                results = [b for b in st.session_state.saved_bills if s in b.get('mobile', '')]
            else:
                d = st.date_input("Select Date", date.today())
                results = [b for b in st.session_state.saved_bills if b['date'] == d.isoformat()]
            
            for r in results:
                st.write(f"{r['bill_id']} - {r['patient']} ({r['date']})")
                st.download_button("Download PDF", create_pdf(r), file_name=f"{r['bill_id']}.pdf", key=f"dl_{r['bill_id']}")

        with t_summary:
            u_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
            for b in u_bills:
                col1, col2 = st.columns([4, 1])
                col1.write(f"{b['bill_id']} | {b['patient']} | LKR {b['final']}")
                if col2.button("Cancel", key=f"can_{b['bill_id']}"):
                    st.session_state.cancel_requests.append({"bill_id": b['bill_id'], "user": st.session_state.current_user})
                    st.info("Request Sent!")
            st.write(f"## Daily Total: LKR {sum(b['final'] for b in u_bills)}")