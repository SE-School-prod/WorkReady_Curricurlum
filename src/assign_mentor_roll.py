"""
@file assign_mentor_roll.py
@date 2025/02/28(金)
@author 藤原光基
@brief メンターロール割り当てbot
@brief Discordへの受講生参加時、担当メンター用ロールを割り振る。
@bar 編集日時 編集者 編集内容
@bar 2025/02/28(金) 藤原光基 新規作成
"""

import discord


async def assign_mentor_roll(member):

    try:
        instructor_roll_name = "メンター00001_藤原浩司"

        role_begginer = discord.utils.get(member.guild.roles, name=instructor_roll_name)
        await member.add_roles(role_begginer)

    except Exception as e:
        print(f"assign_course_roll errored: status_code: {e.status_code}, error: {e.text}")
        raise e
