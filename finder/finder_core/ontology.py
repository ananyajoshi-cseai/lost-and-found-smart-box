from collections import deque

# 1. This i sour tree ontology
TREE = {
    "campusitem": ["stationery", "electronics", "personalitems", "valuables"],
    "stationery": ["notebook", "pen", "calculator"],
    "electronics": ["charger", "earphones", "headphones"],
    "personalitems": ["bottle", "umbrella", "keys", "wallet"],
    "valuables": ["idcard", "watch"]
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


def get_related_categories(start_category, max_depth=2):
    # If the category isn't in our graph, just return the category itself
    if start_category not in GRAPH:
        return [start_category]

    visited = set([start_category])
    # Queue stores tuples of: (current_node, current_depth)
    queue = deque([(start_category, 0)])
    related_categories = []

    while queue:
        current_node, depth = queue.popleft()

        # If depth > 0, it means it's a related neighbor (not the start item itself)
        if depth > 0:
            related_categories.append(current_node)

        # If we haven't hit our limit of 2 steps, explore neighbors
        if depth < max_depth:
            for neighbor in GRAPH[current_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

    return related_categories

