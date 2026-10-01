import json

with open("raw_reviews_dataset.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

print(f"Total raw reviews: {len(raw)}")

candidates = []

for r in raw:
    content = r.get("content", "")
    cl = content.lower()
    score = r.get("score", 0)
    
    # Must be DIRECTLY about search, finding photos, or retrieving photos
    # Exclude UI bugs (folders vanishing), archiving, bloat rants
    is_about_search_or_retrieval = False
    topic = ""
    
    if "search" in cl and any(w in cl for w in ["find", "photo", "picture", "result", "ai", "looking", "query", "wrong"]):
        is_about_search_or_retrieval = True
        topic = "SEARCH_BAR_OR_QUERY"
    elif any(w in cl for w in ["find photo", "find picture", "finding photo", "finding picture", "look for a photo", "look for photos", "looking for a photo", "locate photo"]):
        is_about_search_or_retrieval = True
        topic = "PHOTO_FINDING"
    elif ("can't find" in cl or "cannot find" in cl or "couldn't find" in cl) and any(w in cl for w in ["photo", "picture", "photos", "pictures", "image", "memory"]):
        is_about_search_or_retrieval = True
        topic = "CANNOT_FIND_PHOTO"
    elif "face" in cl and any(w in cl for w in ["recogni", "tag", "group", "person", "find", "search"]):
        # Must be about finding or grouping people
        if any(w in cl for w in ["can't", "cannot", "won't", "doesn't", "poor", "wrong", "unable", "manually add", "enlist", "side"]):
            is_about_search_or_retrieval = True
            topic = "FACE_RECOGNITION_RETRIEVAL"
    elif any(w in cl for w in ["ask photo", "gemini"]) and any(w in cl for w in ["search", "find", "photo"]):
        is_about_search_or_retrieval = True
        topic = "AI_SEARCH"

    # Strict exclusions of UI rants, disappearances, archiving
    if any(w in cl for w in ["automatic albums", "archive photos after 30 days", "folder in the collections tab would vanish", "keeps disappearing"]):
        is_about_search_or_retrieval = False

    if is_about_search_or_retrieval:
        candidates.append((r, topic))

with open("candidates.txt", "w", encoding="utf-8") as out:
    out.write(f"Total pristine search/retrieval candidate reviews: {len(candidates)}\n\n")
    for i, (c, topic) in enumerate(candidates):
        clean_txt = c.get("content", "").replace("\n", " ")
        out.write(f"[{i+1}] ({topic}) Rating: {c.get('score')} | ID: {c.get('reviewId')}\n")
        out.write(f"Review: {clean_txt}\n\n")

print(f"Wrote {len(candidates)} candidates to candidates.txt")
