
Setup
1. Set your api_id and api_hash to setup.ini
2. Run setup.py to login via Telegram
3. In settings.ini:
SETTINGS
    people_txt - message that will be sent to every parsed user separately
    groups_txt - message that will be sent to group where every from these people can read collectively
    groups_links - write links of groups to add it to your collection to spam, separate links with a space
    send_to_whom - (people, groups)
    send_method - (now, interval)
    interval_time - integer in minutes
Notation: don't touch POST section! Settings you can change parallely with when code is running!
4. Ready to spam :)


Run
1. Just run main.py
2. Errors you can check in errors.txt