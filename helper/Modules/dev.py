from helper import register, config
from telethon import events, client
import asyncio
import html
import os

@register(events.NewMessage(incoming=True, pattern=r'/exec(?: \n| |\n)([\s\S]+)$'))
async def execc(e):
    if e.sender_id not in config['config']['owner_id']:
        await e.reply('This command can only be used by my OWNERs!')
        return

    code = e.pattern_match.group(1)
    exec(
        'async def __ex(e, client):' +
        ''.join([f'\n {l}' for l in code.split('\n')])
    )
    aw = await e.reply(
        '<strong>' + 'INPUT\n' + '</strong>'
        '<code>'+html.escape(code)+'</code>\n'
        '<strong>' + 'OUTPUT\n' + '</strong>'
    )
    output = await locals()['__ex'](e, client)
    end = '\n<code>'+html.escape(str(output))+'</code>' if output is not None else '\nNone'
    await aw.edit(
        '<strong>' + 'INPUT\n' + '</strong>'
        '<code>'+html.escape(code)+'</code>\n'
        '<strong>' + 'OUTPUT' + '</strong>'
        f'<code>{end}</code>'
    )

@register(events.NewMessage(incoming=True, pattern=r'/(?:shell|sh|bash|term) (.+)(?:\n([\s\S]+))?'))
async def run_shell(e):
    if e.sender_id not in config['config']['owner_id']:
        await e.reply('This command can only be used by my OWNERs!')
        return

    cmd, stdin = e.pattern_match.group(1), e.pattern_match.group(2)
    stdin = stdin.encode() if stdin else None
    ptext = f'<b>STDIN:</b>\n<code>{html.escape(cmd)}</code>\n'
    if stdin:
        ptext += 'stdin: \n'
        ptext += f'<code>{html.escape(stdin.decode())}</code>\n\n'
    text = ptext
    aw = await e.reply(text)
    proc = await asyncio.create_subprocess_shell(
        cmd, stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate(stdin)
    text = ptext
    text += f'<b>STDERR:</b>\n<code>{html.escape(stderr.decode())}</code>\n\n' if stderr else ''
    text += f'<b>STDOUT:</b>\n<code>{html.escape(stdout.decode())}</code>' if stdout else ''
    text += f'\nReturnCode: <code>{proc.returncode}</code>'
    if len(text) > 4096:
        with open('shell.txt', 'w+') as f:
            f.write(html.escape(text))
        await e.client.send_file(e.chat_id, 'shell.txt')
        os.remove('shell.txt')
    else:
        await aw.edit(text)
