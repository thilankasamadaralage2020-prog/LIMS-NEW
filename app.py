import streamlit as st
from PIL import Image
import os
import pandas as pd
from datetime import datetime, date
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
if 'cancel_requests' not in st.session_state:
    st.session_state.cancel_requests = []

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
        price = next((t['price'] for t in st.session_state.tests if t['name'] == t_name), 0)
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

# --- Login Function ---
def login():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    st.title("🔬 Laboratory Information Management System")
    with st.form("login_form"):
        u_name = st.text_input("User Name")
        u_pass = st.text_input("Password", type="password")
        u_role = st.selectbox("Select Role", ["Admin", "Billing", "Technician", "Satellite"])
        if st.form_submit_button("Login"):
            user_found = next((u for u in st.session_state.users if u['username'] == u_name and u['password'] == u_pass and u['role'] == u_role), None)
            if user_found:
                st.session_state.logged_in = True
                st.session_state.current_user = u_name
                st.session_state.role = u_role
                st.rerun()
            else:
                st.error("Invalid Credentials!")

# --- Admin Dashboard ---
def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    
    t1, t2, t3, t4, t5 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals", "🛠 Edit Bill"])
    
    with t1:
        st.subheader("Add New User")
        # Forms භාවිත නොකර සෘජු Widgets භාවිතය
        nu = st.text_input("New Username", key="admin_nu")
        np = st.text_input("New Password", type="password", key="admin_np")
        nr = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"], key="admin_nr")
        if st.button("Create User"):
            if nu and np:
                st.session_state.users.append({"username": nu, "password": np, "role": nr})
                st.success(f"User {nu} added successfully!")
                st.rerun()
        st.divider()
        st.write("### Existing Users")
        for i, u in enumerate(st.session_state.users):
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{u['username']}** ({u['role']})")
            if c2.button("Delete", key=f"del_u_{i}"):
                st.session_state.users.pop(i)
                st.rerun()

    with t2:
        st.subheader("Add New Doctor")
        nd_name = st.text_input("Doctor Name", key="admin_nd")
        if st.button("Add Doctor"):
            if nd_name:
                st.session_state.doctors.append(nd_name)
                st.success(f"Doctor {nd_name} added!")
                st.rerun()
        st.divider()
        st.write("### Existing Doctors")
        for i, d in enumerate(st.session_state.doctors):
            c1, c2 = st.columns([4, 1])
            c1.write(d)
            if c2.button("Delete", key=f"del_d_{i}"):
                st.session_state.doctors.pop(i)
                st.rerun()

    with t3:
        st.subheader("Add New Test")
        nt_name = st.text_input("Test Name", key="admin_nt")
        nt_price = st.number_input("Price (LKR)", min_value=0.0, step=10.0, key="admin_ntp")
        if st.button("Add Test"):
            if nt_name:
                st.session_state.tests.append({"name": nt_name, "price": nt_price})
                st.success(f"Test {nt_name} added!")
                st.rerun()
        st.divider()
        st.write("### Test List")
        for i, t in enumerate(st.session_state.tests):
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(t['name'])
            c2.write(f"LKR {t['price']:,.2f}")
            if c3.button("Delete", key=f"del_t_{i}"):
                st.session_state.tests.pop(i)
                st.rerun()

    with t4:
        st.subheader("Cancellation Requests")
        if not st.session_state.cancel_requests:
            st.info("No pending requests.")
        for i, req in enumerate(st.session_state.cancel_requests):
            c1, c2 = st.columns([4, 1])
            c1.write(f"Bill ID: **{req['bill_id']}** (Requested by: {req['user']})")
            if c2.button("Approve", key=f"app_can_{i}"):
                st.session_state.saved_bills = [b for b in st.session_state.saved_bills if b['bill_id'] != req['bill_id']]
                st.session_state.cancel_requests.pop(i)
                st.success("Bill Cancelled!")
                st.rerun()

    with t5:
        st.subheader("Edit Bill Details")
        eb_id = st.text_input("Enter Bill Reference Number (e.g., LC...)")
        if eb_id:
            eb_target = next((b for b in st.session_state.saved_bills if b['bill_id'] == eb_id), None)
            if eb_target:
                with st.form("edit_bill_f"):
                    new_name = st.text_input("Patient Name", value=eb_target['patient'])
                    new_doc = st.selectbox("Doctor", options=st.session_state.doctors, index=st.session_state.doctors.index(eb_target['doctor']) if eb_target['doctor'] in st.session_state.doctors else 0)
                    if st.form_submit_button("Save Changes"):
                        eb_target['patient'] = new_name
                        eb_target['doctor'] = new_doc
                        st.success("Bill Updated!")
                        st.rerun()
            else: st.error("Bill not found.")

