import streamlit as st
from PIL import Image
import os
import pandas as pd
from datetime import datetime

# 1. පිටුවේ මූලික සැකසුම්
st.set_page_config(page_title="Life Care LIMS", page_icon="🔬", layout="wide")

# දත්ත ගබඩා කිරීම (Session State)
if 'users' not in st.session_state:
    st.session_state.users = [{"username": "admin", "password": "123", "role": "Admin"}]
if 'doctors' not in st.session_state:
    st.session_state.doctors = ["Self", "Dr. Kamal Perera", "Dr. Sunil Silva"] # Default නිදසුන්
if 'tests' not in st.session_state:
    st.session_state.tests = [{"name": "FBS", "price": 500.0}, {"name": "Full Blood Count", "price": 1200.0}] # Default නිදසුන්
if 'saved_bills' not in st.session_state:
    st.session_state.saved_bills = []
if 'cancel_requests' not in st.session_state:
    st.session_state.cancel_requests = []

# --- Functions ---

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
                st.error("Invalid Credentials!")

def billing_dashboard():
    st.title("💳 Billing Dashboard")
    st.sidebar.write(f"User: **{st.session_state.current_user}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    tab1, tab2 = st.tabs(["📝 New Bill", "📂 Saved Bills"])

    with tab1:
        st.subheader("Patient Registration & Billing")
        col1, col2 = st.columns(2)
        
        with col1:
            salute = st.selectbox("Salute", ["Mr.", "Mrs.", "Mast.", "Miss", "Baby", "Baby of Mrs.", "Rev."])
            p_name = st.text_input("Patient Name")
            p_age = st.text_input("Age")
        
        with col2:
            p_mobile = st.text_input("Mobile Number")
            ref_doc = st.selectbox("Referral Doctor", options=st.session_state.doctors)
            
        st.divider()
        
        # Test selection
        test_names = [t['name'] for t in st.session_state.tests]
        selected_tests = st.multiselect("Select Tests", options=test_names)
        
        # Calculation
        total_amount = sum(t['price'] for t in st.session_state.tests if t['name'] in selected_tests)
        
        st.write(f"#### Total Amount: LKR {total_amount:.2f}")
        discount = st.number_input("Discount Amount (LKR)", min_value=0.0, value=0.0, step=10.0)
        final_amount = total_amount - discount
        st.success(f"### Final Amount: LKR {final_amount:.2f}")

        if st.button("Save & Generate Bill"):
            if p_name and selected_tests:
                bill_id = f"LC-{datetime.now().strftime('%y%m%d%H%M%S')}"
                bill_data = {
                    "bill_id": bill_id,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "patient": f"{salute} {p_name}",
                    "age": p_age,
                    "doctor": ref_doc,
                    "tests": selected_tests,
                    "total": total_amount,
                    "discount": discount,
                    "final": final_amount
                }
                st.session_state.saved_bills.append(bill_data)
                st.balloons()
                st.success(f"Bill {bill_id} saved successfully!")
            else:
                st.warning("Please fill Patient Name and select at least one Test.")

    with tab2:
        st.subheader("Saved Bills History")
        if not st.session_state.saved_bills:
            st.write("No bills found.")
        else:
            df_bills = pd.DataFrame(st.session_state.saved_bills)
            st.table(df_bills[["bill_id", "date", "patient", "final"]])
            
            for i, bill in enumerate(st.session_state.saved_bills):
                with st.expander(f"View Bill: {bill['bill_id']} - {bill['patient']}"):
                    bill_text = f"""
                    LIFE CARE LABORATORY
                    -----------------------
                    Bill ID: {bill['bill_id']}
                    Date: {bill['date']}
                    Patient: {bill['patient']}
                    Age: {bill['age']}
                    Doctor: {bill['doctor']}
                    -----------------------
                    Tests: {', '.join(bill['tests'])}
                    Total: LKR {bill['total']}
                    Discount: LKR {bill['discount']}
                    Final Amount: LKR {bill['final']}
                    -----------------------
                    Thank You!
                    """
                    st.text(bill_text)
                    st.download_button("Download Bill (.txt)", bill_text, file_name=f"{bill['bill_id']}.txt")

# --- (Admin Dashboard remains same as previous code) ---
def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    # ... (මුලින් ලබාදුන් Admin Dashboard කේතය මෙතැනට ඇතුළත් වේ)
    # පහසුව සඳහා Admin Dashboard කේතය මෙහි නැවත කෙටියෙන් දක්වමි
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    
    tab1, tab2, tab3 = st.tabs(["Users", "Doctors", "Tests"])
    with tab1: # User Admin
        new_u = st.text_input("User Name")
        new_p = st.text_input("Password")
        new_r = st.selectbox("Role", ["Admin", "Billing", "Technician"])
        if st.button("Add User"): st.session_state.users.append({"username":new_u, "password":new_p, "role":new_r})
    with tab2: # Doctor Admin
        new_d = st.text_input("Doctor Name")
        if st.button("Add Doctor"): st.session_state.doctors.append(new_d)
    with tab3: # Test Admin
        new_t = st.text_input("Test Name")
        new_pr = st.number_input("Price")
        if st.button("Add Test"): st.session_state.tests.append({"name":new_t, "price":new_pr})

# --- Main Logic ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.role == "Admin": admin_dashboard()
    elif st.session_state.role == "Billing": billing_dashboard()