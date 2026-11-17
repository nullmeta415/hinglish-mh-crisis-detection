# Resources

Small, human-readable lookup files the notebooks use. They are versioned and auditable so anyone can see
exactly which words/rules drove the automatic labelling and preprocessing.

| File | Used by | What it is |
|------|---------|------------|
| `lexicon_mh_v1.json` | 02 (labelling), 12 (face-validity) | Curated mental-health word-list per tier, plus phrases to *demote* (e.g. song lyrics, sarcasm) |
| `crisis_seed_en_v1.json` | 03 (augmentation) | English crisis seed phrases used to generate code-mixed Crisis examples (no scraped data) |
| `translit_map_hi_v1.json` | 05 (preprocessing) | Offline Hinglish → Devanagari transliteration table |
| `anchor_pairs_v1.json` | 06 (representation) | Matched Hindi/English clinical phrase pairs used to validate the embeddings |
