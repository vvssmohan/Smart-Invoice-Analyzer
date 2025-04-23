from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import pandas as pd
import os

# Load dataset (replace with your actual dataset path)
df = pd.read_csv("output.csv")

# Select 1000 first entries
sample_df = df.head(100).reset_index(drop=True)

# Create output folder for invoices
output_folder = "sample_invoices7"
os.makedirs(output_folder, exist_ok=True)

# Generate invoices
for i, row in sample_df.iterrows():
    invoice_file = os.path.join(output_folder, f"Invoice_{i+1}.pdf")
    c = canvas.Canvas(invoice_file, pagesize=letter)
    
    # Invoice Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "INVOICE")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Invoice ID: {row['Invoice_No']}")
    c.drawString(400, 720, f"Date: {row['Invoice Date']}")

    # Buyer and Seller Info
    c.drawString(50, 690, f"Selling company: {row['Company']}")
    c.drawString(50, 670, f"Customer Name: {row['Customer_Name']}")

    # Table Data
    data = [
        ["Product", "Company", "Quantity", "Unit Price (₹)", "Total Price (₹)"],
        [row['Product_Name'], row['Company'], row['Quantity'], row['Unit_Price'], row['Total_Price']]
    ]

    # Create Table
    table = Table(data, colWidths=[120, 100, 120, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Draw Table
    table.wrapOn(c, 50, 500)
    table.drawOn(c, 50, 580)

    
    c.setFont("Helvetica", 12)
    c.drawString(50, 510, f"Description: {row['Description']}")
    c.drawString(50, 530, f"Usage: {row['Usage']}")
    c.drawString(50, 550, f"How To Use: {row['How_to_Use']}")
    # c.drawString(50, 570, f"Fradulent: {row['Fraudulent']}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 480, "Thank you for your purchase!")
    c.save()

print(f"Sample invoices saved in '{output_folder}' folder.")



# import pandas as pd
# import random

# # Load the existing dataset
# df = pd.read_csv("invoice_data.csv")

# # Generate random customer names
# first_names = ["John", "Emma", "Sophia", "Liam", "Olivia", "Noah", "Ava", "Isabella", "Mason", "Ethan"]
# last_names = ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Harris", "Clark", "Walker", "Lewis", "Hall"]

# # Create a new column 'Customer_Name' with random names
# df["Customer_Name"] = [random.choice(first_names) + " " + random.choice(last_names) for _ in range(len(df))]

# # Save the updated CSV file
# df.to_csv("invoice_data_with_customers.csv", index=False)

# print("✅ Customer names added successfully!")
