import streamlit as st
import os
from datetime import datetime, date
from fpdf import FPDF

# 1. Page Config
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'saved_bills' not in st.session_state: st.session_state.saved_bills = []
if 'tests' not in st.session_state: st.session_state.tests = []
if 'doctors' not in st.session_state: st.session_state.doctors = ["Self"]
if 'cancel_requests' not in st.session_state: st.session_state.cancel_requests = []
if 'users' not in st.session_state: 
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

# --- PDF Function ---
def create_pdf(bill):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 33)
        pdf.ln(20)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Life Care Laboratory Pvt (Ltd)", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana.", ln=True, align='C')
    pdf.cell(0, 5, "Tel: 0773326715", ln=True, align='C')
    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.text(10, pdf.get_y() + 5, f"Patient: {bill['patient']}")
    pdf.text(10, pdf.get_y() + 12, f"Age: {bill.get('age_y', 0)}Y {bill.get('age_m', 0)}M")
    pdf.text(10, pdf.get_y() + 19, f"Mobile: {bill.get('mobile', 'N/A')}")
    pdf.text(130, pdf.get_y() + 5, f"Date: {bill['date']}")
    pdf.text(130, pdf.get_y() + 12, f"Ref No: {bill['bill_id']}")
    pdf.ln(25)
    for t_name in bill['tests']:
        pdf.cell(140, 8, str(t_name))
        pdf.cell(40, 8, "-", align='R')
        pdf.ln(7)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.cell(140, 10, "Final Total (LKR):", align='R')
    pdf.cell(40, 10, f"{bill['final']:,.2f}", align='R')
    return pdf.output(dest='S').encode('latin-1')

# --- Login Screen ---
def login_screen():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150) # මැද ලෝගෝ එක
    st.title("🔬 Life Care LIMS")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        r = st.selectbox("Role", ["Admin", "Billing", "Technician"])
        if st.form_submit_button("Login"):
            found = next((user for user in st.session_state.users if user['username'] == u and user['password'] == p and user['role'] == r), None)
            if found:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.session_state.role = r
                st.rerun()
            else: st.error("Invalid Login")

if not st.session_state.logged_in:
    login_screen()
else:
    # Sidebar එකේ ලෝගෝ එක පෙන්වීම
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
    
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))

    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        t1, t2, t3, t4, t5 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals", "🛠 Edit Bill"])
        with t4:
            st.subheader("Cancellation Requests")
            for i, req in enumerate(st.session_state.cancel_requests):
                c1, c2 = st.columns([4, 1])
                c1.write(f"Bill ID: **{req['bill_id']}**")
                if c2.button("Approve", key=f"app_{i}"):
                    st.session_state.saved_bills = [b for b in st.session_state.saved_bills if b['bill_id'] != req['bill_id']]
                    st.session_state.cancel_requests.pop(i)
                    st.rerun()

    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        t_new, t_saved, t_recall, t_summary = st.tabs(["📝 New Bill", "📂 Saved Bills", "🔍 RECALL", "📊 Summary"])

        with t_new:
            c1, c2 = st.columns([1, 3])
            salute = c1.selectbox("Salute", ["Mr.", "Mrs.", "Miss", "Baby"])
            p_name = c2.text_input("Patient Name")
            a1, a2, a3 = st.columns([1, 1, 2])
            age_y = a1.number_input("Age (Y)", 0, 120)
            age_m = a2.number_input("Age (M)", 0, 11)
            p_mobile = a3.text_input("Mobile")
            sel_tests = st.multiselect("Tests", options=[t['name'] for t in st.session_state.tests])
            total = sum(t['price'] for t in st.session_state.tests if t['name'] in sel_tests)
            disc = st.number_input("Discount")
            final = total - disc
            if st.button("Save & Print"):
                bid = f"LC{datetime.now().strftime('%M%S')}"
                st.session_state.saved_bills.append({"bill_id": bid, "date": date.today().isoformat(), "patient": f"{salute} {p_name}", "age_y": age_y, "age_m": age_m, "mobile": p_mobile, "tests": sel_tests, "final": final, "user": st.session_state.current_user})
                st.success("Saved!"); st.rerun()

        with t_recall:
            st.subheader("Search Bills")
            search_mode = st.radio("Search By:", ["Name", "Mobile Number", "Date Range"], horizontal=True)
            res = []
            if search_mode == "Name":
                sn = st.text_input("Enter Name")
                if sn: res = [b for b in st.session_state.saved_bills if sn.lower() in b['patient'].lower()]
            elif search_mode == "Mobile Number":
                sm = st.text_input("Enter Mobile")
                if sm: res = [b for b in st.session_state.saved_bills if sm in b.get('mobile', '')]
            else:
                d1, d2 = st.columns(2); sd = d1.date_input("From", date.today()); ed = d2.date_input("To", date.today())
                res = [b for b in st.session_state.saved_bills if sd.isoformat() <= b['date'] <= ed.isoformat()]
            for r in res:
                st.write(f"{r['bill_id']} - {r['patient']}")
                st.download_button("Download PDF", create_pdf(r), file_name=f"{r['bill_id']}.pdf", key=f"r_{r['bill_id']}")

        with t_summary:
            st.subheader("Daily Summary")
            u_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
            for b in u_bills:
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{b['bill_id']}** | {b['patient']} | LKR {b['final']}")
                if col2.button("Cancel Request", key=f"can_{b['bill_id']}"):
                    st.session_state.cancel_requests.append({"bill_id": b['bill_id'], "user": st.session_state.current_user})
                    st.info("Sent!"); st.rerun()
            st.write(f"### Total: LKR {sum(b['final'] for b in u_bills)}")