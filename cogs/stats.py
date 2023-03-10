import discord
from discord.ext import commands


class Stats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.slash_command(name = "stats", description = "â Shows all the information of the bot.")
	async def stats(self, ctx):
		total_guilds = len(self.bot.guilds)
		total_users = len(self.bot.users)
		pycord_version = discord.__version__
		bot_version = "1.0.0"
		ping = round(self.bot.latency * 1000)
		embed = discord.Embed(title = "đ Indigo Mail Stats", description = "âšī¸ Here are some stats about Indigo Mail.", color = 0x36393F)
		embed.add_field(name = "đĨ Total Guilds", value = f"> {total_guilds}", inline = False)
		embed.add_field(name = "đ¤ Total Users", value = f"> {total_users}", inline = False)
		embed.add_field(name = "đĻ Pycord Version", value = f"> {pycord_version}", inline = False)
		embed.add_field(name = "đĻ Bot Version", value = f"> {bot_version}", inline = False)
		embed.add_field(name = "đĄ Ping", value = f"> {ping}ms", inline = False)
		await ctx.respond(embed = embed)

def setup(bot):
	bot.add_cog(Stats(bot))
