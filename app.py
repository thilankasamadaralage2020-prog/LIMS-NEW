import streamlit as st
import os
from datetime import datetime, date
from fpdf import FPDF

# පිටුවේ මූලික සැකසුම්
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# දත්ත මතකය පවත්වා ගැනීම (Session State)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'saved_bills' not in st.session_state: st.session_state.saved_bills = []
if 'tests' not in st.session_state: st.session_state.tests = []
if 'doctors' not in st.session_state: st.session_state.doctors = ["Self"]
if 'cancel_requests' not in st.session_state: st.session_state.cancel_requests = []
if 'users' not in st.session_state: 
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]

# --- PDF සෑදීමේ Function එක ---
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

# --- Dashboard Logic ---
else:
    # Sidebar සැකසුම්
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
    
    st.sidebar.title(f"Hi, {st.session_state.current_user}")
    if st.sidebar.button("⬅️ Back to Home"): st.rerun()
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- Admin Dashboard ---
    if st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        t1, t2, t3, t4, t5 = st.tabs(["Users", "Doctors", "Tests", "✅ Approvals", "🛠 Edit Bill"])
        
        with t1:
            st.subheader("Add New User")
            nu = st.text_input("New Username", key="nu")
            np = st.text_input("New Password", type="password", key="np")
            nr = st.selectbox("Role", ["Admin", "Billing", "Technician"], key="nr")
            if st.button("Create User"):
                if nu and np:
                    st.session_state.users.append({"username": nu, "password": np, "role": nr})
                    st.success(f"User {nu} added!"); st.rerun()
            st.divider()
            st.subheader("Existing Users")
            for i, u in enumerate(st.session_state.users):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{u['username']}** ({u['role']})")
                if c2.button("Delete", key=f"du_{i}"):
                    st.session_state.users.pop(i); st.rerun()

        with t2:
            st.subheader("Add Doctor")
            nd = st.text_input("Doctor Name", key="nd")
            if st.button("Add Doctor"):
                if nd: st.session_state.doctors.append(nd); st.success("Doctor added!"); st.rerun()
            st.divider()
            for i, d in enumerate(st.session_state.doctors):
                c1, c2 = st.columns([4, 1])
                c1.write(d)
                if c2.button("Delete", key=f"dd_{i}"):
                    st.session_state.doctors.pop(i); st.rerun()

        with t3:
            st.subheader("Add Test & Pricing")
            nt = st.text_input("Test Name", key="nt")
            npr = st.number_input("Price (LKR)", min_value=0.0, key="npr")
            if st.button("Add Test"):
                if nt: st.session_state.tests.append({"name": nt, "price": npr}); st.success("Test added!"); st.rerun()
            st.divider()
            for i, t in enumerate(st.session_state.tests):
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(t['name'])
                c2.write(f"LKR {t['price']:,.2f}")
                if c3.button("Delete", key=f"dt_{i}"):
                    st.session_state.tests.pop(i); st.rerun()

        with t4:
            st.subheader("Cancellation Approvals")
            for i, req in enumerate(st.session_state.cancel_requests):
                c1, c2 = st.columns([4, 1])
                c1.warning(f"Bill: {req['bill_id']} (User: {req['user']})")
                if c2.button("Approve Cancel", key=f"ac_{i}"):
                    st.session_state.saved_bills = [b for b in st.session_state.saved_bills if b['bill_id'] != req['bill_id']]
                    st.session_state.cancel_requests.pop(i)
                    st.rerun()

    # --- Billing Dashboard ---
    elif st.session_state.role == "Billing":
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
            disc = st.number_input("Discount (LKR)")
            final = total - disc
            st.write(f"### Final: LKR {final:,.2f}")
            if st.button("Save & Generate Bill"):
                if p_name and sel_tests:
                    bid = f"LC{datetime.now().strftime('%y%m%d%H%M%S')}"
                    st.session_state.saved_bills.append({
                        "bill_id": bid, "date": date.today().isoformat(), "patient": f"{salute} {p_name}",
                        "age_y": age_y, "age_m": age_m, "mobile": p_mobile, "doctor": ref_doc,
                        "tests": sel_tests, "final": final, "user": st.session_state.current_user
                    })
                    st.success(f"Bill {bid} Saved!"); st.rerun()

        with t_recall:
            st.subheader("Search Bills")
            mode = st.radio("Search By:", ["Name", "Mobile", "Date"], horizontal=True)
            res = []
            if mode == "Name":
                sn = st.text_input("Enter Name")
                if sn: res = [b for b in st.session_state.saved_bills if sn.lower() in b['patient'].lower()]
            elif mode == "Mobile":
                sm = st.text_input("Enter Mobile")
                if sm: res = [b for b in st.session_state.saved_bills if sm in b.get('mobile', '')]
            else:
                c1, c2 = st.columns(2); sd = c1.date_input("From"); ed = c2.date_input("To")
                res = [b for b in st.session_state.saved_bills if sd.isoformat() <= b['date'] <= ed.isoformat()]
            for r in res:
                st.write(f"{r['bill_id']} - {r['patient']}")
                st.download_button("PDF", create_pdf(r), file_name=f"{r['bill_id']}.pdf", key=f"r_{r['bill_id']}")

        with t_summary:
            st.subheader("Daily Summary")
            u_bills = [b for b in st.session_state.saved_bills if b['user'] == st.session_state.current_user]
            for b in u_bills:
                c1, c2 = st.columns([4, 1])
                c1.write(f"{b['bill_id']} | {b['patient']} | LKR {b['final']}")
                if c2.button("Cancel", key=f"can_{b['bill_id']}"):
                    if not any(req['bill_id'] == b['bill_id'] for req in st.session_state.cancel_requests):
                        st.session_state.cancel_requests.append({"bill_id": b['bill_id'], "user": st.session_state.current_user})
                        st.info("Request Sent!")
            st.write(f"### Total Sale: LKR {sum(b['final'] for b in u_bills):,.2f}")