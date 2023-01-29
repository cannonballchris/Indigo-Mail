import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import aiosqlite
from asyncio import sleep
import json
import re

async def valid_hexcode(hex):
	match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hex)
	if match:
		return True
	else:
		return False

async def valid_color(color):
	#Replace # with 0x
	color = color.replace("#", "0x")
	#Convert to int
	color = int(color, 16)
	return color

class EmbedBuilder(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	embed = SlashCommandGroup("embed", description="⚙️Create a beautiful embed to be sent to users for the first time!")

	@commands.Cog.listener()
	async def on_ready(self):
		setattr(self, "db", await aiosqlite.connect("./Database/embed.db"))
		await sleep(2)
		async with self.db.cursor() as cursor:
			await cursor.execute("CREATE TABLE IF NOT EXISTS embed(guild_id INTEGER, embed TEXT)")

	@embed.command(name = "title", description = "📝 Set the title of the embed")
	@commands.has_permissions(manage_guild = True)
	async def title(self, ctx, title: Option(str, "🔍 The title of your beautiful embed")):
		await ctx.defer()
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"title": title}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				print(info[1])
				info = json.loads(info[1])

				#if there's already a title, replace it else add it
				if "title" in info:
					info["title"] = title
				else:
					info.update({"title": title})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				try:
					await ctx.send(embed=embed)
				except:
					await ctx.respond(embed = embed)
	
	@embed.command(name = "description", description = "📝 Set the description of the embed")
	@commands.has_permissions(manage_guild = True)
	async def description(self, ctx, description: Option(str, "🔍 The description of your beautiful embed")):
		await ctx.defer()
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"description": description}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				info = json.loads(info[1])
				#if there's already a description, replace it else add it
				if "description" in info:
					info["description"] = description
				else:
					info.update({"description": description})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				await ctx.send(embed=embed)
	
	@embed.command(name = "color", description = "🎨 Set the color of the embed")
	@commands.has_permissions(manage_guild = True)
	async def color(self, ctx, color: Option(str, "🔍 The color of your beautiful embed")):
		await ctx.defer()
		if await valid_hexcode(color) == False:
			embed = discord.Embed(title = "#️⃣ Invalid Hexcode",description="❌ That is not a valid hex code!\nℹ️ A valid hexcode begins with `#` and is of 6 characters.",color = 0xf01e2c)
			await ctx.respond(embed=embed)
			return
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"color": await valid_color(color)}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				info = json.loads(info[1])
				#if there's already a color, replace it else add it
				if "color" in info:
					info["color"] = await valid_color(color)
				else:
					info.update({"color": await valid_color(color)})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				await ctx.send(embed=embed)
		
	@embed.command(name = "footer", description = "📝 Set the footer of the embed")
	@commands.has_permissions(manage_guild = True)
	async def footer(self, ctx, footer: Option(str, "🔍 The footer of your beautiful embed")):
		await ctx.defer()
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"footer": {"text": footer}}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				info = json.loads(info[1])
				#if there's already a footer, replace it else add it
				if "footer" in info:
					info["footer"]["text"] = footer
				else:
					info.update({"footer": {"text": footer}})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				await ctx.send(embed=embed)

	@embed.command(name = "thumbnail", description = "🖼️ Set the thumbnail of the embed")
	@commands.has_permissions(manage_guild = True)
	async def thumbnail(self, ctx, thumbnail: Option(str, "🔍 The thumbnail of your beautiful embed")):
		await ctx.defer()
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"thumbnail": {"url": thumbnail}}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				info = json.loads(info[1])
				#if there's already a thumbnail, replace it else add it
				if "thumbnail" in info:
					info["thumbnail"]["url"] = thumbnail
				else:
					info.update({"thumbnail": {"url": thumbnail}})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				if "{user.avatar}" in info["thumbnail"]["url"]:
					info["thumbnail"]["url"] = info["thumbnail"]["url"].replace("{user.avatar}", str(ctx.author.avatar.url or ctx.author.default_avatar.url))

				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				#if {user.avatar} in embed's thumbnail url: replace it with the user's avatar
				await ctx.send(embed=embed)

	@embed.command(name = "image", description = "🖼️ Set the image of the embed")
	@commands.has_permissions(manage_guild = True)
	async def image(self, ctx, image: Option(str, "🔍 The image of your beautiful embed")):
		await ctx.defer()
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"image": {"url": image}}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				info = json.loads(info[1])
				#if there's already a image, replace it else add it
				if "image" in info:
					info["image"]["url"] = image
				else:
					info.update({"image": {"url": image}})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				await ctx.send(embed=embed)

	@embed.command(name = "author", description = "🖼️ Set the author of the embed")
	@commands.has_permissions(manage_guild = True)
	async def author(self, ctx, author: Option(str, "🔍 The author of your beautiful embed")):
		await ctx.defer()
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"author": {"name": author}}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				info = json.loads(info[1])
				#if there's already a author, replace it else add it
				if "author" in info:
					info["author"]["name"] = author
				else:
					info.update({"author": {"name": author}})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				await ctx.send(embed=embed)
		
	@embed.command(name = "author_icon", description = "🖼️ Set the author icon of the embed")
	@commands.has_permissions(manage_guild = True)
	async def author_icon(self, ctx, author_icon: Option(str, "🔍 The author icon of your beautiful embed")):
		await ctx.defer()
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"author": {"icon_url": author_icon}}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				info = json.loads(info[1])
				#if there's already a author, replace it else add it
				if "author" in info:
					info["author"]["icon_url"] = author_icon
				else:
					info.update({"author": {"icon_url": author_icon}})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				await ctx.send(embed=embed)

	@embed.command(name = "author_url", description = "🖼️ Set the author url of the embed")
	@commands.has_permissions(manage_guild = True)
	async def author_url(self, ctx, author_url: Option(str, "🔍 The author url of your beautiful embed")):
		await ctx.defer()
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"author": {"url": author_url}}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				info = json.loads(info[1])
				#if there's already a author, replace it else add it
				if "author" in info:
					info["author"]["url"] = author_url
				else:
					info.update({"author": {"url": author_url}})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				await ctx.send(embed=embed)

	@embed.command(name = "field", description = "🖼️ Set the field of the embed")
	@commands.has_permissions(manage_guild = True)
	async def field(self, ctx, name: Option(str, "🔍 The name of the field"), value: Option(str, "🔍 The value of the field"), inline: Option(str, "🔍 The inline of the field", choices = ["true", "false"])):
		if inline == "true":
			inline = True
		elif inline == "false":
			inline = False
		await ctx.defer()
		async with self.db.cursor() as cursor:
			await cursor.execute("SELECT * FROM embed WHERE guild_id = ?", (ctx.guild.id,))
			info = await cursor.fetchone()
			if not info:
				new_info = {"fields": [{"name": name, "value": value, "inline": inline}]}
				await cursor.execute("INSERT INTO embed(guild_id, embed) VALUES(?, ?)", (ctx.guild.id, json.dumps(new_info)))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(new_info)
				await ctx.send(embed=embed)
			else:
				info = json.loads(info[1])

				if "fields" in info:
					del info["fields"][0]
					info["fields"].append({"name": name, "value": value, "inline": inline})
				else:
					info.update({"fields": [{"name": name, "value": value, "inline": inline}]})
				await cursor.execute("UPDATE embed SET embed = ? WHERE guild_id = ?", (json.dumps(info), ctx.guild.id))
				await self.db.commit()
				embed = discord.Embed(description="👍 Okay, I am now sending the embed below to showcase how it looks currently.",color = 0xFFDBAF)
				await ctx.respond(embed=embed)
				embed = discord.Embed().from_dict(info)
				await ctx.send(embed=embed)

		


		#check if the color is valid
		



def setup(bot):
	bot.add_cog(EmbedBuilder(bot))

	#load the embed from a json
	
	
	