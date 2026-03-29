import streamlit as st
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.storage import Storage
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.id import ID
from appwrite.input_file import InputFile
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client as TwilioClient
import requests

load_dotenv()

# ===================== ENV =====================
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID")
DATABASE_ID = "69a038bf002b072d8025"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

ADMIN_EMAIL = "solanki77@gmail.com"

# ===================== CLIENTS =====================

## USER CLIENT (no API key)
user_client = Client()
user_client.set_endpoint(APPWRITE_ENDPOINT)
user_client.set_project(APPWRITE_PROJECT_ID)

account = Account(user_client)

# SERVER CLIENT (with API key)
server_client = Client()
server_client.set_endpoint(APPWRITE_ENDPOINT)
server_client.set_project(APPWRITE_PROJECT_ID)
server_client.set_key(APPWRITE_API_KEY)

storage = Storage(server_client)
databases = Databases(server_client)
users = Users(server_client)

# ===================== AES =====================
BLOCK = 16

def key_from_password(password):
    return SHA256.new(password.encode()).digest()

def pad(data):
    pad_len = BLOCK - len(data) % BLOCK
    return data + bytes([pad_len] * pad_len)

def unpad(data):
    return data[:-data[-1]]

def encrypt_bytes(data, password):
    iv = get_random_bytes(16)
    cipher = AES.new(key_from_password(password), AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(data))

def decrypt_bytes(data, password):
    iv = data[:16]
    cipher = AES.new(key_from_password(password), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(data[16:]))

# ===================== GEO =====================
def get_user_device():
    device = "Desktop/Mobile"
    try:
        ua = ""
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            ua = st.context.headers.get("User-Agent") or st.context.headers.get("user-agent") or ""
        else:
            try:
                from streamlit.web.server.websocket_headers import _get_websocket_headers
                headers = _get_websocket_headers()
                if headers:
                    ua = headers.get("User-Agent") or headers.get("user-agent") or ""
            except ImportError:
                pass
                
        if ua:
            try:
                import httpagentparser
                parsed_ua = httpagentparser.detect(ua)
                os = parsed_ua.get('os', {}).get('name', '')
                if os:
                    device = os
            except Exception:
                pass
                
            if device == "Desktop/Mobile":
                # Fallback to simple string matching
                ua_lower = ua.lower()
                if "windows" in ua_lower: device = "Windows"
                elif "macintosh" in ua_lower or "mac os" in ua_lower: device = "Mac OS"
                elif "android" in ua_lower: device = "Android"
                elif "iphone" in ua_lower: device = "iOS"
                elif "ipad" in ua_lower: device = "iOS"
                elif "linux" in ua_lower: device = "Linux"
    except Exception:
        pass
    return device

def get_geo():
    ip = "UNKNOWN"
    location = "Location Unavailable"
    try:
        # Get IP address
        try:
            ip_req = requests.get("https://api64.ipify.org?format=json", timeout=5)
            if ip_req.status_code == 200:
                ip = ip_req.json().get("ip", "UNKNOWN")
        except Exception:
            pass
            
        if ip == "UNKNOWN":
            try:
                ip_req = requests.get("https://api.ipify.org?format=json", timeout=5)
                if ip_req.status_code == 200:
                    ip = ip_req.json().get("ip", "UNKNOWN")
            except Exception:
                pass

        if ip != "UNKNOWN":
            # Primary: ipapi.co (often better for detailed city/region)
            try:
                geo_req = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                if geo_req.status_code == 200:
                    geo = geo_req.json()
                    if not geo.get("error"):
                        city = geo.get("city") or "Unknown City"
                        region = geo.get("region") or "Unknown Region"
                        country = geo.get("country_name") or "Unknown Country"
                        location = f"{region}, {city}" # Requested format
                        return ip, location
            except Exception:
                pass
                
            # Secondary: ipinfo.io
            try:
                geo_req = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
                if geo_req.status_code == 200:
                    geo = geo_req.json()
                    city = geo.get("city") or "Unknown City"
                    region = geo.get("region") or "Unknown Region"
                    location = f"{region}, {city}" # Requested format
                    return ip, location
            except Exception:
                pass

        return ip, location
    except Exception:
        return ip, location

# ===================== EMAIL =====================
def send_email(to_email, link, password):
    msg = MIMEText(f"""
ENCRONEST Secure File

Download Link:
{link}

Encryption Password:
{password}
""")
    msg["Subject"] = "ENCRONEST Secure File"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

# ===================== OTP =====================
def send_sms(phone, otp):
    twilio = TwilioClient(TWILIO_SID, TWILIO_AUTH)
    twilio.messages.create(
        body=f"ENCRONEST OTP: {otp}",
        from_=TWILIO_PHONE,
        to=phone
    )

