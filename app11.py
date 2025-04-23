import streamlit as st
import datetime
import matplotlib.pyplot as plt
import pdfplumber
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
from datetime import datetime, timedelta
import io
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import re
import os
import dateparser
from datetime import datetime
import base64
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
import asyncio
import plotly.express as px
from PIL import Image
from googletrans import Translator
import pytesseract
import pickle
import numpy as np
from pathlib import Path
import hashlib
import pandas as pd



st.set_page_config(page_title="Invoice Processing App", layout="wide")

USER_DB = Path("user_db2.pkl")
if not USER_DB.exists():
    with open(USER_DB, 'wb') as f:
        pickle.dump({}, f)

def authenticate(username, password):
    # Load users from pickle file
    try:
        with open(USER_DB, "rb") as f:
            users = pickle.load(f)  # Expected to be a list of dictionaries
    except FileNotFoundError:
        print(f"User database '{USER_DB}' not found.")
        return False
    except Exception as e:
        print(f"Error loading user database: {e}")
        return False

    # Convert the list of users to a dictionary {username: hashed_password}
    user_dict = {user["username"]: user["password"] for user in users}

    # Check if username exists and password matches
    return user_dict.get(username) == hash_password(password)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---- ADDING BACKGROUND IMAGE ----
def get_base64_image(image_path):
    with open(image_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    return f"data:jpeg;base64,{encoded}"

def save_to_pickle(data):
    # Check if the pickle file exists
    if os.path.exists(USER_DB):
        # Load existing data
        with open(USER_DB, "rb") as file:
            try:
                existing_data = pickle.load(file)  # Load existing user data
            except EOFError:
                existing_data = []  # File exists but is empty
    else:
        existing_data = []  # No file exists, initialize an empty list

    # Ensure existing data is a list
    if not isinstance(existing_data, list):
        existing_data = []

        # Add new user to data
    existing_data.append(data)

    # Save updated data back to pickle file
    with open(USER_DB, "wb") as file:
        pickle.dump(existing_data, file)

# Function to check if username already exists
def is_username_taken(username):
    if os.path.exists(USER_DB):
        with open(USER_DB, "rb") as file:
            existing_data = pickle.load(file)
        return any(user["username"] == username for user in existing_data)
    return False

def is_valid_email(email):
    """Validate an email address using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "Landing"

def main():
    if st.session_state.page == "Landing":
        landing_page()
    elif st.session_state.page == "Signup":
        sign_up_page()
    elif st.session_state.page == "Login":
        login_page()
    elif st.session_state.page == "Home":
        app_pages()
    elif st.session_state.page == "mainpdf":
        pdf_extractor()
    elif st.session_state.page == "mainimage":
        img_extractor()
    elif st.session_state.page == "home":
        app_pages1()
    elif st.session_state.page == "main":
        main_app()
    elif st.session_state.page == "main1":
        main_app1()
    elif st.session_state.page == "product":
        product()
    elif st.session_state.page == "extract":
        Extractor()
    elif st.session_state.page == "generate":
        Generater()
    elif st.session_state.page == "Image":
        tem_dashboard()
    elif st.session_state.page == "Dashboard":
        chatBot()

def add_custom_css():
    st.markdown("""
    <style>
        body {
            text-align: center;
            background: linear-gradient(to right, #ff7e5f, #feb47b);  /* Gradient background */
            font-family: 'Poppins', sans-serif;
        }
        .stButton>button {
            text-align: center;
            background-color: linear-gradient(94.5deg, #F7A70D 0%, #FACA6E 73.52%, #F7A70D 106.59%);
            color: black;
            border-radius: 50%;
            font-size: 12px;
            transition: 0.3s ease;
            }
        .stButton>button:hover {
        text-align: center;
        }
        .stTextInput>div>div>input {
            text-align: center;
            background-color: #fff;
            padding: 10px;
            border-radius: 10px;
            border-color: black;
            border: 1px solid #ff6f61;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            transition: 0.3s;
        }
        .stTextInput>div>div>input:focus {
            text-align: center;
            border-color: #ff6f61;
            box-shadow: 0 0 0 2px rgba(255, 111, 97, 0.4);
        }
        .stTextInput>div>div>input:hover {
            text-align: center;
            border-color: #ffffff;
            box-shadow: 0 0 0 2px rgba(255, 111, 97, 0.4);
        }
        .Title {
            text-align: center;
            text-align: center;
            font-size: 38px;
            color: black;
            font-weight: bold;
            padding-top: 50px;
        }
        div[data-testid="stTextInput"] label {
            color: black !important;
        }
        .Subheader {
            text-align: center;
            display: center;
            font-size: 18px;
            color: black;
            font-weight: 500;
            margin-bottom: 30px;
        }
        .form-container {
            display: center;
            text-align: center;
            background-color: black;
            padding: 40px;
            border-radius: 2px;
            box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            margin: 0 auto;
        }
        .stForm {
            text-align: center;
            display: center;
            border-color : black;
            flex-direction: row;
            align-items: center;
        }
        .form-container input {
            text-align: center;
            margin-bottom: 20px;
        }
        .white{
            color: black;
        }
        div[data-testid="stForm"] {
            border: 2px solid black !important;  /* Change 'red' to any color */
            border-radius: 10px;  /* Optional: Round the corners */
            padding: 10px;  /* Optional: Add some padding */
        }
    </style>
    """, unsafe_allow_html=True)

# Define the sign-up page function
def sign_up_page():
    image_base64 = get_base64_image("login_page1.png")  # Replace with your local image path
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


    col1,col2,col3 = st.columns(3)
    with col2:
        # Apply custom CSS styling
        add_custom_css()
        success = ""
        with st.form("signup_form"):
            st.markdown("<div class='Title'>✨ Create Your Account</div>", unsafe_allow_html=True)
            st.markdown("<div class='Subheader'>Join us today and enjoy the benefits!</div>", unsafe_allow_html=True)
            st.markdown(f"<div style ='color : black'>_____________________________________________________</div>",unsafe_allow_html=True)

            # Adding fields to the form
            # fname = st.text_input("First Name", max_chars=50, placeholder="Enter your first name")
            # lname = st.text_input("Last Name", max_chars=50, placeholder="Enter your last name")
            username = st.text_input("Username", max_chars=20, placeholder="Choose a unique username")
            email = st.text_input("Email", placeholder="example@gmail.com")
            password = st.text_input("Password", type="password", placeholder="Enter a secure password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            
            submit_button = st.form_submit_button("🚀 Sign Up")
            
            st.markdown("<div class='white'>Already have an account?</div>", unsafe_allow_html=True)

            login_page = st.form_submit_button("Login")

        if submit_button:
            # Validation checks
            if not (email and username and password):
                st.error("❗ All fields are required!")
            elif password != confirm_password:
                st.error("❗ Passwords do not match!")
            elif is_username_taken(username):  # Assuming you have a function to check if the username is already taken
                st.error("❗ Username already exists. Please choose another.")
            elif not is_valid_email(email):  # Assuming you have a phone number validation function
                st.error("❗ Invalid Email Id! Please enter in the format: example@gmail.com")
            else:
                # Hash the password and save the data
                user_data = {
                    "User_Name": username,
                    "Email Id": email,
                    "username": username,
                    "password": hash_password(password)  # Make sure to hash the password before storing
                }
                save_to_pickle(user_data)  # Save user data to your storage
                st.success("✅ Sign up successful! Your data has been saved.")
                st.warning(f"""
                                Remeber these feilds \n
                                **Username** : {username}
                                **Password** :  {password}
                            """)
                
                st.session_state.page = "Login"

                # Redirect to login page after successful registration
                # st.session_state.page = "Login"
                st.rerun()  # Call the login page function (replace with your actual login page)
        
        if login_page:
            st.session_state.page = "Login"
            st.rerun()        
    with col3:
        col1,col2,col3,col4 = st.columns(4)
        with col3:
            st.markdown("   ")
        with col2:
            st.markdown("   ")
        with col1:
            if st.button("🔙"):
                st.session_state.page = "Landing"
                st.rerun()
        with col4:
            st.markdown("   ")

def login_page():
    image_base64 = get_base64_image("login_page1.png")  # Replace with your local image path
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    col1,col2,col3 = st.columns(3)
    with col2:
        add_custom_css()

        # Create a form for sign-up inputs
        with st.form("login_form"):

            st.markdown("<div class='Title'>Sigin</div>", unsafe_allow_html=True)
            st.markdown("<div class='Subheader'>🔐 Enter your credentials to log in.</div>", unsafe_allow_html=True)
            st.markdown(f"<div style ='color : black'>_____________________________________________________</div>",unsafe_allow_html=True)

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submit_button = st.form_submit_button("Login")
            st.markdown("<div class='white'>Don't have an account?</div>", unsafe_allow_html=True)
            sign_up_page = st.form_submit_button("Sign Up")

        if submit_button:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Login successful! Welcome, {username}!")
                st.session_state.page = "Home"
            elif username == "":
                st.error("Please enter a username and Password.")
            else:
                st.error("Invalid username or password.")
        if sign_up_page:
            st.session_state.page = "Signup"
            st.rerun()
    
    with col3:
        col1,col2,col3,col4 = st.columns(4)
        with col3:
            st.markdown("   ")
        with col2:
            st.markdown("   ")
        with col1:
            if st.button("🔙"):
                st.session_state.page = "Landing"
                st.rerun()
        with col4:
            st.markdown("   ")

genai.configure(api_key="AIzaSyCfzJ_B-5Dv7LukfPcxr4urmNzzz4VqPGA")



model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

# Function to get AI response
def get_gemini_response(message):
    response = chat.send_message(message, stream=True)
    return ''.join([chunk.text for chunk in response])

def get_advertisement_ideas(product_name, category, budget, company_name):
    prompt = f"Provide advertisement ideas for a product named '{product_name}' in the '{category}' category with a marketing budget of {budget} from the company {company_name}."
    return get_gemini_response(prompt)
# Initialize the Google Translate API
translator = Translator()
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Map language names to language codes
language_mapping = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Hindi": "hi",
    "Chinese": "zh-cn",
    "Telugu": "te"
}

# Function to prepare input images
def input_image_setup1(uploaded_files):
    image_parts = []
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            byte_data = uploaded_file.getvalue()
            image_parts.append({
                "mime_type": uploaded_file.type,
                "data": byte_data,
                "image": image
            })
    return image_parts

def input_image_setup(uploaded_file):
    image_parts = []
    image = Image.open(uploaded_file)
    byte_data = uploaded_file.getvalue()
    image_parts.append({
        "mime_type": uploaded_file.type,
        "data": byte_data,
        "image": image
    })
    return image


# Function to extract predefined key points from the invoice
def extract_key_points(image):
    key_points_prompt = """
    You are an expert in understanding invoices.
    Please extract the following key points from the invoice:
    - product Name
    - product company
    - quantity
    - Invoice_No
    - Invoice Date
    - Unit_Price
    - Total price
    - Description Usage
    - How_to_Use
    - Customer_name
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([key_points_prompt, image])
    return response.text

def extract_key_points1(image, prompt):
    key_points_prompt = """
    You are an expert in understanding invoices.
    Please extract the following key points from the invoice:
    - Invoice Number
    - Invoice Date
    - Total Amount
    - Billed To
    - Selling company
    - Total Price
    - Unit Price
    - product Name
    - quantity
    - Due Date (if available)
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([key_points_prompt, image, prompt])
    return response.text

# Function to extract product details and quantities from the invoice
def extract_product_details(image, prompt):
    product_details_prompt = """
    Extract the following details about the products in the invoice:
    - Product Name
    - Quantity
    Provide the information in structured English, in the following format:
    Product Name: [Product Name], Quantity: [Quantity],
    product Name: [description],product Name: [item],Quantity: [Qty]
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([product_details_prompt, image, prompt])
    return response.text

async def detect_language_async(translator, text):
    return await translator.detect(text)

# Helper function to translate text
async def translate_text_async(translator, text, src, dest):
    return await translator.translate(text, src=src, dest=dest)

# Synchronous wrapper for the translation functionality
def translate_text(text, target_language):
    language_code = language_mapping.get(target_language, "en")
    async def translate_workflow():
        detected_language = (await detect_language_async(translator, text)).lang
        if detected_language != language_code:
            translated_text = (await translate_text_async(
                translator, text, src=detected_language, dest=language_code
            )).text
            return translated_text
        else:
            return text
    try:
        # Get or create the running event loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
        return loop.run_until_complete(translate_workflow())
    except RuntimeError:
        # Create a new event loop if the existing one is not usable
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        return new_loop.run_until_complete(translate_workflow())

# def translate_text(text, target_language):
#     language_code = language_mapping.get(target_language, "en")
#     detected_language = translator.detect(text).lang
#     if detected_language != language_code:
#         translated_text = translator.translate(text, src=detected_language, dest=language_code).text
#         return translated_text
#     else:
#         return text

def generate_product_quantity_pie_chart(products, quantities):
    fig, ax = plt.subplots(figsize=(8, 8))  # Adjust the size of the pie chart
    ax.pie(quantities, labels=products, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)  # Elegant colors
    ax.set_title('Products and Their Quantities', fontsize=16)  # Set title with larger font
    st.pyplot(fig)  # Display the plot
def categorize_invoice(translated_product_details):
    # Keywords for identifying products or services
    product_keywords = ["product", "item", "goods", "sale"]
    service_keywords = ["service", "consulting", "subscription", "maintenance"]

    # Check if the product details contain any keywords related to products or services
    for product in translated_product_details.lower().split("\n"):
        if any(keyword in product for keyword in product_keywords):
            return "Product Invoice"
        elif any(keyword in product for keyword in service_keywords):
            return "Service Invoice"
        
def categorize_status(translated_key_points):
    # Improved Due Date and Paid Status Detection
    # Look for terms that indicate due date or payment status
    due_date_keywords = ["due date", "payment due", "outstanding", "due",]
    payment_keywords = ["not available on the invoice" ,"paid", "payment completed", "settled", "finalized", "payment received"]

    # Check for specific phrases indicating no due date is mentioned
    no_due_date_phrases = [
        "not available on the invoice",
        "not mentioned",
        "no explicit due date mentioned",
        "Not specified on the invoice",
        "Not available on the provided invoice" 
    ]
    
    # If any of the phrases indicating "no due date" is found, consider the invoice as paid
    if any(phrase.lower() in translated_key_points.lower() for phrase in no_due_date_phrases):
        return "Paid"

    # Check if any of the due date or payment-related terms are found in translated key points
    is_due_date_found = any(keyword in translated_key_points.lower() for keyword in due_date_keywords)
    is_paid_found = any(keyword in translated_key_points.lower() for keyword in payment_keywords)

    # If payment-related terms are found, classify as "Paid"
    if not is_paid_found:
        return "Unpaid"
    
    # If no due date or payment term is found, classify as "Paid" (default behavior)
    if is_due_date_found:
        return "Unpaid"

    # If due date or outstanding terms are found, classify as "Unpaid"
    return "Paid"
    
# Function to generate the product-quantity bar chart
def generate_product_quantity_bar_chart(products, quantities):
    fig, ax = plt.subplots(figsize=(10, 6))  # Set the size of the plot
    ax.bar(products, quantities, color='skyblue')  # Bar chart color
    ax.set_xlabel('Product Name')
    ax.set_ylabel('Quantity')
    ax.set_title('Product Quantities')
    plt.xticks(rotation=45, ha='right')  # Rotate x labels to avoid overlap
    st.pyplot(fig)  # Display the plot

def highlight_box(content, color="lightblue"):
    st.markdown(
        f"""
        <div style="
            background-color: {color};
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-size: 16px;
            font-weight: bold;
            color: black;
        ">
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )

def add_custom_css1():
    # Add custom CSS styles for centering and additional formatting
    st.markdown(
        """
        <style>
        
        .centered-content {
            text-align: center;
            font-size: 18px;
            line-height: 1.6;
        }
        .subheader {
            text-align : center;
            font-size : 28px;
            font-weight: bold;
        }
        .subheader1 {
            color : red;
            text-align : center;
            font-size : 28px;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Define the landing page function
def landing_page():

    st.markdown(
    """
        <style>
            /* Align the tab container to the right */
            div[data-baseweb="tab-list"] {
                display: flex;
                justify-content: flex-end;  /* Aligns tabs to the right */
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 5px;
            }

            /* Style each tab */
            div[data-baseweb="tab"] {
                font-size: 16px;
                font-weight: bold;
                color: black;
                padding: 10px 20px;
                border-radius: 5px;
                margin-left: 10px;  /* Adds spacing between tabs */
            }

            /* Active tab styling */
            div[data-baseweb="tab"][aria-selected="true"] {
                background-color: #ff4b4b;
                color: white;
            }

            /* Hover effect */
            div[data-baseweb="tab"]:hover {
                background-color: #ffb3b3;
            }
            .stButton>button {
            text-align: center;
            background-color: white;
            color: black;
            border-radius: 50%;
            font-size: 12px;
            transition: 0.3s ease;
            }
            .stButton>button:hover {
            text-align: center;
            background-color: lightgreen;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1,col2,col3,col4,col5,col6,col7,col8 = st.columns(8)
    with col1:
        st.markdown("   ")
    with col2:
        st.markdown("   ")
    with col3:
        st.markdown("   ")
    with col4:
        st.markdown("   ")
    with col5:
        st.markdown("   ")
    with col6:
        st.markdown("   ")
    with col7:
        st.markdown("   ")
    with col8:
        col1,col2 = st.columns(2)
        with col1:
            if st.button("signup"):
                st.session_state.page = "Signup"
                st.rerun()
        with col2:
            if st.button("signin"):
                st.session_state.page = "Login"
                st.rerun()

    st.markdown("<h1 style='text-align: center; color: red;'>Welcome to Invoice Extractor</h1>", unsafe_allow_html=True)
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
                add_custom_css1()
                st.markdown("   ")
                st.markdown("   ")
                st.markdown("   ")
                st.markdown("   ")
                st.markdown("   ")
                st.markdown("   ")
                st.markdown("<div class='subheader'>Simplify Your Invoice Management Process!</div>", unsafe_allow_html=True)
                st.markdown("   ")
                st.markdown(
                    """
                    <div class='centered-content'>
                        Are you tired of manually processing invoices? Say goodbye to endless hours of data entry and human errors! 
                        With Invoice Extractor, you can effortlessly extract, organize, and manage invoice data with just a few clicks.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        with col2:
            st.image("invoicce 1.jpg")
        # st.markdown("---")
        # st.header("Welcome to Invoice Extractor")
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            st.image("invoice 3.png")
        with col2:
            add_custom_css1()
            st.markdown("   ")
            st.markdown("   ")
            st.markdown("   ")        
            st.markdown("<div class='subheader'>Why Choose Invoice Extractor</div>",unsafe_allow_html=True)
            # st.markdown("---")
            # st.subheader("Why Choose Invoice Extractor?")
            st.markdown("""
            1. Effortless Automation: Streamline your invoicing process with cutting-edge OCR and AI technology.
            2. Multi-Format Compatibility: Extract data from PDFs, scanned documents, emails, and more.
            3. 99% Accuracy: Minimize errors and ensure consistent, reliable data every time.
            4. Fast & Efficient: Process thousands of invoices in minutes and boost your productivity.
            5. Seamless Integration: Sync effortlessly with your accounting, ERP, and CRM systems.
            """)
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            add_custom_css1()
            points = [
                ("✔","Automatic Data Capture: Extract key details like invoice number, date, total amount, and more."),
                ("✔","Custom Field Mapping: Tailor the extraction process to suit your business needs."),
                ("✔","Smart Validation: Ensure data integrity with built-in error-checking."),
                ("✔","Cloud-Based Access: Work anytime, anywhere with secure cloud storage."),
                ("✔","Multi-Language Support: Process invoices in various languages effortlessly.")
            ]
            # Display the points with styled colors
            st.markdown("   ")
            st.markdown("   ")
            
            st.markdown("<div class='subheader'>Invoice Extractor Features</div>",unsafe_allow_html=True)
            # st.markdown("---")
            for text, test in points:
                st.markdown(f"<p style='font-size: 18px;'><span style='color: purple; font-size : 22px;'>{text}</span> {test}</p>", unsafe_allow_html=True)
        with col2:
            st.image("invoice 1.png")
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    st.markdown("   ")
    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            st.image("invoice 4.jpg")
        with col2:
            add_custom_css1()
            st.markdown("   ")
            st.markdown("   ")
            st.markdown("   ")
            st.markdown("   ")
            st.markdown("<div class='subheader'>📌 AI-Powered Invoice Processing with OCR</div>",unsafe_allow_html=True)
            st.markdown("""<div class='centered-content'>
                                <h2 style="font-size: 18px;">Automate Invoice Management & Reduce Manual Work</h2>
                                Tired of manually processing invoices? Our AI-powered OCR (Optical Character Recognition) solution extracts key data from invoices with high accuracy, helping businesses automate workflows, reduce errors, and save time.
                            </div> 
                        """,unsafe_allow_html=True)


def save_to_pickle1(data):
    username = st.session_state.username
    # Check if the pickle file exists
    if os.path.exists(f"{username}.pkl"):
        # Load existing data
        with open(f'{username}.pkl', "rb") as file:
            try:
                existing_data = pickle.load(file)  # Load existing user data
            except EOFError:
                existing_data = []  # File exists but is empty
    else:
        existing_data = []  # No file exists, initialize an empty list

    # Ensure existing data is a list
    if not isinstance(existing_data, list):
        existing_data = []

        # Add new user to data
    temp = 0
    for item in existing_data:
        if item['Id'] == data['Id']:
            temp = temp + 1
    
    if temp == 0:
        existing_data.append(data)

    # Save updated data back to pickle file
    with open(f'{username}.pkl', "wb") as file:
        pickle.dump(existing_data, file)


def answer_user_question_directly(image, user_prompt):
        try:
            dynamic_answer_prompt = f"""
            Here is an invoice. Provide a response to the user's query based on this image content:
            User Query: {user_prompt}
            """
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([dynamic_answer_prompt, image])
            return response.text.strip()
        except Exception as e:
            return f"Error while answering the question: {str(e)}"
        
def add_custom_css11():
    st.markdown("""
    <style>
        body {
            text-align: center;
            background: linear-gradient(to right, #ff7e5f, #feb47b);  /* Gradient background */
            font-family: 'Poppins', sans-serif;
        }
        .stButton>button {
            text-align: center;
            background-color: linear-gradient(94.5deg, #F7A70D 0%, #FACA6E 73.52%, #F7A70D 106.59%);
            color: black;
            border-radius: 10%;
            font-size: 12px;
            transition: 0.3s ease;
            }
        .stButton>button:hover {
            text-align: center;
            background-color: lightgreen; 
        }
        .stTextInput>div>div>input {
            text-align: center;
            background-color: #fff;
            padding: 10px;
            border-radius: 10px;
            border-color: white;
            border: 1px solid #ff6f61;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            transition: 0.3s;
        }
        .stTextInput>div>div>input:focus {
            text-align: center;
            border-color: #ff6f61;
            box-shadow: 0 0 0 2px rgba(255, 111, 97, 0.4);
        }
        .stTextInput>div>div>input:hover {
            text-align: center;
            border-color: #ff6f61;
            box-shadow: 0 0 0 2px rgba(255, 111, 97, 0.4);
        }
        .Title {
            text-align: center;
            text-align: center;
            font-size: 24px;
            color: black;
            font-weight: bold;
            padding-top: 50px;
        }
        .para{
            text-align: center;
            text-align: center;
            font-size: 15px;
            color: black;
            font-weight: bold;
            padding-top: 10px;
        }
        div[data-testid="stTextInput"] label {
            color: white !important;
        }
        .Subheader {
            text-align: center;
            display: center;
            font-size: 18px;
            color: black;
            font-weight: 500;
            margin-bottom: 30px;
        }
        .form-container {
            display: center;
            text-align: center;
            background-color: black;
            padding: 40px;
            border-radius: 5px;
            box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            margin: 0 auto;
        }
        .stForm {
            text-align: center;
            display: flex;
            border-color : black;
            left-padding : 20px;
            flex-direction: row;
            align-items: center;
        }
        div[data-testid="stForm"] {
            border: 2px solid black !important;  /* Change 'red' to any color */
            border-radius: 40px;  /* Optional: Round the corners */
            box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1);
            transform: translateY(-10px);
        }div[data-testid="stForm"]:hover {
            background-color: #e0f7fa; /* Light cyan color */
            border: 2px solid black !important;  /* Change 'red' to any color */
            border-radius: 40px;  /* Optional: Round the corners */
            box-shadow: 10px 30px 50px rgba(0, 0, 0, 0.1);
            transform: translateY(-1px);
        }
    </style>
    """, unsafe_allow_html=True)


def main_app1():
    st.markdown("""
        <style>
        .css-1d391kg {background-color: #0e0e0e;}
        .block-container {padding: 2rem; border-radius: 10px; background-color: #fff;}
        .stButton button {border-radius: 8px; color: black;}
        </style>
        """, unsafe_allow_html=True)

    # In-memory invoice history stored in session state
    if "invoice_history" not in st.session_state:
        st.session_state.invoice_history = []

    # Updated PDF Generation Function with Template Styles
    def generate_invoice_pdf(invoice_data, logo, industry, item_label, theme_color, template_style):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Set style-specific parameters
        if template_style == "Modern":
            border_color = colors.HexColor(theme_color)
            title_font = "Helvetica-Bold"
            title_size = 20
            body_font = "Helvetica"
            body_size = 12
            border_width = 1.5
        elif template_style == "Classic":
            border_color = colors.black
            title_font = "Times-Bold"
            title_size = 22
            body_font = "Times-Roman"
            body_size = 12
            border_width = 1
        elif template_style == "Minimalist":
            border_color = None  # No border for a minimalist look
            title_font = "Helvetica"
            title_size = 18
            body_font = "Helvetica"
            body_size = 11
            border_width = 0
        else:
            # Fallback to Modern style if not matched
            border_color = colors.HexColor(theme_color)
            title_font = "Helvetica-Bold"
            title_size = 20
            body_font = "Helvetica"
            body_size = 12
            border_width = 1.5

        # Draw border if applicable
        if border_color and border_width:
            c.setStrokeColor(border_color)
            c.setLineWidth(border_width)
            c.rect(30, 30, width - 60, height - 60)

        # Add Logo if uploaded
        if logo is not None:
            c.drawImage(ImageReader(logo), 50, height - 100, width=100, height=50, mask='auto')

        # Set title
        c.setFont(title_font, title_size)
        c.drawString(200, height - 50, "INVOICE")

        # Business details (common)
        c.setFont(body_font, body_size)
        c.drawString(50, height - 120, invoice_data['business_name'])
        c.drawString(50, height - 140, invoice_data['business_address'])
        c.drawString(50, height - 160, invoice_data['business_phone'])
        c.drawString(50, height - 180, invoice_data['business_email'])

        # Starting vertical position for industry-specific info
        y_start = height - 220

        # Industry-specific sections
        if industry == "Medical Clinic":
            c.setFont(body_font, body_size)
            c.setFont(body_font, body_size)
            c.drawString(50, y_start, "Patient Information:")
            c.drawString(50, y_start - 20, f"Patient Name: {invoice_data.get('patient_name', '')}")
            c.drawString(50, y_start - 40, f"Patient ID: {invoice_data.get('patient_id', '')}")
            c.drawString(50, y_start - 60, f"Treatment: {invoice_data.get('treatment_details', '')}")
            y_start -= 80
        elif industry == "Construction":
            c.setFont(body_font, body_size)
            c.drawString(50, y_start, "Project Information:")
            c.drawString(50, y_start - 20, f"Project Name: {invoice_data.get('project_name', '')}")
            c.drawString(50, y_start - 40, f"Project Address: {invoice_data.get('project_address', '')}")
            c.drawString(50, y_start - 60, f"Contract Details: {invoice_data.get('contract_details', '')}")
            y_start -= 80
        elif industry == "E-Commerce & Retail":
            c.setFont(body_font, body_size)
            c.drawString(50, y_start, "Order Information:")
            c.drawString(50, y_start - 20, f"Order Number: {invoice_data.get('order_number', '')}")
            c.drawString(50, y_start - 40, f"Shipping Address: {invoice_data.get('shipping_address', '')}")
            y_start -= 60
        elif industry == "Freelancer":
            c.setFont(body_font, body_size)
            c.drawString(50, y_start, "Service Information:")
            c.drawString(50, y_start - 20, f"Project Description: {invoice_data.get('project_description', '')}")
            y_start -= 40

        # Buyer details (common to all industries)
        c.setFont(body_font, body_size)
        c.drawString(50, y_start, "Bill to:")
        c.drawString(50, y_start - 20, invoice_data['buyer_name'])
        c.drawString(50, y_start - 40, invoice_data['buyer_address'])
        c.drawString(50, y_start - 60, invoice_data['buyer_phone'])
        c.drawString(50, y_start - 80, invoice_data['buyer_email'])

        # Invoice info & Payment Details
        c.setFont(body_font, body_size)
        c.drawString(350, height - 120, f"Invoice #: {invoice_data['invoice_number']}")
        c.drawString(350, height - 140, f"Invoice Date: {invoice_data['invoice_date']}")
        c.drawString(350, height - 160, f"Payment Due: {invoice_data['payment_due']}")
        c.drawString(350, height - 180, f"Payment Method: {invoice_data['payment_method']}")
        c.drawString(350, height - 200, f"Payment Link: {invoice_data['payment_link']}")

        # Table Header for items
        table_y_start = y_start - 110
        c.setFont(body_font, body_size)
        c.drawString(50, table_y_start, item_label)
        c.drawString(200, table_y_start, "Quantity")
        c.drawString(300, table_y_start, "Price per unit")
        c.drawString(450, table_y_start, "Amount")
        c.line(50, table_y_start - 5, 550, table_y_start - 5)

        # Table Data for items
        y = table_y_start - 25
        subtotal = 0
        for item in invoice_data["items"]:
            c.setFont(body_font, body_size)
            c.drawString(50, y, item["name"])
            c.drawString(200, y, str(item["quantity"]))
            c.drawString(300, y, f"{invoice_data['currency']} {item['price']:.2f}")
            c.drawString(450, y, f"{invoice_data['currency']} {item['total']:.2f}")
            subtotal += item["total"]
            y -= 20

        # Apply discount if provided
        discount_amount = 0
        if invoice_data["discount_type"] == "Percentage":
            discount_amount = subtotal * (invoice_data["discount"] / 100)
        elif invoice_data["discount_type"] == "Flat":
            discount_amount = invoice_data["discount"]

        # Additional charges (like shipping)
        additional_charges = invoice_data["additional_charges"]

        # Totals calculation
        c.setFont(body_font, body_size)
        c.drawString(350, y - 20, "Subtotal:")
        c.drawString(450, y - 20, f"{invoice_data['currency']} {subtotal:.2f}")

        c.drawString(350, y - 40, "Discount:")
        c.drawString(450, y - 40, f"- {invoice_data['currency']} {discount_amount:.2f}")

        c.drawString(350, y - 60, "Additional Charges:")
        c.drawString(450, y - 60, f"{invoice_data['currency']} {additional_charges:.2f}")

        tax = (subtotal - discount_amount + additional_charges) * (invoice_data["tax"] / 100)
        c.drawString(350, y - 80, f"Tax ({invoice_data['tax']}%):")
        c.drawString(450, y - 80, f"{invoice_data['currency']} {tax:.2f}")

        grand_total = subtotal - discount_amount + additional_charges + tax
        c.drawString(350, y - 100, "TOTAL:")
        c.drawString(450, y - 100, f"{invoice_data['currency']} {grand_total:.2f}")

        # Notes and Comments
        c.setFont("Helvetica", 10)
        c.drawString(50, y - 140, "Additional Notes:")
        c.setFont("Helvetica-Oblique", 10)
        text_obj = c.beginText(50, y - 155)
        for line in invoice_data["notes"].split("\n"):
            text_obj.textLine(line)
        c.drawText(text_obj)

        # QR Code integration: generate a QR code for the payment link
        if invoice_data["payment_link"]:
            qr = qrcode.QRCode(box_size=2, border=1)
            qr.add_data(invoice_data["payment_link"])
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            qr_img.save(buf, format='PNG')
            buf.seek(0)
            c.drawImage(ImageReader(buf), 400, y - 200, width=100, height=100)

        # Signature line
        c.line(400, y - 230, 550, y - 230)
        c.setFont("Helvetica", 10)
        c.drawString(420, y - 245, "Authorized Signature")

        c.save()
        buffer.seek(0)
        return buffer

    # --- Streamlit UI ---

    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col6:
            col7,col8,col9 = st.columns(3)
            with col9:
                if st.button("🔙"):
                    st.session_state.page = "Home"
                    st.rerun()

    st.title("🧾 Multi-Industry Invoice Generator")

    # Sidebar for Analytics & Invoice History
    with st.sidebar:
        st.header("Analytics & History")
        num_invoices = len(st.session_state.invoice_history)
        st.write(f"Total Invoices: {num_invoices}")
        total_revenue = sum(inv["grand_total"] for inv in st.session_state.invoice_history) if num_invoices else 0
        st.write(f"Total Revenue: {total_revenue}")
        if num_invoices > 0:
            st.subheader("Past Invoices")
            for inv in st.session_state.invoice_history:
                st.write(f"{inv['invoice_number']} - {inv['invoice_date']} - {inv['currency']} {inv['grand_total']:.2f}")

    # Invoice Customization options
    st.header("Customization Options")
    currency = st.selectbox("Select Currency", ["$", "€", "₹"])
    theme_color = st.color_picker("Select Theme Color", "#6200EA")
    template_style = st.radio("Template Style", ["Modern", "Classic", "Minimalist"])

    # Industry selection
    industry = st.selectbox("Select Industry", ["Medical Clinic", "Construction", "E-Commerce & Retail", "Freelancer"])

    # Dynamic label for item section
    if industry == "Freelancer":
        item_label = "Service"
    elif industry == "E-Commerce & Retail":
        item_label = "Item"
    else:
        item_label = "Item"

    # Upload Logo (Optional)
    st.header("Upload Company Logo (Optional)")
    logo = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg"])

    # Business Details (common for all industries)
    st.header("Business Information")
    business_name = st.text_input("Business Name")
    business_address = st.text_input("Business Address")
    business_phone = st.text_input("Business Phone")
    business_email = st.text_input("Business Email")

    # Industry-specific Fields
    if industry == "Medical Clinic":
        st.header("Patient Information")
        patient_name = st.text_input("Patient Name")
        patient_id = st.text_input("Patient ID")
        treatment_details = st.text_area("Treatment Details")
    elif industry == "Construction":
        st.header("Project Information")
        project_name = st.text_input("Project Name")
        project_address = st.text_input("Project Address")
        contract_details = st.text_area("Contract Details")
    elif industry == "E-Commerce & Retail":
        st.header("Order Information")
        order_number = st.text_input("Order Number")
        shipping_address = st.text_input("Shipping Address")
    elif industry == "Freelancer":
        st.header("Service Information")
        project_description = st.text_area("Project/Service Description")

    # Buyer Details (common)
    st.header("Buyer Information")
    buyer_name = st.text_input("Buyer Name")
    buyer_address = st.text_input("Buyer Address")
    buyer_phone = st.text_input("Buyer Phone")
    buyer_email = st.text_input("Buyer Email")

    # Invoice Details & Payment
    st.header("Invoice Details")
    invoice_number = st.text_input("Invoice Number")
    invoice_date = st.date_input("Invoice Date", datetime.today())
    payment_method = st.selectbox("Payment Method", ["Prepaid", "Cash on Delivery", "Bank Transfer"])
    if payment_method != "Cash on Delivery":
        payment_due = st.date_input("Payment Due Date", datetime.today().date() + timedelta(days=30))
    else:
        payment_due = "N/A"
    payment_link = st.text_input("Payment Link / Bank Details", "https://yourpaymentgateway.com/pay")

    # Items / Services / Products Section
    st.header("Items / Services / Products")
    num_items = st.number_input("Number of Entries", min_value=1, step=1, value=1)
    items = []
    for i in range(num_items):
        with st.expander(f"{item_label} {i+1} Details"):
            name = st.text_input(f"{item_label} {i+1} Name")
            quantity = st.number_input(f"{item_label} {i+1} Quantity", min_value=1, step=1, value=1)
            price = st.number_input(f"{item_label} {i+1} Price per unit", min_value=0.0, step=0.01, value=0.0)
            total = quantity * price
            items.append({"name": name, "quantity": quantity, "price": price, "total": total})

    # Discounts & Additional Charges
    st.header("Discounts & Additional Charges")
    discount = st.number_input("Discount (Enter value)", min_value=0.0, step=0.1, value=0.0)
    discount_type = st.radio("Discount Type", ["Percentage", "Flat"])
    additional_charges = st.number_input("Additional Charges (e.g., shipping)", min_value=0.0, step=0.1, value=0.0)

    # Tax & Additional Notes
    st.header("Additional Information")
    tax = st.number_input("Tax Percentage (%)", min_value=0.0, step=0.1, value=0.0)
    notes = st.text_area("Additional Notes / Comments", "Any extra information here.")

    # Validate required fields (simple demo)
    if not business_name or not invoice_number or not buyer_name:
        st.warning("Please fill in the required fields: Business Name, Invoice Number, and Buyer Name.")

    # Generate Invoice PDF Button
    if st.button("Generate Invoice PDF"):
        invoice_data = {
            "business_name": business_name,
            "business_address": business_address,
            "business_phone": business_phone,
            "business_email": business_email,
            "buyer_name": buyer_name,
            "buyer_address": buyer_address,
            "buyer_phone": buyer_phone,
            "buyer_email": buyer_email,
            "invoice_number": invoice_number,
            "invoice_date": str(invoice_date),
            "payment_due": str(payment_due),
            "payment_method": payment_method,
            "payment_link": payment_link,
            "items": items,
            "discount": discount,
            "discount_type": discount_type,
            "additional_charges": additional_charges,
            "tax": tax,
            "notes": notes,
            "currency": currency
        }

        # Append industry-specific data
        if industry == "Medical Clinic":
            invoice_data["patient_name"] = patient_name
            invoice_data["patient_id"] = patient_id
            invoice_data["treatment_details"] = treatment_details
        elif industry == "Construction":
            invoice_data["project_name"] = project_name
            invoice_data["project_address"] = project_address
            invoice_data["contract_details"] = contract_details
        elif industry == "E-Commerce & Retail":
            invoice_data["order_number"] = order_number
            invoice_data["shipping_address"] = shipping_address
        elif industry == "Freelancer":
            invoice_data["project_description"] = project_description

        pdf = generate_invoice_pdf(invoice_data, logo, industry, item_label, theme_color, template_style)

        # Calculate grand total for history (for demo)
        subtotal = sum(item["total"] for item in items)
        discount_amount = subtotal * (discount / 100) if discount_type == "Percentage" else discount
        grand_total = subtotal - discount_amount + additional_charges + ((subtotal - discount_amount + additional_charges) * (tax/100))
        invoice_data["grand_total"] = grand_total

        # Store invoice in history
        st.session_state.invoice_history.append(invoice_data)

        # Provide download button
        st.download_button(
            label="Download Invoice PDF",
            data=pdf,
            file_name="invoice.pdf",
            mime="application/pdf"
        )

def main_app():
    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col6:
            col7,col8,col9 = st.columns(3)
            with col9:
                add_custom_css11()
                if st.button("🔙"):
                    st.session_state.page = "Home"
                    st.rerun()

    st.header("Invoice Processing App")

    input_prompt = st.text_area(
        "Describe the task",
        value="You are an expert in understanding invoices. Extract data from invoices based on user questions.",
        key="task_description"
    )
    
    uploaded_files = st.file_uploader("Choose image(s)...", type=["jpg", "jpeg", "png","webp"], accept_multiple_files=True)

    # Language selection for translation
    target_language = st.selectbox(
        "Select the language to translate the invoice text for extraction:",
        options=list(language_mapping.keys()),
        index=0
    )
    
    submit = st.button("Process Invoices")

    # Handle submission
    if submit:
        if not uploaded_files:
            st.error("Please upload at least one image.")
        else:
            # Display the uploaded images
            
            data_to_store = ''
            User_info = Path("data.pkl")
            if not User_info.exists():
                with open(User_info, 'wb') as f:
                    pickle.dump({}, f)
            else:
                data_to_store = {
                    "uploaded_files": uploaded_files
                }
            with open(User_info, 'wb') as f:
                pickle.dump(data_to_store, f)

            # Prepare image data for Gemini API
            image_data = input_image_setup1(uploaded_files)

            # Process each file and collect responses
            extracted_data = []
            extracted_data1=[]
            for idx, image in enumerate(image_data):
                try:
                    # Extract key points (essential information) from the invoice
                    key_points_response = extract_key_points1(image['image'], input_prompt)
                
                    # Translate key points to the target language
                    key_points_response = translate_text(key_points_response, target_language)

                    # Translate key points to the English language
                    key_points_response1 = translate_text(key_points_response, "en")

                    # Extract product details and quantities
                    product_details_response = extract_product_details(image['image'], input_prompt)
                
                    # Translate product details to the English language
                    product_details_response1 = translate_text(product_details_response, "en")
                    
                    # Translate product details to the target language
                    product_details_response = translate_text(product_details_response, target_language)

                    category1 = categorize_invoice(product_details_response1)
                    status1 = categorize_status(key_points_response1)

                    category = translate_text(category1,target_language)
                    status = translate_text(status1,target_language)
                    
                    products = []
                    quantities = []

                    products1 = []
                    quantities1 = []

                    

                    for line in product_details_response1.splitlines():
                        if "Product Name:" in line and "Quantity:" in line:
                            parts = line.split(",")
                            product = parts[0].split(":")[1].strip()
                            quantity = int(parts[1].split(":")[1].strip())
                            product1 = translate_text(product,target_language)
                            quantity1 = translate_text(quantity,target_language)
                            
                            products.append(product1)
                            quantities.append(quantity1)

                            products1.append(product)
                            quantities1.append(quantity)

                    extracted_data.append({
                        "File Name": uploaded_files[idx].name,
                        "Key Points": key_points_response.strip(),
                        "Product Details": product_details_response.strip(),
                        "Categeory" : category,
                        "Status" : status
                    })
                    extracted_data1.append({
                        "File Name": uploaded_files[idx].name,
                        "Key Points": key_points_response.strip(),
                        "Key Points1": key_points_response1.strip(),
                        "target_language":target_language,
                        "Product Details": product_details_response.strip(),
                        "category" : category,
                        "status" : status,
                        "category1" : category1,
                        "status1" : status1,
                        "products" : products,
                        "quantities" : quantities,
                        "products1" : products1,
                        "quantities1" : quantities1
                    })
                except Exception as e:
                    extracted_data.append({
                        "File Name": uploaded_files[idx].name,
                        "Key Points": f"Error: {e}",
                        "Product Details": f"Error: {e}"
                    })
            # df = pd.DataFrame(extracted_data1)
            # st.table(df)        
            with open('user_db3.pkl','wb') as f:
                pickle.dump(extracted_data1,f)
            sucess = st.success("Uploaded Invoices are successfully Extracted ✅")
            if sucess:
                st.session_state.page = "Image"
                st.rerun()

    if st.button("Result"):
        st.session_state.page = "Image"
        st.rerun()

def Extractor():
    add_custom_css1()
    with st.container():
        sol1,sol2,sol3 = st.columns(3)
        with sol3:
            col7,col8,col9 = st.columns(3)
            with col9:
                add_custom_css11()
                if st.button("🔙"):
                    st.session_state.page = "Home"
                    st.rerun()
    
    with st.container():
        st.markdown("<div class='subheader'> Invoice Extractor </div>",unsafe_allow_html=True)
        st.markdown("<div class='centered-content'>An Invoice Generator is a tool designed to help businesses create professional, accurate invoices quickly and efficiently. It allows users to enter details such as the client’s name, contact information, services/products provided, payment terms, and total amount due. Many modern invoice generators offer customizable templates to ensure that the invoices align with a company’s branding. Users can easily generate invoices in various formats like PDF or Word, and some systems even provide features like automatic numbering, tax calculation, and payment reminders. This tool can be used by small businesses, freelancers, and large enterprises alike to manage their billing processes seamlessly.</div>",unsafe_allow_html=True)
        st.markdown("  ")
        st.markdown("  ")
        st.image('InvoExtract.jpg')
        st.markdown("  ")
        st.markdown("  ")
        st.markdown("<div style="'font-size:48px; text-align: left;'"> Features </div>",unsafe_allow_html=True)
        points = [
            ("Customizable Templates", "Choose from various templates to match your business’s brand or create your own."),
            ("Automatic Calculations", "Automatically calculate totals, taxes, discounts, and due dates to reduce errors."),
            ("Multiple Payment Methods", "Include payment instructions for different payment methods (e.g., bank transfer, PayPal)."),
            ("PDF Generation", "Export invoices as professional PDFs for easy emailing or printing."),
            ("Recurring Invoices"," Set up recurring billing for regular clients or subscriptions."),
            ("Tracking and Reminders", "Track sent invoices and get reminders for overdue payments.")
        ]

        for text, test in points:
            st.markdown(f"<p style='font-size: 18px; text-aligin : left;'><span style='color: black; font-size : 26px;'>{text}</span> : {test}</p>", unsafe_allow_html=True)
        
        st.markdown("<div style="'font-size:48px; text-align: left;'"> Benifits </div>",unsafe_allow_html=True)
        points = [
            ("Saves Time", "Automates the process of generating invoices, which reduces the time spent on manual calculations and formatting."),
            ("Reduces Errors", "Automatically calculates totals, taxes, and discounts, reducing the chance of human error."),
            ("Improves Professionalism", "Customizable templates and neat formatting give a professional look to your invoices."),
            ("Streamlines Billing", "Businesses can easily create and send invoices, making the billing cycle more efficient and organized.")
        ]
        for text, test in points:
            st.markdown(f"<p style='font-size: 18px; text-aligin : left;'><span style='color: black; font-size : 26px;'>{text}</span> : {test}</p>", unsafe_allow_html=True)
    with st.container():
        sol1,sol2,sol3 = st.columns(3)
        with sol2:
            if st.button("Extractor"):
                st.session_state.page = "Image"
                st.rerun()

def Generater():
    add_custom_css1()
    sol1,sol2,sol3 = st.columns(3)
    with sol3:
        col7,col8,col9 = st.columns(3)
        with col9:
            add_custom_css11()
            if st.button("🔙"):
                st.session_state.page = "Home"
                st.rerun()
    
    with st.container():
        st.markdown("<div class='subheader'> Invoice Generator </div>",unsafe_allow_html=True)
        st.markdown("<div class='centered-content'>An Invoice Generator is a tool designed to help businesses create professional, accurate invoices quickly and efficiently. It allows users to enter details such as the client’s name, contact information, services/products provided, payment terms, and total amount due. Many modern invoice generators offer customizable templates to ensure that the invoices align with a company’s branding. Users can easily generate invoices in various formats like PDF or Word, and some systems even provide features like automatic numbering, tax calculation, and payment reminders. This tool can be used by small businesses, freelancers, and large enterprises alike to manage their billing processes seamlessly.</div>",unsafe_allow_html=True)
        st.markdown("  ")
        st.markdown("  ")
        st.image('invoice 5.jpg')
        st.markdown("  ")
        st.markdown("  ")
        st.markdown("<div style="'font-size:48px; text-align: left;'"> Features </div>",unsafe_allow_html=True)
        points = [
            ("Customizable Templates", "Choose from various templates to match your business’s brand or create your own."),
            ("Automatic Calculations", "Automatically calculate totals, taxes, discounts, and due dates to reduce errors."),
            ("Multiple Payment Methods", "Include payment instructions for different payment methods (e.g., bank transfer, PayPal)."),
            ("PDF Generation", "Export invoices as professional PDFs for easy emailing or printing."),
            ("Recurring Invoices"," Set up recurring billing for regular clients or subscriptions."),
            ("Tracking and Reminders", "Track sent invoices and get reminders for overdue payments.")
        ]

        for text, test in points:
            st.markdown(f"<p style='font-size: 18px; text-aligin : left;'><span style='color: black; font-size : 26px;'>{text}</span> : {test}</p>", unsafe_allow_html=True)
        
        st.markdown("<div style="'font-size:48px; text-align: left;'"> Benifits </div>",unsafe_allow_html=True)
        points = [
            ("Saves Time", "Automates the process of generating invoices, which reduces the time spent on manual calculations and formatting."),
            ("Reduces Errors", "Automatically calculates totals, taxes, and discounts, reducing the chance of human error."),
            ("Improves Professionalism", "Customizable templates and neat formatting give a professional look to your invoices."),
            ("Streamlines Billing", "Businesses can easily create and send invoices, making the billing cycle more efficient and organized.")
        ]
        for text, test in points:
            st.markdown(f"<p style='font-size: 18px; text-aligin : left;'><span style='color: black; font-size : 26px;'>{text}</span> : {test}</p>", unsafe_allow_html=True)

    with st.container():
        sol1,sol2,sol3 = st.columns(3)
        with sol2:
            if st.button("Generater"):
                st.session_state.page = "main1"
                st.rerun()

def product():
    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col6:
            col7,col8,col9 = st.columns(3)
            with col9:
                add_custom_css11()
                if st.button("🔙"):
                    st.session_state.page = "Home"
                    st.rerun()

        # Load dataset
        df = pd.read_csv("invoices2.csv")

        # Convert 'Invoice Date' to datetime format
        df["Invoice Date"] = pd.to_datetime(df["Invoice Date"], errors="coerce")

        # Streamlit UI
        st.title("Product Insights Dashboard")

        # Step 1: Select Date Range
        date_options = ["Past 7 Days", "Past 30 Days", "Past 60 Days", "Past 90 Days", "All Time"]
        selected_range = st.selectbox("Select Date Range:", date_options)
        # selected_range = st.number_input("Select how many days ago",min_value=1,step=1)

        # Get the start date based on selection
        end_date = datetime(2025,2,24)
        # st.write(end)
        if selected_range == "Past 7 Days":
            start_date = end_date - timedelta(days=7)
        elif selected_range == "Past 30 Days":
            start_date = end_date - timedelta(days=30)
        elif selected_range == "Past 60 Days":
            start_date = end_date - timedelta(days=60)
        elif selected_range == "Past 90 Days":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = df["Invoice Date"].min()  # All-time data

        # Filter data by date
        filtered_df = df[(df["Invoice Date"] >= start_date) & (df["Invoice Date"] <= end_date)]

        # Step 2: Select Product Category
        categories = ["Laptop", "Mobile", "Printer", "Tablet", "TV", "AC", "Washing Machine", "Refrigerator"]
        selected_category = st.selectbox("Select a Product Category:", categories)

        # Filter data for the selected category


        category_df = filtered_df[filtered_df["Product_Name"].str.contains(selected_category, na=False)]

        st.table(category_df)

        # Step 3: Display Graph for Product Count
        if not category_df.empty:
            st.subheader(f"{selected_category} Sales Count ({selected_range})")

            # Count occurrences of each product in the selected category
            product_counts = category_df["Product_Name"].value_counts()
            max_count = product_counts.max()

            # Plot the bar chart
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(x=product_counts.index, y=product_counts.values, palette="viridis", ax=ax)
            ax.set_xlabel("Product Models")
            ax.set_ylabel("Number of Invoices")
            ax.set_title(f"{selected_category} Sales Count ({selected_range})")
            ax.set_xticklabels(product_counts.index, rotation=90)

            # Show plot in Streamlit
            st.pyplot(fig)

            # Step 4: Select Specific Product
            selected_product = st.selectbox("Select a Product:", product_counts.index)

            # Get product details
            product_info = category_df[category_df["Product_Name"] == selected_product].iloc[0]

            # Step 5: Display Product Details
            st.subheader(f"Details of {selected_product}")
            st.write(f"**Product Name:** {selected_product}")
            st.write(f"**Description:** {product_info['Description']}")
            st.write(f"**Usage:** {product_info['Usage']}")
            st.write(f"**How to Use:** {product_info['How_to_Use']}")

        else:
            st.warning(f"No products found in the selected category within {selected_range}.")

        selected_product1 = product_counts.get(f"{selected_product}", 0)  # Returns 0 if "LG" is not found
        percentage = ((selected_product1 / max_count) * 100).astype(int)
        st.subheader(f"Demand of {selected_product}: {percentage}%")
        # Define the percentage
        progress = ((selected_product1 / max_count) * 100)
        st.progress(progress/100)

        st.subheader(f"Frequency of {selected_product} in Invoices: {selected_product1}")

def img_extractor():
    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col6:
            col7,col8,col9 = st.columns(3)
            with col9:
                add_custom_css11()
                if st.button("🔙"):
                    st.session_state.page = "Home"
                    st.rerun()

    data = []
    data1=[]
    rfc = pickle.load(open('RFC.pkl','rb'))

    def preprocess(product_name,company,quantity,total_price):
                
        product_encoded = {
            ' Asus Laptop Asus': 1,
            ' Epson Printer Epson': 2,
            ' Samsung Mobile Samsung': 3,
            ' Samsung TV Samsung': 4,
            ' OnePlus Mobile OnePlus': 5,
            ' Samsung Printer Samsung': 6,
            ' Google Mobile Google': 7,
            ' Godrej Refrigerator Godrej': 8,
            ' Amazon Tablet Amazon': 9,
            ' Voltas AC Voltas': 10,
            ' Haier Refrigerator Haier': 11,
            ' Samsung Refrigerator Samsung': 12,
            ' LG Washing Machine LG': 13,
            ' LG Refrigerator LG': 14,
            ' Blue Star AC Blue Star': 15,
            ' Panasonic TV Panasonic': 16,
            ' Bosch Washing Machine Bosch': 17,
            ' Samsung Washing Machine Samsung': 18,
            ' Xiaomi Mobile Xiaomi': 19,
            ' Sony TV Sony': 20,
            ' TCL TV TCL': 21,
            ' HP Printer HP': 22,
            ' LG TV LG': 23,
            ' Whirlpool Refrigerator Whirlpool': 24,
            ' Whirlpool Washing Machine Whirlpool': 25,
            ' HP Laptop HP': 26,
            ' Apple Mobile Apple': 27,
            ' IFB Washing Machine IFB': 28,
            ' Lenovo Tablet Lenovo': 29,
            ' LG AC LG': 30,
            ' Microsoft Tablet Microsoft': 31,
            ' Brother Printer Brother': 32,
            ' Samsung AC Samsung': 33,
            ' Canon Printer Canon': 34,
            ' Dell Laptop Dell': 35,
            ' Apple Laptop Apple': 36,
            ' Apple Tablet Apple': 37,
            ' Daikin AC Daikin': 38,
            ' Lenovo Laptop Lenovo': 39,
            ' Samsung Tablet Samsung': 40
        }
        product_id = product_encoded.get(product_name, 40)

        company_encoded = {
            ' Asus': 1, ' Epson': 2, ' Samsung': 3, ' OnePlus': 4, ' Google': 5, 
            ' Godrej': 6, ' Amazon': 7, ' Voltas': 8, ' Haier': 9, ' LG': 10, 
            ' Blue Star': 11, ' Panasonic': 12, ' Bosch': 13, ' Xiaomi': 14, ' Sony': 15, 
            ' TCL': 16, ' HP': 17, ' Whirlpool': 18, ' Apple': 19, ' IFB': 20, 
            ' Lenovo': 21, ' Microsoft': 22, ' Brother': 23, ' Canon': 24, ' Dell': 25, 
            ' Daikin': 26
        }
        company_id = company_encoded.get(company, 26)

        return np.array([product_id,company_id,quantity,total_price]).reshape(1, -1)
    
    uploaded_file = st.file_uploader("Choose image(s)...", type=["jpg", "jpeg", "png","webp"])

    if uploaded_file:
        image = input_image_setup(uploaded_file)

        text = extract_key_points(image)

        if text:
            translated_details = text.split("\n") 
            
            for line in translated_details:
                try:
                    if "Product Name" in line:
                        product_name = line.split(":")[1].strip("**")
                    elif "Product Company" in line:
                        product_company = line.split(":")[1].strip("**")
                    # elif "Price" in line:
                    #     price = line.split(":")[1].strip("(This is the unit price)")
                    #     price = line.split(":")[1].strip("** (currency not specified in The invoice image, but it's likely the local currency)")
                    #     price = line.split(":")[1].strip("** (Currency not specified in the image, but likely Rupees (INR) given the seller's location)")
                    elif "Quantity" in line:
                        quantity = line.split(":")[1].strip("**")
                    elif "Invoice_No" in line:
                        invoice_no = line.split(":")[1].strip("**")
                    elif "Invoice Date" in line:
                        invoice_date = line.split(":")[1].strip("**")
                    elif "Unit_Price" in line:
                        Unit_Price = line.split(":")[1].strip("**")
                    elif "Total price" in line:
                        Total_price = line.split(":")[1].strip("**")
                    elif "Description Usage" in line:
                        Description_Usage = line.split(":")[1].strip("**")
                    elif "How_to_Use" in line:
                        How_to_Use = line.split(":")[1].strip("**")
                    elif "Customer_name" in line:
                        Customer_name = line.split(":")[1].strip("**")

                except Exception as e:
                    print(f"Error processing line '{line}': {e}")

            product_name1 = product_name + product_company        
            data.append({"product_name1" : product_name1,
                         "product_company": product_company,
                         "price":Total_price,
                         "quantity":quantity
                         
                    })
            
            data1.append({"Invoice_No":invoice_no,
                          "Invoice Date":invoice_date,
                          "product_name1" : product_name1,
                          "product_company": product_company,
                          "quantity":quantity,	
                          "Unit_Price":Unit_Price,
                          "Total price":Total_price,
                          "Description_Usage":Description_Usage,
                          "How_to_Use":How_to_Use,
                          "Customer_name":Customer_name
                    })
            st.table(data1)
            input = preprocess(product_name1,product_company,quantity,Total_price)
            rfc_pred = rfc.predict(input)

                # Load the CSV file
            file_path = "output.csv"  # Path to your uploaded file
            df1 = pd.read_csv(file_path)

            # User input for invoice number
            invoice_no1 = invoice_no.strip()
            # Check if Invoice_No exists
            if invoice_no1 in df1["Invoice_No"].astype(str).values:
                if rfc_pred == 1:
                    st.error("Invoice is Tampered")
                else:
                    st.success("Invoice is not Tampered")
                    df = pd.DataFrame(data1)
                    st.table(df)
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download CSV", csv, "invoice_data.csv", "text/csv")
            else:
                st.error("Invoice Tampered")
                

def pdf_extractor():
    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col6:
            col7,col8,col9 = st.columns(3)
            with col9:
                add_custom_css11()
                if st.button("🔙"):
                    st.session_state.page = "Home"
                    st.rerun()

    rfc = pickle.load(open('RFC.pkl','rb'))

    def preprocess(product_name,company,quantity,total_price):
                
        product_encoded = {
            'Asus Laptop Asus': 1,
            'Epson Printer Epson': 2,
            'Samsung Mobile Samsung': 3,
            'Samsung TV Samsung': 4,
            'OnePlus Mobile OnePlus': 5,
            'Samsung Printer Samsung': 6,
            'Google Mobile Google': 7,
            'Godrej Refrigerator Godrej': 8,
            'Amazon Tablet Amazon': 9,
            'Voltas AC Voltas': 10,
            'Haier Refrigerator Haier': 11,
            'Samsung Refrigerator Samsung': 12,
            'LG Washing Machine LG': 13,
            'LG Refrigerator LG': 14,
            'Blue Star AC Blue Star': 15,
            'Panasonic TV Panasonic': 16,
            'Bosch Washing Machine Bosch': 17,
            'Samsung Washing Machine Samsung': 18,
            'Xiaomi Mobile Xiaomi': 19,
            'Sony TV Sony': 20,
            'TCL TV TCL': 21,
            'HP Printer HP': 22,
            'LG TV LG': 23,
            'Whirlpool Refrigerator Whirlpool': 24,
            'Whirlpool Washing Machine Whirlpool': 25,
            'HP Laptop HP': 26,
            'Apple Mobile Apple': 27,
            'IFB Washing Machine IFB': 28,
            'Lenovo Tablet Lenovo': 29,
            'LG AC LG': 30,
            'Microsoft Tablet Microsoft': 31,
            'Brother Printer Brother': 32,
            'Samsung AC Samsung': 33,
            'Canon Printer Canon': 34,
            'Dell Laptop Dell': 35,
            'Apple Laptop Apple': 36,
            'Apple Tablet Apple': 37,
            'Daikin AC Daikin': 38,
            'Lenovo Laptop Lenovo': 39,
            'Samsung Tablet Samsung': 40
        }.get(product_name, 40)

        company_encoded = {
            'Asus': 1, 'Epson': 2, 'Samsung': 3, 'OnePlus': 4, 'Google': 5, 
            'Godrej': 6, 'Amazon': 7, 'Voltas': 8, 'Haier': 9, 'LG': 10, 
            'Blue Star': 11, 'Panasonic': 12, 'Bosch': 13, 'Xiaomi': 14, 'Sony': 15, 
            'TCL': 16, 'HP': 17, 'Whirlpool': 18, 'Apple': 19, 'IFB': 20, 
            'Lenovo': 21, 'Microsoft': 22, 'Brother': 23, 'Canon': 24, 'Dell': 25, 
            'Daikin': 26
        }.get(company, 26)

        return np.array([product_encoded,company_encoded,quantity,total_price]).reshape(1, -1)
    
    # Define the CSV headers
    headers = [
        "Invoice_No", "Invoice Date", "Product_Name", "Company", "Quantity", 
        "Unit_Price", "Total_Price", "Description", "Usage", "How_to_Use","Customer_name"
        ]

    # Function to extract invoice data
    def extract_invoice_data(text):
        invoices = []
        pattern = re.compile(
            r"Invoice ID: (\w+) Date: (\d{4}-\d{2}-\d{2})\n"
            r"Selling company: (.+?)\n"
            r"Customer Name: (.+?)\n"
            r"Product (.+?) (\d+) ([\d,]+) ([\d,]+)\n"
            r"How To Use: (.+?)\n"
            r"Usage: (.+?)\n"
            r"Description: (.+?)\n",
            re.DOTALL
        )
        
        matches = pattern.findall(text)
        for match in matches:
            invoice_no, date, company, Customer, product, quantity, unit_price, total_price, how_to_use, usage, description = match
                    
            lines = product.split("\n")  # Split by newline
            product1 = lines[1]  # Print the second line
            # print(product1)

            invoices.append([
                invoice_no, date,product1.strip(), company.strip(), quantity.strip(), 
                unit_price.replace(",", "").strip(), total_price.replace(",", "").strip(), 
                description.strip(), usage.strip(), how_to_use.strip(),Customer.strip()
            ])
            

        return invoices

    # Open the PDFs and extract text
    # Function to extract data from multiple PDFs
    def process_pdfs(uploaded_files):
        data = []
        with pdfplumber.open(uploaded_files) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    data.extend(extract_invoice_data(text))

        # Convert to Pandas DataFrame
        df = pd.DataFrame(data, columns=headers)
        return df

    # Streamlit UI
    st.title("Extract Invoice Data from PDFs")

    # Upload multiple PDFs
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf")

    if uploaded_files:
        df = process_pdfs(uploaded_files)

        if df.empty:
            st.error("Please Upload Valid Invoices")
        else:
            inputs = preprocess(df['Product_Name'].values[0],df['Company'].values[0],df['Quantity'].values[0],df['Total_Price'].values[0])
            rfc_pred = rfc.predict(inputs)

            # Load the CSV file
            file_path = "output.csv"  # Path to your uploaded file
            df1 = pd.read_csv(file_path)

            # User input for invoice number
            invoice_no = df["Invoice_No"].values[0]
            # Check if Invoice_No exists
            if invoice_no in df1["Invoice_No"].astype(str).values:
                if rfc_pred == 1:
                    st.error("Invoice is Tampered")
                else:
                    st.success("Invoice is not Tampered")
                    st.table(df)
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download CSV", csv, "invoice_data.csv", "text/csv")
                        # st.write(f"Extracted {len(df)} rows from {len(uploaded_files)} PDFs")
            else:
                st.error("Invoice Tampered")
                    
def app_pages():

    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col6:
            col8,col9 = st.columns(2)
            with col9:
                add_custom_css11()
                if st.button("👤"):
                    st.session_state.page = "home"
                    st.rerun()
                                
    tabs = st.tabs(["Home", "About", "Contact Us"])
    with tabs[0]:
        st.image('invoice1.png')
        with st.container():
            col1,col2,col3,col4 = st.columns(4)
            with col1:
                add_custom_css11()
                with st.form("Card1"):
                    st.markdown("<div class='Title'>Fraud Detection</div>",unsafe_allow_html=True)
                    image = Image.open('fraud.jpg')
                    resized_image = image.resize((700,350))
                    st.image(resized_image)
                    # st.markdown("<div class='para'style="'padding:10px;'"> Quickly and accurately extract key details from your invoices with our powerful Invoice Extractor. Save time, reduce manual effort, and streamline your data processing by automatically extracting important information like dates, amounts, and vendor details in seconds! </div>",unsafe_allow_html=True)
                    submit = st.form_submit_button('Image')
                    submit1 = st.form_submit_button('PDF')
                if submit:
                    st.session_state.page = "mainimage"
                    st.rerun()
                if submit1:
                    st.session_state.page = "mainpdf"
                    st.rerun()
            
            with col4:
                add_custom_css11()
                with st.form("Car,d4"):
                    st.markdown("<div class='Title'>Invoice Extractor</div>",unsafe_allow_html=True)
                    image = Image.open('InvoExtract.jpg')
                    resized_image = image.resize((700,350))
                    st.image(resized_image)
                    # st.markdown("<div class='para'style="'padding:10px;'"> Quickly and accurately extract key details from your invoices with our powerful Invoice Extractor. Save time, reduce manual effort, and streamline your data processing by automatically extracting important information like dates, amounts, and vendor details in seconds! </div>",unsafe_allow_html=True)
                    submit = st.form_submit_button('Readmore')
                    submit1 = st.form_submit_button('Extractor')
                if submit:
                    st.session_state.page = "extract"
                    st.rerun()
                if submit1:
                    st.session_state.page = "main"
                    st.rerun()
                        
            with col2:
                add_custom_css11()
                with st.form("Card2"):
                    st.markdown("<div class='Title' >Smart Product Insight</div>",unsafe_allow_html=True)
                    image = Image.open('InvoExtract.jpg')
                    resized_image = image.resize((700,350))
                    st.image(resized_image)
                    # st.markdown("<div class='para'style="'padding:30px;'"> Quickly and accurately extract key details from your invoices with our powerful Invoice Extractor. Save time, reduce manual effort, and streamline your data processing by automatically extracting important information like dates, amounts, and vendor details in seconds! </div>",unsafe_allow_html=True)
                    # submit = st.form_submit_button('Readmore') 
                    st.markdown(f"<div style = 'padding:30px; '></div>",unsafe_allow_html=True)     
                    submit1 = st.form_submit_button('Smart Product Insights')
                # if submit:
                #     st.session_state.page = "extract"
                #     st.rerun()
                if submit1:
                    st.session_state.page = "product"
                    st.rerun()
                        
            with col3:
                add_custom_css11()
                with st.form("Card3"):
                    st.markdown("<div class='Title'>Invoice Generator</div>",unsafe_allow_html=True)
                    # st.markdown(" ")
                    image = Image.open('invoice 5.jpg')
                    resized_image = image.resize((700,350))
                    st.image(resized_image)
                    # st.markdown(" ")
                    # st.markdown("<div class='para'> Effortlessly create and customize professional invoices in seconds with our easy-to-use generator. Save time, reduce errors, and streamline your billing process for a stress-free invoicing experience! </div>",unsafe_allow_html=True)
                    # st.markdown(" ")
                    submit = st.form_submit_button('Readmore')
                    submit1 = st.form_submit_button('Generator')
                if submit:
                    st.session_state.page = "generate"
                    st.rerun()
                if submit1:
                    st.session_state.page = "main1"
                    st.rerun()
        
        with st.container():
            st.markdown(
                """
                <style>
                .card {
                    background-color: rgb(144,238,144);
                    padding: 20px;
                    margin: 10px;
                    border-radius: 10px;
                    box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.2);
                    transition: box-shadow 0.3s ease, transform 0.3s ease;
                    transform: translateY(-10px);
                }

                .card:hover {
                    box-shadow: 50px 40px 60px rgba(225, 225, 225, 225);
                    transform: translateY(-1px);
                }

                .card-header {
                    font-size: 1.5em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }

                .card-body {
                    font-size: 1em;
                    color: #555;
                }
                .card-header1 {
                    font-size: 1.5em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }

                .card-body1 {
                    font-size: 1em;
                    color: #555;
                    padding : 20px;
                }

                </style>
                """, unsafe_allow_html=True
            )

            # Card 1
            with st.container():
                col1,col2,col3,col4 = st.columns(4)
                with col1:
                    st.markdown(f"""<div class="card">
                                <div class="card-header1">Invoice Data Entry</div>
                                <div class="card-body" style="font-size: 15px;">Streamline your accounting with accurate and automated invoice data entry, reducing manual effort.</div>
                                <div class="card-body1">Known More in About page</div>
                                </div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""<div class="card"><div class="card-header">Intelligent Invoice Processing Workflow</div>
                                <div class="card-body">Automate data capture, validation, and approval in a seamless, efficient workflow.</div>
                                <div class="card-body" ">Known More in About page</div>
                                </div>""", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""<div class="card"><div class="card-header">Automated Invoice Processing</div>
                                <div class="card-body">Enhance efficiency by automating invoice processing, reducing errors and speeding up workflows.</div>
                                <div class="card-body" ">Known More in About page</div>
                                </div>""", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""<div class="card"><div class="card-header1">Invoice OCR</div>
                                <div class="card-body">Leverage AI and OCR to extract and process invoice data with exceptional accuracy and speed.</div>
                                <div class="card-body1">Known More in About page</div>
                                </div>""", unsafe_allow_html=True)
                    
    with tabs[1]:
        st.markdown("<h1 style='text-align: center; color: red;'>About Us</h1>", unsafe_allow_html=True)
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                    add_custom_css1()
                    st.markdown("   ")
                    st.markdown("   ")
                    st.markdown("   ")
                    st.markdown("   ")
                    st.markdown("   ")
                    st.markdown("   ")
                    st.markdown("<div class='subheader'> Invoice Data Entry </div>", unsafe_allow_html=True)
                    st.markdown("   ")
                    st.markdown(
                        """
                        <div class='centered-content'>
                            Invoice Data Entry refers to the process of manually or automatically inputting invoice details (such as amounts, dates, item descriptions, and vendor information) into accounting or enterprise systems. Automated Invoice Data Entry solutions reduce human error, ensure consistency, and save time. With automated tools, invoices can be processed in bulk, and the data can be extracted directly from documents, entered into systems like ERP or accounting software, and even validated, which minimizes the need for manual intervention.   
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            with col2:
                st.image("invoicce 1.jpg")
            # st.markdown("---")
            # st.header("Welcome to Invoice Extractor")
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        with st.container():

            col1,col2 = st.columns(2)
            with col1:
                st.image("invoice 3.png")
            with col2:
                add_custom_css1()
                st.markdown("   ")
                st.markdown("   ")
                st.markdown("   ")
                # st.markdown("---")
                # st.subheader("Why Choose Invoice Extractor?")
                points = [
                    ("✔","Increased operational efficiency and faster invoice processing cycles."),
                    ("✔","Improved compliance and reduced manual intervention."),
                    ("✔","AI-driven insights that help to detect errors or fraud."),
                    ("✔","Flexible workflows for routing approvals based on predefined rules.")
                ]
                st.markdown("<div class='subheader'> Intelligent Invoice Processing Workflow </div>",unsafe_allow_html=True)
                for text, test in points:
                    st.markdown(f"<p style='font-size: 18px;'><span style='color: purple; font-size : 22px;'>{text}</span> {test}</p>", unsafe_allow_html=True)
                
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        with st.container():
            col1,col2 = st.columns(2)
            with col1:
                add_custom_css1()
                points = [
                    ("✔","Automatic Data Capture: Extract key details like invoice number, date, total amount, and more."),
                    ("✔","Custom Field Mapping: Tailor the extraction process to suit your business needs."),
                    ("✔","Smart Validation: Ensure data integrity with built-in error-checking."),
                    ("✔","Cloud-Based Access: Work anytime, anywhere with secure cloud storage."),
                    ("✔","Multi-Language Support: Process invoices in various languages effortlessly.")
                ]
                # Display the points with styled colors
                st.markdown("   ")
                st.markdown("   ")
                
                st.markdown("<div class='subheader'> Automated Invoice Processing </div>",unsafe_allow_html=True)
                # st.markdown("---")
                st.markdown(f"<div class='centered-content'>Automated Invoice Processing is the use of technology to automatically handle the complete invoicing cycle. This includes capturing invoice data, validating it, matching it against purchase orders, and sending invoices for approval and payment. The entire process eliminates manual data entry and validation, improving the speed and accuracy of processing. Using intelligent automation tools, businesses can ensure that invoices are processed on time and errors are reduced significantly.</div>", unsafe_allow_html=True)
            with col2:
                st.image("invoice 1.png")
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        with st.container():
            col1,col2 = st.columns(2)
            with col1:
                st.image("invoice 4.jpg")
            with col2:
                add_custom_css1()
                st.markdown("   ")
                st.markdown("   ")
                st.markdown("   ")
                st.markdown("   ")
                st.markdown("<div class='subheader'>📌 AI-Powered Invoice Processing with OCR</div>",unsafe_allow_html=True)
                st.markdown("""<div class='centered-content'>
                                    <h2 style="font-size: 18px;">Automate Invoice Management & Reduce Manual Work</h2>
                                    Tired of manually processing invoices? Our AI-powered OCR (Optical Character Recognition) solution extracts key data from invoices with high accuracy, helping businesses automate workflows, reduce errors, and save time.
                                </div> 
                            """,unsafe_allow_html=True)

        st.markdown("   ")
        st.markdown("   ")
        st.markdown("   ")
        with st.container():
            st.markdown("<h2 style='text-align: center; color: black;'>Get Started Today!</h1>", unsafe_allow_html=True)
            st.markdown(""" <div class="centered-content">
                        Say goodbye to manual invoice processing and experience the power of automation. Try [Your Website Name] today and take control of your financial operations effortlessly.
                        <div> """, unsafe_allow_html=True
                    )
            

    with tabs[2]:
        st.header("Contact Us")
        st.write("For queries, email us at support@example.com.")

def app_pages1():
    with st.sidebar:
        st.sidebar.title("👤 Account Menu")
        page5 = st.sidebar.radio("Go To", ["main","Home", "Dashboard & chatbot"])

        if page5 == "main":
            st.session_state.page = "home"
        elif page5 == "Home":
            st.session_state.page = "Home"
            st.rerun()
        elif page5 == "Dashboard & chatbot":
            st.session_state.page = "Dashboard"
            st.rerun()
        if st.button("logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.page = "Landing"
            st.rerun()
        if st.button('close'):
            st.session_state.page = "Home"
            st.rerun()
    
    st.image('invoice1.png')
    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            col3,col4 = st.columns(2)
            with col4:
                add_custom_css11()
                with st.form("Card1"):
                    st.markdown("<div class='Title'>Invoice Extractor</div>",unsafe_allow_html=True)
                    image = Image.open('InvoExtract.jpg')
                    resized_image = image.resize((700,350))
                    st.image(resized_image)
                    st.markdown("<div class='para'> Quickly and accurately extract key details from your invoices with our powerful Invoice Extractor. Save time, reduce manual effort, and streamline your data processing by automatically extracting important information like dates, amounts, and vendor details in seconds! </div>",unsafe_allow_html=True)
                    submit = st.form_submit_button('Readmore')
                    submit1 = st.form_submit_button('Extractor')
                if submit:
                    st.session_state.page = "extract"
                    st.rerun()
                if submit1:
                    st.session_state.page = "main"
                    st.rerun()
                    
        with col2:
            col3,col4 = st.columns(2)
            with col3:
                add_custom_css11()
                with st.form("Card2"):
                    st.markdown("<div class='Title'>Invoice Generator</div>",unsafe_allow_html=True)
                    st.markdown(" ")
                    image = Image.open('invoice 5.jpg')
                    resized_image = image.resize((700,350))
                    st.image(resized_image)
                    st.markdown(" ")
                    st.markdown("<div class='para'> Effortlessly create and customize professional invoices in seconds with our easy-to-use generator. Save time, reduce errors, and streamline your billing process for a stress-free invoicing experience! </div>",unsafe_allow_html=True)
                    st.markdown(" ")
                    submit = st.form_submit_button('Readmore')
                    submit1 = st.form_submit_button('Generator')
                if submit:
                    st.session_state.page = "generate"
                    st.rerun()
                if submit1:
                    st.session_state.page = "main1"
                    st.rerun()
    
    with st.container():
        st.markdown(
            """
            <style>
            .card {
                background-color: #f0f0f5;
                padding: 20px;
                margin: 10px;
                border-radius: 10px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                transition: box-shadow 0.3s ease, transform 0.3s ease;
            }

            .card:hover {
                box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.2);
                transform: translateY(-5px);
            }

            .card-header {
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 10px;
            }

            .card-body {
                font-size: 1em;
                color: #555;
            }
            .card-header1 {
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 10px;
            }

            .card-body1 {
                font-size: 1em;
                color: #555;
                padding : 20px;
            }

            </style>
            """, unsafe_allow_html=True
        )

        # Card 1
        with st.container():
            col1,col2,col3,col4 = st.columns(4)
            with col1:
                st.markdown(f"""<div class="card">
                            <div class="card-header1">Invoice Data Entry</div>
                            <div class="card-body1" style="font-size: 15px;">Streamline your accounting with accurate and automated invoice data entry, reducing manual effort.</div>
                            <div class="card-body1">Known More in About page</div>
                            </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="card"><div class="card-header">Intelligent Invoice Processing Workflow</div>
                            <div class="card-body">Automate data capture, validation, and approval in a seamless, efficient workflow.</div>
                            <div class="card-body1">Known More in About page</div>
                            </div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class="card"><div class="card-header">Automated Invoice Processing</div>
                            <div class="card-body">Enhance efficiency by automating invoice processing, reducing errors and speeding up workflows.</div>
                            <div class="card-body1">Known More in About page</div>
                            </div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""<div class="card"><div class="card-header1">Invoice OCR</div>
                            <div class="card-body1">Leverage AI and OCR to extract and process invoice data with exceptional accuracy and speed.</div>
                            <div class="card-body1">Known More in About page</div>
                            </div>""", unsafe_allow_html=True)
    

def tem_dashboard():
    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col6:
            col7,col8,col9 = st.columns(3)
            with col9:
                add_custom_css11()
                if st.button("🔙"):
                    st.session_state.page = "main"
                    st.rerun()
    try:
        # Load data from the pickle file
        load = pickle.load(open("data.pkl", 'rb'))
        load1 = pickle.load(open("user_db3.pkl",'rb'))
    except (FileNotFoundError, EOFError):
        st.error("No data found. Please upload images first.")
        return

    image_data = input_image_setup1(load["uploaded_files"])
    df = pd.DataFrame(load1)
    tabs = st.tabs(["Image", "Summarize","User Query" , "Payment Status", "Graphs","Extracted Data And Download"])
    total = len(df)
    with tabs[0]:
        st.header("Uploaded Images")
        # Ensure 'uploaded_files' key exists in the loaded dictionary
        if not load.get("uploaded_files"):
            st.error("Please upload at least one image.")
        else:
            st.subheader("Uploaded Invoices:")
            col1,col2,col3 = st.columns(3)
            with col2:
                for idx, image_info in enumerate(image_data):
                    st.image(image_info["image"], caption=f"Image {idx + 1}", use_container_width=True)

    with tabs[1]:
        for i in range(total):
            key_response = df['Key Points'].values[i]
            product_details = df['Product Details'].values[i]
            st.subheader(f"Essential Information from Image{i+1}:")
            highlight_box(key_response,color='lavender')
            highlight_box(product_details,color='white')

    with tabs[2]:
        input_text = st.text_input(
                "Enter your question (e.g., 'What is the invoice date?' or 'Who is the invoice billed to?')",
                key="input",
                placeholder="e.g., Extract invoice date or billing name"
            )
        image_data = input_image_setup1(load['uploaded_files'])
        for idx, image in enumerate(image_data):
            user_answer = answer_user_question_directly(image["image"], input_text)
            if input_text == "":
                continue
            st.subheader(f"Answer to Your Question: {input_text}")
            highlight_box(user_answer, color="lightyellow")

    with tabs[3]:
        df1 = ""
        for i in range(total):
            status = df.loc[i, "status"]
            category = df.loc[i, "category"]
            st.subheader(f"status of  image:{i+1}")
            highlight_box(f"Category: {category}")
            highlight_box(f"Status: {status}", color="lightgreen" if status == "Paid" else "lightcoral")

            key_response = df['Key Points1'].values[i]
            # st.subheader(f"Essential Information from Image{i+1}:")

            translated_details_lines = key_response.split("\n")
            total_amount=""
            # Extracting key details
            for line in translated_details_lines:
                try:
                    if "Invoice Number" in line:
                        invoice_number = line.split(":")[1].strip("**")
                    elif "Invoice Date" in line:
                        invoice_date = line.split(":")[1].strip("**")
                    elif "Total Amount" in line:
                        total_amount = line.split(":")[1].strip("** ₹")
                except Exception as e:
                    print(f"Error processing line '{line}': {e}")

            df1 = pd.DataFrame([{
                "Invoice Number": invoice_number,
                "Invoice Date": invoice_date,
                "status" : status,
                "Total Amount": total_amount
            }])
            # Displaying the DataFrame
            
            # st.dataframe(df1)

            data_to_store = {
                "Id": invoice_number,
                "date": invoice_date,
                "status": status,
                "amount": total_amount,
            }
            save_to_pickle1(data_to_store)


    with tabs[4]:
            st.subheader('Bar Graphs and pie charts')
            
            with st.container():
                col1,col2,col3 = st.columns(3)
                with col2:
                    select = st.selectbox("Select a graph type:", ["none", "bar", "pie"])
                    if select == "none":
                        st.header("select one grapgh")
                    elif select == "bar":
                        for i in range(total):
                            products = df.loc[i, "products"]
                            quantities = df.loc[i, "quantities"]
                            generate_product_quantity_bar_chart(products, quantities)
                    elif select == "pie":
                        for i in range(total):
                            products = df.loc[i, "products"]
                            quantities = df.loc[i, "quantities"]
                            generate_product_quantity_pie_chart(products, quantities)
        
    
    
    with tabs[5]:
        df_new = df.drop(columns=['products', 'quantities','products1', 'quantities1','Key Points1','category1','status1'])
        st.subheader("Extracted Data:")
        st.table(df_new)

        # Provide a download button for the extracted data
        st.download_button(
            label="Download Extracted Data as CSV",
            data=df.to_csv(index=False),
            file_name="extracted_data.csv",
            mime="text/csv"
        )

        if st.button("Dashboard and Chatbot"):
            st.session_state.page = "Dashboard"
            st.rerun()

def chatBot():
    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col6:
            col7,col8,col9 = st.columns(3)
            with col9:
                if st.button("🔙"):
                    st.session_state.page = "Home"
                    st.rerun()

    tabs = st.tabs(['Dashboard', 'chatBot'])
    
    with tabs[0]:
        load = pickle.load(open(f"{st.session_state.username}.pkl", 'rb'))
        df = pd.DataFrame([load])


        st.title("📊 Invoice Report Dashboard")
        total_invoices = 0

        if isinstance(load, dict):  
            df = pd.DataFrame([load])  # Convert single dictionary to DataFrame
        elif isinstance(load, list):
            df = pd.DataFrame(load)  # Convert list of dictionaries to DataFrame
        elif isinstance(load, pd.DataFrame):
            df = load  # Already a DataFrame
        else:
            raise ValueError(f"Unexpected data format: {type(load)}")


        # Debugging: Show DataFrame structure
        print(df.head())
        
        n = len(df) + 1
        for i in range(n - 1):
            df.at[i, "Id"] = i
        def convert_date(date_str, output_format="%Y-%m-%d"):
            # Parse the date from any format
            date_obj = dateparser.parse(date_str)
            # If parsing fails, return None
            if not date_obj:
                return None
            # Convert to specified format
            return date_obj.strftime(output_format)

        if "date" in df.columns:
            str_date = df["date"].astype(str)
            df["date"] = str_date.apply(convert_date)
        else:
            df["date"] = "0000-00-00"

        
        df.drop([1,4,6],inplace=True)
        df["Id"] = [1,2,3,4,5,6,7,8 ]

        
  
        # Check if "status" column exists before counting
        if "status" in df.columns:
            total_invoices = len(df)  # Total number of invoices
            paid_count = df["status"].eq("Paid").sum()  # Count "Paid" invoices correctly
            unpaid_count = df["status"].eq("Unpaid").sum()  # Count "Unpaid" invoices correctly
            overdue_count = df["status"].eq("Overdue").sum()    # Count "Overdue" invoices correctly
        else:
            paid_count = 0  # Default if "status" column is missing
            unpaid_count = 0  # Default if "status" column is missing
            overdue_count = 0  # Default if "status" column is missing
        
        # df.fillna({'date' : '0000-00-00 00:00:00'}, inplace=True)
        # Summary Section
        col1, col2, col3, col4 = st.columns(4)
        # col1.metric("Total Invoices", total_invoices)
        col1.metric("Total Invoices",total_invoices)
        col2.metric("Paid Invoices", paid_count)
        col3.metric("Unpaid Invoices", unpaid_count)
        col4.metric("Overdue Invoices", overdue_count)

        col1,col2 = st.columns(2)
        with col1:    
            # Invoice Table
            st.subheader("📄 Invoice Details")
            st.dataframe(df)

        with col2:
            # Pie Chart for Payment Status
            st.subheader("💰 Payment Status Distribution")
            status_counts = df["status"].value_counts()
            fig1 = px.pie(names=status_counts.index, values=status_counts.values, title="Invoices Status")
            st.plotly_chart(fig1, use_container_width=True)
            
        col1,col2 = st.columns(2)
        with col1:
            # Line Chart for Invoice Amounts
            st.subheader("📈 Invoice Amounts")
            fig2, ax = plt.subplots()
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            ax.plot(df["date"], df["amount"], marker="o")
            ax.set_ylabel("amount")
            ax.set_title("Invoice Amounts Over Time")
            st.pyplot(fig2)
        with col2:
            # Ensure column names are clean
            df.columns = df.columns.str.strip().str.lower()

            # Convert "amount" column to numeric, forcing errors to NaN
            df["amount"] = pd.to_numeric(df["amount"].str.replace("[^0-9.]", "", regex=True), errors="coerce")

            # Check if conversion was successful
            if df["amount"].isnull().any():
                print("Warning: Some values in 'amount' could not be converted.")
            # Bar Chart for Invoice Amounts
            st.subheader("📊 Invoice Amounts")
            fig2, ax = plt.subplots()
            df.groupby("status")["amount"].sum().plot(kind="bar", ax=ax, color=["green", "red", "orange"])
            ax.set_ylabel("Total Amount")
            ax.set_title("Total Invoice Amount by Status")
            st.pyplot(fig2)
            
        # Filters (Optional)
        status_filter = st.selectbox("Filter by Status:", ["All"] + list(df["status"].unique()))
        if status_filter != "All":
            filtered_df = df[df["status"] == status_filter]
            st.dataframe(filtered_df)

        if st.button("Back to Extractor"):
            st.session_state.page = "Image"
            st.rerun()
        
    with tabs[1]:
        st.markdown(
            """
            <style>
                body {
                    background-color: black;
                    color: white;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <h3 style="font-size:22px; text-align:center; color:black;">
                Advertisement Ideas & Strategy Chatbot
            </h3>
            """,
            unsafe_allow_html=True
        )
            
        col1,col2,col3 = st.columns(3)
        with col1:
            st.markdown("   ")
        with col2:
            st.markdown("""
                <style>
                    
                .user-message {
                    background-color: #dcf8c6;
                    border-radius: 10px;
                    padding: 10px;
                    margin: 10px 0;
                    text-align: right;
                    width: fit-content;
                    margin-left: auto;
                }
                .bot-message {
                    background-color: #f0f0f0;
                    border-radius: 10px;
                    padding: 10px;
                    margin: 10px 0;
                    text-align: left;
                    width: fit-content;
                    margin-right: auto;
                    border: 1px solid #ccc;
                }

                .chat-container {
                    max-width: 600px;
                    margin: auto;
                    border: 1px solid #ccc;
                    padding: 10px;
                    border-radius: 10px;
                    background: #f0f0f0;
                    overflow-y: auto;
                    height: 400px;
                }
                .user-msg {
                    background-color: #dcf8c6;
                    padding: 10px;
                    border-radius: 10px;
                    margin-bottom: 5px;
                    text-align: right;
                    animation: moveRight 0.5s ease;
                }
                .bot-msg {
                    background-color: #fff;
                    padding: 10px;
                    border-radius: 10px;
                    margin-bottom: 5px;
                    border: 1px solid #ccc;
                    text-align: left;
                    animation: moveLeft 0.5s ease;
                }
                @keyframes moveRight {
                    from { transform: translateX(-50px); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes moveLeft {
                    from { transform: translateX(50px); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                </style>
                """, unsafe_allow_html=True)
            
            if 'user_choice' not in st.session_state:
                st.session_state['user_choice'] = None
            if 'chat_history' not in st.session_state:
                st.session_state['chat_history'] = []
                
            search_query = st.text_input("🔍 Search messages...", key="search")
            filtered_messages = [msg for msg in st.session_state['chat_history'] if search_query.lower() in msg[1].lower()] if search_query else st.session_state['chat_history']

            # Display the chat history
            for sender, message in filtered_messages:
                if sender == "user":
                    st.markdown(f"<div class='user-message'>{message}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='bot-message'>{message}</div>", unsafe_allow_html=True)


            # If the user is asked for advertisement details, collect the information
            if st.session_state['user_choice'] == "request_details":
                # Ask for product name, category, budget, and company name
                product_name = st.text_input("What is the name of your product?", key="product_name")
                product_category = st.text_input("What is the product category?", key="product_category")
                budget = st.text_input("What is your marketing budget?", key="budget")
                company_name = st.text_input("What is your company name?", key="company_name")

                if product_name and product_category and budget and company_name:
                    # Generate advertisement ideas once all details are provided
                    advertisement_ideas = get_advertisement_ideas(product_name, product_category, budget, company_name)
                    st.session_state['chat_history'].append(("user", f"Product Name: {product_name}, Category: {product_category}, Budget: {budget}, Company: {company_name}"))
                    st.session_state['chat_history'].append(("bot", advertisement_ideas))
                    
                    # Clear user choice
                    st.session_state['user_choice'] = None
                    
                    # Display generated advertisement ideas
                    st.write(f"<div class='bot-message'>{advertisement_ideas}</div>", unsafe_allow_html=True)

            # Input field for user message
            input_text = st.text_input("What do you need advertisement ideas for?", key="input")

            # Button to submit the message
            submit = st.button("Send")

            # If submit is clicked and there is input, process the message
            if submit and input_text:
                if "advertisement" in input_text.lower():
                    # If the question is about advertisement, ask for further details
                    st.session_state['user_choice'] = "request_details"
                    bot_response = "I can help you with advertisement ideas! Please provide the following details for the product:" \
                                "\n1. Product Name 🛍\n2. Product Category 🏷\n3. Marketing Budget 💵\n4. Company Name 🏢"
                else:
                    bot_response = get_gemini_response(input_text)

                # Update chat history
                st.session_state['chat_history'].append(("user", input_text))
                st.session_state['chat_history'].append(("bot", bot_response))
        with col3:
            st.markdown("   ")


if __name__ == "__main__":
    main()
