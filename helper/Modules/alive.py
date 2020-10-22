from helper import register, help_dict, config
from telethon import events
from telethon import Button
import time
import asyncio

data = {}

@register(events.NewMessage(pattern=r'/(?:start|alive)$'))
async def start(e):
    r = await e.client.send_message(
            e.chat_id,
            "<b>Yes, I'm alive!</b>\nPython version: <code>3.8.5</code>\nTelethon version: <code>1.10.10</code>",
            reply_to=e.id,
            buttons=
            [
                [Button.url('Pyrogram', url='docs.pyrogram.org'), Button.url('Python', url='python.org'), Button.url('Telethon', url='docs.telethon.dev')],
                [Button.inline('More', data='alive_more')]
            ])
    data[(e.chat_id, r.id)] = e.sender_id

morebutton_lock = asyncio.Lock()
@register(events.CallbackQuery())
async def more_button(e):
    async with morebutton_lock:
        if e.data == b'alive_more':
            if e.sender_id not in config['config']['owner_id']:
                await e.answer('Only sudo or higher can use this button!', alert=True)
                return
            if e.sender_id not in config['config']['owner_id']:
                await e.answer('Only sudo or higher can use this button!', alert=True)
                return
            try:
                if e.sender_id != data[(e.chat_id, e.message_id)]:
                    await e.answer('...no', cache_time=3600)
                    return
            except KeyError:
                await e.answer()
                return
            try:
                await e.answer()
                owner_names = []
                sudo_names = []
                for owner in config['config']['owner_id']:
                    owner_name = (await e.client.get_entity(owner)).first_name
                    owner_names.append(owner_name)

                for sudo in config['config']['sudo_id']:
                    sudo_name = (await e.client.get_entity(sudo)).first_name
                    sudo_names.append(sudo_name)
    
                username = (await e.client.get_me()).username
                _id = (await e.client.get_me()).id
                await e.client.edit_message(
                    e.chat_id,
                    e.message_id,
                    f"<b>Helper Bot</b>\n\nMy ID: <code>{_id}</code>\nMy Username: @{username}\nOwners: {', '.join(owner_names)}\nSudos: {', '.join(sudo_names)}\nPython version: <code>3.8.5</code>\nTelethon version: <code>1.10.10</code>",
                    buttons=[[Button.inline('Back', data='alive_back')]]
                )
            except:
                pass

aliveback_lock = asyncio.Lock()
@register(events.CallbackQuery())
async def back_button(e):
    async with aliveback_lock:
        if e.data == b'alive_back':
            try:
                if e.sender_id != data[(e.chat_id, e.message_id)]:
                    await e.answer('...no', cache_time=3600)
                    return
            except KeyError:
                await e.answer()
                return
            try:
                await e.answer()
                await e.client.edit_message(
                    e.chat_id,
                    e.message_id,
                    "<b>Yes, I'm alive!</b>\nPython version: <code>3.8.5</code>\nTelethon version: <code>1.10.10</code>",
                    buttons=
                    [
                        [Button.url('Python', url='python.org'), Button.url('Telethon', url='docs.telethon.dev')],
                        [Button.inline('More', data='alive_more')]
                    ])
            except:
                pass

@register(events.NewMessage(incoming=True, pattern=r'/ping$'))
async def pinging(e):
    start = time.time()
    aw = await e.reply('Pinging...')
    end = time.time()
    between = int((end - start)*1000)
    await aw.edit(f'<b>Pong!</b>\n<code>{between}ms</code>')

help_dict.update({"Ping": "**Commands:**\n/start or /alive: to check if I'm alive and contains additional information about me.\n/ping: to see my ping."})
