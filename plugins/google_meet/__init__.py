# -*- coding: utf-8 -*-
"""plugins/google_meet/__init__.py — Google Meet Entegrasyon Plugin.

Toplanti olusturma, baglanma, transkript. Opsiyonel bagimlilik.
"""


__all__ = ['Credentials', 'build', 'kaydet', 'meet_katil', 'meet_olustur']
plugin_adi = "google_meet"
plugin_aciklamasi = "Google Meet toplantisi olusturma ve katilma"


def kaydet(motor):
    try:
        def meet_olustur(args):
            """Yeni bir Google Meet toplantisi olustur."""
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
            except ImportError:
                return "[Meet] Bagimlilik eksik: pip install google-auth google-api-python-client"
            try:
                import os
                creds = None
                token_json = os.environ.get("GOOGLE_MEET_TOKEN")
                if token_json:
                    import json
                    creds = Credentials.from_authorized_user_info(json.loads(token_json))
                if not creds:
                    return "[Meet] Google Meet token ayarlanmamis. GOOGLE_MEET_TOKEN ortam degiskeni gerekli."
                service = build("calendar", "v3", credentials=creds)
                baslik = args.strip() or "ReYMeN Toplantisi"
                event = {
                    "summary": baslik,
                    "conferenceData": {"createRequest": {"requestId": f"remeet-{id(baslik)}"}},
                    "start": {"dateTime": "", "timeZone": "Europe/Istanbul"},
                    "end": {"dateTime": "", "timeZone": "Europe/Istanbul"},
                }
                event = service.events().insert(
                    calendarId="primary",
                    body=event,
                    conferenceDataVersion=1,
                ).execute()
                link = event.get("hangoutLink", "")
                return f"[Meet] '{baslik}' olusturuldu: {link}"
            except Exception as e:
                return f"[Meet] Hata: {e}"

        def meet_katil(args):
            """Bir Google Meet toplantisina baglan."""
            link = args.strip()
            if not link:
                return "[Meet] Baglanti linki gerekli."
            import webbrowser
            webbrowser.open(link)
            return f"[Meet] {link} adresine baglaniyor..."

        if hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("MEET_OLUSTUR", meet_olustur)
            motor._registry.kaydet("MEET_KATIL", meet_katil)
    except Exception:
        pass
