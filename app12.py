import pandas as pd

# Load CSV file
file_path = "output.csv"  # Path to your uploaded file
df = pd.read_csv(file_path)

# User input for invoice number
invoice_no = input("Enter Invoice Number to check: ")

# Check if Invoice_No exists
if invoice_no in df["Invoice_No"].astype(str).values:
    print(f"Invoice No {invoice_no} exists in the CSV file.")
else:
    print(f"Invoice No {invoice_no} does not exist in the CSV file.")
