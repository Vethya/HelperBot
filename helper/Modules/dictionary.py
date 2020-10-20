from helper import register, help_dict
from telethon import events
import json
import aiohttp
import requests
import html
from urllib.parse import quote as urlencode
from telethon import Button
import asyncio
from pprint import pprint
import re

gdefamount = {}
data = {}

@register(events.NewMessage(incoming=True, pattern=r'/u(?:rban)?d(?:ictionary)?(?: (\d+))? (.+)'))
async def urbandictionary(e):
    global gdefamount
    defamount = int(e.pattern_match.group(1) or 1)-1
    query = e.pattern_match.group(2)
    aw = await e.reply('Searching...')

    url = f'https://api.urbandictionary.com/v0/define?term={urlencode(query)}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as raw_resp:
            resp = await raw_resp.text()
            rcode = raw_resp.status
    if rcode != 200:
        await aw.edit('Word not found!')
        return
    definitions = json.loads(resp)['list']
    try:
        definition = definitions[defamount]
    except IndexError:
        await aw.edit('Not enough definitions')
        return

    author = definition["author"]
    text = f"<b>{html.escape(definition['word'])}</b> by <a href='http://www.urbandictionary.com/author.php?author={urlencode(author)}'>{author}</a>\n\n"
    meaning = definition['definition']
    text += f'<b>Definition:</b>\n{meaning}\n'
    text += f'<b>Examples:</b>\n{html.escape(definition["example"])}\n\n'
    text += f'👍 {definition["thumbs_up"]} 👎 {definition["thumbs_down"]}'
    await aw.delete()
    r = await e.client.send_message(
            e.chat_id,
            text,
            reply_to=e.id,
            buttons=[
                    [Button.inline('Back', data='ud_back'), Button.inline(f'{defamount+1}/{len(definitions)}', data='ud_page'), Button.inline('Next', data='ud_next')],
                    [Button.url('Link to defintion', url=html.escape(definition['permalink']))]
                ],
            link_preview=False
            )
    data[(r.chat_id, r.id)] = definitions
    gdefamount[(r.chat_id, r.id)] = defamount

callback_lock = asyncio.Lock()
@register(events.CallbackQuery())
async def ud_buttons(e):
    global gdefamount
    cdata = e.data.decode()
    if cdata not in ('ud_back', 'ud_page', 'ud_next'):
        return
    if cdata == 'ud_page':
        await e.answer(cache_time=3600)
        return
    async with callback_lock:
        defamount = gdefamount.get((e.chat_id, e.message_id))
        try:
            odefamount = defamount
            if cdata == 'ud_back':
                defamount -= 1
            elif cdata == 'ud_next':
                defamount += 1
            if defamount < 0:
                defamount = 0
            gdefamount[(e.chat_id, e.message_id)] = defamount
        except TypeError:
            await e.answer()
            # await e.reply('Data stored was deleted due to restarting the bot! Please make a new query!')
            return
        if odefamount != defamount:
            definitions = data.get((e.chat_id, e.message_id))
            try:
                definition = definitions[defamount]
            except IndexError:
                await e.answer()
                return
            author = definition["author"]
            meaning = definition['definition']
            text = f"<b>{html.escape(definition['word'])}</b> by <a href='http://www.urbandictionary.com/author.php?author={urlencode(author)}'>{author}</a>\n\n"
            text += f'<b>Definition:</b>\n{meaning}\n'
            text += f'<b>Examples:</b>\n{html.escape(definition["example"])}\n\n'
            text += f'👍 {definition["thumbs_up"]} 👎 {definition["thumbs_down"]}'
            try:
                await e.client.edit_message(
                    e.chat_id,
                    e.message_id,
                    text,
                    buttons=[
                            [Button.inline('Back', data='ud_back'), Button.inline(f'{defamount+1}/{len(definitions)}', data='ud_page'), Button.inline('Next', data='ud_next')],
                            [Button.url('Link to definition', html.escape(definition['permalink']))]
                        ],
                    link_preview=False
                    )
            except:
                pass
    await e.answer()

