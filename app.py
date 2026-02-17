import streamlit as st
from PIL import Image
import os

# 1. පිටුවේ මූලික සැකසුම්
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# දත්ත ගබඩා කිරීම සඳහා මූලික සැකසුම් (Initial Database Simulation)
if 'users' not in st.session_state:
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]
if 'doctors' not in st.session_state:
    st.session_state.doctors = []
if 'tests' not in st.session_state:
    st.session_state.tests = []
if 'cancel_requests' not in st.session_state:
    st.session_state.cancel_requests = []
if 'billing_summary' not in st.session_state:
    st.session_state.billing_summary = 5000.00  # උදාහරණයක් ලෙස පවතින මුදල

# --- Functions ---

def login():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    st.title("🔬 Life Care LIMS Login")
    
    with st.form("login_form"):
        u_name = st.text_input("User Name")
        u_pass = st.text_input("Password", type="password")
        u_role = st.selectbox("Select Role", ["Admin", "Billing", "Technician", "Satellite"])
        submitted = st.form_submit_button("Login")

        if submitted:
            # User පරීක්ෂාව
            user_found = next((u for u in st.session_state.users if u['username'] == u_name and u['password'] == u_pass and u['role'] == u_role), None)
            
            if user_found:
                st.session_state.logged_in = True
                st.session_state.current_user = u_name
                st.session_state.role = u_role
                st.rerun()
            else:
                st.error("Invalid Username, Password or Role!")

def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    st.sidebar.write(f"Logged in as: **{st.session_state.current_user}**")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["👥 User Management", "🩺 Doctors", "🧪 Tests & Pricing", "✅ Approvals"])

    # 1. Create & Delete User
    with tab1:
        st.subheader("Add New User")
        with st.form("add_user_form"):
            new_u = st.text_input("New Username")
            new_p = st.text_input("New Password")
            new_r = st.selectbox("Role", ["Admin", "Billing", "Technician", "Satellite"])
            if st.form_submit_button("Add User"):
                if new_u:
                    st.session_state.users.append({"username": new_u, "password": new_p, "role": new_r})
                    st.success(f"User {new_u} added!")
                    st.rerun()

        st.divider()
        st.subheader("Existing Users")
        for i, u in enumerate(st.session_state.users):
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{u['username']}** ({u['role']})")
            if col2.button("Delete", key=f"del_user_{i}"):
                st.session_state.users.pop(i)
                st.rerun()

    # 2. Add & Delete Doctor
    with tab2:
        st.subheader("Register Doctor")
        with st.form("add_doc_form"):
            d_name = st.text_input("Doctor Name")
            if st.form_submit_button("Add Doctor"):
                if d_name:
                    st.session_state.doctors.append(d_name)
                    st.rerun()
        
        st.divider()
        for i, d in enumerate(st.session_state.doctors):
            col1, col2 = st.columns([3, 1])
            col1.write(d)
            if col2.button("Delete", key=f"del_doc_{i}"):
                st.session_state.doctors.pop(i)
                st.rerun()

    # 3. Add Tests with Price (LKR)
    with tab3:
        st.subheader("Add New Test")
        with st.form("add_test_form"):
            t_name = st.text_input("Test Name")
            t_price = st.number_input("Price (LKR)", min_value=0.0, step=100.0)
            if st.form_submit_button("Add Test"):
                if t_name:
                    st.session_state.tests.append({"name": t_name, "price": t_price})
                    st.rerun()
        
        st.divider()
        for i, t in enumerate(st.session_state.tests):
            col1, col2, col3 = st.columns([2, 2, 1])
            col1.write(t['name'])
            col2.write(f"LKR {t['price']:.2f}")
            if col3.button("Delete", key=f"del_test_{i}"):
                st.session_state.tests.pop(i)
                st.rerun()

    # 4. Approve Bill Cancellations
    with tab4:
        st.subheader("Bill Cancellation Requests")
        st.info(f"Current Billing Total: **LKR {st.session_state.billing_summary:.2f}**")
        
        if not st.session_state.cancel_requests:
            st.write("No pending requests.")
        else:
            for i, req in enumerate(st.session_state.cancel_requests):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"Bill ID: {req['bill_id']} | Amount: LKR {req['amount']}")
                if col2.button("Approve", key=f"app_{i}"):
                    st.session_state.billing_summary -= req['amount']
                    st.session_state.cancel_requests.pop(i)
                    st.success("Bill Cancelled & Summary Updated!")
                    st.rerun()
                if col3.button("Reject", key=f"rej_{i}"):
                    st.session_state.cancel_requests.pop(i)
                    st.rerun()

# --- Main App Logic ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    if st.session_state.role == "Admin":
        admin_dashboard()
    else:
        st.title(f"{st.session_state.role} Dashboard")
        st.write("Welcome! Work in progress...")
        if st.button("Add Test Cancel Request (Demo)"):
            st.session_state.cancel_requests.append({"bill_id": "B001", "amount": 1500.00})
            st.success("Request sent to Admin!")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()