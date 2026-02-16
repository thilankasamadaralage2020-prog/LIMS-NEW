import streamlit as st

# පිටුවේ සැකසුම්
st.set_page_config(page_title="LIMS Dashboard", layout="centered")

# සරල Login පද්ධතියක් (පසුව මෙය Database එකකට සම්බන්ධ කළ හැක)
def login():
    st.title("🔬 Laboratory Information Management System")
    
    with st.form("login_form"):
        username = st.text_input("User Name")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Select Role", ["Admin", "Billing", "Technician", "Satellite"])
        submit = st.form_submit_button("Login")

        if submit:
            # සරල තහවුරු කිරීමක් (උදාහරණයක් ලෙස password එක '123' යැයි සිතමු)
            if username and password == "123":
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("වැරදි පරිශීලක නාමයක් හෝ මුරපදයක්!")

# Dashboard එක පෙන්වීම
def main_dashboard():
    role = st.session_state['role']
    st.sidebar.title(f"Welcome, {st.session_state['username']}")
    st.sidebar.write(f"Role: **{role}**")
    
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.header(f"{role} Dashboard")
    st.divider()

    # එක් එක් Role එකට අදාළ පහසුකම්
    if role == "Admin":
        st.write("පද්ධති කළමනාකරණය සහ වාර්තා බැලීම මෙතැනින් සිදු කරන්න.")
        st.button("Manage Users")
        st.button("View System Logs")

    elif role == "Billing":
        st.write("බිල්පත් නිකුත් කිරීම සහ මුදල් ගෙවීම් පරීක්ෂා කිරීම.")
        st.number_input("Enter Amount")
        st.button("Generate Invoice")

    elif role == "Technician":
        st.write("පරීක්ෂණ වාර්තා ඇතුළත් කිරීම (Lab Reports).")
        st.file_uploader("Upload Lab Results")
        st.button("Verify Sample")

    elif role == "Satellite":
        st.write("පිටත මධ්‍යස්ථාන වල සාම්පල ලියාපදිංචි කිරීම.")
        st.text_input("Patient Name")
        st.button("Register Sample")

# Session State පරීක්ෂාව
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    login()
else:
    main_dashboard()