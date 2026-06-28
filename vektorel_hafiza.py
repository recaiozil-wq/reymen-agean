# -*- coding: utf-8 -*-
# SHIM — reymen/hafiza/vektorel_hafiza.py yönlendirir
# import * tum public isimleri alir, _BasitYedek gibi private olanlari
# ayrica import et (test'lerin ve ic modullerin ihtiyaci icin)
from reymen.hafiza.vektorel_hafiza import *  # noqa: F401, F403
from reymen.hafiza.vektorel_hafiza import _BasitYedek, _budama_yap  # noqa: F401, F403

