import os
import discord
from discord.commands import option
from dotenv import load_dotenv
from io import BytesIO
from random import randint, choice
import math
import json
import requests
from prettytable import PrettyTable
from collections import Counter
import time

intents = discord.Intents.default()
intents.messages = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = discord.Bot() # Create a bot object

class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="😎") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked

@bot.slash_command() # Create a slash command
async def button(ctx):
    await ctx.respond("This is a button!", view=MyView()) # Send a message with our View class that contains the button

bot.run(TOKEN) # Run the bot
