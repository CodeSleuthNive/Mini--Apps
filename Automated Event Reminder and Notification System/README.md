# **Automated Event Reminder and Notification System**
This project is a Python-based automation tool designed to send email alerts for upcoming birthdays and festivals based on data in Google Sheets. It connects to specified Google Sheets, retrieves event information, and sends a formatted email alert to designated recipients.

## **Features**
##### Automated Event Retrieval: 
    Connects to multiple Google Sheets to fetch data for specified events based on the current and upcoming months.
##### Email Alerts: 
    Sends customized email alerts with details of events happening soon.
##### Date Matching: 
    Supports single-day and date-range events, notifying the team if they fall within the next 7 days.
##### Customizable Configurations: 
    Easily configure sheets, recipient emails, and notification rules.

## **Prerequisites**
##### Python 3.x: Ensure Python is installed and set up.
**Libraries** : Install required packages via pip:
* bash
* Copy code
* pip install gspread google-auth smtplib
  
**Google Cloud Service Account:**
* Create a service account in Google Cloud.
* Enable Google Sheets and Google Drive API.
* Download the JSON key file for the service account and save it in the working directory.
  
**Google Sheets Configuration:**
* Share each Google Sheet with the service account email.
* Note down the sheet ID and specify the column names required for each sheet configuration.
  
**Email Setup:**
Replace sender_email and sender_password with your email and password for SMTP authentication.
Enable "Allow less secure apps" in your email account if necessary.


python main.py - run this line in Anaconda Prompt 
