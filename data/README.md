# Data

## Why the real dataset is not in this repository (by default)

The dataset is made of **real social-media posts** collected from YouTube, Reddit, and Twitter/X.
Even though usernames are removed (replaced by a one-way salted hash), the post text itself is real
user content about a **sensitive topic (mental health)**. Publishing it would breach user privacy and
the platforms' terms of service, so the raw corpus is **deliberately excluded** from this repository
(it is git-ignored).

## What is included instead

- **`release/corpus_ids_labels.csv`** — one row per post for all 4,614 posts used in the paper:
  an internal random `record_id`, platform, train/test split, posting month, language and tier label
  (with how it was assigned and its confidence). It holds **no post text, URLs, platform post IDs,
  user hashes or exact timestamps**, so no row can be traced back to a person (see §6 of the
  top-level README).

- **`sample/example_corpus.jsonl`** — a tiny, **fully synthetic** example (the rows are made up, not
  real people) that shows the exact format the notebooks expect.

## The data format

Each line is one post. The fields the model actually uses are:

| Field | Meaning |
|-------|---------|
| `record_id` | Unique id for the post |
| `platform` | `youtube`, `reddit`, or `twitter` |
| `anonymized_user_id` | One-way salted hash of the username (never the real name) |
| `timestamp` | When it was posted (UTC) |
| `post_text` | The text of the post |
| `lang` | Detected language: `english`, `hinglish`, or `hindi` |
| `tier` | Risk label: 0 = Neutral, 1 = Stress, 2 = Moderate, 3 = Crisis |

(The full pipeline also derives time-of-day features from the timestamp — see notebook `04`.)

## How to rebuild the real dataset

Notebook **`01_data_collection`** (available from the authors on request, see §6 of the top-level
README) collects fresh posts from all three platforms using
your own API keys (copy `.env.example` to `.env` and fill them in first). The collected files are
written here, into `data/`, and the later notebooks pick them up automatically.

> Note: social-media feeds change constantly, so a fresh collection will not reproduce the exact same
> posts — but it will reproduce the same *format* and *pipeline*.
