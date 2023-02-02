import discord
from discord.ext import commands
import datetime
import aiosqlite
import asyncio
from discord.commands import Option
import chat_exporter
import io
import json
class Mail(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_ready(self):
		setattr(self, "users", await aiosqlite.connect("./Database/user.db"))
		setattr(self, "threads", await aiosqlite.connect("./Database/threads.db"))
		setattr(self, "config", await aiosqlite.connect("./Database/setup.db"))
		setattr(self, "embed", await aiosqlite.connect("./Database/embed.db"))
		await asyncio.sleep(2)
		async with self.users.cursor() as cursor:
			await cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, guild_id INTEGER, anonymous BOOL)")
		async with self.threads.cursor() as cursor:
			await cursor.execute("CREATE TABLE IF NOT EXISTS threads(user_id INTEGER, guild_id INTEGER, channel_id INTEGER)")

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		if message.content == "":
			if message.attachments == []:
				return
			else:
				for attachment in message.attachments:
					#Append the attachment url with \n 
					message.content += f"{attachment.url}\n"
		elif message.content == None:
			if message.attachments:
				for attachment in message.attachments:
					#Append the attachment url with \n 
					message.content += f"{attachment.url}\n"
		if isinstance(message.channel, discord.DMChannel):
			async with self.users.cursor() as cursor:
				await cursor.execute("SELECT * FROM users WHERE user_id = ?", (message.author.id,))
				guild_info = await cursor.fetchone()
				if guild_info is None:
					mutual_guilds = message.author.mutual_guilds
					if len(mutual_guilds) == 0:
						return
					else:
						guild_list = []
						for guild in mutual_guilds:
							async with self.config.cursor() as cursor:
								await cursor.execute("SELECT * FROM setup WHERE guild_id = ?", (guild.id,))
								guild_info = await cursor.fetchone()
								if guild_info is None:
									continue
								elif guild_info[3] == 0:
									continue
								else:
									guild_list.append(guild)
						if len(guild_list) == 0:
							return

						text_string = ""
						for guild_id in guild_list:
							text_string += f"{guild_id.id} - {guild_id.name}\n"
						embed = discord.Embed(title = ":wave: Hey there!", description=f":x: Thank you for reaching support channels. However, I see that you have not selected any guild you wish to send your message to.\n :white_check_mark: Please select one of the following guilds you wish to send your message to by using `/choose` command.\n\n `{text_string}`", color = 0xf01e2c)
						await message.channel.send(embed = embed)
						return
				else:
					guild_id = guild_info[1]
					async with self.config.cursor() as cursor:
						await cursor.execute("SELECT * FROM setup WHERE guild_id = ?", (guild_id,))
						guild_info = await cursor.fetchone()
						if guild_info is None:
							return
						elif guild_info[3] == 0:
							return
						else:
							guild = self.bot.get_guild(guild_id)
							if guild is None:
								return
							async with self.threads.cursor() as cursor:
								await cursor.execute("SELECT * FROM threads WHERE user_id = ? AND guild_id = ?", (message.author.id,guild_id,))
								thread_info = await cursor.fetchone()
								if thread_info is None:
									category_id = guild_info[1]
									log_channel_id = guild_info[2]
									log_channel = self.bot.get_channel(log_channel_id)
									if log_channel is not None:
										new_thread_embed = discord.Embed(title = "📝New Ticket", description = f"👤**User:** {message.author.mention}\n📄**User Name:** {message.author.name}#{message.author.discriminator}", color = 0x502380)
										new_thread_embed.set_thumbnail(url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
										new_thread_embed.set_footer(text = f"User ID: {message.author.id}")
										try:
											await log_channel.send(embed = new_thread_embed)
										except:
											pass
									#Create a new channel
									category = discord.utils.get(guild.categories, id = category_id)
									if category is None:
										return
									channel = await guild.create_text_channel(name = f"ticket-{message.author.name}", category = category)
									#Add channel id and user id to database
									async with self.threads.cursor() as cursor:
										await cursor.execute("INSERT INTO threads (channel_id, user_id, guild_id) VALUES (?, ?, ?)", (channel.id, message.author.id, guild_id,))
										await self.threads.commit()
									#Send the message to the thread
									first_embed = discord.Embed(title = "📬 New Message", description = f"{message.author.name}#{message.author.discriminator} wishes to contact support.\nℹ️ All their messages to this bot will now be sent to this channel.", color = discord.Color.og_blurple())
									await channel.send(embed = first_embed)
									embed = discord.Embed(description = message.content, color = 0xf01e2c)
									embed.set_author(name = f"{message.author.name}#{message.author.discriminator}", icon_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
									embed.set_footer(text = f"User ID: {message.author.id}")
									await channel.send(embed = embed)
									#Send the message to the user
									async with self.embed.cursor() as dragger:
										await dragger.execute("SELECT * FROM embed WHERE guild_id = ?", (guild_id,))
										embed_info = await dragger.fetchone()
										if embed_info is None:
											embed = discord.Embed(title = ":white_check_mark: Message sent!", description = f"✅ Your message has been sent to {guild.name}.\nℹ️ A support member will be with you shortly!", color = 0xf01e2c)
											await message.channel.send(embed = embed)
											return
										else:
											embed_json = embed_info[1]
											try:
												embed = discord.Embed().from_dict(json.loads(embed_json))
												#Get embed's description if any
												description = embed.description
												if description:
													#Replace the placeholders
													description = description.replace("{user.name}", message.author.author)
													description = description.replace("{user.id}", str(message.author.id))
													description = description.replace("{user.mention}", message.author.mention)
													description = description.replace("{user.discriminator}", message.author.discriminator)
												#Get thumbnail
												thumbnail = embed.thumbnail
												if thumbnail:
													#Replace the placeholders
													thumbnail = thumbnail.replace("{user.avatar}", message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
													
												await message.channel.send(embed = embed)
											except:
												embed = discord.Embed(title = ":white_check_mark: Message sent!", description = f"✅ Your message has been sent to {guild.name}.\nℹ️ A support member will be with you shortly!", color = 0xf01e2c)
												await message.channel.send(embed = embed)
												return
								else:
									channel_id = thread_info[2]
									channel = self.bot.get_channel(channel_id)
									if channel is None:
										return
									
									embed = discord.Embed(title = f"✉️ New message from {message.author.name}", description = message.content, color = 0xf01e2c)
									embed.set_footer(text = f"User ID: {message.author.id}", icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
									await channel.send(embed = embed)
									embed = discord.Embed(title = ":white_check_mark: Message sent!", description = f"✅ Your message has been sent to {guild.name}.", color = 0xf01e2c)
									await message.channel.send(embed = embed)
									return
		if isinstance(message.channel, discord.TextChannel):
			async with self.threads.cursor() as cursor:
				await cursor.execute("SELECT * FROM threads WHERE channel_id = ?", (message.channel.id,))
				thread_info = await cursor.fetchone()
				if thread_info is None:
					return
				else:
					user_id = thread_info[0]
					user = self.bot.get_user(user_id)
					if user is None:
						return
					async with self.users.cursor() as cursor:
						await cursor.execute("SELECT * FROM users WHERE user_id = ?", (message.author.id,))
						user_info = await cursor.fetchone()
						if user_info is not None:
							anonymity = user_info[2]
							if anonymity == 1:
								embed = discord.Embed(title = f"✉️ New message from {message.guild.name}", description = message.content, color = 0xEFD033, timestamp = datetime.datetime.utcnow())
								await user.send(embed = embed)
								#Add reaction to message
								await message.add_reaction("✔️")
								return
					embed = discord.Embed(title = f"✉️ New message from {message.guild.name}", description = message.content, color = 0xEFD033, timestamp = datetime.datetime.utcnow())
					embed.set_author(name = f"{message.author.name}#{message.author.discriminator}", icon_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
					await user.send(embed = embed)
					#Add reaction to message
					await message.add_reaction("✅")
					return


############################################################################################################################################################################################################################################################################
# 																															 Thread related commands#																														 


	@commands.slash_command(name = "choose", description = "Choose a guild to send your message to.")
	@commands.dm_only()
	async def choose(self, ctx, guild_id: Option(str, "The guild you wish to bound your messages to.")):
		try:
			guild_id = int(guild_id)
		except:
			embed = discord.Embed(title = ":x: Invalid Input", description=f"⚠️ {guild_id} is not a valid guild ID. You need to enter guild ID to use this command.\nℹ️ You can refer the documentation to know how to get the guild id!", color = 0xf01e2c)
			await ctx.respond(embed = embed)
			return
		async with self.config.cursor() as cursor:
			await cursor.execute("SELECT * FROM setup WHERE guild_id = ?", (guild_id,))
			guild_info = await cursor.fetchone()
			if guild_info is None:
				no_config_found_embed = discord.Embed(title = ":x: No Config Found", description=f"⚠️ This server do not have any configuration setup. Please ask the server administrators to complete my [setup](https://google.com)", color = 0xf01e2c)
				await ctx.respond(embed = no_config_found_embed)
				return
			elif guild_info[3] == 0:
				disabled_error_embed = discord.Embed(title = "😞 Disabled Modmail", description=f":x: This server is not accepting any more modmail threads.\n :white_check_mark: Please contact an admin of the server for further information.", color = 0xf01e2c)
				await ctx.respond(embed = disabled_error_embed)
				return
			else:
				async with self.users.cursor() as pointer:
					await pointer.execute("SELECT * FROM users WHERE user_id = ?", (ctx.author.id,))
					user_info = await pointer.fetchone()
					if user_info is None:
						await pointer.execute("INSERT INTO users VALUES (?, ?, ?)", (ctx.author.id, guild_id, 0))
						await self.users.commit()
						embed = discord.Embed(title = ":white_check_mark: Success", description=f"ℹ️ You have successfully bound your messages to {guild_id}.\n Any messages you now send to me, I will redirect it to that guild only.", color = 0xffb933)
						await ctx.respond(embed = embed)
						return
					else:
						await pointer.execute("UPDATE users SET guild_id = ? WHERE user_id = ?", (guild_id, ctx.author.id))
						await self.users.commit()
						embed = discord.Embed(title = ":white_check_mark: Success", description=f"ℹ️ You have successfully bound your messages to {guild_id}.\n Any messages you now send to me, I will redirect it to that guild only.", color = 0xffb933)
						await ctx.respond(embed = embed)
						return

	@commands.slash_command(name = "anonymous", description = "👤 Send an anonymous message to the user. (Can only be used in tickets)")
	@commands.guild_only()
	async def anonymous(self, ctx):
		#If channel is not a ticket, return
		async with self.threads.cursor() as cursor:
			await cursor.execute("SELECT * FROM threads WHERE channel_id = ?", (ctx.channel.id,))
			thread_info = await cursor.fetchone()
			if thread_info is None:
				not_a_ticket_embed = discord.Embed(title = ":x: Not a ticket", description=f"⚠️ This channel is not a ticket. You can only use this command in a ticket.", color = 0xf01e2c)
				await ctx.respond(embed = not_a_ticket_embed)
				return
			else:
				async with self.users.cursor() as pointer:
					await pointer.execute("SELECT * FROM users WHERE user_id = ?", (thread_info[0],))
					user_info = await pointer.fetchone()
					if user_info is None:
						#Insert into db.
						await pointer.execute("INSERT INTO users(user_id, anonymous) VALUES (?, ?)", (ctx.author.id, 1))
						await self.users.commit()
						embed = discord.Embed(title = ":white_check_mark: Success", description=f"ℹ️ You have successfully enabled anonymous mode for all threads.\n Any messages you now send to me, I will send it to the user anonymously.", color = 0xffb933)
						await ctx.respond(embed = embed)
					else:
						#get the current value of anonymous
						if user_info[2] == 0 or user_info[2] == None:
							value = 1
							mode = "enabled"

						else:
							value = 0
							mode = "disabled"
						await pointer.execute("UPDATE users SET anonymous = ? WHERE user_id = ?", (value, ctx.author.id))
						await self.users.commit()
						embed = discord.Embed(title = ":white_check_mark: Success", description=f"ℹ️ You have successfully {mode} the anonymous mode for all threads.\n Any messages you now send to me, I will send it to the user anonymously.", color = 0xffb933)
						await ctx.respond(embed = embed)

	@commands.slash_command(name = "close", description = "🔒 Close the current modmail.")
	async def close_command(self, ctx):
		await ctx.defer()
		if isinstance(ctx.channel, discord.PartialMessageable):
			if ctx.channel.type == discord.ChannelType.private:
				async with self.users.cursor() as cursor1:
					await cursor1.execute("SELECT * FROM users WHERE user_id = ?", (ctx.author.id,))
					user_info = await cursor1.fetchone()
					if user_info is None:
						no_thread_embed = discord.Embed(title = ":x: No thread", description=f"⚠️ You do not have an active thread in this server. Please make sure right server is selected.", color = 0xf01e2c)
						await ctx.respond(embed = no_thread_embed)
						return
					else:
						async with self.threads.cursor() as cursor2:
							await cursor2.execute("SELECT * FROM threads WHERE user_id = ? AND guild_id = ?", (ctx.author.id,user_info[1]))
							thread_info = await cursor2.fetchone()
							if thread_info is None:
								no_thread_embed = discord.Embed(title = ":x: No thread", description=f"⚠️ You do not have an active thread in this server. Please make sure right server is selected.", color = 0xf01e2c)
								await ctx.respond(embed = no_thread_embed)
								return
							else:
								#Generate a transcript.
								#Get the channel
								channel = self.bot.get_channel(thread_info[2])
								if not channel:
									no_thread_embed = discord.Embed(title = ":x: No thread", description=f"⚠️ Your thread was not found in the server. Please make sure, you have an active thread.\nℹ️ Incase you find this as an error, you may contact the [Support Server](https://discord.gg/cortexbotservices).", color = 0xf01e2c)
									await ctx.respond(embed = no_thread_embed)
									return
								else:
									#Get the guild's log channel from config
									async with self.config.cursor() as cursor3:
										await cursor3.execute("SELECT log_channel FROM setup WHERE guild_id = ?", (channel.guild.id,))
										log_channel = await cursor3.fetchone()
										if log_channel is not None:
											log_channel = channel.guild.get_channel(log_channel[0])
											if log_channel:
												#Generate the trasncript and send it to the log channel.
												transcript_bytes = await chat_exporter.export(channel)
												transcript = discord.File(io.BytesIO(transcript_bytes.encode()), filename=f"scritp-{channel.name}.html")
												#Make and send an embed to the log channel that thread closed.
												embed = discord.Embed(title = ":white_check_mark: Thread closed", description=f"ℹ️ Thread closed by {ctx.author.mention}.", color = 0xffb933, timestamp=datetime.datetime.utcnow())
												embed.add_field(name = "Details", value = f"🆔Thread ID: {channel.id}")

												try:
													await log_channel.send(embed = embed)
													await log_channel.send(file = transcript)
												except:
													pass
									#Make an embed.
									embed = discord.Embed(title = ":white_check_mark: Thread closed", description=f"ℹ️ Your thread has been closed. You can open a new thread by sending a message to me.", color = 0xffb933)
									await ctx.respond(embed = embed)
									#Delete the thread from the database.
									await cursor2.execute("DELETE FROM threads WHERE user_id = ? AND guild_id = ?", (ctx.author.id,user_info[1]))
									await self.threads.commit()
									#Delete the channel
									await channel.delete()
									#Delete the user from the database.
		#Else if its a guild channel
		else:
			#Check if the channel is a thread channel.
			async with self.threads.cursor() as cursor:
				await cursor.execute("SELECT * FROM threads WHERE channel_id = ?", (ctx.channel.id,))
				thread_info = await cursor.fetchone()
				if thread_info is None:
					no_thread_embed = discord.Embed(title = ":x: No thread", description=f"⚠️ This channel is not a thread channel. Please make sure you are in a thread channel.", color = 0xf01e2c)
					await ctx.respond(embed = no_thread_embed)
					return
				else:
					thread_user = self.bot.get_user(thread_info[0])
					async with self.users.cursor() as cursor1:
						await cursor1.execute("SELECT * FROM users WHERE user_id = ?", (thread_info[0],))
						user_info = await cursor1.fetchone()
						if not user_info:
							no_user_found_err = discord.Embed(title = ":x: No user found", description=f"⚠️ The user was not found in the database. Please contact the [Support Server](https://discord.gg/cortexbotservices).", color = 0xf01e2c)
							await ctx.respond(embed = no_user_found_err)
							return
						else:
							#Create a transcript.
							transcript = await chat_exporter.export(ctx.channel)
							transcript = discord.File(io.BytesIO(transcript.encode()), filename=f"scritp-{ctx.channel.name}.html")
							#Get log channel 
							async with self.config.cursor() as cursor2:
								await cursor2.execute("SELECT log_channel FROM setup WHERE guild_id = ?", (ctx.guild.id,))
								log_channel = await cursor2.fetchone()
								if log_channel is not None:
									log_channel = ctx.guild.get_channel(log_channel[0])
									if log_channel:
										#Make and send an embed to the log channel that thread closed.
										embed = discord.Embed(title = ":white_check_mark: Thread closed", description=f"ℹ️ Thread closed by {ctx.author.mention}.", color = 0xffb933, timestamp=datetime.datetime.utcnow())
										embed.add_field(name = "Details", value = f"🆔Thread ID: {ctx.channel.id}")

										try:
											await log_channel.send(embed = embed)
											await log_channel.send(file = transcript)
										except:
											pass
							#Make an embed.
							embed = discord.Embed(title = ":white_check_mark: Thread closed", description=f"ℹ️ Your thread has been closed. You can open a new thread by sending a message to me.", color = 0xffb933)
							await thread_user.send(embed = embed)
							#Delete the thread from the database.
							await cursor.execute("DELETE FROM threads WHERE user_id = ? AND guild_id = ?", (thread_user.id,user_info[1]))
							await self.threads.commit()
							#Delete user from the database.
							await ctx.respond("Thread closed.")
							#Delete the channel
							await ctx.channel.delete()

def setup(bot):
	bot.add_cog(Mail(bot))

