import streamlit as st
import os
from datetime import datetime, date
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# Session State Initialize
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'saved_bills' not in st.session_state: st.session_state.saved_bills = []
if 'tests' not in st.session_state: st.session_state.tests = []
if 'doctors' not in st.session_state: st.session_state.doctors = ["Self"]
if 'cancel_requests' not in st.session_state: st.session_state.cancel_requests = []
if 'users' not in st.session_state: 
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

# --- PDF Generator (නිවැරදි කරන ලද Format එක) ---
def create_pdf(bill):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 33)
        pdf.ln(20)
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
    
    # Test පේළිය ආරම්භය
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "Test Description", ln=0)
    pdf.cell(40, 8, "Price (LKR)", ln=1, align='R')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("Arial", size=10)
    total_val = 0
    for t_name in bill['tests']:
        # මෙහි මිල ගණන් පෙන්වීමට Test list එක පරීක්ෂා කරයි
        price = next((t['price'] for t in st.session_state.tests if t['name'] == t_name), 0)
        total_val += price
        pdf.cell(140, 8, str(t_name), ln=0)
        pdf.cell(40, 8, f"{price:,.2f}", ln=1, align='R')
    
    pdf.ln(2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # පරීක්ෂණ වලට පහළින් ඇති රේඛාව
    pdf.ln(2)
    
    # Total, Discount සහ Final rows
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "Total Amount (LKR):", align='R')
    pdf.cell(40, 8, f"{total_val:,.2f}", align='R', ln=1)
    
    pdf.cell(140, 8, "Discount (LKR):", align='R')
    pdf.cell(40, 8, f"{bill.get('discount', 0):,.2f}", align='R', ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Final Amount (LKR):", align='R')
    pdf.cell(40, 10, f"{bill['final']:,.2f}", align='R', ln=1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- Login Logic ---
if not st.session_state.logged_in:
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: st.image("logo.png", width=200)
    st.markdown("<h1 style='text-align: center;'>🔬 Life Care LIMS</h1>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    r = st.selectbox("Role", ["Admin", "Billing", "Technician"])
    if st.button("Login", use_container_width=True):
        user = next((x for x in st.session_state.users if x['username'] == u and x['password'] == p and x['role'] == r), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = u
            st.session_state.role = r
            st.rerun()
        else: st.error("Invalid Username or Password")
else:
    # Sidebar
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
    
    # --- Back Button (නිවැරදි කරන ලදී) ---
    if st.sidebar.button("⬅️ Back to Home"):
        st.rerun()
        
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- Billing Dashboard ---
    if st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        t_new, t_saved, t_recall, t_summary = st.tabs(["📝 New Bill", "📂 Saved Bills", "🔍 RECALL", "📊 Summary"])

        with t_new:
            c1, c2 = st.columns([1, 3])
            salute = c1.selectbox("Salute", ["Mr.", "Mrs.", "Miss", "Baby", "Rev."])
            p_name = c2.text_input("Patient Name")
            a1, a2, a3 = st.columns([1, 1, 2])
            age_y = a1.number_input("Years", 0, 120)
            age_m = a2.number_input("Months", 0, 11)
            p_mobile = a3.text_input("Mobile")
            ref_doc = st.selectbox("Doctor", options=st.session_state.doctors)
            sel_tests = st.multiselect("Tests", options=[t['name'] for t in st.session_state.tests])
            total = sum(t['price'] for t in st.session_state.tests if t['name'] in sel_tests)
            disc = st.number_input("Discount (LKR)", min_value=0.0)
            final = total - disc
            if st.button("Save & Generate Bill"):
                if p_name and sel_tests:
                    bid = f"LC{datetime.now().strftime('%y%m%d%H%M%S')}"
                    st.session_state.saved_bills.append({
                        "bill_id": bid, "date": date.today().isoformat(), "patient": f"{salute} {p_name}",
                        "age_y": age_y, "age_m": age_m, "mobile": p_mobile, "doctor": ref_doc,
                        "tests": sel_tests, "final": final, "discount": disc, "user": st.session_state.current_user
                    })
                    st.success("Bill Saved!"); st.rerun()

        with t_saved:
            st.subheader("Your Saved Bills")
            # --- Saved Bills දර්ශනය වීම නිවැරදි කරන ලදී ---
            my_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
            if not my_bills:
                st.info("No saved bills found.")
            else:
                for b in reversed(my_bills):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{b['bill_id']}** | {b['patient']} | {b['date']}")
                    c2.download_button("PDF", create_pdf(b), file_name=f"{b['bill_id']}.pdf", key=f"dl_{b['bill_id']}")

        with t_recall:
            # පවතින සෙවුම් පහසුකම් මෙහි තිබේ...
            pass

    # --- Admin Dashboard ---
    elif st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        # Admin tabs logic here...
        pass