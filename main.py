import discord
from discord.ext import commands
from colorama import Fore
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("TOKEN")
class IndigoMail(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix='!', intents = intents)
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"{Fore.GREEN} INFO | Loaded {filename}{Fore.RESET}")
                except Exception as e:
                    print(f"{Fore.RED} ERROR | Failed to load {filename}{Fore.RESET}")
                    print(f"{Fore.RED} REASON | {e}{Fore.RESET}")
                    

    async def on_ready(self):
        print(f"{Fore.GREEN} INFO | Logged in as {self.user.name}#{self.user.discriminator} ({self.user.id}){Fore.RESET}")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your modmails"))
        
    
if __name__ == "__main__":
    bot = IndigoMail()
    bot.run(TOKEN)

