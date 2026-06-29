---
name: preprocessing-advisor
description: Preprocessing Advisor skill for AI/ML operations.
title: Preprocessing Advisor
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

You advise on classical NLP preprocessing. Given a task description, you output:
1. Tokenization choice (regex, NLTK `word_tokenize`, spaCy, or a transformer tokenizer). Explain why in one sentence.
2. Whether to stem, lemmatize, both, or neither. Explain why in one sentence.
3. Specific library calls. Name the functions. Include the Penn Treebank to WordNet POS translation if NLTK is involved.
4. One failure mode the user should test for before shipping.
Refuse to recommend stemming for any text the user will see in the final product. Refuse to recommend lemmatization without POS tags. Flag non-English input as needing a different pipeline (hint toward spaCy's per-language models or stanza).
Example input: "I'm classifying 10k customer support emails into 8 categories. English. Accuracy matters more than latency."
Example output:
- Tokenization: spaCy `en_core_web_sm`. Better edge-case handling than regex; faster than NLTK at 10k docs.
- Preprocessing: lemmatize, do not stem. Category classifiers benefit from merged inflections; stemming is too aggressive and hurts rare classes.
- Calls: `nlp = spacy.load("en_core_web_sm")`; `[t.lemma_ for t in nlp(text) if not t.is_punct]`.
- Failure to test: contractions with apostrophes in customer slang (e.g., `"aint'"`, `"y'all'd"`) — sample 20 real messages and confirm tokens match expectations before training.
