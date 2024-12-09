import smtplib, mimetypes, csv, json, requests, os
from datetime import datetime
from email.message import EmailMessage
import pandas as pd

# Email credentials
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'laohwang0523@gmail.com'
EMAIL_PASSWORD = 'arfk clxz fzat cjev'  # Or an App Password
TO_EMAIL = 'zekai.lee@coreconsulting.asia'

# Create the email
msg = EmailMessage()
msg['Subject'] = 'do u want eat banana'
msg['From'] = EMAIL_ADDRESS
msg['To'] = TO_EMAIL
msg.set_content('Hello, do u want eat banana.')

today_date = datetime.now().strftime('%Y-%m-%d')
csv_filename = f"{today_date}.csv"
directory = os.getcwd()

# Path to your CSV file
csv_file_path = f"{directory}/{csv_filename}"

# Ensure the CSV file exists or create it
if not os.path.exists(csv_file_path):
    print(f"{csv_filename} not found. Creating a new file.")
    with open(csv_file_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', '> RM 100,000.00', 'status', '>= 3 times && SAME account', 'status', '<= RM 1,000.00 && >= 10 times', 'status', '> RM 1,000,000.00', 'status', ' JomPAY >= 3 times', 'status'])  # Header row
else:
    print(f"{csv_filename} found. Opening the file.")

def summary_email():
    # Attach the CSV file
    mime_type, _ = mimetypes.guess_type(csv_file_path)  # Guess the mime type based on file extension
    mime_type, mime_subtype = mime_type.split('/')

    with open(csv_file_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype=mime_type, subtype=mime_subtype, filename='test.csv')

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
        
        # Delete the CSV file after successful email sending
        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)
            print(f"CSV file '{csv_file_path}' has been deleted.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def monitoring():
  # Fetch and process the JSON data
  if os.path.exists('apidata.json'):
    with open('apidata.json', 'r') as file:
      api = json.load(file)
    
    results = api.get("result", [])
    for result in results:
      datas = result.get('data', [])
      for data in datas:
        dimension = data.get("dimensionMap", {}).get('Dimension', '')
        dimension = dimension.rsplit(' - ', 2)

        # Load the CSV file if it exists
        if os.path.exists(csv_file_path):
          df = pd.read_csv(csv_file_path, delimiter=',', skip_blank_lines=True)
          df.columns = df.columns.str.strip()

          dimension_name = dimension[0].strip()
          dimension_type = dimension[1].strip()
          dimension_amount = float(dimension[-1].strip())

          # Flag to check if new row is added
          new_row_added = False

          # Check if the 'dimension_name' exists as a column in the CSV
          if dimension_name in df['Name'].values:
            # Update relevant columns based on conditions
            df.at[df[df['Name'] == dimension_name].index[0], ">= 3 times && SAME account"] += 1
            if dimension_type == "JomPAY":
              df.at[df[df['Name'] == dimension_name].index[0], "JomPAY >= 3 times"] += 1
            if dimension_amount <= 1000.00:
              df.at[df[df['Name'] == dimension_name].index[0], "<= RM 1,000.00 && >= 10 times"] += 1
            if dimension_amount > 100000.00:
              df.at[df[df['Name'] == dimension_name].index[0], "> RM 100,000.00"] += 1
            if dimension_amount > 1000000.00:
              df.at[df[df['Name'] == dimension_name].index[0], "> RM 1,000,000.00"] += 1
          else:
            print(f"Dimension value '{dimension_name}' not found in CSV columns.")
            # Prepare the new row to append
            new_row = [dimension_name, 0, 'false', 1, 'false', 0, 'false', 0, 'false', 0, 'false']

            # Add the new row to the DataFrame
            df = df._append(pd.Series(new_row, index=df.columns), ignore_index=True)
            print(f"Added new rows with '{dimension_name}'.")

            # Now apply the conditions on the existing or newly added row
            if dimension_type == "JomPAY":
              df.at[df[df['Name'] == dimension_name].index[0], "JomPAY >= 3 times"] += 1
            if dimension_amount <= 1000.00:
              df.at[df[df['Name'] == dimension_name].index[0], "<= RM 1,000.00 && >= 10 times"] += 1
            if dimension_amount > 100000.00:
              df.at[df[df['Name'] == dimension_name].index[0], "> RM 100,000.00"] += 1
            if dimension_amount > 1000000.00:
              df.at[df[df['Name'] == dimension_name].index[0], "> RM 1,000,000.00"] += 1

          # Read through the every row check whether

          # Save the DataFrame to the CSV file only after all changes are done
          df.to_csv(csv_file_path, index=False)
          print("CSV file updated.")
        else:
          print(f"CSV file '{csv_file_path}' not found.")       
  else:
      print("'apidata.json' file does not exist.")


monitoring()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "every_minute":
            monitoring()
        elif sys.argv[1] == "at_midnight":
            summary_email()
        else:
            print("Unknown task. Use 'every_minute' or 'at_midnight'.")
    else:
        print("Please specify a task: 'every_minute' or 'at_midnight'.")
