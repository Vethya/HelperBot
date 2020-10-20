from telethon import events
from telethon import Button
from helper import register, help_dict

@register(events.NewMessage(incoming=True, pattern=r'/help(?: (.+))?'))
async def help_(e):
    username = (await e.client.get_me()).username
    module = e.pattern_match.group(1) if e.pattern_match.group(1) is not None else None
        
    if module is not None:
        if module in help_dict:
            await e.client.send_message(
                        e.chat_id,
                        f"Help for **{module}** module:\n\n{help_dict[module]}",
                        reply_to=e.id,
                        buttons=[[Button.inline('Back', data='help_back')]],
                        parse_mode='md'
                    )
        else:
            text = "Here are the help for all available modules\n\nClick on each button to get its help!"
            buttons = []
            to_append = []
            for module_name in sorted(help_dict):
                to_append.append(Button.inline(module_name.strip(), data=f"help_{module_name}"))

                if len(to_append) > 2:
                    buttons.append(to_append)
                    to_append = []

            if to_append:
                buttons.append(to_append)

            await e.client.send_message(
                    e.chat_id,
                    text,
                    reply_to=e.id,
                    buttons=buttons
                )
    else:
        text = "Here are the help for all available modules\n\nClick on each button to get its help!"
        buttons = []
        to_append = []
        for module_name in sorted(help_dict):
            to_append.append(Button.inline(module_name.strip(), data=f"help_{module_name}"))

            if len(to_append) > 2:
                buttons.append(to_append)
                to_append = []

        if to_append:
            buttons.append(to_append)

        await e.client.send_message(
                    e.chat_id,
                    text,
                    reply_to=e.id,
                    buttons=buttons
                )

@register(events.CallbackQuery())
async def help_buttons(e):
    module = str(e.data.decode())[5:]
    if module in help_dict:
        await e.answer()
        await e.client.edit_message(
                    e.chat_id,
                    e.message_id,
                    f"Help for **{module}** module:\n\n{help_dict[module]}",
                    buttons=[[Button.inline('Back', data='help_back')]],
                    parse_mode='md'
                )
    if e.data == b'help_back':
        text = "Here are the help for all available modules\n\nClick on each button to get its help!"
        buttons = []
        to_append = []
        for module_name in sorted(help_dict):
            to_append.append(Button.inline(module_name, data="help_{}".format(module_name)))
            if len(to_append) > 2:
                buttons.append(to_append)
                to_append = []
        if to_append:
            buttons.append(to_append)
            await e.answer()
        await e.client.edit_message(
                    e.chat_id,
                    e.message_id,
                    text,
                    buttons=buttons
                )
