import json
import csv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def json_to_csv(json_directory, csv_file):
    writer = csv.writer(csv_file)
    writer.writerow(['Keys', 'Amount', 'Unit'])

    for filename in os.listdir(json_directory):
        if filename.endswith(".json"):
            json_file = os.path.join(json_directory, filename)
            with open(json_file, "r") as f:
                try:
                    data = json.load(f)
                    keys_ = data.get('ResultsByTime')

                    if keys_:
                        for key in keys_:
                            groups = key.get('Groups')
                            if groups:
                                for group in groups:
                                    keys = group.get('Keys')
                                    metrics = group.get('Metrics')
                                    if keys and metrics:
                                        key_value = keys[0].split("$")[-1]
                                        net_cost = metrics.get('NetUnblendedCost')
                                        amount = net_cost.get('Amount')
                                        unit = net_cost.get('Unit')

                                        writer.writerow([key_value, amount, unit])
                            else:
                                total = key.get('Total')
                                if total:
                                    net_cost = total.get('NetUnblendedCost')
                                    amount = net_cost.get('Amount')
                                    unit = net_cost.get('Unit')

                                    writer.writerow(['Total', amount, unit])
                except json.decoder.JSONDecodeError:
                    print(f"Error: Invalid JSON format in file '{json_file}'")


# Directory containing the JSON files
json_directory = "json_files"

# Output directory for CSV file
csv_directory = "csv_files"

# Output CSV file
csv_file_path = os.path.join(csv_directory, "output.csv")

# Create the CSV directory if it doesn't exist
os.makedirs(csv_directory, exist_ok=True)

# Create the output CSV file
with open(csv_file_path, 'w', newline='') as csv_file:
    json_to_csv(json_directory, csv_file)

# Email configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "your-email"
receiver_email = "receiver-email"
password = "sender-password"

# Create the email message
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "CSV File Attachment"

# Add the CSV file attachment
with open(csv_file_path, "r") as attachment:
    csv_attachment = MIMEText(attachment.read(), 'plain')
    csv_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(csv_file_path))
    message.attach(csv_attachment)

# Connect to the SMTP server and send the email
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, password)
    server.send_message(message)
    print("Email sent successfully")
except Exception as e:
    print("Error sending email:", str(e))
finally:
    if 'server' in locals():
        server.quit()
