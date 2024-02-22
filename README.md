# Automated Upwork Past Job Monitoring System

## Overview

The Automated Upwork Job Monitoring System is a sophisticated Python application designed to automate the process of monitoring and retrieving job postings from Upwork based on specific search criteria. The system leverages a combination of web scraping, automated web browsing, and interaction with the Telegram API to notify users of new job opportunities. This project utilizes several Python libraries, including Selenium for web automation, BeautifulSoup for HTML parsing, gspread for Google Sheets integration, and python-telegram-bot for sending alerts via Telegram.

## Features

- **Automated Login**: Securely logs into Upwork using credentials stored as environment variables.
- **Custom Job Search**: Performs searches on Upwork for jobs matching predefined keywords and filters, such as "python", "automation", "scrap", and ensures payment verification.
- **Data Extraction**: Utilizes BeautifulSoup to parse job posting details from the search results.
- **Notification System**: Sends real-time alerts to a specified Telegram chat with detailed information about new job postings.
- **Robust Error Handling**: Implements exception handling and retry mechanisms to manage login timeouts and other potential errors.
- **Environment Variable Management**: Uses the dotenv library to manage sensitive information securely.

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.6 or higher
- Google Chrome Browser
- ChromeDriver compatible with your Chrome version
- Required Python libraries: `selenium`, `beautifulsoup4`, `python-telegram-bot`, `gspread`, `oauth2client`, `webdriver-manager`, `python-dotenv`

Additionally, you will need:

- A Telegram bot token and chat ID for notifications.
- Upwork account credentials.
- Google Cloud project with the Sheets API enabled and configured for `gspread` if you plan to use Google Sheets integration (optional).

## Installation

1. Clone the repository to your local machine:

```bash
git clone <repository_url>
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory and add your Upwork credentials and Telegram bot information:

```plaintext
TELEGRAM_TOKEN=<your_telegram_bot_token>
UPWORK_USERNAME=<your_upwork_username>
UPWORK_PASSWORD=<your_upwork_password>
TELEGRAM_CHAT_ID=<your_telegram_chat_id>
```

4. Ensure that ChromeDriver is installed and its path is correctly set up in your system.

## Usage

To run the system, execute the main script from the command line:

```bash
python main.py
```

The script will automatically start monitoring Upwork for new job postings based on the specified criteria. When a matching job is found, the system will send a detailed notification to the specified Telegram chat.

## Functionality

The system operates by initiating a headless Chrome browser session using Selenium, logging into Upwork with the provided credentials, and navigating through the job search results pages. It parses each job posting using BeautifulSoup, extracts relevant details, and checks for specific conditions such as the number of proposals and hires. If a job meets the criteria, it sends a formatted message to the specified Telegram chat, including job details, client information, and activity metrics.

## Customization

You can customize the job search criteria and the information extracted from each posting by modifying the `main()` function and the `send_mail()` asynchronous function. Adjust the search URL parameters and the BeautifulSoup selectors to fit your needs.

## Contributing

Contributions to the Automated Upwork Job Monitoring System are welcome. Please fork the repository, make your changes, and submit a pull request.

## License

This project is open-source and available under the MIT License. See the LICENSE file for more details.