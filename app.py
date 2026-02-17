import streamlit as st
import os
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF

# පිටුවේ මූලික සැකසුම්
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# Session State Initialize
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'saved_bills' not in st.session_state: st.session_state.saved_bills = []
if 'tests' not in st.session_state: st.session_state.tests = []
if 'doctors' not in st.session_state: st.session_state.doctors = ["Self"]
if 'cancel_requests' not in st.session_state: st.session_state.cancel_requests = []
if 'users' not in st.session_state: st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

# PDF Generator Function
def create_pdf(bill):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Life Care Laboratory", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"Bill ID: {bill['bill_id']} | Date: {bill['date']}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, f"Patient: {bill['patient']}", ln=True)
    pdf.cell(0, 7, f"Doctor: {bill['doctor']}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.cell(140, 10, "Test Name")
    pdf.cell(40, 10, "Price", align='R')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    for t in bill['tests']:
        pdf.cell(140, 7, str(t))
        pdf.cell(40, 7, "-", align='R')
        pdf.ln(7)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Final Total (LKR):", align='R')
    pdf.cell(40, 10, f"{bill['final']:,.2f}", align='R')
    return pdf.output(dest='S').encode('latin-1')

# --- Login ---
def login_screen():
    st.title("🔬 Life Care LIMS - Login")
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

# --- Dashboard ---
if not st.session_state.logged_in:
    login_screen()
else:
    # ⬅️ BACK BUTTON (Sidebar එකේ සැමවිටම පවතී)
    if st.sidebar.button("⬅️ Back to Home"):
        st.rerun()
    
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    
    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        t1, t2, t3, t4, t5 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals", "🛠 Edit Bill"])
        # (Admin functions follow...)
        with t2:
            nd = st.text_input("Doctor Name")
            if st.button("Add Doctor"): 
                st.session_state.doctors.append(nd)
                st.success("Added")
        with t3:
            nt = st.text_input("Test Name")
            np = st.number_input("Price")
            if st.button("Add Test"):
                st.session_state.tests.append({"name": nt, "price": np})
                st.success("Added")

    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        # ඔබ ඉල්ලා සිටි Tab එක මෙතැන ඇත
        t_new, t_saved, t_recall, t_summary = st.tabs(["📝 New Bill", "📂 Saved Bills", "🔍 RECALL", "📊 Summary"])

        with t_new:
            p_name = st.text_input("Patient Name")
            ref_doc = st.selectbox("Doctor", options=st.session_state.doctors)
            sel_tests = st.multiselect("Tests", options=[t['name'] for t in st.session_state.tests])
            total = sum(t['price'] for t in st.session_state.tests if t['name'] in sel_tests)
            disc = st.number_input("Discount")
            final = total - disc
            st.write(f"### Final: LKR {final:,.2f}")
            if st.button("Save & Generate Bill"):
                bid = f"LC{datetime.now().strftime('%H%M%S')}"
                st.session_state.saved_bills.append({
                    "bill_id": bid, "date": date.today().isoformat(), "patient": p_name,
                    "doctor": ref_doc, "tests": sel_tests, "final": final, "user": st.session_state.current_user
                })
                st.success(f"Bill {bid} Saved!")

        with t_saved:
            st.subheader("Last 10 Saved Bills")
            my_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
            for b in reversed(my_bills[-10:]):
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{b['bill_id']}** - {b['patient']}")
                col2.download_button("Download PDF", create_pdf(b), file_name=f"{b['bill_id']}.pdf", key=b['bill_id'])