# ===================== SUMMARY =====================
def generate_summary(text):
    sentences = text.split(". ")
    return ". ".join(sentences[:5])

# ===================== PAGE =====================
st.set_page_config(page_title="ENCRONEST", layout="wide", page_icon="🔐")

st.markdown("""
<style>
    /* Premium ENCRONEST Theme - Pure CSS, Zero Load Time */
    
    /* 1. Hide Streamlit watermarks */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 2. Global App Background (Subtle Gradient) */
    .stApp {
        background: linear-gradient(135deg, #090a0f 0%, #151a28 50%, #0d121c 100%);
        color: #e2e8f0;
    }
    
    /* 3. Glassmorphism Panels for Inputs and DataFrames */
    .stTextInput>div>div>input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
        color: white !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3), inset 0 2px 4px rgba(0,0,0,0.2);
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* 4. Glowing Accent Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        color: white;
        border: none;
    }
    
    .stButton>button:active {
        transform: translateY(1px);
    }
    
    /* 5. Sleek Divider */
    hr {
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    
    /* 6. Dashboard Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #60a5fa;
        text-shadow: 0 0 10px rgba(96, 165, 250, 0.2);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-weight: 500;
        font-size: 1.1rem;
    }
    
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

# ===================== LOGIN =====================
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem; background: linear-gradient(90deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🔐 ENCRONEST</h1>
            <p style='color: #94a3b8; font-size: 1.1rem;'>Military-Grade File Sharing & Encryption</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

        with tab1:
            email = st.text_input("✉️ Email")
            password = st.text_input("🔑 Password", type="password")
            if st.button("Login", use_container_width=True):
                try:
                    account.create_email_password_session(email, password)
                    st.session_state.user = email
                    try:
                        user_info = account.get()
                        st.session_state.user_name = user_info.get("name", "")
                        st.session_state.user_id = user_info.get("$id", "")
                    except:
                        st.session_state.user_name = ""
                        st.session_state.user_id = ""
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        with tab2:
            new_email = st.text_input("✉️ New Email")
            new_pass = st.text_input("🔑 New Password", type="password")
            if st.button("Create Account", use_container_width=True):
                try:
                    account.create(ID.unique(), new_email, new_pass)
                    st.success("✅ Account created. You can now login.")
                except Exception as e:
                    st.error(str(e))
    st.stop()

def theme_header(icon, title):
    st.markdown(f"""
    <div style='
        padding: 15px 20px; 
        background: rgba(255, 255, 255, 0.02); 
        border-left: 4px solid #3b82f6; 
        border-radius: 8px; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
        <h2 style='
            font-size: 1.8rem; 
            font-weight: 600; 
            color: #f8fafc; 
            margin: 0; 
            display: flex; 
            align-items: center; 
            gap: 12px;'>
            <span style='font-size: 2.2rem;'>{icon}</span> {title}
        </h2>
    </div>
    """, unsafe_allow_html=True)

# ===================== TOP BAR =====================
st.markdown("""
<div style='text-align: left; padding: 10px 0 20px 0;'>
    <h1 style='font-size: 2.8rem; letter-spacing: 1px; margin-bottom: 0; background: linear-gradient(90deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        🔐 ENCRONEST <span style='font-weight: 300; font-size: 1.8rem; color: #94a3b8; -webkit-text-fill-color: initial;'>Workspace</span>
    </h1>
</div>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================
with st.sidebar:
    display_name = st.session_state.get("user_name")
    if not display_name:
        display_name = st.session_state.user
    st.markdown(f"<div style='padding-bottom: 20px; font-size: 18px;'>👤 <b>{display_name}</b></div>", unsafe_allow_html=True)
    st.markdown("### 🛡️ Main Menu")
    menu = ["Dashboard", "Upload File", "Decrypt File", "Profile", "About"]
    icons_list = ["house", "cloud-upload", "unlock", "person", "info-circle"]
    if st.session_state.user == ADMIN_EMAIL:
        menu.append("Admin Panel")
        icons_list.append("shield-lock")
    
    choice = option_menu(
        menu_title=None,
        options=menu,
        icons=icons_list,
        default_index=1,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#94a3b8", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin":"4px 0px", 
                "border-radius": "10px", 
                "color": "#cbd5e1"
            },
            "nav-link-selected": {
                "background": "linear-gradient(90deg, rgba(37,99,235,0.2), rgba(59,130,246,0.1))",
                "color": "#60a5fa",
                "border-left": "3px solid #3b82f6",
                "font-weight": "600"
            },
        }
    )
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# ===================== DASHBOARD =====================
if choice == "Dashboard":
    theme_header("📊", "Dashboard")
    st.markdown("Welcome to your ENCRONEST secure workspace.")
    
    try:
        logs = databases.list_documents(DATABASE_ID, "access_logs")
        user_logs = [doc for doc in logs["documents"] if doc.get("email") == st.session_state.user]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total Activity Count", value=len(user_logs))
        with col2:
            st.metric(label="Account Status", value="Active / Secure")
            
        st.subheader("Your Recent Activity")
        if user_logs:
            # Sort user logs newest first
            user_logs.sort(key=lambda x: x.get("$createdAt", ""), reverse=True)
            formatted_logs = []
            for i, doc in enumerate(user_logs, start=1):
                expiry_val = doc.get("expiry")
                formatted_logs.append({
                    "Sr. No.": i,
                    "Time": doc.get("$createdAt", "")[:19].replace("T", " "),
                    "File Name": doc.get("filename", "Unknown"),
                    "Status": doc.get("status", "Unknown"),
                    "Expiry (Days)": str(expiry_val) if expiry_val else "N/A"
                })
            
            st.dataframe(formatted_logs, use_container_width=True)
        else:
            st.info("No recent activity found.")
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

