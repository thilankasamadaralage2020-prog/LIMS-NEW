import streamlit as st
from PIL import Image
import os
import pandas as pd
from datetime import datetime

# 1. පිටුවේ මූලික සැකසුම්
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# දත්ත ගබඩා කිරීම (Session State) - මෙහි දත්ත පවතින්නේ වෙබ් අඩවිය Refresh වන තෙක් පමණි
if 'users' not in st.session_state:
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]
if 'doctors' not in st.session_state:
    # Admin විසින් ඇතුළත් කරන තෙක් පරීක්ෂණ සඳහා නම් කිහිපයක්
    st.session_state.doctors = ["Self", "Dr. Kamal Perera", "Dr. Sunil Silva"]
if 'tests' not in st.session_state:
    # Admin විසින් ඇතුළත් කරන තෙක් නිදසුන් පරීක්ෂණ
    st.session_state.tests = [{"name": "FBS", "price": 500.0}, {"name": "Full Blood Count", "price": 1200.0}, {"name": "Lipid Profile", "price": 2500.0}]
if 'saved_bills' not in st.session_state:
    st.session_state.saved_bills = []
if 'cancel_requests' not in st.session_state:
    st.session_state.cancel_requests = []

# --- Login Function ---
def login():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    st.title("🔬 Life Care LIMS Login")
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
                st.error("පරිශීලක නාමය හෝ මුරපදය වැරදියි!")

# --- Billing Dashboard ---
def billing_dashboard():
    st.title("💳 Billing Dashboard")
    st.sidebar.write(f"Logged in as: **{st.session_state.current_user}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    tab1, tab2 = st.tabs(["📝 New Bill", "📂 Saved Bills"])

    with tab1:
        st.subheader("Patient Registration")
        # එක පේළියක කොටස් 3ක් පෙන්වීමට
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            salute = st.selectbox("Salute", ["Mr.", "Mrs.", "Mast.", "Miss", "Baby", "Baby of Mrs.", "Rev."])
        with c2:
            p_name = st.text_input("Patient Name")
        with c3:
            p_age = st.text_input("Age")

        c4, c5 = st.columns(2)
        with c4:
            p_mobile = st.text_input("Mobile Number")
        with c5:
            # Admin add කළ doctor list එක මෙතැනට ලැබේ
            ref_doc = st.selectbox("Referral Doctor (Search & Select)", options=st.session_state.doctors)
            
        st.divider()
        st.subheader("Test Selection")
        
        # Admin add කළ test list එක මෙතැනට ලැබේ
        test_names = [t['name'] for t in st.session_state.tests]
        selected_tests = st.multiselect("Select Tests (Search & Add)", options=test_names)
        
        # තෝරාගත් පරීක්ෂණ වල මුළු එකතුව ගණනය කිරීම
        total_amount = sum(t['price'] for t in st.session_state.tests if t['name'] in selected_tests)
        
        st.write(f"#### Total Amount: LKR {total_amount:.2f}")
        
        # Discount සහ Final Amount
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            discount = st.number_input("Discount Amount (LKR)", min_value=0.0, value=0.0, step=10.0)
        
        final_amount = total_amount - discount
        
        with col_d2:
            st.write("#### Final Amount")
            st.subheader(f"LKR {final_amount:.2f}")

        if st.button("Save & Generate Bill"):
            if p_name and selected_tests:
                bill_id = f"LC-{datetime.now().strftime('%y%m%d%H%M%S')}"
                new_bill = {
                    "bill_id": bill_id,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "patient": f"{salute} {p_name}",
                    "age": p_age,
                    "mobile": p_mobile,
                    "doctor": ref_doc,
                    "tests": selected_tests,
                    "total": total_amount,
                    "discount": discount,
                    "final": final_amount
                }
                st.session_state.saved_bills.append(new_bill)
                st.success(f"Bill {bill_id} Saved Successfully!")
                st.balloons()
            else:
                st.error("කරුණාකර රෝගියාගේ නම සහ අවම වශයෙන් එක් පරීක්ෂණයක්වත් තෝරන්න.")

    with tab2:
        st.subheader("Saved Bills")
        if not st.session_state.saved_bills:
            st.info("තවමත් බිල්පත් කිසිවක් සුරැකී නැත.")
        else:
            for i, bill in enumerate(reversed(st.session_state.saved_bills)):
                with st.expander(f"Bill ID: {bill['bill_id']} | Patient: {bill['patient']}"):
                    # බිල්පත ලස්සනට පෙන්වීම
                    bill_content = f"""
                    LIFE CARE LABORATORY
                    -------------------------------
                    Bill ID    : {bill['bill_id']}
                    Date       : {bill['date']}
                    Patient    : {bill['patient']}
                    Age/Mobile : {bill['age']} / {bill['mobile']}
                    Doctor     : {bill['doctor']}
                    -------------------------------
                    Tests      : {', '.join(bill['tests'])}
                    -------------------------------
                    Total Amount : LKR {bill['total']:.2f}
                    Discount     : LKR {bill['discount']:.2f}
                    Final Amount : LKR {bill['final']:.2f}
                    -------------------------------
                    Thank You!
                    """
                    st.text(bill_content)
                    st.download_button(
                        label="Download & Print Bill",
                        data=bill_content,
                        file_name=f"Bill_{bill['bill_id']}.txt",
                        mime="text/plain",
                        key=f"dl_{i}"
                    )

# --- Admin Dashboard ---
def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    
    t1, t2, t3, t4 = st.tabs(["User Management", "Add Doctor", "Add Tests", "Approvals"])
    
    with t1:
        st.subheader("Create New User")
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        nr = st.selectbox("Role", ["Admin", "Billing", "Technician"])
        if st.button("Add User"):
            st.session_state.users.append({"username": nu, "password": np, "role": nr})
            st.success("User added!")
            
    with t2:
        st.subheader("Register New Doctor")
        nd = st.text_input("Doctor Name")
        if st.button("Add Doctor"):
            st.session_state.doctors.append(nd)
            st.success(f"{nd} added to system.")
            
    with t3:
        st.subheader("Add Test with Price")
        nt = st.text_input("Test Name")
        npr = st.number_input("Price (LKR)", min_value=0.0)
        if st.button("Add Test"):
            st.session_state.tests.append({"name": nt, "price": npr})
            st.success(f"{nt} added with price LKR {npr}")

    with t4:
        st.subheader("Pending Approvals")
        st.write("No cancellation requests at the moment.")

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
        st.title("Technician Portal")
        st.write("Results entry coming soon...")
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))