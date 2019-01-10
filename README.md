## OLX flat parser.
Simple python script which can be running by crontab every 30 minutes for instance, 
looking up about new flats in Odessa and notifying in the telegram through the bot.
The script is looking for apartments that were added yesterday and today only.

### Prerequisites
0. `python 3.6 or higher`
0. `pipenv`
0. `sqlite3`

## Getting Started
0. Clone project to your own local machine - `git clone https://github.com/digitalashes/olx-parser.git`
0. Go to the script directory - `cd olx-parser`
0. Copy file env.example to config directory and rename it to *.env* - `cp env.example ./config/.env`
0. Fill in **TELEGRAM_BOT_KEY** and **TELEGRAM_CHAT_IDS** in `config/.env` also if you want, you can uncomment and change others constants.
0. Create new pipenv environment - `pipenv install`
0. Run `pipenv shell main.py` and waiting messages.

#### Settings description:

Crontab rule (every 30 minutes) - `0/30 * * * * <path to python interpritator> <path to file main.py>`

0. **BASE_URL** - Base url of olx with protocol. - `https://www.olx.ua/` 
0. **PHONE_URL** - Url for fetching seller telephone numbers. 
0. **CATEGORY** - `nedvizhimost` 
0. **SUB_CATEGORY** - `arenda-kvartir`
0. **SUB_SUB_CATEGORY** - `dolgosrochnaya-arenda-kvartir`
0. **CITY** - `odessa`
0. **DISTRICT_ID** - `85` (Киевский), `199` (Коминтерновский), `87` (Малиновский), `89` (Приморский), `91` (Суворовский)
0. **MIN_PRICE** - Min price of flat rent (not set less 1000). `2500`
0. **MAX_PRICE** - Max price of flat rent. `5000`
0. **MIN_ROOMS** - Min rooms amount in flat. `1`
0. **MAX_ROOMS** - Max rooms amount in flat. `1`
0. **WITH_PHOTOS** - Search ads with photos only or not. `True`
0. **WITH_PROMOTED** - Include promoted ads. `False`
0. **PUBLICATION_DATE** - List of values with information when ad was published. `['сегодня', 'вчера']`
0. **TELEGRAM_BOT_API_URL** - Telegram api url.
0. **TELEGRAM_BOT_KEY** - Api key of telegram bot which will be sending messages.
0. **TELEGRAM_CHAT_IDS** - List of conversations ids when messages will be sending.
0. **LOG_FILENAME** - Name of logfile.
