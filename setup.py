from configparser import ConfigParser

from pyrogram import Client

config = ConfigParser()
config.read('setup.ini')

app = Client('SUTB',
             api_id=config["LOGIN"]["api_id"],
             api_hash=config["LOGIN"]["api_hash"]
             )

app.run()