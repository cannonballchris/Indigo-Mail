import discord
from discord.ext import commands


class Stats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.slash_command(name = "stats", description = "✅ Shows all the information of the bot.")
	async def stats(self, ctx):
		total_guilds = len(self.bot.guilds)
		total_users = len(self.bot.users)
		total_channels = len(self.bot.channels)
		pycord_version = discord.__version__
		bot_version = "1.0.0"
		ping = round(self.bot.latency * 1000)
		embed = discord.Embed(title = "📊 Indigo Mail Stats", description = "ℹ️ Here are some stats about Indigo Mail.", color = 0x36393F)
		embed.add_field(name = "👥 Total Guilds", value = f"> {total_guilds}", inline = False)
		embed.add_field(name = "👤 Total Users", value = f"> {total_users}", inline = False)
		embed.add_field(name = "📁 Total Channels", value = f"> {total_channels}", inline = False)
		embed.add_field(name = "📦 Pycord Version", value = f"> {pycord_version}", inline = False)
		embed.add_field(name = "📦 Bot Version", value = f"> {bot_version}", inline = False)
		embed.add_field(name = "📡 Ping", value = f"> {ping}ms", inline = False)
		await ctx.respond(embed = embed)

def setup(bot):
	bot.add_cog(Stats(bot))