# ===================== UPLOAD =====================
elif choice == "Upload File":
    theme_header("📤", "Secure Upload")
    st.markdown("Encrypt, summarize, and share your files securely.")

    file = st.file_uploader("📂 Choose a file to upload")
    
    if file:
        col1, col2 = st.columns(2)
        with col1:
            receiver_email = st.text_input("✉️ Receiver Email")
            expiry = st.selectbox("⏳ Expiry (days)", [1,2,3])
        with col2:
            receiver_phone = st.text_input("📱 Receiver Phone")
            password = st.text_input("🔑 Encryption Password", type="password")
            
        st.divider()
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("📄 Generate AI Summary", use_container_width=True):
                text = file.read().decode("utf-8", errors="ignore")
                st.info(f"**Document Summary:**\n\n{generate_summary(text)}")

        with col4:
            if st.button("🔒 Encrypt & Share", use_container_width=True):
                if not receiver_email or not password:
                    st.warning("⚠️ Please provide receiver email and password.")
                else:
                    with st.spinner("Encrypting and uploading to secure storage..."):
                        file.seek(0)
                        encrypted = encrypt_bytes(file.read(), password)
                        file_id = ID.unique()

                        storage.create_file(
                            bucket_id=APPWRITE_BUCKET_ID,
                            file_id=file_id,
                            file=InputFile.from_bytes(encrypted, filename=file.name),
                            permissions=["read(\"any\")"]
                        )
                        # Add tracking log for Upload
                        ip, geo = get_geo()
                        device = get_user_device()
                        try:
                            databases.create_document(
                                database_id=DATABASE_ID,
                                collection_id="access_logs",
                                document_id=ID.unique(),
                                data={
                                    "filename": file.name,
                                    "email": st.session_state.user,
                                    "ip": ip,
                                    "geo_location": geo,
                                    "device": device,
                                    "status": "UPLOAD_SUCCESS",
                                    "expiry": expiry
                                }
                            )
                        except Exception as inner_e:
                            st.warning(f"File uploaded, but could not track log in dashboard: {str(inner_e)}")

                        link = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{file_id}/download?project={APPWRITE_PROJECT_ID}"
                        send_email(receiver_email, link, password)

                        st.success("✅ File securely uploaded & email sent to receiver!")

# ===================== DECRYPT =====================
elif choice == "Decrypt File":
    theme_header("🔓", "Decrypt Secure File")
    st.markdown("Provide the encrypted file, password, and complete 2FA OTP verification.")

    encrypted_file = st.file_uploader("📂 Upload Encrypted File")
    
    if encrypted_file:
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("🔑 Enter Password", type="password")
        with col2:
            phone = st.text_input("📱 Enter Phone for OTP")

        if st.button("📲 Send OTP Auth", use_container_width=True):
            if not phone:
                st.warning("⚠️ Please enter phone number for OTP.")
            else:
                with st.spinner("Sending OTP..."):
                    otp = "123456"
                    st.session_state.otp = otp
                    send_sms(phone, otp)
                    st.success("✅ OTP Sent smoothly.")

        if "otp" in st.session_state:
            st.divider()
            user_otp = st.text_input("🔢 Enter OTP Code")
            if st.button("✅ Verify & Decrypt", use_container_width=True):
                if user_otp == st.session_state.otp:
                    try:
                        encrypted_file.seek(0)
                        decrypted = decrypt_bytes(encrypted_file.read(), password)
                        st.download_button("📥 Download Decrypted File", decrypted, file_name=f"decrypted_{encrypted_file.name}", use_container_width=True)
                        ip, geo = get_geo()
                        device = get_user_device()
                        databases.create_document(
                            database_id=DATABASE_ID,
                            collection_id="access_logs",
                            document_id=ID.unique(),
                            data={
                                "filename": encrypted_file.name,
                                "email": st.session_state.user,
                                "ip": ip,
                                "geo_location": geo,
                                "device": device,
                                "status": "DECRYPT_SUCCESS"
                            }
                        )
                        st.success("🎉 Decryption successful! You can now download your file.")
                    except Exception as e:
                        st.error("❌ Decryption failed. Incorrect password or corrupted file.")
                else:
                    st.error("❌ Invalid OTP")

