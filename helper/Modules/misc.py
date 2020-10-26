from telethon import events
from telethon.tl.types import User
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

ZWS = '\u200B'
def _generate_sexy(entity, ping):
    text = getattr(entity, 'title', None)
    if not text:
        text = entity.first_name
        if entity.last_name:
            text += f' {entity.last_name}'
    sexy_text = html.escape(text or 'Empty???')
    if ping and isinstance(entity, User):
        sexy_text = f'<a href="tg://user?id={entity.id}">{sexy_text}</a>'
    elif entity.username:
        sexy_text = f'<a href="https://t.me/{entity.username}">{sexy_text}</a>'
    elif not ping:
        sexy_text = sexy_text.replace('@', f'@{ZWS}')
    if getattr(entity, 'bot', None):
        sexy_text += ' <code>[BOT]</code>'
    if entity.verified:
        sexy_text += ' <code>[VERIFIED]</code>'
    if getattr(entity, 'support', None):
        sexy_text += ' <code>[SUPPORT]</code>'
    if entity.scam:
        sexy_text += ' <code>[SCAM]</code>'
    return sexy_text

@register(events.NewMessage(incoming=True, pattern=r'/(?:info|whois)(?:\s+(.+))?$'))
async def info(e):
    entity = e.pattern_match.group(1)
    if entity:
        try:
            entity = int(entity)
        except ValueError:
            pass
    else:
        r = await e.get_reply_message()
        if r:
            entity = await r.get_user()
        else:
            entity = e.sender or e.sender_id
    if isinstance(entity, (str, int)):
        entity = await e.client.get_entity(entity)
    text_ping = _generate_sexy(entity, True)
    text_unping = _generate_sexy(entity, False)
    text_ping += f'\n<b>ID:</b> <code>{entity.id}</code>'
    text_unping += f'\n<b>ID:</b> <code>{entity.id}</code>'
    if entity.username:
        text_ping += f'\n<b>Username:</b> @{entity.username}'
        text_unping += f'\n<b>Username:</b> @{ZWS}{entity.username}'
    if getattr(entity, 'participants_count', None) is not None:
        text_ping += f'\n<b>Members:</b> {entity.participants_count}'
        text_unping += f'\n<b>Members:</b> {entity.participants_count}'
    r = await e.reply(text_unping, parse_mode='html', link_preview=True)
    if text_ping != text_unping:
        await r.edit(text_ping, parse_mode='html')

help_dict.update({"Misc": "**Commands:**\n- /echo <text>: used by SUDO or higher to make the bot say something.\n- /info <entity> - Get entity info."})
