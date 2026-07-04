# -*- coding: utf-8 -*-
"""Plugin platform adapter stub."""


class IRCAdapter:
    name = "irc"

    async def start(self):
        pass

    async def stop(self):
        pass

    async def send_message(self, chat_id, text, **kw):
        return True
