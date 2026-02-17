import streamlit as st
from PIL import Image
import os
from datetime import datetime
from fpdf import FPDF

# 1. පිටුවේ මූලික සැකසුම්
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# දත්ත ගබඩා කිරීම
if 'doctors' not in st.session_state:
    st.session_state.doctors = ["Self", "Dr. Kamal Perera"]
if 'tests' not in st.session_state:
    st.session_state.tests = [{"name": "FBS", "price": 500.0}]
if 'saved_bills' not in st.session_state:
    st.session_state.saved_bills = []

# --- PDF සැකසීමේ Function එක ---
def create_pdf(bill):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo එක එක් කිරීම
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 33)
    
    # රසායනාගාර ලිපිනය (Header)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 5, "Life care laboratory Pvt (Ltd)", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, "Infront of Hospital, Kotuwegoda, Katuwana.", ln=True, align='C')
    pdf.cell(0, 5, "Tel: 0773326715", ln=True, align='C')
    pdf.ln(10)
    pdf.line(10, 35, 200, 35) # තනි ඉරක්
    
    # රෝගී විස්තර (වම්පස) සහ බිල් විස්තර (දකුණුපස)
    pdf.set_font("Arial", size=11)
    
    # වම්පස තීරුව
    pdf.text(10, 45, f"Patient Name: {bill['patient']}")
    pdf.text(10, 52, f"Age: {bill['age_y']}Y {bill['age_m']}M")
    pdf.text(10, 59, f"Ref. Doctor: {bill['doctor']}")
    
    # දකුණුපස තීරුව
    pdf.text(140, 45, f"Date: {bill['date']}")
    pdf.text(140, 52, f"Bill Ref: {bill['bill_id']}")
    
    pdf.ln(30)
    pdf.line(10, 65, 200, 65) # වෙන් කිරීමේ ඉර
    
    # Tests සහ පිරිවැය
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(130, 10, "Test Description", border=0)
    pdf.cell(30, 10, "Price (LKR)", border=0, align='R')
    pdf.ln(8)
    pdf.set_font("Arial", size=10)
    
    for t_name in bill['tests']:
        # මිල සෙවීම
        price = next((t['price'] for t in st.session_state.tests if t['name'] == t_name), 0)
        pdf.cell(130, 8, t_name, border=0)
        pdf.cell(30, 8, f"{price:.2f}", border=0, align='R')
        pdf.ln(6)
        
    pdf.line(130, pdf.get_y()+2, 175, pdf.get_y()+2)
    pdf.ln(5)
    
    # එකතුව සහ අවසාන මුදල
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(130, 8, "Total Amount:", align='R')
    pdf.cell(30, 8, f"{bill['total']:.2f}", align='R')
    pdf.ln(6)
    pdf.cell(130, 8, "Discount:", align='R')
    pdf.cell(30, 8, f"{bill['discount']:.2f}", align='R')
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(130, 8, "Final Amount (LKR):", align='R')
    pdf.cell(30, 8, f"{bill['final']:.2f}", align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- Billing Dashboard ---
def billing_dashboard():
    st.title("💳 Billing Dashboard")
    tab1, tab2 = st.tabs(["📝 New Bill", "📂 Saved Bills"])

    with tab1:
        st.subheader("Patient Registration")
        c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
        with c1: salute = st.selectbox("Salute", ["Mr.", "Mrs.", "Miss", "Baby"])
        with c2: p_name = st.text_input("Patient Name")
        with c3: p_age_y = st.number_input("Age (Years)", min_value=0, step=1)
        with c4: p_age_m = st.number_input("Age (Months)", min_value=0, max_value=11, step=1)

        c5, c6 = st.columns(2)
        with c5: p_mobile = st.text_input("Mobile")
        with c6: ref_doc = st.selectbox("Referral Doctor", options=st.session_state.doctors)

        selected_tests = st.multiselect("Select Tests", options=[t['name'] for t in st.session_state.tests])
        total = sum(t['price'] for t in st.session_state.tests if t['name'] in selected_tests)
        
        st.write(f"Total: LKR {total}")
        discount = st.number_input("Discount", min_value=0.0)
        final = total - discount
        st.subheader(f"Final Amount: LKR {final}")

        if st.button("Save Bill"):
            bill_id = f"LC{datetime.now().strftime('%y%m%d%H%M')}"
            bill_data = {
                "bill_id": bill_id, "date": datetime.now().strftime("%Y-%m-%d"),
                "patient": f"{salute} {p_name}", "age_y": p_age_y, "age_m": p_age_m,
                "doctor": ref_doc, "tests": selected_tests, "total": total,
                "discount": discount, "final": final
            }
            st.session_state.saved_bills.append(bill_data)
            st.success("Bill Saved!")

    with tab2:
        for b in reversed(st.session_state.saved_bills):
            with st.expander(f"{b['bill_id']} - {b['patient']}"):
                pdf_data = create_pdf(b)
                st.download_button(f"Download PDF {b['bill_id']}", data=pdf_data, file_name=f"{b['bill_id']}.pdf", mime="application/pdf")

# (Main Logic)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    # Login function (කලින් කේතයම භාවිතා කරන්න)
    u_name = st.text_input("User")
    u_pass = st.text_input("Pass", type="password")
    if st.button("Login"):
        if u_name=="admin" and u_pass=="123":
            st.session_state.logged_in = True
            st.session_state.role = "Billing"
            st.rerun()
else:
    billing_dashboard()