# -*- coding: utf-8 -*-
"""SHIM — optional-skills/productivity/memento-flashcards/scripts/memento_cards.py"""
import sys, os
_memento_dir = os.path.join(os.path.dirname(__file__), 'optional-skills', 'productivity', 'memento-flashcards', 'scripts')
if _memento_dir not in sys.path:
    sys.path.insert(0, _memento_dir)
from memento_cards import *  # noqa: F401, F403
