from redbot.core import commands
from datetime import datetime
import discord
import re

class autoMod(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, msg):
		
		#Block markdown urls
		if "](http" in msg.content.lower() or "](<http" in msg.content.lower() or " discord.gg" in msg.content.lower():
			if "](https://cdn.discordapp.com/" in msg.content.lower() or "](https://media.discordapp.net/" in msg.content.lower():
				return
			await self.block(msg, '** Fake Markdown URL blocked by user:** ' + msg.author.name + ' [' + str(msg.author.id) + ']')

		#Block discord invites with suspicious servers
		elif "discord.gg" in msg.content.lower():
			blacklist = ['nude','adult','onlyfan','porn','leaks','sex','18','teen','xxx','tiktok','nsfw','girls','exotic','hentai','18+']
			in_blacklist = any([url in msg.content.lower() for url in blacklist])
			if in_blacklist:
				await self.block(msg, '** Suspicious URL blocked by user:** ' + msg.author.name + ' [' + str(msg.author.id) + ']')

		#Block use of @everyone tag
		elif "@everyone" in msg.content:
			await self.block(msg, '** Use of @everyone by:** ' + msg.author.name + ' [' + str(msg.author.id) + ']')

		#Block use of non-whitelisted domains by new users
		else:
			#check server age of user id
			join_date = msg.author.joined_at.replace(tzinfo=None)
			current_date = datetime.utcnow().replace(tzinfo=None)
			time_on_server = current_date - join_date
			minutes_on_server = round(time_on_server.total_seconds() / 60)
			
			if minutes_on_server < 30:
				#check for url in message		
				url_pattern = re.compile(r'https?://\S+')
				if url_pattern.search(msg.content.lower()):
					whitelist = ['modding-guild.com', 'skyrim-guild.com', 'nexusmods.com', 'youtube.com', 'tenor.com', 'pastebin.com']
					in_whitelist = any([url in msg.content.lower() for url in whitelist])
					if not in_whitelist:
						await self.block('**URL blocked by new user:** ' + msg.author.name + ' [' + str(msg.author.id) + ']')

	async def block(self, msg, report):
		#Ignore if user is Umbrael or Staff
		staff_role = discord.utils.get(msg.guild.roles, id=1059586973033050142)
		if msg.author == self.bot.user or staff_role in msg.author.roles:
			return
		else:
			automod_channel = self.bot.get_channel(1196506188821561506)
			await automod_channel.send(report)
			message_content =  msg.content
			#Format markdown url and @ in text so they don't trigger
			message_content = message_content.replace('[', '**[**')
			message_content = message_content.replace(']', '**]**')
			message_content = message_content.replace('@', '**@**')
			await automod_channel.send('>>> ' + message_content)
			await msg.delete()