# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3

# பக்கத்தின் தலைப்பு மற்றும் வடிவமைப்பு
st.set_page_config(
    page_title="ஹாப்பி பில்லிங் மொபைல் வெர்ஷன்",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="expanded"
)

# டேட்டாபேஸ் மற்றும் டேபிள்களை உருவாக்குதல்
def init_db():
    conn = sqlite3.connect("happy_billing.db")
    cursor = conn.cursor()
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    # Default Admin
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', '1234')")
    
    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            price REAL,
            stock INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Session State பராமரிப்பு
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# லாகின் பக்கம்
def show_login():
    st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>📱 ஹாப்பி பில்லிங்</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Mobile Billing App</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("பயனர் பெயர் (Username)")
        password = st.text_input("பாஸ்வேர்டு (Password)", type="password")
        submit = st.form_submit_button("உள்நுழை (Login)", use_container_width=True)
        
        if submit:
            conn = sqlite3.connect("happy_billing.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("உள்நுழைவு வெற்றி!")
                st.rerun()
            else:
                st.error("தவறான பயனர் பெயர் அல்லது பாஸ்வேர்டு!")

# மெயின் ஆப் இயக்கம்
if not st.session_state.logged_in:
    show_login()
else:
    st.sidebar.title("⚡ ஹாப்பி பில்லிங்")
    st.sidebar.write(f"வணக்கம், **{st.session_state.username}**")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("மெனு (Menu)", ["🛒 புதிய பில் (Billing)", "📦 பொருட்கள் சேர்ப்பு (Products)", "📊 பில் வரலாறு (History)"])
    
    if st.sidebar.button("வெளியேறு (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
        
    # பக்கங்களின் இணைப்பு
    if menu == "🛒 புதிய பில் (Billing)":
        # billing.py-ல் உள்ள ஃபங்ஷனை இங்கு அழைக்கலாம்
        st.title("🛒 புதிய பில் உருவாக்குதல்")
        st.info("பில்லிங் பகுதி இங்கே செயல்படும்...")
        
    elif menu == "📦 பொருட்கள் சேர்ப்பு (Products)":
        st.title("📦 பொருட்கள் மேலாண்மை")
        st.info("புதிய பொருட்களைச் சேர்க்கும் பகுதி...")
        
    elif menu == "📊 பில் வரலாறு (History)":
        st.title("📊 கடந்த கால பில்கள்")
        st.info("பில் ஹிஸ்டரி பகுதி இங்கே செயல்படும்...")