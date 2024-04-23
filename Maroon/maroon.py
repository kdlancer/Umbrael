from redbot.core import commands
from datetime import datetime
import discord
import json
import time
import re

class maroon(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.settings = []

	def writeSettings(self):
		try:
			with open("maroon.settings.json", "w") as file:
				json.dump(self.settings, file)
		except:
			return None

	def loadSettings(self):
		try:
			with open("maroon.settings.json", "r") as file:
				self.settings = json.load(file)
		except:
			return None

	@commands.command()
	@commands.guild_only()
	@commands.mod_or_permissions(manage_messages=True)
	#Adds the helpless role to a person
	async def maroon(self, ctx, user: discord.Member, *query: str):
		self.loadSettings()
		
		#Combine entire query array into a string
		query = ' '.join(query).lower().strip()
				
		#Parse out the punishment time
		pattern = r'^(\d+)d'
		matches = re.search(pattern, query)
		if matches:
			num_days = int(matches.group(1))
		else:
			num_days = 5
		
		#Parse out the reason
		reason = query.replace(str(num_days)+'d', '').strip()
		if reason:
			await ctx.send(f"{user.mention} has lost their #help channel privileges for {num_days} days.")
		else:
			await ctx.send("A reason is required for marooning.")
			return
			
		#Epoch time at which time to remove the maroon
		until = time.time() + num_days * 86400
		
		#Add the Helpless role to the user
		helpless_role = ctx.guild.get_role(1232170560046366741)
		await user.add_roles(helpless_role)
		
		#Make sure there are no duplicates made
		for line in self.settings:
			if line['userid'] == user.id:
				self.settings.remove(line)
				
		self.settings.append({'userid': user.id, 'until': until, 'reason': reason})	
		self.writeSettings()
	
	@commands.Cog.listener()
	#Pseudo cron task to unmaroon people
	async def on_thread_create(self, thread):
		self.loadSettings()
		
		current_time = time.time()
		for line in self.settings:
			if current_time > line['until']:
				helpless_role = thread.guild.get_role(1232170560046366741)
				user = thread.guild.get_member(line['userid'])
				await user.remove_roles(helpless_role)
				self.settings.remove(line)
		
		self.writeSettings()
		
	@commands.command()
	@commands.guild_only()
	@commands.mod_or_permissions(manage_messages=True)
	#Returns list of all marooned users
	async def maroons(self, ctx):
		self.loadSettings()
		
		message = ''
		for line in self.settings:
			user = ctx.guild.get_member(line['userid'])
			#convert until time to human readable time
			until = datetime.fromtimestamp(float(line['until']))
			until = until.strftime('%B %d, %Y at %I:%M%p')
			
			message = message + f"@{user.name} is marooned until {until} days for: {line['reason']}\n"
		
		if message :
			await ctx.send('**Users currently maroone from #help:**\n' + message)
		else:
			await ctx.send("There are currently no users marooned.")
			
	@commands.command()
	@commands.guild_only()
	@commands.mod_or_permissions(manage_messages=True)
	#removes the helpless role from a person
	async def unmaroon(self, ctx, user: discord.Member):
		self.loadSettings()
		helpless_role = ctx.guild.get_role(1232170560046366741)
		i = 0
		for line in self.settings:
			if line['userid'] == user.id:
				i = i + 1
				self.settings.remove(line)
				await user.remove_roles(helpless_role)
				
		if i == 0:
			await ctx.send("That user is not currently marooned.")
		else:
			self.writeSettings()
			await ctx.send("User has regained their #help privileges.")