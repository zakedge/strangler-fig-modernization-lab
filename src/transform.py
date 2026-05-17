import csv
import json
import os
import logging
from datetime import datetime

input_file = os.path.join("data", "messy_transactions.csv")
valid_output_file = os.path.join("output","valid_transactions.json")
invalid_output_file = os.path.join("output","invalid_transactions.json")
summary_output_file = os.path.join("output","summary_report.json")
log_file = os.path.join("logs","transaction_processor.log")


log_dir = os.path.dirname(log_file)

if log_dir:
    os.makedirs(log_dir,exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filename= log_file,
    filemode="a"
)

logging.info("Transaction processing started")


valid_transactions = []
invalid_transactions = []

def standardize_date(date_value):
    date_value = date_value.strip()

    accepted_formats = [
    "%Y-%m-%d",      # 2024-01-05
    "%m/%d/%Y",      # 01/06/2024
    "%Y/%m/%d",      # 2024/01/07
    "%b %d %Y",      # Jan 8 2024
    "%B %d %Y",      # January 8 2024
    "%m-%d-%Y",      # 02-01-2024
    "%d-%m-%Y",      # 31-01-2024
    "%d/%m/%Y",      # 31/01/2024
    "%Y.%m.%d",      # 2024.01.05
    "%d.%m.%Y",      # 31.01.2024
    "%d %b %Y",      # 08 Jan 2024
    "%d %B %Y",      # 08 January 2024
    "%Y%m%d",        # 20240105
    "%m%d%Y",        # 01052024
    "%d%m%Y",        # 05012024
    "%Y-%m-%d %H:%M:%S",  # 2024-01-05 14:30:00
    "%m/%d/%Y %H:%M:%S",  # 01/05/2024 14:30:00
    "%Y-%d-%m"
    ] 

    for date_format in accepted_formats:
        try: 
            parsed_date = datetime.strptime(date_value,date_format)
            return parsed_date.strftime("%m/%d/%Y")
        except ValueError:
            pass

    return None

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
            "amount": (
                row["amount"]
                .replace(",", "")
                .replace("$", "")
                .replace("(", "-")
                .replace(")", "")
                .strip()
            ),
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
        standardized_date = standardize_date(cleaned_row["transaction_date"])

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

        if standardized_date:
            cleaned_row["transaction_date"] = standardized_date
        else:
            validation_errors.append("Invalid transaction date")

        cleaned_row["is_valid"] = len(validation_errors) == 0
        cleaned_row["validation_errors"] = validation_errors

        if cleaned_row["is_valid"]:
            valid_transactions.append(cleaned_row)
        else:
            invalid_transactions.append(cleaned_row)
            logging.warning(
            f"Invalid transaction {transaction_id}: {validation_errors}"
)


summary_report = {
    "total_transactions": len(valid_transactions) + len(invalid_transactions),
    "valid_transactions": len(valid_transactions),
    "invalid_transactions": len(invalid_transactions)
}


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

summary_report_dir = os.path.dirname(summary_output_file)
if summary_report_dir:
    os.makedirs(summary_report_dir, exist_ok=True)
with open(summary_output_file, mode="w", encoding="utf-8") as summary_file:
    json.dump(summary_report, summary_file, indent=4)


logging.info(f"Processed {summary_report['total_transactions']} transactions.")

logging.info("Transaction processing completed")