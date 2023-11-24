# ScansNotify-Bot

ScansNotify-Bot is a Telegram bot written in Python that leverages web scraping to retrieve scans of (manhwa, manhua) from a curated list of compatible websites. The bot stores data, including user preferences and website information, in MongoDB. Users can input their preferences and receive notifications whenever new content is available.

## Features

- **Web Scraping:** ScansNotify-Bot uses web scraping techniques to extract information from compatible websites.
- **User Preferences:** Users can customize their notification preferences to receive personalized alerts.
- **MongoDB Integration:** Cataloging of compatible sites and user preferences is managed using MongoDB.
- **Telegram Integration:** Notifications are sent to users via Telegram for a seamless user experience.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/scansnotify-bot.git
   ```

2. Install dependencies:

   ```bash
   cd scansnotify-bot
   pip install -r requirements.txt
   ```

3. Set up MongoDB:

   - Create a MongoDB database and obtain the connection string.
   - Configure the connection string in the `.env` file.

4. Set up Telegram Bot:

   - Create a Telegram bot using the BotFather on Telegram.
   - Obtain the bot token and configure it in the `.env` file.

5. Run the bot:

   ```bash
   python start.py
   ```

## Configuration

Configure the bot by editing the `config.py` file. Set the MongoDB connection string, Telegram bot token, and other parameters as needed.

```.env
TELEGRAM_TOKEN= "YOUR_MONGODB_CONNECTION_STRING"
# MongoDB connection string
MONGO_URL= YOUR_TELEGRAM_BOT_TOKEN

# MongoDB database name
MONGO_DB_NAME="TelegramBot"

# MongoDB collection name
MONGO_COLLECTION_NAME="User"
```

## Usage

1. Start the bot on Telegram.
2. Set your preferences using the provided commands.
3. Receive timely notifications about new scans based on your preferences.

## Contributing

Contributions are welcome! If you'd like to contribute to the development of ScansNotify-Bot, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the creators of the web scraping and Telegram API libraries used in this project.
- Special thanks to our users for their feedback and support.

Feel free to reach out with any questions or issues. Happy scanning! 📚✨
```
