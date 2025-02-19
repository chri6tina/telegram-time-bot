# EST ↔ PHT Time Converter Bot

This is a simple Telegram bot that allows users to convert between **Eastern Standard Time (EST)** and **Philippine Time (PHT)**. The bot also allows users to check the current time in PHT and convert custom times.

## Features

- **Time Right Now in PHT**: See the current Philippine Time (PHT).
- **Custom EST to PHT**: Convert custom times from Eastern Standard Time (EST) to Philippine Time (PHT).
- **Custom PHT to EST**: Convert custom times from Philippine Time (PHT) to Eastern Standard Time (EST).

## Installation

### Requirements
- Python 3.10.12 (or any compatible version)
- Python packages listed in `requirements.txt`

### Setup Instructions

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/telegram-time-bot.git
    cd telegram-time-bot
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set your Telegram Bot Token as an environment variable:
    ```bash
    export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
    ```

   For Windows users, use:
    ```bash
    set TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
    ```

4. Run the bot:
    ```bash
    python telegram-time-bot.py
    ```

## Usage

Once the bot is running, you can start it by searching for it in Telegram and typing `/start`. You will be presented with a few options:
1. See the **current time in PHT**.
2. Convert **custom EST to PHT** and vice versa.

## Deployment

This bot can also be deployed on **Railway** or any other platform that supports Python apps. You can follow these instructions to deploy the bot on **Railway**:

1. Fork the repository and push your changes.
2. Link your GitHub repository to **Railway** and deploy it.
3. Set your **Telegram Bot Token** in **Railway’s environment variables**.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
