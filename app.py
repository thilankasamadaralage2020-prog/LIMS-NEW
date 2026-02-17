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

# --- PDF Generator Function ---
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
    
    # PDF එකට නව දත්ත එක් කිරීම
    pdf.text(10, pdf.get_y() + 5, f"Patient: {bill['patient']}")
    pdf.text(10, pdf.get_y() + 12, f"Age: {bill['age_y']}Y {bill['age_m']}M")
    pdf.text(10, pdf.get_y() + 19, f"Mobile: {bill['mobile']}")
    pdf.text(130, pdf.get_y() + 5, f"Date: {bill['date']}")
    pdf.text(130, pdf.get_y() + 12, f"Ref No: {bill['bill_id']}")
    pdf.text(130, pdf.get_y() + 19, f"Doctor: {bill['doctor']}")
    pdf.ln(25)
    
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

# --- Login Screen ---
def login_screen():
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: st.image("logo.png", width=200)
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
            else: st.error("Invalid Login Details")

# --- Main Application Logic ---
if not st.session_state.logged_in:
    login_screen()
else:
    if st.sidebar.button("⬅️ Back to Home"): st.rerun()
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))

    # --- Admin Dashboard ---
    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        t1, t2, t3, t4, t5 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals", "🛠 Edit Bill"])
        
        with t1:
            st.subheader("User Management")
            nu = st.text_input("New Username", key="admin_nu")
            np = st.text_input("New Password", type="password", key="admin_np")
            nr = st.selectbox("Role", ["Admin", "Billing", "Technician"], key="admin_nr")
            if st.button("Create User"):
                if nu and np:
                    st.session_state.users.append({"username": nu, "password": np, "role": nr})
                    st.success(f"User {nu} created!")
                    st.rerun()
            st.divider()
            for i, u in enumerate(st.session_state.users):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{u['username']}** ({u['role']})")
                if c2.button("Del", key=f"del_u_{i}"):
                    st.session_state.users.pop(i)
                    st.rerun()

        with t2:
            st.subheader("Doctor Management")
            nd = st.text_input("Doctor Name", key="admin_nd")
            if st.button("Add Doctor"):
                if nd:
                    st.session_state.doctors.append(nd)
                    st.success("Doctor added!")
                    st.rerun()
            st.divider()
            for i, d in enumerate(st.session_state.doctors):
                c1, c2 = st.columns([4, 1])
                c1.write(d)
                if c2.button("Del", key=f"del_d_{i}"):
                    st.session_state.doctors.pop(i)
                    st.rerun()

        with t3:
            st.subheader("Test Management")
            nt = st.text_input("Test Name", key="admin_nt")
            npr = st.number_input("Price", min_value=0.0, key="admin_npr")
            if st.button("Add Test"):
                if nt:
                    st.session_state.tests.append({"name": nt, "price": npr})
                    st.success("Test added!")
                    st.rerun()
            st.divider()
            for i, t in enumerate(st.session_state.tests):
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(t['name'])
                c2.write(f"LKR {t['price']:,.2f}")
                if c3.button("Del", key=f"del_t_{i}"):
                    st.session_state.tests.pop(i)
                    st.rerun()

        with t4:
            st.subheader("Pending Approvals")
            for i, req in enumerate(st.session_state.cancel_requests):
                c1, c2 = st.columns([4, 1])
                c1.write(f"Bill: {req['bill_id']} by {req['user']}")
                if c2.button("Approve", key=f"app_{i}"):
                    st.session_state.saved_bills = [b for b in st.session_state.saved_bills if b['bill_id'] != req['bill_id']]
                    st.session_state.cancel_requests.pop(i)
                    st.rerun()

        with t5:
            st.subheader("Edit Bill")
            eb_id = st.text_input("Bill ID")
            if eb_id:
                eb = next((b for b in st.session_state.saved_bills if b['bill_id'] == eb_id), None)
                if eb:
                    en = st.text_input("Patient Name", value=eb['patient'])
                    if st.button("Update"):
                        eb['patient'] = en
                        st.success("Updated!")

    # --- Billing Dashboard (Updated Form) ---
    elif st.session_state.role == "Billing":
        st.title("💳 Billing Dashboard")
        t_new, t_saved, t_recall, t_summary = st.tabs(["📝 New Bill", "📂 Saved Bills", "🔍 RECALL", "📊 Summary"])

        with t_new:
            st.subheader("New Patient Bill")
            
            # පෝරමයේ නව කොටස් (Salute, Name, Age, Mobile)
            c1, c2 = st.columns([1, 3])
            salute = c1.selectbox("Salute", ["Mr.", "Mrs.", "Miss", "Mast.", "Baby", "Rev."])
            p_name = c2.text_input("Patient Name")
            
            a1, a2, a3 = st.columns([1, 1, 2])
            age_y = a1.number_input("Age (Years)", min_value=0, max_value=120, step=1)
            age_m = a2.number_input("Age (Months)", min_value=0, max_value=11, step=1)
            p_mobile = a3.text_input("Mobile Number")
            
            ref_doc = st.selectbox("Doctor", options=st.session_state.doctors)
            sel_tests = st.multiselect("Tests", options=[t['name'] for t in st.session_state.tests])
            
            total = sum(t['price'] for t in st.session_state.tests if t['name'] in sel_tests)
            disc = st.number_input("Discount (LKR)", min_value=0.0)
            final = total - disc
            
            st.write(f"### Final Amount: LKR {final:,.2f}")
            
            if st.button("Save & Generate Bill"):
                if p_name and sel_tests:
                    bid = f"LC{datetime.now().strftime('%y%m%d%H%M%S')}"
                    full_name = f"{salute} {p_name}"
                    st.session_state.saved_bills.append({
                        "bill_id": bid, "date": date.today().isoformat(), 
                        "patient": full_name, "age_y": age_y, "age_m": age_m,
                        "mobile": p_mobile, "doctor": ref_doc, 
                        "tests": sel_tests, "final": final, 
                        "user": st.session_state.current_user
                    })
                    st.success(f"Bill {bid} Saved Successfully!")
                    st.rerun()
                else:
                    st.warning("Please enter Patient Name and select at least one Test.")

        with t_saved:
            st.subheader("Recently Saved Bills")
            my_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
            if my_bills:
                for b in reversed(my_bills[-10:]):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{b['bill_id']}** - {b['patient']} (LKR {b['final']:,.2f})")
                    c2.download_button("PDF", create_pdf(b), file_name=f"{b['bill_id']}.pdf", key=f"dl_{b['bill_id']}")
            else: st.info("No bills saved yet.")

        with t_recall:
            st.subheader("Search Bills")
            sn = st.text_input("Search Name")
            if sn:
                results = [b for b in st.session_state.saved_bills if sn.lower() in b['patient'].lower()]
                for r in results:
                    st.write(f"{r['bill_id']} - {r['patient']} (Mobile: {r.get('mobile', 'N/A')})")

        with t_summary:
            st.subheader(f"Sale Summary: {st.session_state.current_user}")
            u_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
            if u_bills:
                st.table(pd.DataFrame(u_bills)[["patient", "bill_id", "final"]])
                st.write(f"## Total: LKR {sum(b['final'] for b in u_bills):,.2f}")