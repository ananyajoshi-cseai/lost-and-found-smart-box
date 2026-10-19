from .ontology import bfs

WEIGHTS = {"category": 40, "color": 25, "brand": 15, "location": 10, "mark": 10}
THRESHOLD = 50


def rank(query, items, broaden=False):
    facts = query["positive"]
    if query["ambiguous"] or not facts:
        return []
    eligible = [item for item in items if item.get("status") == "available"
                and not any(item.get(field) in values for field, values in query["excluded"].items())]
    category = facts.get("category")
    related = False
    if category:
        exact = [item for item in eligible if item.get("category") == category]
        if exact:
            eligible = exact
        elif broaden:
            neighbours = bfs(category)
            eligible = [item for item in eligible if item.get("category") in neighbours]
            related = True
        else:
            return []
    denominator = sum(WEIGHTS[field] for field in facts)
    results = []
    for item in eligible:
        reasons = [{"field": field, "weight": WEIGHTS[field],
                    "points": WEIGHTS[field] if item.get(field) == value else 0,
                    "matched": item.get(field) == value} for field, value in facts.items()]
        score = 100 * sum(reason["points"] for reason in reasons) / denominator
        if score < THRESHOLD:
            continue
        results.append({"id": item["id"], "score": round(score, 2),
                        "coverage": len(facts), "denominator": denominator, "reasons": reasons,
                        "strong_candidate": all(field in facts and item.get(field) == facts[field]
                                                for field in ("category", "color", "brand")),
                        "related": related})
    return sorted(results, key=lambda result: (-result["score"], result["id"]))[:3]
