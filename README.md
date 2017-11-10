## OLX flat parser.
### Description:
Script run by crontab every 30 minutes, looks for new flats in odessa and notify in the telegram through the bot.
Script find flats which added yesterday and today only.
Data keep saved into Firebase.
#### Requirements and settings description:
Crontab rule (every 30 minutes) - `0/30 * * * * <path to python interpritator> <path to file main.py>`
1. Python >= 3.4.3
2. **BASE_URL** - Base url of olx with protocol. - `https://www.olx.ua/` 
3. **PHONE_URL** - Url for fetching seller telephone numbers. 
4. **CATEGORY** - `nedvizhimost` 
5. **SUB_CATEGORY** - `arenda-kvartir`
6. **SUB_SUB_CATEGORY** - `dolgosrochnaya-arenda-kvartir`
7. **CITY** - `odessa`
8. **DISTRICT_ID** - `85` (Киевский), `199` (Коминтерновский), `87` (Малиновский), `89` (Приморский), `91` (Суворовский)
9. **MIN_PRICE** - Min price of flat rent (not set less 1000). `2500`
10. **MAX_PRICE** - Max price of flat rent. `5000`
11. **MIN_ROOMS** - Min rooms amount in flat. `1`
12. **MAX_ROOMS** - Max rooms amount in flat. `1`
13. **WITH_PHOTOS** - Search ads with photos only or not. `True`
14. **WITH_PROMOTED** - Include promoted ads. `False`
15. **PUBLICATION_DATE** - List of values with information when ad was published. `['сегодня', 'вчера']`
16. **DB_API_KEY** - Api key for firebase db.
17. **DB_AUTH_DOMAIN** - Domain for authorization through Firebase. 
18. **DB_DATABASE_URL** - Url for firebase db.
19. **DB_STORAGE_BUCKET** - Url for firebase bucket.
20. **USER_EMAIL** - Email of user in firebase app who have permission on work with db. 
21. **USER_PASSWORD** - Password of user in firebase app who have permission on work with db. 
22. **TELEGRAM_BOT_API_URL** - Telegram api url.
23. **TELEGRAM_BOT_KEY** - Api key of telegram bot which will be sending messages.
24. **TELEGRAM_CHAT_IDS** - List of conversations ids when messages will be sending.
25. **LOG_FILENAME** - Name of logfile.