@register(events.NewMessage(incoming=True, pattern=r'/jisho(?: (\d+))? (.+)'))
async def jisho_dictionary(e):
    global gdefamount
    word = e.pattern_match.group(2)
    defamount = int((e.pattern_match.group(1) or 1))-1
    aw = await e.reply('Searching...')

    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://beta.jisho.org/api/v1/search/words?keyword={urlencode(word)}') as res:
            res = await res.text()

    definitions = json.loads(res)['data']
    if len(definitions) == 0:
        await aw.edit('No results found!')
        return
    try:
        definition = definitions[defamount]
    except IndexError:
        await aw.edit('Not enough definitions!')
        return
    text = f"<b>Word:</b> {word}\n"
    try:
        if definition['japanese'][0]['reading']:
            text += f"<b>Japanese:</b> {definition['japanese'][0]['reading']}\n"
        elif definition['japanese'][0]['word']:
            text += f"<b>Japanese:</b> {definition['japanese'][0]['word']}\n"
        elif (definition['japanese'][0]['reading'], definition['japanese'][0]['word']):
            text += f"<b>Japanese:</b> {definition['japanese'][0]['reading']}({definition['japanese'][0]['word']})\n"
    except KeyError:
        pass
    if len(definition['senses'][0]['english_definitions']) == 1:
        text += f"- {definition['senses'][0]['english_definitions'][0]}\n"
    else:
        eng_def = ''
        for i in definition['senses'][0]['english_definitions']:
            eng_def += f'- {i}\n'
        text += eng_def

    await aw.delete()
    r = await e.client.send_message(
            e.chat_id,
            text,
            reply_to=e.id,
            buttons=[
                    [Button.inline('Back', data='jisho_back'), Button.inline(f'{defamount+1}/{len(definitions)}', data='jisho_page'), Button.inline('Next', data='jisho_next')],
                    [Button.url('Show on jisho.org', url=f"http://jisho.org/search/{urlencode(word)}")]
                ],
            link_preview=False
            )
    data[(r.chat_id, r.id)] = (word, definitions)
    gdefamount[(r.chat_id, r.id)] = defamount


@register(events.CallbackQuery())
async def jisho_buttons(e):
    global gdefamount
    cdata = e.data.decode()
    if cdata not in ('jisho_back', 'jisho_page', 'jisho_next'):
        return
    if cdata == 'jisho_page':
        await e.answer(cache_time=3600)
        return
    async with callback_lock:
        defamount = gdefamount.get((e.chat_id, e.message_id))
        try:
            odefamount = defamount
            if cdata == 'jisho_back':
                defamount -= 1
            elif cdata == 'jisho_next':
                defamount += 1
            if defamount < 0:
                defamount = 0
            gdefamount[(e.chat_id, e.message_id)] = defamount
        except TypeError:
            await e.answer()
            # await e.reply('Data stored was deleted due to restarting the bot! Please make a new query!')
            return
        if odefamount != defamount:
            word, definitions = data.get((e.chat_id, e.message_id))
            try:
                definition = definitions[defamount]
            except IndexError:
                await e.answer()
                return
            text = f"<b>Word:</b> {word}\n"
            try:
                if definition['japanese'][0]['reading']:
                    text += f"<b>Japanese:</b> {definition['japanese'][0]['reading']}\n"
                elif definition['japanese'][0]['word']:
                    text += f"<b>Japanese:</b> {definition['japanese'][0]['word']}\n"
                elif (definition['japanese'][0]['reading'], definition['japanese'][0]['word']):
                    text += f"<b>Japanese:</b> {definition['japanese'][0]['reading']}({definition['japanese'][0]['word']})\n"
            except KeyError:
                pass
            if len(definition['senses'][0]['english_definitions']) == 1:
                text += f"- {definition['senses'][0]['english_definitions'][0]}\n"
            else:
                eng_def = ''
                for i in definition['senses'][0]['english_definitions']:
                    eng_def += f'- {i}\n'
                text += eng_def
            await e.client.edit_message(
                    e.chat_id,
                    e.message_id,
                    text,
                    buttons=[
                            [Button.inline('Back', data='jisho_back'), Button.inline(f'{defamount+1}/{len(definitions)}', data='jisho_page'), Button.inline('Next', data='jisho_next')],
                            [Button.url('Show on jisho.org', url=f"http://jisho.org/search/{urlencode(word)}")]
                        ],
                    link_preview=False
                    )
    await e.answer()

help_dict.update({"Dictionary": "**Commands:**\n/urbandictionary or /ud <defamount> <word>: to search a word using Urban Dictionary.\n/jisho <defamount> <word>: to search a word on jisho."})
