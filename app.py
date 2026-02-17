import streamlit as st
from PIL import Image
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. පිටුවේ මූලික සැකසුම්
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# දත්ත ගබඩා කිරීම (Session State)
if 'users' not in st.session_state:
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]
if 'doctors' not in st.session_state:
    st.session_state.doctors = ["Self"]
if 'tests' not in st.session_state:
    st.session_state.tests = []
if 'saved_bills' not in st.session_state:
    st.session_state.saved_bills = []

# --- PDF සැකසීමේ Function එක ---
def create_pdf(bill):
    pdf = FPDF()
    pdf.add_page()
    
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 30)
    
    pdf.set_font("Arial", 'B', 15)
    pdf.cell(0, 7, "Life care laboratory Pvt (Ltd)", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana.", ln=True, align='C')
    pdf.cell(0, 5, "Tel: 0773326715", ln=True, align='C')
    pdf.ln(15)
    
    pdf.set_font("Arial", size=11)
    pdf.text(10, 45, f"Patient Name : {bill['patient']}")
    pdf.text(10, 52, f"Age          : {bill['age_y']} Years {bill['age_m']} Months")
    pdf.text(10, 59, f"Ref. Doctor  : {bill['doctor']}")
    
    pdf.text(130, 45, f"Billing Date : {bill['date']}")
    pdf.text(130, 52, f"Bill Ref No  : {bill['bill_id']}")
    
    pdf.ln(25)
    pdf.line(10, 65, 200, 65)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 10, "Test Description", border=0)
    pdf.cell(40, 10, "Price (LKR)", border=0, align='R')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    
    for t_name in bill['tests']:
        price = next((t['price'] for t in st.session_state.tests if t['name'] in t_name), 0)
        pdf.cell(140, 8, t_name, border=0)
        pdf.cell(40, 8, f"{price:,.2f}", border=0, align='R')
        pdf.ln(7)
        
    pdf.ln(5)
    pdf.line(130, pdf.get_y(), 190, pdf.get_y())
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 7, "Total Amount:", align='R')
    pdf.cell(40, 7, f"{bill['total']:,.2f}", align='R')
    pdf.ln(7)
    pdf.cell(140, 7, "Discount:", align='R')
    pdf.cell(40, 7, f"{bill['discount']:,.2f}", align='R')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 8, "Final Amount (LKR):", align='R')
    pdf.cell(40, 8, f"{bill['final']:,.2f}", align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- Login Function (පැරණි පෙනුම සහ සියලුම Roles සහිතව) ---
def login():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    st.title("🔬 Laboratory Information Management System")
    with st.form("login_form"):
        u_name = st.text_input("User Name")
        u_pass = st.text_input("Password", type="password")
        # ඔබ ඉල්ලූ සියලුම Roles මෙහි ඇතුළත් කර ඇත
        u_role = st.selectbox("Select Role", ["Admin", "Billing", "Technician", "Satellite"])
        if st.form_submit_button("Login"):
            user_found = next((u for u in st.session_state.users if u['username'] == u_name and u['password'] == u_pass and u['role'] == u_role), None)
            if user_found:
                st.session_state.logged_in = True
                st.session_state.current_user = u_name
                st.session_state.role = u_role
                st.rerun()
            else:
                st.error("Invalid Username, Password or Role!")

# --- Admin Dashboard (නිවැරදි කරන ලද Add/Delete පහසුකම් සහිතව) ---
def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    st.sidebar.write(f"Logged in as: **{st.session_state.current_user}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "🩺 Doctors", "🧪 Tests & Pricing"])
    
    with tab1:
        st.subheader("Add New User")
        with st.form("new_user_form"):
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            nr = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"])
            if st.form_submit_button("Create User"):
                if nu and np:
                    st.session_state.users.append({"username": nu, "password": np, "role": nr})
                    st.success(f"User {nu} added!")
                    st.rerun()

        st.divider()
        st.subheader("Existing Users")
        for i, u in enumerate(st.session_state.users):
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{u['username']}** ({u['role']})")
            if c2.button("Delete", key=f"del_u_{i}"):
                st.session_state.users.pop(i)
                st.rerun()

    with tab2:
        st.subheader("Register Doctor")
        with st.form("new_doc_form"):
            nd = st.text_input("Doctor Name")
            if st.form_submit_button("Add Doctor"):
                if nd:
                    st.session_state.doctors.append(nd)
                    st.success(f"Dr. {nd} registered!")
                    st.rerun()
        
        st.divider()
        for i, d in enumerate(st.session_state.doctors):
            c1, c2 = st.columns([3, 1])
            c1.write(d)
            if c2.button("Delete", key=f"del_d_{i}"):
                st.session_state.doctors.pop(i)
                st.rerun()

    with tab3:
        st.subheader("Add New Test")
        with st.form("new_test_form"):
            nt = st.text_input("Test Name")
            npr = st.number_input("Price (LKR)", min_value=0.0)
            if st.form_submit_button("Add Test"):
                if nt:
                    st.session_state.tests.append({"name": nt, "price": npr})
                    st.success(f"Test {nt} added!")
                    st.rerun()
        
        st.divider()
        for i, t in enumerate(st.session_state.tests):
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(t['name'])
            c2.write(f"LKR {t['price']:.2f}")
            if c3.button("Delete", key=f"del_t_{i}"):
                st.session_state.tests.pop(i)
                st.rerun()

# --- Billing Dashboard (Age Months සහ PDF සමග) ---
def billing_dashboard():
    st.title("💳 Billing Dashboard")
    st.sidebar.write(f"User: **{st.session_state.current_user}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    tab1, tab2 = st.tabs(["📝 New Bill", "📂 Saved Bills"])
    with tab1:
        st.subheader("New Patient Bill")
        c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
        with c1: salute = st.selectbox("Salute", ["Mr.", "Mrs.", "Mast.", "Miss", "Baby", "Baby of Mrs.", "Rev."])
        with c2: p_name = st.text_input("Patient Name")
        with c3: p_age_y = st.number_input("Age (Years)", min_value=0, step=1)
        with c4: p_age_m = st.number_input("Age (Months)", min_value=0, max_value=11, step=1)

        c5, c6 = st.columns(2)
        with c5: p_mobile = st.text_input("Mobile Number")
        with c6: ref_doc = st.selectbox("Referral Doctor", options=st.session_state.doctors)

        st.divider()
        test_names = [t['name'] for t in st.session_state.tests]
        selected_tests = st.multiselect("Select Tests", options=test_names)
        
        total = sum(t['price'] for t in st.session_state.tests if t['name'] in selected_tests)
        st.write(f"#### Total Amount: LKR {total:,.2f}")
        
        discount = st.number_input("Discount Amount (LKR)", min_value=0.0)
        final = total - discount
        st.success(f"### Final Amount: LKR {final:,.2f}")

        if st.button("Save & Generate Bill"):
            if p_name and selected_tests:
                bill_id = f"LC{datetime.now().strftime('%y%m%d%H%M')}"
                new_bill = {
                    "bill_id": bill_id, "date": datetime.now().strftime("%Y-%m-%d"),
                    "patient": f"{salute} {p_name}", "age_y": p_age_y, "age_m": p_age_m,
                    "doctor": ref_doc, "tests": selected_tests, "total": total,
                    "discount": discount, "final": final
                }
                st.session_state.saved_bills.append(new_bill)
                st.success(f"Bill {bill_id} Saved!")
                st.balloons()
            else:
                st.error("Please provide Patient Name and select Tests.")

    with tab2:
        st.subheader("Saved Bills")
        for b in reversed(st.session_state.saved_bills):
            with st.expander(f"Bill: {b['bill_id']} - {b['patient']}"):
                pdf_data = create_pdf(b)
                st.download_button(f"Download PDF {b['bill_id']}", data=pdf_data, file_name=f"{b['bill_id']}.pdf", mime="application/pdf")

# --- Main Logic ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    if st.session_state.role == "Admin":
        admin_dashboard()
    elif st.session_state.role == "Billing":
        billing_dashboard()
    else:
        st.title(f"{st.session_state.role} Dashboard")
        st.write("Work in progress...")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()