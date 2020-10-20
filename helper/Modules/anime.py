import asyncio
import html
from jikanpy import Jikan
from telethon import events
from helper import register, help_dict, app
from telethon import Button
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

jikan = Jikan()
zws = '\u200b'

def get_anime(name, loop):
    def _get_anime(name):
        sr = jikan.search('anime', name)
        try:
            a = sr['results'][0]['mal_id']
        except Exception:
            return
        return jikan.anime(a)
    return loop.run_in_executor(None, _get_anime, name)

def shorten(text):
    if len(text) > 1024:
        text = text[0:1021] + '...'
    return text

@register(events.NewMessage(incoming=True, pattern=r'/m(?:y)?a(?:nime)?l(?:ist)? a(?:nime)? (.+)'))
async def mal_anime(e):
    aw = await e.reply('Searching...')
    a = await get_anime(e.pattern_match.group(1), e.client.loop)
    if not a:
        await aw.edit('No results found!')
        return
    text = f'<b>{html.escape(a["title"])} ({html.escape(a["title_japanese"])})</b>\n'
    text += f'<b>Score:</b> {a["score"]}\n'
    text += f'<b>Type:</b> {html.escape(a["type"])}\n'
    text += f'<b>Genres:</b> {", ".join([html.escape(i["name"]) for i in a["genres"]])}\n'
    text += f'<b>Status:</b> {html.escape(a["status"])}\n'
    text += f'<b>Episodes:</b> {a["episodes"]}\n'
    text += f'<b>Duration:</b> {html.escape(a["duration"])}\n'
    text += f'<i>{html.escape(a["synopsis"])}</i>\n'
    text = shorten(text)
    await aw.delete()
    await e.client.send_message(
            e.chat_id,
            text.strip(),
            reply_to=e.id,
            buttons=Button.url('More Information', url=a['url']),
            link_preview=True,
            file=a['image_url']
            )

def get_manga(name, loop):
    def _get_manga(name):
        sr = jikan.search('manga', name)
        try:
            m = sr['results'][0]['mal_id']
        except Exception:
            return
        return jikan.manga(m)
    return loop.run_in_executor(None, _get_manga, name)

@register(events.NewMessage(incoming=True, pattern=r'/m(?:y)?a(?:nime)?l(?:ist)? m(?:anga)? (.+)'))
async def mal_manga(e):
    aw = await e.reply('Searching...')
    m = await get_manga(e.pattern_match.group(1), e.client.loop)
    if not m:
        await aw.edit('No results found!')
        return
    text = f'<b>{html.escape(m["title"])} ({html.escape(m["title_japanese"])})</b>\n'
    text += f'<b>Score:</b> {m["score"]}\n'
    text += f'<b>Type:</b> {html.escape(m["type"])}\n'
    text += f'<b>Genres:</b> {", ".join([html.escape(i["name"]) for i in m["genres"]])}\n'
    text += f'<b>Status:</b> {html.escape(m["status"])}\n'
    if m['volumes']:
        text += f'<b>Volumes:</b> {m["volumes"]}\n'
    if m['chapters']:
        text += f'<b>Chapters:</b> {m["chapters"]}\n'
    text += f'<i>{html.escape(m["synopsis"])}</i>\n'
    text = shorten(text)

    await aw.delete()
    await e.client.send_message(
            e.chat_id,
            text.strip(),
            reply_to=e.id,
            buttons=Button.url('More Information', url=m['url']),
            link_preview=True,
            file=m['image_url']
            )

def get_character(name, loop):
    def _get_character(name):
        sr = jikan.search('character', name)
        try:
            c = sr['results'][0]['mal_id']
        except Exception:
            return
        return jikan.character(c)
    return loop.run_in_executor(None, _get_character, name)

@register(events.NewMessage(incoming=True, pattern=r'/m(?:y)?a(?:nime)?l(?:ist)? c(?:haracter)? (.+)'))
async def mal_character(e):
    aw = await e.reply('Searching...')
    c = await get_character(e.pattern_match.group(1), e.client.loop)
    if not c:
        await aw.edit('No results found!')
        return
    text = f'<b>{c["name"]} ({c["name_kanji"]})</b>\n'
    about = html.escape(c['about'].replace('\\n', ''))
    text += f'<i>{about}</i>\n'
    text = shorten(text)
    await aw.delete()
    await e.client.send_message(
            e.chat_id,
            text.strip(),
            reply_to=e.id,
            buttons=Button.url('More Information', url=c['url']),
            link_preview=True,
            file=c['image_url']
            )

# https://github.com/DragSama/AniFluid-Base
anime_query = '''
   query ($id: Int,$search: String) { 
      Media (id: $id, type: ANIME,search: $search) { 
        id
        title {
          romaji
          english
          native
        }
        description (asHtml: false)
        startDate{
            year
          }
          episodes
          season
          type
          format
          status
          duration
          siteUrl
          averageScore
          genres
        }
    }
'''

