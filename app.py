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
    
    # 1. Logo එක එක් කිරීම (වම්පස උඩ කෙළවරේ)
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 30)
    
    # 2. රසායනාගාර ලිපිනය (Header - මැදට වන්නට)
    pdf.set_font("Arial", 'B', 15)
    pdf.cell(0, 7, "Life care laboratory Pvt (Ltd)", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana.", ln=True, align='C')
    pdf.cell(0, 5, "Tel: 0773326715", ln=True, align='C')
    pdf.ln(15)
    
    # 3. රෝගී විස්තර (වම්පස) සහ බිල් විස්තර (දකුණුපස)
    pdf.set_font("Arial", size=11)
    # වම්පස: Patient Info
    pdf.text(10, 45, f"Patient Name : {bill['patient']}")
    pdf.text(10, 52, f"Age          : {bill['age_y']} Years {bill['age_m']} Months")
    pdf.text(10, 59, f"Ref. Doctor  : {bill['doctor']}")
    
    # දකුණුපස: Billing Info
    pdf.text(130, 45, f"Billing Date : {bill['date']}")
    pdf.text(130, 52, f"Bill Ref No  : {bill['bill_id']}")
    
    pdf.ln(25)
    pdf.line(10, 65, 200, 65) # තනි ඉරක් (වෙන් කිරීම)
    
    # 4. Tests සහ පිරිවැය දක්වන කොටස
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 10, "Test Description", border=0)
    pdf.cell(40, 10, "Price (LKR)", border=0, align='R')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    
    for t_name in bill['tests']:
        # Admin ඇතුළත් කළ පරීක්ෂණ අතරින් මිල සොයා ගැනීම
        price = next((t['price'] for t in st.session_state.tests if t['name'] == t_name), 0)
        pdf.cell(140, 8, t_name, border=0)
        pdf.cell(40, 8, f"{price:,.2f}", border=0, align='R')
        pdf.ln(7)
        
    pdf.ln(5)
    pdf.line(130, pdf.get_y(), 190, pdf.get_y()) # මුදලට උඩින් ඉරක්
    
    # 5. Total, Discount සහ Final Amount
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

# --- Login Function (මුල් පිටුව එලෙසම) ---
def login():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    st.title("🔬 Laboratory Information Management System")
    with st.form("login_form"):
        u_name = st.text_input("User Name")
        u_pass = st.text_input("Password", type="password")
        u_role = st.selectbox("Select Role", ["Admin", "Billing", "Technician"])
        if st.form_submit_button("Login"):
            user_found = next((u for u in st.session_state.users if u['username'] == u_name and u['password'] == u_pass and u['role'] == u_role), None)
            if user_found:
                st.session_state.logged_in = True
                st.session_state.current_user = u_name
                st.session_state.role = u_role
                st.rerun()
            else:
                st.error("Invalid Username or Password!")

# --- Billing Dashboard (යාවත්කාලීන කළ Age Months සමග) ---
def billing_dashboard():
    st.title("💳 Billing Dashboard")
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
        selected_tests = st.multiselect("Select Test (Search & Add)", options=test_names)
        
        total = sum(t['price'] for t in st.session_state.tests if t['name'] in selected_tests)
        st.write(f"#### Total Amount: LKR {total:,.2f}")
        
        discount = st.number_input("Discount Amount (LKR)", min_value=0.0, step=10.0)
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
                st.success("Bill Saved!")
            else:
                st.warning("Please fill required fields.")

    with tab2:
        st.subheader("Saved Bills History")
        for b in reversed(st.session_state.saved_bills):
            with st.expander(f"Bill: {b['bill_id']} - {b['patient']}"):
                pdf_data = create_pdf(b)
                st.download_button(f"Download PDF {b['bill_id']}", data=pdf_data, file_name=f"{b['bill_id']}.pdf", mime="application/pdf")

# --- (Admin Dashboard කේතය මෙතැනට) ---
def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    t1, t2, t3 = st.tabs(["Users", "Doctors", "Tests"])
    with t1:
        nu, np, nr = st.text_input("User"), st.text_input("Pass", type="password"), st.selectbox("Role", ["Admin", "Billing"])
        if st.button("Add User"): st.session_state.users.append({"username": nu, "password": np, "role": nr})
    with t2:
        nd = st.text_input("Doctor Name")
        if st.button("Add Doctor"): st.session_state.doctors.append(nd)
    with t3:
        nt, npr = st.text_input("Test Name"), st.number_input("Price")
        if st.button("Add Test"): st.session_state.tests.append({"name": nt, "price": npr})

# --- Main Logic ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.role == "Admin": admin_dashboard()
    elif st.session_state.role == "Billing": billing_dashboard()