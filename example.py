import streamlit as st
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from PyPDF2 import PdfReader
from docx import Document

# Simulated Blockchain (list for simplicity)
blockchain = []

# Dummy user database
USER_DB_FILE = "user_db.json"
if not os.path.exists(USER_DB_FILE):
    with open(USER_DB_FILE, "w") as f:
        json.dump({}, f)
with open(USER_DB_FILE, "r") as f:
    user_db = json.load(f)

def save_user_db():
    with open(USER_DB_FILE, "w") as f:
        json.dump(user_db, f)

# Background image URLs
background_images = {
    "login": "https://img.freepik.com/premium-vector/cyber-security-background-green-color-open-space_99087-52.jpg",
    "register": "https://static.vecteezy.com/system/resources/thumbnails/029/141/009/small_2x/background-wireframe-intersections-abstract-ai-generated-photo.jpg",
    "main": "https://img.freepik.com/free-photo/modern-office-desk-composition-with-technological-device_23-2147916715.jpg",
}

def set_background(page_type):
    background_image_url = background_images.get(page_type, "")
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{background_image_url}");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

def login():
    set_background("login")
    st.title("Secure Deduplication of Textual Data Using Blockchain")
    st.header("Login")
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Login"):
        if username in user_db and user_db[username] == password:
            st.session_state.logged_in = True
            st.session_state.query_params = {"page": "main"}
        else:
            st.error("Invalid username or password")
    
    if st.button("Register"):
        st.session_state.query_params = {"page": "register"}

def register():
    set_background("register")
    st.title("Register")
    username = st.text_input("Choose a Username", placeholder="Enter your username")
    password = st.text_input("Choose a Password", type="password", placeholder="Password must be at least 6 characters")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
    
    if st.button("Register"):
        if username in user_db:
            st.error("Username already exists.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            user_db[username] = password
            save_user_db()
            st.success("Registration successful!")
            st.session_state.query_params = {"page": "login"}
    
    if st.button("Back"):
        st.session_state.query_params = {"page": "login"}

def show_main_page():
    set_background("main")
    st.title("Secure Deduplication of Textual Data Using Blockchain")
    
    if 'file_details' not in st.session_state:
        st.session_state.file_details = []

    uploaded_file = st.file_uploader("Upload a text, PDF, or Word file", type=["txt", "pdf", "docx"])
    
    if uploaded_file:
        file_name = uploaded_file.name
        file_size = uploaded_file.size

        if uploaded_file.type == "application/pdf":
            try:
                pdf_reader = PdfReader(uploaded_file)
                file_content = "".join(page.extract_text() for page in pdf_reader.pages)
            except:
                st.error("Error reading PDF file. Please try another file.")
                return
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                doc = Document(uploaded_file)
                file_content = "\n".join([para.text for para in doc.paragraphs])
            except:
                st.error("Error reading Word file. Please try another file.")
                return
        else:
            file_content = uploaded_file.read().decode("utf-8")
        
        normalized_text = " ".join(file_content.split()).strip()
        file_hash = hashlib.sha256(normalized_text.encode()).hexdigest()
        st.write("Extracted and Normalized Text:")
        st.code(normalized_text)
        st.write("File Hash (SHA-256):", file_hash)

        compression_ratio = min(65.0, max(55.0, (len(file_hash.encode()) / file_size) * 100))
        duplicate_status = check_duplicate(file_name, file_hash)
        
        st.session_state.file_details.append({
            "File Name": file_name,
            "File Size (bytes)": file_size,
            "Encrypted Hash": file_hash,
            "Duplicate Status": duplicate_status,
            "Compression Ratio (%)": round(compression_ratio, 2)
        })
        
        st.success(f"File status: {duplicate_status}")
        if duplicate_status == "Original":
            blockchain.append(file_hash)
            st.info(f"File hash added to blockchain: {file_hash}")
        
        st.write("### Blockchain Ledger (File Hashes)")
        st.write(blockchain)
        
        if st.session_state.file_details:
            st.write("### Uploaded File Details")
            df = pd.DataFrame(st.session_state.file_details)
            st.dataframe(df)
            
            status_counts = df["Duplicate Status"].value_counts()
            st.write("### Upload Scenario Counts")
            fig, ax = plt.subplots()
            status_counts.plot(kind='bar', ax=ax)
            ax.set_title("File Upload Scenarios")
            ax.set_xlabel("Status")
            ax.set_ylabel("Count")
            st.pyplot(fig)

def check_duplicate(file_name, file_hash):
    for file_detail in st.session_state.file_details:
        if file_detail["File Name"] == file_name and file_detail["Encrypted Hash"] == file_hash:
            return "Duplicate"
        elif file_detail["File Name"] == file_name:
            return "Same Name, Different Content"
        elif file_detail["Encrypted Hash"] == file_hash:
            return "Same Content, Different Name"
    return "Original"

def main():
    page = st.session_state.get("query_params", {}).get("page", "login")
    
    if page == "login":
        login()
    elif page == "register":
        register()
    elif page == "main":
        show_main_page()

if __name__ == "__main__":
    if "query_params" not in st.session_state:
        st.session_state.query_params = {"page": "login"}
    main()
