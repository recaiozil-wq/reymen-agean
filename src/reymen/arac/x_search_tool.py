# -*- coding: utf-8 -*-
"""x_search_tool.py â€” X (Twitter) Arama AracÄ±.

X/Twitter v2 API kullanarak tweet arar, kullanÄ±cÄ± profili çeker,
trend konularÄ± listeler. Bearer Token yeterli â€” OAuth 1.0a gerekmez.
ENV: X_BEARER_TOKEN
"""

import json
import os
import urllib.parse
import urllib.request
from typing import Optional

X_BEARER = os.environ.get("X_BEARER_TOKEN", "")
X_BASE = "https://api.twitter.com/2"


def _x_get(yol: str, params: dict) -> dict:
    if not X_BEARER:
        return {"error": "X_BEARER_TOKEN ayarlanmamÄ±ÅŸ."}
    url = f"{X_BASE}{yol}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {X_BEARER}"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def tweet_ara(
    sorgu: str,
    max_sonuc: int = 10,
    lang: str = "",
    exclude_replies: bool = True,
    exclude_retweets: bool = True,
) -> str:
    """X'te tweet ara.

    Args:
        sorgu:            Arama terimi (#hashtag, @kullanici, kelime)
        max_sonuc:        Kaç tweet döneceÄŸi (10-100)
        lang:             Dil filtresi (tr, en, â€¦)
        exclude_replies:  YanÄ±tlarÄ± hariç tut
        exclude_retweets: RT'leri hariç tut

    Returns:
        Sonuçlar metin formatÄ±nda
    """
    q = sorgu
    if lang:
        q += f" lang:{lang}"
    if exclude_replies:
        q += " -is:reply"
    if exclude_retweets:
        q += " -is:retweet"

    yanit = _x_get(
        "/tweets/search/recent",
        {
            "query": q,
            "max_results": min(max(max_sonuc, 10), 100),
            "tweet.fields": "created_at,author_id,public_metrics,lang",
            "expansions": "author_id",
            "user.fields": "name,username",
        },
    )

    if "error" in yanit:
        return f"[X Arama]: {yanit['error']}"

    tweetler = yanit.get("data", [])
    kullanicilar = {u["id"]: u for u in yanit.get("includes", {}).get("users", [])}

    if not tweetler:
        return f"'{sorgu}' için sonuç bulunamadÄ±."

    satirlar = [f"X Arama: '{sorgu}' â€” {len(tweetler)} tweet"]
    for t in tweetler:
        yazar_id = t.get("author_id", "")
        yazar = kullanicilar.get(yazar_id, {})
        kullanici = yazar.get("username", yazar_id)
        metrikler = t.get("public_metrics", {})
        satirlar.append(
            f"\n@{kullanici} | â™¥{metrikler.get('like_count',0)} "
            f"ğŸ”{metrikler.get('retweet_count',0)} | {t.get('created_at','')}\n"
            f"{t['text']}"
        )
    return "\n".join(satirlar)


def kullanici_profili(kullanici_adi: str) -> str:
    """X kullanÄ±cÄ± profili getir.

    Args:
        kullanici_adi: @ iÅŸareti olmadan (ör. elonmusk)

    Returns:
        Profil bilgisi metin olarak
    """
    yanit = _x_get(
        f"/users/by/username/{kullanici_adi}",
        {
            "user.fields": "name,description,public_metrics,created_at,verified",
        },
    )

    if "error" in yanit:
        return f"[X Profil]: {yanit['error']}"

    data = yanit.get("data", {})
    if not data:
        return f"@{kullanici_adi} bulunamadÄ±."

    m = data.get("public_metrics", {})
    return (
        f"@{data.get('username')} â€” {data.get('name')}\n"
        f"{data.get('description','')}\n"
        f"Takipçi: {m.get('followers_count',0):,} | "
        f"Takip: {m.get('following_count',0):,} | "
        f"Tweet: {m.get('tweet_count',0):,}"
    )


def son_tweetler(kullanici_adi: str, max_sonuc: int = 5) -> str:
    """KullanÄ±cÄ±nÄ±n son tweetlerini getir."""
    profil = _x_get(f"/users/by/username/{kullanici_adi}", {"user.fields": "id"})
    uid = profil.get("data", {}).get("id", "")
    if not uid:
        return f"[X]: @{kullanici_adi} bulunamadÄ±."

    yanit = _x_get(
        f"/users/{uid}/tweets",
        {
            "max_results": min(max(max_sonuc, 5), 100),
            "tweet.fields": "created_at,public_metrics",
            "exclude": "retweets,replies",
        },
    )

    tweetler = yanit.get("data", [])
    if not tweetler:
        return f"@{kullanici_adi} için tweet bulunamadÄ±."

    satirlar = [f"@{kullanici_adi} â€” Son {len(tweetler)} Tweet"]
    for t in tweetler:
        m = t.get("public_metrics", {})
        satirlar.append(
            f"\nâ™¥{m.get('like_count',0)} | {t.get('created_at','')}\n{t['text']}"
        )
    return "\n".join(satirlar)


def motor_kaydet(motor):
    """X araçlarÄ±nÄ± motora kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "X_TWEET_ARA",
        lambda sorgu, max_sonuc=10, lang="": tweet_ara(sorgu, int(max_sonuc), lang),
        "X/Twitter'da tweet ara",
    )
    motor._plugin_arac_kaydet(
        "X_KULLANICI_PROFIL",
        lambda kullanici_adi: kullanici_profili(kullanici_adi),
        "X kullanÄ±cÄ± profilini getir",
    )
    motor._plugin_arac_kaydet(
        "X_SON_TWEETLER",
        lambda kullanici_adi, max_sonuc=5: son_tweetler(kullanici_adi, int(max_sonuc)),
        "X kullanÄ±cÄ±sÄ±nÄ±n son tweetlerini getir",
    )


if __name__ == "__main__":
    print(tweet_ara("yapay zeka", max_sonuc=3, lang="tr"))