character_query = """
    query ($query: String) {
        Character (search: $query) {
               id
               name {
                     full
                     native
                     alternative
               }
               siteUrl
               image {
                        large
               }
               description
               favourites
        }
    }
"""

manga_query = """
query ($id: Int,$search: String) { 
      Media (id: $id, type: MANGA,search: $search) { 
        id
        title {
          romaji
          english
          native
        }
        description (asHtml: false)
        startDate{
            year
          }
        coverImage {
            large
        }
          type
          format
          status
          siteUrl
          averageScore
          genres
          chapters
      }
    }
"""

url = 'https://graphql.anilist.co'

@app.on_message(filters.text & filters.regex(r'/a(?:ni)?l(?:ist)? a(?:nime)? (.+)'))
async def anilist_anime(client, m):
    aw = await m.reply_text('Searching...')

    query = m.matches[0].group(1)
    variables = {'search': query}

    res = requests.post(url, json={'query': anime_query, 'variables': variables}).json()['data'].get('Media', None)

    if res:
        text = f"<b>{res['title']['romaji']}</b>({res['title']['native']})\n"
        text += f"<b>Types:</b> {res['format']}\n"
        text += f"<b>Status:</b> {res['status']}\n"
        text += f"<b>Episodes:</b> {res.get('episodes', 'Unknown')}\n"
        text += f"<b>Duration:</b> {res.get('duration', 'N/A')} per episode\n"
        text += f"<b>Score:</b> {res['averageScore']}\n"
        genres = res['genres']
        if len(genres) > 1:
            genres = ', '.join(genres)
        text += f"<b>Genres:</b> {genres}\n"
        text += f"<b>Description:</b>\n{res['description']}"
        text = shorten(text)
        info = res['siteUrl']
        image = f"https://img.anili.st/media/{res['id']}"
        await aw.delete()
        if image:
            await m.reply_photo(
                        image,
                        caption=text,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("More Information", url=info)]]
                            )
                    )
        else:
            await m.reply_text(
                        text,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("More Information", url=info)]]
                            )
                    )
    else:
        aw.edit_text('No results found!')

@app.on_message(filters.text & filters.regex(r'/a(?:ni)?l(?:ist)? c(?:haracter)? (.+)'))
async def anilist_character(client, m):
    aw = await m.reply_text('Searching...')
    query = m.matches[0].group(1)
    variables = {'query': query}
    
    res = requests.post(url, json={'query': character_query, 'variables': variables}).json()['data']['Character']
    if res:
        text = f"<b>{res['name']['full']}</b>({res['name']['native']})\n"
        synonyms = res['name']['alternative']
        if len(synonyms) > 1:
            synonyms = ', '.join(synonyms)
        if len(synonyms) == 1:
            synonyms = None
        text += f"<b>Synonyms:</b> {synonyms}\n"
        text += f"<b>Favourites:</b> {res['favourites']}\n"
        text += f"<b>Description:</b>\n{res['description']}"
        text = shorten(text)
        info = res['siteUrl']
        image = res['image']['large']
        await aw.delete()
        if image:
            await m.reply_photo(
                        image,
                        caption=text,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("More Information", url=info)]]
                            )
                    )
        else:
            await m.reply_text(
                        text,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("More Information", url=info)]]
                            )
                    )
    else:
        await aw.edit_text('No results found!')

@app.on_message(filters.text & filters.regex(r'/a(?:ni)?l(?:ist)? m(?:anga)? (.+)'))
async def anilist_manga(client, m):
    aw = await m.reply_text('Searching...')
    query = m.matches[0].group(1)
    variables = {'search': query}
    
    res = requests.post(url, json={'query': manga_query, 'variables': variables}).json()['data']['Media']
    if res:
        text = f"<b>{res['title']['romaji']}</b>({res['title']['native']})\n"
        text += f"<b>Start Date:</b> {res['startDate']['year']}\n"
        text += f"<b>Status:</b> {res['status']}\n"
        text += f"<b>Score:</b> {res['averageScore']}\n"
        text += f"<b>Chapters:</b> {res['chapters']}\n"
        genres = res['genres']
        if len(genres) > 1:
            genres = ', '.join(genres)
        text += f"<b>Genres:</b> {genres}\n"
        text += f"<b>Description:</b>\n{res['description']}"
        image = res['coverImage']['large']
        info = res['siteUrl']
        text = shorten(text)
        await aw.delete()
        if image:
            await m.reply_photo(
                        image,
                        caption=text,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("More Information", url=info)]]
                            )
                    )
        else:
            await m.reply_text(
                        text,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("More Information", url=info)]]
                           )
                    )
    else:
        await aw.edit_text('No results found!')

help_dict.update({"Anime": "**Commands:**\n/myanimelist or /mal <search type> <query>: to make a query to myanimelist.net\n/anilist or /al <search type> <query>: to make a query to anilist.co\n\n**Search Types:**\nAnime: `anime` or `a`\nManga: `manga` or `m`\nCharacter: `character` or `c`"})
