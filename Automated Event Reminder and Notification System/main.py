#!/usr/bin/env python
# coding: utf-8

import gspread
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from google.oauth2 import service_account

# Step 1: Authenticate Google Sheets using Service Account
def authenticate_google_sheets():
    creds = service_account.Credentials.from_service_account_file(
        "C:\Users\nivet\Documents\Alert_Mail\alert\service_account_credentials.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
    )
    return creds

# Step 2: Access Google Sheets and retrieve data from a specific sheet
def get_google_sheet(sheet_id, sheet_name):
    creds = authenticate_google_sheets()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    records = sheet.get_all_records()
    return records

# Step 3: Send Email Alert
def send_email(subject, message, to_emails, cc_emails=None):
    sender_email = "abc@gmail.in"  # Replace with your email
    sender_password = "abcabcabc"  # Replace with your email password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(to_emails)
    if cc_emails:
        msg['Cc'] = ', '.join(cc_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))

    recipients = to_emails + (cc_emails if cc_emails else [])

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())


def check_for_upcoming_events():
    sheet_configs = [
        {
            "sheet_id": "abcdefghijklmnopqrstuvwxyz", # give your sheet id 
            "to_emails": ["abc@gmail.in"],
            "cc_emails": ["abc@gmail.in"],
            "subject_prefix": "Odia",
            "columns": ["Name", "Type", "Month", "Date"]
        }

    ]

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    today = datetime.now()
    current_month_index = today.month - 1
    selected_months = [months[current_month_index], months[(current_month_index + 1) % 12]]

    for config in sheet_configs:
        upcoming_events = []
        sheet_id = config["sheet_id"]
        to_emails = config["to_emails"]
        cc_emails = config["cc_emails"]
        subject_prefix = config["subject_prefix"]
        columns = config["columns"]

        for month in selected_months:
            try:
                records = get_google_sheet(sheet_id, month)
            except gspread.exceptions.WorksheetNotFound:
                print(f"Worksheet for {month} not found in Sheet ID: {sheet_id}")
                continue

            for record in records:
                date_str = str(record['Date'])

                if '-' in date_str:
                    start_day, end_day = map(int, date_str.split('-'))
                    event_start_date = datetime(today.year, months.index(month) + 1, start_day)
                    event_end_date = datetime(today.year, months.index(month) + 1, end_day)

                    if today <= event_end_date and today >= event_start_date:
                        record['Month'] = month
                        upcoming_events.append(record)

                else:
                    try:
                        event_day = int(date_str)
                        event_date = datetime(today.year, months.index(month) + 1, event_day)

                        if today.date() == event_date.date() or (today >= (event_date - timedelta(days=7)) and today <= event_date):
                            record['Month'] = month
                            upcoming_events.append(record)
                    except ValueError:
                        continue

        if upcoming_events:
            upcoming_events.sort(key=lambda x: (months.index(x['Month']), int(x['Date'])))
            subject = f"{subject_prefix} Upcoming Events Alert"
            body = """
            <p>Hi Team,</p>
            <p>Please prepare posts for the upcoming birthdays and festivals:</p>
            <h2>Upcoming Birthdays/Festivals:</h2>
            <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; border: 1px solid #ddd;">
                <thead style="background-color: #f2f2f2;">
                    <tr>{}</tr>
                </thead>
                <tbody>
            """.format(''.join(f'<th style="padding: 8px; text-align: left; border: 1px solid #ddd;">{col}</th>' for col in columns))

            for record in upcoming_events:
                row_data = ''.join(f"<td style='padding: 8px; border: 1px solid #ddd;'>{record[col]}</td>" for col in columns)
                body += f"<tr>{row_data}</tr>"

            body += """
                </tbody>
            </table>
            <p>Don't forget to create posts for these events!</p>
            """

            send_email(subject, body, to_emails, cc_emails)
            print(f'email sent successfully - {subject_prefix}')





# Step 5: Main function
if __name__ == "__main__":
    check_for_upcoming_events()


