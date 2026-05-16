import csv
import json
import os

input_file = os.path.join("data", "messy_transactions.csv")
output_file = os.path.join("output", "clean_transactions.json")

cleaned_transactions = []

seen_transactions_ids = set()

with open(input_file, mode="r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        validation_errors = []
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
        transaction_id = cleaned_row["transaction_id"]
        amount = cleaned_row["amount"]
        currency = cleaned_row["currency"]
        transaction_type = cleaned_row["transaction_type"]

        if not transaction_id:
            validation_errors.append("Missing transaction ID")

        if transaction_id in seen_transactions_ids:
            validation_errors.append("Duplicate transaction ID")
        else:
            seen_transactions_ids.add(transaction_id)

        if not amount or amount.upper() == "NULL":
            validation_errors.append("Missing amount")

        if currency != "USD":
            validation_errors.append("Invalid or unsupported currency")

        if transaction_type not in ["debit", "credit"]:
            validation_errors.append("Invalid transaction type")

        cleaned_row["is_valid"] = len(validation_errors) == 0
        cleaned_row["validation_errors"] = validation_errors

        cleaned_transactions.append(cleaned_row)

output_dir = os.path.dirname(output_file)
# Only create the output directory if output_dir is not an empty string (i.e., output_file is not just a filename)
if output_dir:
    os.makedirs(output_dir, exist_ok=True)
with open(output_file, mode="w", encoding="utf-8") as json_file:
    json.dump(cleaned_transactions, json_file, indent=4)
print(f"Processed {len(cleaned_transactions)} transactions")
print(f"Clean JSON saved to : {output_file}")
