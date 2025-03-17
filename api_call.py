import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import json
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

if __name__ == "__main__":

    def get_cash_prices(url):
        # print("NEW STATION")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all script tags
        scripts = soup.find_all('script')


        cash_price = None
        for script in scripts:
            # Check if the script contains cash prices
            if '"cash"' in script.text:
                # Extract the JSON part from the script content
                json_text = re.search(r'(?<=\{).*?(?=\};)', script.string, re.DOTALL)
                if json_text:
                    # Load the JSON into a Python dictionary
                    data = json.loads('{' + json_text.group(0) + '}')
                    # print(data.keys())
                    # print()
                    station_number = url.split('/')[-1]
                    price_data = data[f'Station:{station_number}']['prices']
                    # print(price_data)
                    # Loop through the price data
                    for price_report in price_data:
                        if price_report['cash'] is not None:
                            if price_report['fuelProduct'] == 'regular_gas' and price_report['cash'][
                                'nickname'] is not None:
                                cash_price = price_report['cash']['price']
                                break
                    # print(cash_price)

        # Return cash prices or "---" if none found
        return cash_price if cash_price else "---"


    # Function to get gas prices from a GasBuddy station URL
    def get_gas_prices(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            print(f"Access forbidden for URL: {url}")
            return {}

        soup = BeautifulSoup(response.content, 'html.parser')

        prices = {}
        try:
            price_elements = soup.find_all('div', {'class': 'GasPriceCollection-module__priceDisplay___1pnaL'})
            if len(price_elements) >= 3:
                prices['regular'] = price_elements[0].find('span', {
                    'class': 'FuelTypePriceDisplay-module__price___3iizb'}).text.strip().replace('$', '')
                prices['midgrade'] = price_elements[1].find('span', {
                    'class': 'FuelTypePriceDisplay-module__price___3iizb'}).text.strip().replace('$', '')
                prices['premium'] = price_elements[2].find('span', {
                    'class': 'FuelTypePriceDisplay-module__price___3iizb'}).text.strip().replace('$', '')
        except Exception as e:
            print(f"Error parsing prices from URL: {url} - {e}")

        return prices


    # List of GasBuddy station URLs and corresponding nicknames
    station_data = [
        {'url': 'https://www.gasbuddy.com/station/72802', 'nickname': 'Fastrak', 'location': 'Broadway'},
        {'url': 'https://www.gasbuddy.com/station/105460', 'nickname': 'Fastrak Fremont', 'location': 'Broadway'},
        {'url': 'https://www.gasbuddy.com/station/29803', 'nickname': 'Shell 33rd', 'location': 'Broadway'},

        {'url': 'https://www.gasbuddy.com/station/41005', 'nickname': 'Fastrak', 'location': 'Milwaukie'},
        {'url': 'https://www.gasbuddy.com/station/76591', 'nickname': 'Safeway', 'location': 'Milwaukie'},
        {'url': 'https://www.gasbuddy.com/station/80434', 'nickname': 'SpaceAge', 'location': 'Milwaukie'},
        {'url': 'https://www.gasbuddy.com/station/97767', 'nickname': 'Astro', 'location': 'Milwaukie'},

        {'url': 'https://www.gasbuddy.com/station/10847', 'nickname': 'Roadrunner', 'location': 'Scappoose'},
        {'url': 'https://www.gasbuddy.com/station/14297', 'nickname': 'Fred Meyer', 'location': 'Scappoose'},
        {'url': 'https://www.gasbuddy.com/station/32005', 'nickname': '76', 'location': 'Scappoose'},
        {'url': 'https://www.gasbuddy.com/station/32007', 'nickname': 'Shell', 'location': 'Scappoose'}

        # Add more station data as needed
    ]

    # List to hold all data
    data = []

    # Get the current date
    date = datetime.now().strftime('%Y-%m-%d')

    # Loop through each station data and get prices
    for station in station_data:
        prices = get_gas_prices(station['url'])
        cash_price = get_cash_prices(station['url'])
        prices['cash_price'] = cash_price
        prices['date'] = date
        prices['station_nickname'] = station['nickname']
        prices['location'] = station['location']
        data.append(prices)

    # Create a DataFrame with the new data
    new_df = pd.DataFrame(data)
    # print(new_df)
    # Filepath to the CSV file
    file_path = 'gas_prices.csv'

    # Check if the file exists
    if os.path.exists(file_path):
        # If the file exists, append the new data without writing the header
        new_df.to_csv(file_path, mode='a', header=False, index=False)  # mode = 'a' and header = False to append data
        print("Gas prices have been appended to gas_prices.csv")
    else:
        # If the file does not exist, create it and write the header
        new_df.to_csv(file_path, mode='w', header=True, index=False)
        print("Creating gas_prices.csv file")


    # Function to filter gas prices for a specific day
    #NOTE--if the script is run more than once then we will have more than 1 entry for each station for the same day
    def filter_for_day(file_path, target_date):
        if not os.path.exists(file_path):
            print(f"No data file found at {file_path}")
            return None

        # Read the CSV file
        df = pd.read_csv(file_path)

        # Convert the 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'])

        # Filter rows where 'date' matches the target date
        day_df = df[df['date'] == target_date]

        return day_df


    # Target date (today's date)
    target_date = datetime.now().strftime('%Y-%m-%d')

    # Get data for the target date
    day_df = filter_for_day(file_path, target_date)

    if day_df is not None and not day_df.empty:
        print(f"Filtered data for the target date: {target_date}")
        print(day_df)
    else:
        print("No data available for the target date.")


    # Function to format data as text
    def format_data_as_text(df):
        text = f"Gas Prices for {target_date}:\n *Regular Prices Only"
        curr_location = ""
        print(df)
        for index, row in df.iterrows():
            if curr_location != row['location']:
                curr_location = row['location']
                text += f"\n"
                text += f"\n"
                text += f"{row['location']}"
                text += f"\n"

            # if(row['regular'] != "- - -"):
            text += f"\n"
            text += f"{row['station_nickname']} \n CREDIT: ${row['regular']} | CASH: ${row['cash_price']}\n"
                # text += f"Regular: ${row['regular']}\n"
            # text += f"Midgrade: ${row['midgrade']}\n"
            # text += f"Premium: ${row['premium']}\n"
            #     text += "\n"
        text += "\n"
        # text += "*Note -- stations without prices today are not included"
        return text


    if new_df is not None and not new_df.empty:
        email_body = format_data_as_text(new_df) #new_df is created every time the script is run, so it will always be the most recent data
        # print("Formatted data for email:")
        # print(email_body)
    else:
        email_body = "No data available for the target date."


    # Function to send email
    def send_email(subject, body, to_emails):
        # Email credentials
        smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server
        smtp_port = 587  # Replace with your SMTP port (usually 587 for TLS)
        smtp_user = 'coleodegardm@gmail.com'  # Replace with your email address
        smtp_password = 'rdoo abhb ntta yrek'  # Replace with your email password

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()

        # Login with your email and password
        smtp.login(smtp_user, smtp_password)
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, to_emails, text)
        server.quit()

        print("Email sent successfully.")

    # Recipients list
    recipients = ['coleodegardm@gmail.com', 'm_odegard@yahoo.com', 'lknudsen1234@yahoo.com', 'nerosnesdunk@yahoo.com', 'baodegard@yahoo.com']  # Replace with your recipient list

    # Send email with the formatted data
    send_email(
        subject=f"Cash & Credit Gas Prices for {target_date}",
        body=email_body,
        to_emails=recipients
    )



