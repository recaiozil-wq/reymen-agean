# -*- coding: utf-8 -*-
"""
plugins/spotify/__init__.py — Spotify Kontrol Plugin.

Araçlar: SPOTIFY_OYNAT, SPOTIFY_DUR, SPOTIFY_SIRADAKI, SPOTIFY_ARAMA
spotipy varsa gercek API, yoksa sistem komutlari ile fallback.

.env'de gerekli:
    SPOTIFY_CLIENT_ID=...
    SPOTIFY_CLIENT_SECRET=...
    SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
"""

__all__ = ['SpotifyOAuth', 'kaydet', 'spotify_arama', 'spotify_dur', 'spotify_oynat', 'spotify_siradaki']
import os
import re

PLUGIN_ADI = "spotify"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Spotify muzik kontrol plugini"


def _spotipy_al():
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.environ.get("SPOTIFY_CLIENT_ID", ""),
            client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET", ""),
            redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"),
            scope="user-modify-playback-state user-read-playback-state user-read-currently-playing",
        ))
        return sp
    except Exception:
        return None


def _sistem_oynat(sarki: str) -> str:
    """Sistem media player ile basit oynatma."""
    try:
        import subprocess
        subprocess.Popen(["start", "spotify:", f"search:{sarki}"], shell=True)
        return f"[Spotify] Spotify acildi: {sarki}"
    except Exception as e:
        return f"[Spotify] Hata: {e}"


def kaydet(motor):
    def spotify_oynat(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        sorgu = params[0] if params else ham.strip('"')
        sp = _spotipy_al()
        if sp:
            try:
                sonuclar = sp.search(sorgu, limit=1, type="track")
                parcalar = sonuclar.get("tracks", {}).get("items", [])
                if parcalar:
                    uri = parcalar[0]["uri"]
                    ad = parcalar[0]["name"]
                    sp.start_playback(uris=[uri])
                    return f"[Spotify] Oynatiliyor: {ad}"
                return f"[Spotify] Bulunamadi: {sorgu}"
            except Exception as e:
                return f"[Spotify] API Hatasi: {e}"
        return _sistem_oynat(sorgu)

    def spotify_dur(ham: str) -> str:
        sp = _spotipy_al()
        if sp:
            try:
                sp.pause_playback()
                return "[Spotify] Duraklatildi."
            except Exception as e:
                return f"[Spotify] Hata: {e}"
        return "[Spotify] spotipy yuklu degil."

    def spotify_siradaki(ham: str) -> str:
        sp = _spotipy_al()
        if sp:
            try:
                sp.next_track()
                return "[Spotify] Siradaki sarki."
            except Exception as e:
                return f"[Spotify] Hata: {e}"
        return "[Spotify] spotipy yuklu degil."

    def spotify_arama(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        sorgu = params[0] if params else ham.strip('"')
        sp = _spotipy_al()
        if sp:
            try:
                import json
                sonuclar = sp.search(sorgu, limit=5, type="track")
                parcalar = sonuclar.get("tracks", {}).get("items", [])
                liste = [f"  {p['name']} — {p['artists'][0]['name']}" for p in parcalar]
                return "[Spotify Arama]\n" + "\n".join(liste)
            except Exception as e:
                return f"[Spotify] Hata: {e}"
        return "[Spotify] spotipy yuklu degil. pip install spotipy"

    from plugins.kanban import _plugin_arac_kaydet
    _plugin_arac_kaydet(motor, "SPOTIFY_OYNAT",    spotify_oynat)
    _plugin_arac_kaydet(motor, "SPOTIFY_DUR",       spotify_dur)
    _plugin_arac_kaydet(motor, "SPOTIFY_SIRADAKI",  spotify_siradaki)
    _plugin_arac_kaydet(motor, "SPOTIFY_ARAMA",     spotify_arama)
    print(f"[Plugin:{PLUGIN_ADI}] 4 arac kayit edildi.")
