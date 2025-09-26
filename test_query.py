from utils import get_chroma_collection, query_collection

coll = get_chroma_collection()
print("Total chunks:", coll.count())

results = query_collection("What is a function?", k=3)
for r in results:
    print(r["document"][:200], "...\n")

