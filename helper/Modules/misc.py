from telethon import events
from helper import register, whitelisted_chats, help_dict, config
import html

@register(events.ChatAction())
async def leave(e):
    if e.user_added and (await e.client.get_me()).id in e.action_message.action.users:
        if e.chat_id not in whitelisted_chats:
            await e.reply('This bot is for <b>personal use</b> only! If you want to add it to your group please contact the owner of this bot for access!')
            await e.client.kick_participant(e.chat_id, 'me')
            return
        else:
            await e.reply('O! This chat is one of the whitelist ones you can use me here :)')

@register(events.NewMessage(incoming=True, pattern=r'/echo (.+)'))
async def echo(e):
    if e.sender_id not in config['config']['sudo_id']:
        await e.reply('This command can only be used my SUDOs or higher!')
        return

    await e.delete()
    await e.respond(e.pattern_match.group(1), reply_to=e.reply_to_msg_id, parse_mode=None)

help_dict.update({"Misc": "**Commands:**\n- /echo <text>: used by SUDO or higher to make the bot say something."})
