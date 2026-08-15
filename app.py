# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
from PIL import Image
import io

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
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', '1234')")
    
    # Products Table (Added image column as BLOB or text)
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
        st.title("🛒 புதிய பில் உருவாக்குதல்")
        st.info("பில்லிங் பகுதி விரைவில் இணைக்கப்படும்...")
        
    elif menu == "📦 பொருட்கள் சேர்ப்பு (Products)":
        st.title("📦 புதிய பொருள் சேர்ப்பு")
        st.markdown("---")
        
        # சேர்ப்பதற்கான வழியைத் தேர்ந்தெடுத்தல் (Manual அல்லது Photo)
        add_mode = st.radio("சேர்க்கும் முறை (Input Mode)", ["மேனுவல் என்ட்ரி (Manual Entry)", "புகைப்படம் மூலம் (Camera / Upload)"], horizontal=True)
        
        if add_mode == "மேனுவல் என்ட்ரி (Manual Entry)":
            with st.form("manual_product_form"):
                p_name = st.text_input("பொருளின் பெயர் (Product Name)")
                p_price = st.number_input("விலை (Price in Rs.)", min_value=0.0, step=1.0)
                p_stock = st.number_input("இருப்பு / ஸ்டாக் (Stock Qty)", min_value=0, step=1)
                
                submitted = st.form_submit_button("பொருளைச் சேமி (Save Product)", use_container_width=True)
                
                if submitted:
                    if p_name.strip() != "":
                        conn = sqlite3.connect("happy_billing.db")
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO products (product_name, price, stock) VALUES (?, ?, ?)", (p_name.strip(), p_price, p_stock))
                        conn.commit()
                        conn.close()
                        st.success(f"'{p_name}' வெற்றிகரமாகச் சேர்க்கப்பட்டது!")
                    else:
                        st.warning("தயவுசெய்து சரியான பொருளின் பெயரை உள்ளிடவும்!")
                        
        else:
            st.info("📷 மொபைல் கேமரா மூலம் புகைப்படம் எடுத்தோ அல்லது கேலரியில் இருந்தோ பொருளின் போட்டோவை இணைக்கலாம்.")
            
            # கேமரா அல்லது அப்லோட் ஆப்ஷன்
            img_source = st.radio("புகைப்பட மூலம்", ["கேமரா (Camera)", "கோப்பு பதிவேற்றம் (Upload Image)"], horizontal=True)
            
            captured_image = None
            if img_source == "கேமரா (Camera)":
                captured_image = st.camera_input("பொருளின் போட்டோ எடுக்கவும்")
            else:
                captured_image = st.file_uploader("பொருளின் போட்டோவைத் தேர்ந்தெடுக்கவும்", type=["jpg", "jpeg", "png"])
                
            with st.form("photo_product_form"):
                p_name_photo = st.text_input("பொருளின் பெயர் (Product Name)")
                p_price_photo = st.number_input("விலை (Price in Rs.)", min_value=0.0, step=1.0, key="photo_price")
                p_stock_photo = st.number_input("இருப்பு / ஸ்டாக் (Stock Qty)", min_value=0, step=1, key="photo_stock")
                
                submitted_photo = st.form_submit_button("புகைப்படத்துடன் சேமி (Save)", use_container_width=True)
                
                if submitted_photo:
                    if p_name_photo.strip() != "":
                        conn = sqlite3.connect("happy_billing.db")
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO products (product_name, price, stock) VALUES (?, ?, ?)", (p_name_photo.strip(), p_price_photo, p_stock_photo))
                        conn.commit()
                        conn.close()
                        
                        if captured_image:
                            st.image(captured_image, caption="சேமிக்கப்பட்ட பொருள் புகைப்படம்", width=150)
                            
                        st.success(f"'{p_name_photo}' புகைப்படம் மற்றும் விவரங்களுடன் வெற்றிகரமாகச் சேர்க்கப்பட்டது!")
                    else:
                        st.warning("தயவுசெய்து பொருளின் பெயரை உள்ளிடவும்!")

        # ஏற்கனவே உள்ள பொருட்கள் பட்டியல்
        st.markdown("---")
        st.subheader("📋 தற்போதைய பொருட்கள் பட்டியல் (Product List)")
        
        conn = sqlite3.connect("happy_billing.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, product_name, price, stock FROM products")
        all_products = cursor.fetchall()
        conn.close()
        
        if all_products:
            for prod in all_products:
                st.write(f"🔹 **{prod[1]}** | விலை: Rs. {prod[2]} | ஸ்டாக்: {prod[3]}")
        else:
            st.info("இதுவரை பொருட்கள் எதுவும் சேர்க்கப்படவில்லை.")
        
    elif menu == "📊 பில் வரலாறு (History)":
        st.title("📊 கடந்த கால பில்கள்")
        st.info("பில் ஹிஸ்டரி பகுதி இங்கே செயல்படும்...")
