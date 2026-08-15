# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
from datetime import datetime
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
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "cust_name" not in st.session_state: st.session_state.cust_name = ""
if "cust_mobile" not in st.session_state: st.session_state.cust_mobile = ""
if "cart_items" not in st.session_state: st.session_state.cart_items = []
if "form_counter" not in st.session_state: st.session_state.form_counter = 0

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
        st.title("🛒 புதிய பில் & எஸ்டிமேஷன்")
        st.markdown("---")
        
        # டேட்டாபேஸ் மூலம் ப்ராடக்ட் பட்டியலை எடுத்தல்
        conn = sqlite3.connect("happy_billing.db")
        cursor = conn.cursor()
        cursor.execute("SELECT product_name, price FROM products")
        products_db = cursor.fetchall()
        conn.close()
        
        product_dict = {str(p[0]).strip(): float(p[1]) for p in products_db} if products_db else {}

        # வாடிக்கையாளர் விவரங்கள்
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.cust_name = st.text_input("வாடிக்கையாளர் பெயர் (Customer Name)", value=st.session_state.cust_name)
        with col2:
            st.session_state.cust_mobile = st.text_input("மொபைல் எண் (Mobile Number)", value=st.session_state.cust_mobile)
            
        bill_type = st.selectbox("பில் வகை (Bill Type)", ["ESTIMATION", "INVOICE", "QUOTATION"])
        
        st.subheader("பொருட்களைத் தேர்ந்தெடுத்தல்")
        fc = st.session_state.form_counter
        
        search_query = st.text_input("🔍 பொருள் தேடல் (Search Product...)", key=f"search_box_{fc}")
        clean_query = search_query.strip().lower()
        
        matching_products = []
        if clean_query != "":
            for db_name, db_price in product_dict.items():
                if clean_query in db_name.lower():
                    matching_products.append((db_name, db_price))
                    
        forced_name = st.session_state.get(f"forced_prod_{fc}", "")
        
        if matching_products and not forced_name:
            st.info("📌 தொடர்புடைய பொருட்கள்:")
            cols = st.columns(min(len(matching_products), 3))
            for idx, (m_name, m_price) in enumerate(matching_products):
                col_idx = idx % 3
                if cols[col_idx].button(f"{m_name} (Rs.{m_price})", key=f"btn_match_{fc}_{idx}"):
                    st.session_state[f"forced_prod_{fc}"] = m_name
                    st.rerun()

        if forced_name:
            final_p_name = forced_name
            default_price = product_dict.get(final_p_name, 0.0)
        elif len(matching_products) == 1:
            final_p_name = matching_products[0][0]
            default_price = matching_products[0][1]
        elif search_query.strip() != "":
            final_p_name = search_query.strip()
            default_price = float(product_dict.get(final_p_name, 0.0))
        else:
            final_p_name = ""
            default_price = 0.0

        if final_p_name:
            st.success(f"தேர்ந்தெடுக்கப்பட்டது: **{final_p_name}** (விலை: Rs. {default_price})")
        else:
            st.warning("தேர்ந்தெடுக்கப்பட்ட பொருள்: **எதுவுமில்லை**")

        col_p2, col_p3, col_p4 = st.columns(3)
        with col_p2:
            price = st.number_input("விலை (Rs.)", min_value=0.0, value=float(default_price), step=1.0, key=f"price_{fc}")
        with col_p3:
            qty = st.number_input("அளவு (Qty)", min_value=1, value=1, step=1, key=f"qty_{fc}")
        with col_p4:
            discount = st.number_input("தள்ளுபடி (Disc.)", min_value=0.0, value=0.0, step=1.0, key=f"disc_{fc}")
            
        if st.button("பில்லில் சேர் (Add to Bill)", use_container_width=True):
            if final_p_name != "":
                tot = (price * qty) - discount
                if tot < 0: tot = 0
                st.session_state.cart_items.append([final_p_name, qty, price, discount, tot])
                
                if f"forced_prod_{fc}" in st.session_state:
                    del st.session_state[f"forced_prod_{fc}"]
                st.session_state.form_counter += 1
                st.success(f"'{final_p_name}' பில்லில் சேர்க்கப்பட்டது!")
                st.rerun()
            else:
                st.warning("⚠️ சரியான பொருளின் பெயரைத் தேர்ந்தெடுக்கவும்!")
                
        # கார்ட் பட்டியல்
        if st.session_state.cart_items:
            st.markdown("### 🛒 தற்போதைய பில் பொருட்கள்")
            
            display_data = []
            grand_total = 0
            for idx, item in enumerate(st.session_state.cart_items, 1):
                display_data.append([idx, item[0], f"Rs. {item[2]}", item[1], f"Rs. {item[3]}", f"Rs. {item[4]}"])
                grand_total += item[4]
                
            st.table(display_data)
            st.markdown(f"### **மொத்த தொகை (Grand Total): Rs. {grand_total}**")
            
            st.subheader("💳 பேமெண்ட் முறை")
            pay_mode = st.radio("வகை", ["Cash", "UPI", "Split"], horizontal=True)
            
            cash_amt = grand_total if pay_mode == "Cash" else (0 if pay_mode == "UPI" else grand_total // 2)
            upi_amt = 0 if pay_mode == "Cash" else (grand_total if pay_mode == "UPI" else grand_total - cash_amt)

            col5, col6 = st.columns(2)
            with col5:
                if st.button("பில்லை அழி (Clear)", use_container_width=True):
                    st.session_state.cart_items = []
                    st.session_state.cust_name = ""
                    st.session_state.cust_mobile = ""
                    st.session_state.form_counter += 1
                    st.rerun()
            with col6:
                if st.button("இன்வாய்ஸ் முடிக்க (Finish Bill)", use_container_width=True):
                    st.success("🎉 பில் வெற்றிகரமாக முடிக்கப்பட்டது!")
                    st.session_state.cart_items = []
                    st.session_state.cust_name = ""
                    st.session_state.cust_mobile = ""
                    st.session_state.form_counter += 1
                    st.rerun()

    elif menu == "📦 பொருட்கள் சேர்ப்பு (Products)":
        st.title("📦 புதிய பொருள் சேர்ப்பு")
        st.markdown("---")
        
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

        st.markdown("---")
        st.subheader("📋 தற்போதைய பொருட்கள் பட்டியல்")
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
        st.info("பில் ஹிஸ்டரி பகுதி விரைவில் இணைக்கப்படும்...")
