import streamlit as st
from PIL import Image
import os

# 1. පිටුවේ මූලික සැකසුම් (Page Configuration)
st.set_page_config(
    page_title="Life Care LIMS", 
    page_icon="🔬",
    layout="centered"
)

# 2. පිවිසුම් පිටුව (Login Page Function)
def login():
    # රසායනාගාර ලෝගෝ එක ඇතුළත් කිරීම
    # 'logo.png' නමින් පින්තූරය ඔබේ ෆෝල්ඩරයේ තිබිය යුතුය
    if os.path.exists("logo.png"):
        logo = Image.open("logo.png")
        st.image(logo, width=200)
    else:
        st.info("💡 රසායනාගාර ලෝගෝ එක ඇතුළත් කිරීමට 'logo.png' ගොනුව ෆෝල්ඩරයට එක් කරන්න.")

    st.title("🔬 Life Care LIMS")
    st.subheader("Laboratory Information Management System")
    
    # Login Form එක සෑදීම
    with st.form("login_form"):
        st.markdown("### User Login")
        username = st.text_input("User Name")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Select Role", ["Admin", "Billing", "Technician", "Satellite"])
        
        submit = st.form_submit_button("Login")

        if submit:
            # සරල මුරපද පරීක්ෂාව (මුරපදය '123' ලෙස සකසා ඇත)
            if username != "" and password == "123":
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['username'] = username
                st.success(f"Welcome {username}! Loading {role} Dashboard...")
                st.rerun()
            else:
                st.error("පරිශීලක නාමය හෝ මුරපදය වැරදියි! (Password: 123)")

# 3. ප්‍රධාන පාලක පුවරුව (Main Dashboard Function)
def main_dashboard():
    role = st.session_state['role']
    username = st.session_state['username']
    
    # Sidebar එක සැකසීම
    st.sidebar.title("Navigation")
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", width=100)
    
    st.sidebar.write(f"Logged in as: **{username}**")
    st.sidebar.write(f"Role: **{role}**")
    
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    # එක් එක් Role එකට අදාළ දර්ශනය
    st.header(f"🚀 {role} Portal")
    st.divider()

    if role == "Admin":
        st.subheader("පද්ධති පරිපාලනය")
        col1, col2 = st.columns(2)
        with col1:
            st.button("Manage Users")
            st.button("View System Reports")
        with col2:
            st.button("Database Backup")
            st.button("Configuration Settings")

    elif role == "Billing":
        st.subheader("බිල්පත් කළමනාකරණය")
        patient_name = st.text_input("Patient Name")
        test_type = st.multiselect("Select Tests", ["FBS", "Lipid Profile", "Full Blood Count", "Urine Full Report"])
        if st.button("Generate Invoice"):
            st.success(f"Invoice generated for {patient_name}")

    elif role == "Technician":
        st.subheader("පරීක්ෂණ වාර්තා ඇතුළත් කිරීම")
        lab_id = st.text_input("Enter Lab ID")
        uploaded_file = st.file_uploader("Upload Machine Result (CSV/PDF)")
        if st.button("Submit Results"):
            st.info("Result submitted for verification.")

    elif role == "Satellite":
        st.subheader("සාම්පල ලියාපදිංචිය (Satellite Center)")
        st.text_input("Center Name")
        st.date_input("Collection Date")
        st.button("Register Sample Transfer")

# 4. පද්ධතිය ක්‍රියාත්මක කිරීම (Execution)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    main_dashboard()