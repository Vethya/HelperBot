import html
from telethon import events
from telethon.tl.types import User
from .. import register, help_dict

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

help_dict.update({'Info': '**Commands:**\n- /info <entity> - Get entity info'})
