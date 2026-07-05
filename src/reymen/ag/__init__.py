# -*- coding: utf-8 -*-

"""
reymen.ag â€” Ag Geçitleri (Gateway) Paketi.

Gateway'ler, ReYMeN'in farkli platformlarla iletisim kurmasini saglar:
  - discord_bot: Discord bot wrapper (discord.py)
  - email_gateway: E-posta gonderme (smtplib)
  - whatsapp_gateway: WhatsApp mesaj gonderme (Twilio REST API)
  - slack_gateway: Slack mesaj gonderme (Incoming Webhook)
"""

__all__ = [
    "discord_bot",
    "email_gateway",
    "whatsapp_gateway",
    "slack_gateway",
]
