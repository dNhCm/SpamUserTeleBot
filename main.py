import asyncio
from configparser import ConfigParser
from typing import Any

from pyrogram import Client

import time as t

from pyrogram.types import Chat


async def error(func) -> Any:
	async def find_error():
		try:
			await func()
		except Exception as ex:
			with open("errors.txt", "a") as errors:
				print("\033[31m Error!")
				errors.write(f"\n\r {ex}")

	return await find_error()


class Postman:
	info = ConfigParser()
	info.read('settings.ini', encoding='UTF-8')

	app: Client

	@classmethod
	async def checkpoint_info_updating(cls):
		"""
		Check if information has changed in config, and if yes, then update it to new one.

		:return:
		"""

		while True:
			await asyncio.sleep(5)

			new_info = ConfigParser()
			new_info.read("settings.ini", encoding='UTF-8')

			new_info_sections = new_info.sections()
			new_info_sections.remove("POST")

			info_sections = cls.info.sections()
			info_sections.remove("POST")

			is_break = False
			for new_info_section, info_section in zip(new_info_sections, info_sections):
				new_info_vars = new_info[new_info_section]
				info_vars = cls.info[info_section]

				for new_info_v, info_v in zip(new_info_vars, info_vars):
					if not new_info_vars[new_info_v] == info_vars[info_v]:
						cls.info = new_info

						print("\033[32m Settings changes successfully accepted!")

						cls.info.set("POST", "last_sent_time", str(t.time()))
						with open('settings.ini', 'w', encoding="UTF-8") as info:
							cls.info.write(info)

						await cls.parse_ids()

						is_break = True
						break

				if is_break:
					break

	@classmethod
	async def parse_ids(cls):
		await error(cls.parsing_groups_ids)
		print("\033[32m ID group successfully parsed!")
		await error(cls.parsing_people_ids)
		print("\033[32m ID people successfully parsed!")
			
		with open("settings.ini", "w", encoding="UTF-8") as info:
			cls.info.write(info)

	@classmethod
	async def parsing_groups_ids(cls):
		"""
		Parse groups ids by link that gives by user
		Check if our agent account is in chat.
		Because without it, we can't to parse id
		As a consequence can't parse members

		:return:
		"""

		async with cls.app:
			groups_links = cls.info["SETTINGS"]["groups_links"].split(' ')

			cls.info.set("POST", "groups_ids", '')
			for group_link in groups_links:
				chat: Chat = await cls.app.get_chat(group_link)

				if not type(chat) is Chat:
					continue

				if cls.info["POST"]["groups_ids"] == '':
					cls.info.set("POST", "groups_ids", str(chat.id))
				else:
					cls.info.set("POST", "groups_ids", f'{cls.info["POST"]["groups_ids"]} {chat.id}')

	@classmethod
	async def parsing_people_ids(cls):
		"""
		Parsing by already parsed groups ids members ids of these chats
		It changes only configs, so save all to configs

		:return:
		"""

		async with cls.app:
			groups_ids = list(map(int, cls.info["POST"]["groups_ids"].split(' ')))
			
			cls.info.set("POST", "people_ids", '')
			for group_id in groups_ids:
				members = cls.app.get_chat_members(chat_id=group_id)
				if type(members) is None:
					continue

				async for member in members:
					if not member.user.is_bot and not member.user.is_scam:
						if cls.info["POST"]["people_ids"] == '':
							cls.info.set("POST", "people_ids", str(member.user.id))
						else:
							cls.info.set("POST", "people_ids", f'{cls.info["POST"]["people_ids"]} {member.user.id}')

	@classmethod
	async def regulator(cls):
		"""
		Regulate sending by parameter send_method

		:return:
		"""
		while True:
			await asyncio.sleep(5)

			if cls.info["SETTINGS"]["send_method"] == "now":
				await cls.post_now()
			elif cls.info["SETTINGS"]["send_method"] == "interval":
				await cls.interval_post()

	@classmethod
	async def post_now(cls):
		"""
		Post, changes send method from now to interval with hour interval time, and save these values

		:return:
		"""

		# Now sending
		await error(cls.posting)

		# Updating of the self.info
		cls.info.set("SETTINGS", "send_method", "interval")
		cls.info.set("SETTINGS", "interval_time", "60")
		
		# Saving updates of the self.info
		with open("settings.ini", "w", encoding="UTF-8") as info:
			cls.info.write(info)

	@classmethod
	async def interval_post(cls):
		"""
		If it's time to send, then send, else wait for a next checking

		:return:
		"""

		# Checkpoint if it's time to send
		if float(cls.info["POST"]["last_sent_time"]) - t.time() + float(cls.info["SETTINGS"]["interval_time"])*60 <= 0:
			# Send
			await error(cls.posting)

			# Update and saving last sent time
			cls.info.set("POST", "last_sent_time", str(t.time()))
			with open("settings.ini", "w", encoding="UTF-8") as info:
				cls.info.write(info)

	@classmethod
	async def posting(cls):
		"""
		Send message to groups or people by send_to_whom parameter

		:return:
		"""

		async with cls.app:
			if cls.info["SETTINGS"]["send_to_whom"] == "people":
				text = cls.info["SETTINGS"]["people_txt"]
				chat_ids = cls.info["POST"]["people_ids"].split(' ')
			elif cls.info["SETTINGS"]["send_to_whom"] == "groups":
				text = cls.info["SETTINGS"]["groups_txt"]
				chat_ids = cls.info["POST"]["groups_ids"].split(' ')

			for chat_id in chat_ids:
				await cls.app.send_message(chat_id=chat_id, text=text)
				print("\033[32m Text sent successfully")

	@classmethod
	async def main(cls):
		config = ConfigParser()
		config.read('setup.ini')
		cls.app = Client("SoRB", api_id=int(config["LOGIN"]["api_id"]), api_hash=config["LOGIN"]["api_hash"])
		print("\033[32m Successful account login!")

		await cls.parse_ids()

		await asyncio.gather(
			cls.regulator(),
			cls.checkpoint_info_updating(),
		)


def main():
	asyncio.run(Postman.main())


if __name__ == "__main__":
	main()
