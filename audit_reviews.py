import json

with open("raw_reviews_dataset.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

targets = []
for r in raw:
    c = r.get("content", "")
    cl = c.lower()
    signals = []
    
    # 1. Search experience
    if "search" in cl and any(x in cl for x in ["photo", "picture", "image", "find", "result", "ai", "bar", "accuracy", "slow", "wrong", "query", "button"]):
        signals.append("SEARCH_EXPERIENCE")
    
    # 2. Face / Person Recognition
    if any(x in cl for x in ["face", "facial", "person"]) and any(x in cl for x in ["tag", "recogniz", "label", "assign", "group", "identif", "merge", "album", "name"]):
        signals.append("FACE_RECOGNITION")
    elif "peoples" in cl and any(x in cl for x in ["label", "tag", "group", "recogniz"]):
        signals.append("FACE_RECOGNITION")
        
    # 3. Photo Retrieval / Inability to find
    if any(x in cl for x in ["find photo", "find picture", "finding photo", "finding picture", "locate photo", "retrieve", "look for photo", "looking for photo"]):
        signals.append("PHOTO_RETRIEVAL")
    elif ("can't find" in cl or "cannot find" in cl or "couldn't find" in cl or "unable to find" in cl) and any(x in cl for x in ["photo", "picture", "video", "image", "media", "album", "old", "it"]):
        signals.append("PHOTO_RETRIEVAL")
        
    # 4. AI Search
    if any(x in cl for x in ["ask photo", "gemini", "ai search", "natural language", "semantic search"]):
        signals.append("AI_SEARCH")
        
    # 5. Massive Library / Scrolling
    if any(x in cl for x in ["scroll", "scrolling"]) and any(x in cl for x in ["thousand", "hours", "forever", "library", "gallery", "all my photo", "find", "looking"]):
        signals.append("LIBRARY_OVERLOAD_SCROLLING")
        
    # 6. Object / Document Retrieval
    if any(x in cl for x in ["receipt", "document", "screenshot"]) and any(x in cl for x in ["find", "search", "sort", "folder", "album", "recogniz"]):
        signals.append("DOCUMENT_OBJECT_RETRIEVAL")

    if signals:
        targets.append((r, signals))

print(f"Total matching genuine retrieval signals: {len(targets)}")
for i, (r, s) in enumerate(targets[:25]):
    print(f"\n[{i+1}] Score: {r.get('score')} | Signals: {s}")
    print(r.get("content").strip())
