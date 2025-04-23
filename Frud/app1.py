import streamlit as st
import pdfplumber
import pandas as pd
import google.generativeai as genai
import asyncio
import plotly.express as px
from PIL import Image
from googletrans import Translator
import pytesseract
import pickle
import numpy as np
import re
from pathlib import Path
import hashlib




genai.configure(api_key="AIzaSyCfzJ_B-5Dv7LukfPcxr4urmNzzz4VqPGA")
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


def extract_key_points(image):
    key_points_prompt = """
    You are an expert in understanding invoices.
    Please extract the following key points from the invoice:
    - product Name
    - product company
    - Price
    - quantity
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([key_points_prompt, image])
    return response.text



if "page" not in st.session_state:
    st.session_state.page = "pdf"


def main():
    if st.session_state.page == "pdf":
        pdf1()
    elif st.session_state.page == "image":
        image1()

def pdf1():
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

            if rfc_pred == 1:
                st.error("Invoice is Tampered")
            else:
                st.success("Invoice is not Tampered")
                st.table(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, "invoice_data.csv", "text/csv")
                if st.button("Imgae"):
                    st.session_state.page = "image"

def image1():
    data = []
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
        }
        product_id = product_encoded.get(product_name, 40)

        company_encoded = {
            'Asus': 1, 'Epson': 2, 'Samsung': 3, 'OnePlus': 4, 'Google': 5, 
            'Godrej': 6, 'Amazon': 7, 'Voltas': 8, 'Haier': 9, 'LG': 10, 
            'Blue Star': 11, 'Panasonic': 12, 'Bosch': 13, 'Xiaomi': 14, 'Sony': 15, 
            'TCL': 16, 'HP': 17, 'Whirlpool': 18, 'Apple': 19, 'IFB': 20, 
            'Lenovo': 21, 'Microsoft': 22, 'Brother': 23, 'Canon': 24, 'Dell': 25, 
            'Daikin': 26
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
                    elif "Price" in line:
                        
                        price = line.split(":")[1].strip("(This is the unit price)")
                        price = line.split(":")[1].strip("** (currency not specified in The invoice image, but it's likely the local currency)")
                        price = line.split(":")[1].strip("** (Currency not specified in the image, but likely Rupees (INR) given the seller's location)")
                    elif "Quantity" in line:
                        quantity = line.split(":")[1].strip("**")
                except Exception as e:
                    print(f"Error processing line '{line}': {e}")

            product_name1 = product_name + product_company        
            data.append({"product_name1" : product_name1,
                         "product_company": product_company,
                         "price":price,
                         "quantity":quantity
                    })
            
            input = preprocess(product_name1,product_company,quantity,price)
            rfc_pred = rfc.predict(input)

            if rfc_pred == 1:
                st.error("Invoice is Tampered")
            else:
                st.success("Invoice is not Tampered")
                df = pd.DataFrame(data)
                st.table(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, "invoice_data.csv", "text/csv")
                if st.button("PDF"):
                    st.session_state.page = "pdf"


if __name__ == "__main__":
    main()