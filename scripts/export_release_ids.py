"""Export the public labels file from the private labeled corpus (no post text, no way back to a user).

Usage: python scripts/export_release_ids.py <path/to/labeled_corpus.jsonl> data/release/corpus_ids_labels.csv
"""
import csv, json, sys

TIERS = {0: "Neutral", 1: "Stress", 2: "Moderate", 3: "Crisis"}
SPLIT = {"youtube": "train", "reddit": "test", "twitter": "test"}  # train on YouTube, test on unseen Reddit + X

src, dst = sys.argv[1], sys.argv[2]
rows = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
# No URLs, native IDs, user hashes or exact timestamps: with a mental-health label they re-identify people.
cols = ["record_id", "platform", "split", "month", "lang", "tier", "tier_name", "tier_source", "tier_confidence"]
with open(dst, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    for r in rows:
        p = r["platform"]
        w.writerow({"record_id": r["record_id"], "platform": p, "split": SPLIT[p], "month": r["timestamp"][:7],
                    "lang": r["lang"], "tier": r["tier"], "tier_name": TIERS[r["tier"]],
                    "tier_source": r["tier_source"], "tier_confidence": r["tier_confidence"]})

assert len(rows) == 4614, f"expected the paper's 4,614 records, got {len(rows)}"
print(f"wrote {len(rows)} rows -> {dst}")
