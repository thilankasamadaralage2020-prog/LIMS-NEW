import streamlit as st
import os
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF

# 1. පිටුවේ මූලික සැකසුම්
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# Session State Initialize
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'saved_bills' not in st.session_state: st.session_state.saved_bills = []
if 'tests' not in st.session_state: st.session_state.tests = []
if 'doctors' not in st.session_state: st.session_state.doctors = ["Self"]
if 'cancel_requests' not in st.session_state: st.session_state.cancel_requests = []
if 'users' not in st.session_state: 
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

# --- PDF Generator Function (Logo එක ඇතුළත් කර ඇත) ---
def create_pdf(bill):
    pdf = FPDF()
    pdf.add_page()
    
    # PDF එකට Logo එක ඇතුළත් කිරීම
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 33)
        pdf.ln(20) # Logo එක නිසා ඉඩ තැබීම
    
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
    pdf.text(130, pdf.get_y() + 5, f"Date: {bill['date']}")
    pdf.text(10, pdf.get_y() + 12, f"Doctor: {bill['doctor']}")
    pdf.text(130, pdf.get_y() + 12, f"Ref No: {bill['bill_id']}")
    pdf.ln(20)
    
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.cell(140, 10, "Test Description", border=0)
    pdf.cell(40, 10, "Price (LKR)", border=0, align='R')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=10)
    for t_name in bill['tests']:
        pdf.cell(140, 8, str(t_name))
        pdf.cell(40, 8, "-", align='R')
        pdf.ln(7)
        
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Final Total (LKR):", align='R')
    pdf.cell(40, 10, f"{bill['final']:,.2f}", align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- Login Screen (Logo එක ඇතුළත් කර ඇත) ---
def login_screen():
    # Login එකේ Logo එක පෙන්වීම
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("logo.png", width=200)
            
    st.markdown("<h1 style='text-align: center;'>🔬 Life Care LIMS</h1>", unsafe_allow_html=True)
    
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
            else: st.error("Invalid Username, Password or Role")

# --- Main Application Logic ---
if not st.session_state.logged_in:
    login_screen()
else:
    # ⬅️ BACK BUTTON
    if st.sidebar.button("⬅️ Back to Home"):
        st.rerun()
    
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    
    # --- Admin Dashboard ---
    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        t1, t2, t3, t4, t5 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals", "🛠 Edit Bill"])
        
        with t2:
            st.subheader("Add Doctor")
            nd = st.text_input("Doctor Name", key="add_doc_input")
            if st.button("Add Doctor"):
                if nd:
                    st.session_state.doctors.append(nd)
                    st.success(f"Doctor {nd} added!")
                    st.rerun()
        
        with t3:
            st.subheader("Add Test")
            nt = st.text_input("Test Name", key="add_test_input")
            np = st.number_input("Price", min_value=0.0)
            if st.button("Add Test"):
                if nt:
                    st.session_state.tests.append({"name": nt, "price": np})
                    st.success(f"Test {nt} added!")
                    st.rerun()
        # (Other admin tabs content...)

    # --- Billing Dashboard ---
    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        t_new, t_saved, t_recall, t_summary = st.tabs(["📝 New Bill", "📂 Saved Bills", "🔍 RECALL", "📊 Summary"])

        with t_new:
            p_name = st.text_input("Patient Name")
            ref_doc = st.selectbox("Doctor", options=st.session_state.doctors)
            sel_tests = st.multiselect("Select Tests", options=[t['name'] for t in st.session_state.tests])
            
            total = sum(t['price'] for t in st.session_state.tests if t['name'] in sel_tests)
            disc = st.number_input("Discount (LKR)", min_value=0.0)
            final = total - disc
            
            st.write(f"### Final Amount: LKR {final:,.2f}")
            if st.button("Save & Generate Bill"):
                if p_name and sel_tests:
                    bid = f"LC{datetime.now().strftime('%y%m%d%H%M%S')}"
                    st.session_state.saved_bills.append({
                        "bill_id": bid, "date": date.today().isoformat(), "patient": p_name,
                        "doctor": ref_doc, "tests": sel_tests, "final": final, "user": st.session_state.current_user
                    })
                    st.success(f"Bill {bid} Saved!")
                    st.rerun()

        with t_saved:
            st.subheader("Recently Saved Bills")
            my_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
            if my_bills:
                for b in reversed(my_bills[-10:]):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{b['bill_id']}** - {b['patient']} (LKR {b['final']:,.2f})")
                    pdf_data = create_pdf(b)
                    c2.download_button("Download PDF", pdf_data, file_name=f"{b['bill_id']}.pdf", key=f"dl_{b['bill_id']}")
            else: st.info("No bills saved yet.")

        with t_recall:
            st.subheader("Search Bills")
            search_name = st.text_input("Search by Patient Name")
            if search_name:
                results = [b for b in st.session_state.saved_bills if search_name.lower() in b['patient'].lower()]
                for r in results:
                    with st.expander(f"{r['bill_id']} - {r['patient']}"):
                        st.download_button("Download", create_pdf(r), file_name=f"{r['bill_id']}.pdf", key=f"rec_{r['bill_id']}")

        with t_summary:
            st.subheader(f"Summary for {st.session_state.current_user}")
            u_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
            if u_bills:
                st.table(pd.DataFrame(u_bills)[["patient", "bill_id", "final"]])
                st.write(f"## Total Sale: LKR {sum(b['final'] for b in u_bills):,.2f}")