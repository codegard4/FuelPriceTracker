# Gas Price Monitoring and Reporting Across the Portland Metro

## Overview
This project automates the collection, storage, and reporting of gas price data in Portland OR. It gathers price information from various fuel stations, compiles the data into a CSV file, and sends a daily email summarizing the latest prices. Additionally, a Power BI dashboard visualizes trends across multiple fuel markets.

*NOTE -- the dashboard layout is also viewable in an easier-to-open .png file

## Features
- **Automated Data Collection**: Fetches gas prices from GasBuddy stations autonomously via Microsoft Task Scheduler
- **Daily CSV Logging**: Stores historical price data in `gas_prices.csv`.
- **Email Notifications**: Sends formatted daily gas price updates via email.
- **Power BI Dashboard**: Displays price trends and comparisons across multiple fuel markets.

## Project Structure
```
.
├── config/
│   ├── params.conf  # Configuration file with credentials and headers
├── gas_prices.csv   # Historical gas price data (generated and updated daily)
├── api_call.py  # Main script for fetching prices and sending emails
├── FuelAndSalesDashboard.pbix  # Power BI dashboard file
├── .gitignore  # Ignore confidential server data
├── README.md  # Project documentation
```

## Installation
### Prerequisites
- Python 3.x
- Required Python libraries:
  ```sh
  pip install requests beautifulsoup4 pandas smtplib configparser
  ```

### Configuration
1. **Set up `params.conf` in the `config/` directory:**  
It will look something like this:  
   ```ini
   [DEFAULT]
   server = smtp.example.com
   port = 587
   user = your-email@example.com
   password = 'your-email-password'
   emails = recipient1@example.com, recipient2@example.com
   header = '{"User-Agent": "Mozilla/5.0"}'
   ```

3. **Modify `station_data` in `api_call.py`** to include the fuel stations you want to monitor.

## Usage
### Running the Script
To fetch gas prices and send daily email updates, run the following command within the project:
```sh
python api_call.py
```

### Viewing Data in Power BI
1. Open `gas_prices_dashboard.pbix` in Power BI.
2. Refresh data to load the latest `gas_prices.csv`.
3. Analyze fuel price trends across different markets.

## Future Improvements
- Expand data sources beyond GasBuddy? Maybe an API plug-in  
- Add a logging email
- Combine price with sales information (which will be private)

## License
This project is open-source. Feel free to modify and expand its functionality as needed.