# --- Billing Dashboard ---
def billing_dashboard():
    st.title("💳 Billing Dashboard")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    
    t_new, t_recall, t_summary = st.tabs(["📝 New Bill", "🔍 RECALL", "📊 Summary"])

    with t_new:
        c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
        salute = c1.selectbox("Salute", ["Mr.", "Mrs.", "Mast.", "Miss", "Baby", "Rev."])
        p_name = c2.text_input("Patient Name")
        p_age_y = c3.number_input("Age (Y)", min_value=0, step=1)
        p_age_m = c4.number_input("Age (M)", min_value=0, max_value=11, step=1)
        p_mobile = st.text_input("Mobile Number")
        ref_doc = st.selectbox("Referral Doctor", options=st.session_state.doctors)
        selected_tests = st.multiselect("Select Tests", options=[t['name'] for t in st.session_state.tests])
        
        total = sum(t['price'] for t in st.session_state.tests if t['name'] in selected_tests)
        discount = st.number_input("Discount (LKR)", min_value=0.0)
        final = total - discount
        
        st.write(f"### Total: LKR {total:,.2f}")
        st.write(f"## Final Amount: LKR {final:,.2f}")
        
        if st.button("Save & Generate Bill"):
            if p_name and selected_tests:
                bid = f"LC{datetime.now().strftime('%y%m%d%H%M%S')}"
                st.session_state.saved_bills.append({
                    "bill_id": bid, "date": date.today().isoformat(), "patient": f"{salute} {p_name}",
                    "age_y": p_age_y, "age_m": p_age_m, "mobile": p_mobile, "doctor": ref_doc,
                    "tests": selected_tests, "total": total, "discount": discount, "final": final,
                    "user": st.session_state.current_user
                })
                st.success(f"Bill {bid} Saved!"); st.rerun()
            else: st.error("Name and Tests are required.")

    with t_recall:
        st.subheader("Search & Recall Bills")
        s_mode = st.radio("Search By:", ["Name", "Mobile", "Date Range"], horizontal=True)
        results = []
        if s_mode == "Name":
            sn = st.text_input("Enter Name")
            if sn: results = [b for b in st.session_state.saved_bills if sn.lower() in b['patient'].lower()]
        elif s_mode == "Mobile":
            sm = st.text_input("Enter Mobile")
            if sm: results = [b for b in st.session_state.saved_bills if sm in b['mobile']]
        else:
            d1, d2 = st.columns(2)
            df = d1.date_input("From")
            dt = d2.date_input("To")
            results = [b for b in st.session_state.saved_bills if df.isoformat() <= b['date'] <= dt.isoformat()]
        
        for r in results:
            with st.expander(f"{r['bill_id']} - {r['patient']}"):
                st.write(f"Date: {r['date']} | Total: LKR {r['final']:,.2f}")
                pdf_data = create_pdf(r)
                st.download_button("Download PDF", pdf_data, file_name=f"{r['bill_id']}.pdf", key=f"dl_{r['bill_id']}")

    with t_summary:
        st.subheader(f"Sale Summary for {st.session_state.current_user}")
        u_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
        if u_bills:
            df_sum = pd.DataFrame(u_bills)[["patient", "bill_id", "final"]]
            st.table(df_sum)
            st.write(f"## Total Sale: LKR {sum(b['final'] for b in u_bills):,.2f}")
            st.divider()
            for b in u_bills:
                c1, c2 = st.columns([4, 1])
                c1.write(f"{b['bill_id']} - {b['patient']}")
                if c2.button("Send Cancel", key=f"sum_can_{b['bill_id']}"):
                    st.session_state.cancel_requests.append({"bill_id": b['bill_id'], "user": st.session_state.current_user})
                    st.info("Cancel request sent to Admin.")
        else: st.info("No bills found for your account.")

# --- Main Logic ---
if not st.session_state.get('logged_in'): login()
else:
    if st.session_state.role == "Admin": admin_dashboard()
    elif st.session_state.role == "Billing": billing_dashboard()
    else: 
        st.title(f"{st.session_state.role} Dashboard")
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))