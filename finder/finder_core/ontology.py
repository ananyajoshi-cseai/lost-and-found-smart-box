from collections import deque


TREE = {
    "campusitem": ["stationery", "electronics", "personalitems", "valuables"],
    "stationery": ["notebook", "pen", "calculator"],
    "electronics": ["charger", "earphones", "headphones"],
    "personalitems": ["bottle", "umbrella", "keys", "backpack"],
    "valuables": ["idcard", "watch", "wallet", "glasses"]
}


GRAPH = {}
for parent, children in TREE.items():
    if parent not in GRAPH:
        GRAPH[parent] = []
    for child in children:
        if child not in GRAPH:
            GRAPH[child] = []
        # Add two-way connection: parent points to child, and child points to parent
        GRAPH[parent].append(child)
        GRAPH[child].append(parent)


def bfs(start, max_depth=2):
    """Distance from start to every category within max_depth steps (start = 0)."""
    if type(max_depth) is not int or max_depth < 0:
        raise ValueError("max_depth must be a nonnegative integer")
    if start not in GRAPH:
        return {}
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if dist[node] == max_depth:
            continue
        for neighbor in GRAPH.get(node, ()):
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist


def get_related_categories(start_category, max_depth=2):
    """Convenience view of BFS, excluding the start itself."""
    return [name for name, d in bfs(start_category, max_depth).items() if d > 0]
