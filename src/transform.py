import csv
import json
import os

input_file = os.path.join("data", "messy_transactions.csv")
output_file = os.path.join("output", "clean_transactions.json")

cleaned_transactions = []

with open(input_file, mode="r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        # Amount kept as string to preserve formatting or handle non-numeric values
        cleaned_row = {
            "transaction_id": row["transaction_id"].strip(),
            "account_id": row["account_id"].strip(),
            "customer_name": row["customer_name"].strip(),
            "transaction_date": row["transaction_date"].strip(),
            "amount": row["amount"].strip(),
            "currency": row["currency"].strip().upper(),
            "transaction_type": row["transaction_type"].strip().lower(),
            "merchant": row["merchant"].strip(),
            "category": row["category"].strip(),
            "notes": (row.get("notes") or "").strip()
        }
        cleaned_transactions.append(cleaned_row)

output_dir = os.path.dirname(output_file)
# Only create the output directory if output_dir is not an empty string (i.e., output_file is not just a filename)
if output_dir:
    os.makedirs(output_dir, exist_ok=True)
with open(output_file, mode="w", encoding="utf-8") as json_file:
    json.dump(cleaned_transactions, json_file, indent=4)
print(f"Processed {len(cleaned_transactions)} transactions")
print(f"Clean JSON saved to : {output_file}")
