##
# @file main.py
# @date 2025/02/28(金)
# @author 藤原光基
# @brief 各bot実行用bot
##

import os

import discord
from discord.ext import tasks, commands

import keep_alive

from src.assign_mentor_roll import assign_mentor_roll
from src.assign_course_roll import assign_course_roll

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
client = discord.Client(intents=discord.Intents.all())


def main():

    @bot.event
    async def on_member_join(member):
        await assign_mentor_roll(member)
        await assign_course_roll(member)


if __name__ == "__main__":
    main()
    keep_alive.keep_alive()
    bot.run(os.environ["DISCORD_TOKEN"])