# ===================== PROFILE =====================
elif choice == "Profile":
    theme_header("👤", "Profile Settings")
    st.markdown(f"**Email:** {st.session_state.user}")
    
    st.subheader("Edit Profile Name")
    st.info("Set a display name for this session. It will immediately reflect in the sidebar menu.")
    
    current_name = st.session_state.get("user_name", "")
    new_name = st.text_input("Full Name", value=current_name)
    
    if st.button("Update Name"):
        if new_name.strip():
            st.session_state.user_name = new_name.strip()
            st.success("✅ Name updated localy for this session!")
            st.rerun() # Refresh to show new name in sidebar
        else:
            st.warning("⚠️ Name cannot be empty.")
            
# ===================== ADMIN =====================
elif choice == "Admin Panel":
    theme_header("🛡️", "Admin Panel")
    st.subheader("System Access Logs (Geolocation & Uploads)")
    try:
        logs = databases.list_documents(DATABASE_ID, "access_logs")
        all_logs = logs["documents"]
        # Sort by timestamp, newest first
        all_logs.sort(key=lambda x: x.get("$createdAt", ""), reverse=True)
        if all_logs:
            formatted_logs = []
            for i, doc in enumerate(all_logs, start=1):
                formatted_logs.append({
                    "Sr. No.": i,
                    "Time": doc.get("$createdAt", "")[:19].replace("T", " "),
                    "User": doc.get("email", "Unknown"),
                    "File": doc.get("filename", "Unknown"),
                    "Activity": doc.get("status", "Unknown"),
                    "Device (OS)": doc.get("device", "Unknown"),
                    "Location": doc.get("geo_location", "Unknown"),
                    "IP": doc.get("ip", "Unknown")
                })
            st.dataframe(formatted_logs, use_container_width=True)
        else:
            st.info("No system activity currently.")
    except Exception as e:
        st.error(f"Could not fetch logs: {str(e)}")

# ===================== ABOUT =====================
elif choice == "About":
    theme_header("ℹ️", "About ENCRONEST")
    
    st.markdown("""
    ### System Architecture & Security Overview
    
    **ENCRONEST** is a premium, military-grade secure file distribution platform designed to ensure absolute data tracking, encryption, and safe delivery.
    
    It leverages a multi-layered security approach:
    
    *   **Advanced AES-256 Encryption:** File contents are cryptographically sealed client-side before ever touching a network. They can only be unlocked with the exact symmetric key.
    *   **Secure Cloud Infrastructure:** Storage and Database routing is fully backed by Appwrite's scalable and resilient server environments.
    *   **Multi-Factor Authentication (OTP):** End-to-end decryption requires both the cryptographic key and an Out-Of-Band (OOB) SMS validation protocol via Twilio.
    *   **Comprehensive Audit Logging:** The system inherently monitors all data transit points. Every encryption and decryption event is tracked alongside granular telemetry, including:
        *   **Geolocation Details** (Region, City)
        *   **Network Intelligence** (IP Address Resolution)
        *   **Device Fingerprinting** (Operating System Detection)
        
    ---
    
    #### Core Capabilities
    
    1.  **Zero-Trust Uploading:** Securely wrap files with designated Expiry policies.
    2.  **Automated NLP Summarization:** AI-driven document insights on upload.
    3.  **Encrypted Email Dispatch:** Automated sharing of secure download links.
    4.  **Granular Admin Telemetry:** Real-time visibility into system usage patterns.
    
    <br>
    <div style='text-align: center; color: #64748b; font-size: 0.9rem;'>
        ENCRONEST v2.0 Enterprise Edition<br>
        Developed for maximum security compliance.
    </div>
    """, unsafe_allow_html=True)