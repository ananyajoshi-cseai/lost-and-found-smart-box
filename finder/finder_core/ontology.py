from collections import deque

TREE = {"campusitem": ["stationery", "electronics", "personalitems"],
        "stationery": ["notebook", "pen"], "electronics": ["charger", "earphones"],
        "personalitems": ["bottle", "umbrella", "keys"]}
GRAPH = {}
for parent, children in TREE.items():
    GRAPH.setdefault(parent, [])
    for child in children:
        GRAPH[parent].append(child)
        GRAPH.setdefault(child, []).append(parent)


def bfs(start, limit=2):
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    if start not in GRAPH:
        return {}
    distance, queue = {start: 0}, deque([start])
    while queue:
        node = queue.popleft()
        if distance[node] == limit:
            continue
        for neighbour in GRAPH[node]:
            if neighbour not in distance:
                distance[neighbour] = distance[node] + 1
                queue.append(neighbour)
    return distance
