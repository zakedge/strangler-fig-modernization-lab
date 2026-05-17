import csv
import json
import os

input_file = os.path.join("data", "messy_transactions.csv")
valid_output_file = os.path.join("output","valid_transactions.json")
invalid_output_file = os.path.join("output","invalid_transactions.json")


valid_transactions = []
invalid_transactions = []



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
            "amount": row["amount"].replace(",", "").replace("$", "").strip(),
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
        else:
            try:
                float(amount)
            except ValueError:
                validation_errors.append("Amount is not a valid number")    

        if currency != "USD":
            validation_errors.append("Invalid or unsupported currency")

        if transaction_type not in ["debit", "credit"]:
            validation_errors.append("Invalid transaction type")

        cleaned_row["is_valid"] = len(validation_errors) == 0
        cleaned_row["validation_errors"] = validation_errors

        if cleaned_row["is_valid"]:
            valid_transactions.append(cleaned_row)
        else:
            invalid_transactions.append(cleaned_row)

valid_output_dir = os.path.dirname(valid_output_file)
if valid_output_dir:
    os.makedirs(valid_output_dir, exist_ok=True)
with open(valid_output_file, mode="w", encoding="utf-8") as json_file:
    json.dump(valid_transactions, json_file, indent=4)

invalid_output_dir = os.path.dirname(invalid_output_file)
if invalid_output_dir:
    os.makedirs(invalid_output_dir, exist_ok=True)
with open(invalid_output_file, mode="w", encoding="utf-8") as json_file:
    json.dump(invalid_transactions, json_file, indent=4)

total_transactions = len(valid_transactions) + len(invalid_transactions)
print(f"Processed {total_transactions} transactions.")
print(f"Processed {len(valid_transactions) + len(invalid_transactions)} transactions.")
print(f"Invalid transactions: {len(invalid_transactions)}")
print(f"Valid JSON saved to: {valid_output_file}")
print(f"Invalid JSON saved to: {invalid_output_file}")