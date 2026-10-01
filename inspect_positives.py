import json

with open("raw_reviews_dataset.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

positives = []
for r in raw:
    if r.get("score", 0) >= 4:
        c = r.get("content", "").lower()
        if any(w in c for w in ["search", "find", "face", "recognize", "gemini", "ask photo", "locate", "album", "memory", "memories"]):
            positives.append(r)

print(f"Positive reviews with retrieval signals: {len(positives)}")
for i, r in enumerate(positives[:10]):
    score = r.get("score")
    txt = r.get("content", "").replace("\n", " ")[:140]
    print(f"[{i+1}] Score: {score} | {txt}")
