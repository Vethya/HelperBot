import logging
from telethon.sync import TelegramClient, events
from telethon import errors
from telethon import events
from .Modules import ALL as modules
import importlib
import traceback
import time
from pyrogram import Client
import yaml

with open('config.yaml') as config:
    config = yaml.safe_load(config)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Telethon
client = TelegramClient(
        'helperbot-telethon',
        config['telegram']['api_id'],
        config['telegram']['api_hash']
        )
client.parse_mode = 'html'

# Pyrogram
app = Client(
            'helperbot-pyrogram',
            api_id=config['telegram']['api_id'],
            api_hash=config['telegram']['api_hash'],
            bot_token=config['telegram']['bot_token']
        )

ratelimits = dict()
help_dict = {}
whitelisted_chats = config['config']['whitelisted_chats']

def _check_ratelimit(e):
    global ratelimits
    if not getattr(e, 'sender_id', None):
        return True
    print('ratelimit called', e.sender_id)
    if e.sender_id not in ratelimits:
        ratelimits[e.sender_id] = 0
        print('set ratelimit for', e.sender_id, 'to 0')
    old_time = ratelimits[e.sender_id]
    ratelimits[e.sender_id] = int(time.time())
    print('ratelimit for', e.sender_id, 'is', old_time)
    if int(time.time())-old_time < 2:
        print('returning for', e.sender_id)
        return False
    print('execution passes for', e.sender_id)
    return True

def register(event, ratelimit=True):
    def decorator(func):
        nonlocal ratelimit
        @client.on(event)
        async def wrapper(e):
            nonlocal ratelimit
            global ratelimits
            if not getattr(e, 'out', False) and ratelimit and not isinstance(e, events.CallbackQuery.Event):
                if not _check_ratelimit(e):
                    return
            if getattr(e, 'edit', None):
                e._edit = e.edit
            if (not getattr(e, 'out', False) or e.forward) and isinstance(e, (events.NewMessage.Event, events.MessageEdited.Event)):
                e._message = None
                async def wrapped_edit(*args, **kw):
                    if not e._message:
                        e._message = await e.reply(*args, **kw)
                    else:
                        return await e._message.edit(*args, **kw)
                    return e._message
                e.edit = wrapped_edit
            try:
                await func(e)
            except Exception as ex:
                if isinstance(ex, events.StopPropagation):
                    raise
                logging.exception('Unhandled exception in %s', str(func))
                await e.reply(traceback.format_exc(), parse_mode=None)
        return wrapper
    return decorator

logging.basicConfig(level=logging.INFO)

for module in modules:
    logging.info('Importing module %s', module)
    try:
        importlib.import_module('helper.Modules.' + module)
    except Exception:
        logging.exception('Failed to import %s!', module)
    else:
        logging.info('%s imported successfully', module)

print('----------- Telethon -----------')
client.start(bot_token=config['telegram']['bot_token'])

print('----------- Pyrogram -----------')
app.run()
