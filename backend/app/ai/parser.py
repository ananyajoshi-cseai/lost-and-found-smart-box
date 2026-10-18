import re
from .vocabulary import VOCAB


def parse(text):
    """Longest phrase first; only immediate not/no/without negation."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    positive, excluded, ambiguous = {}, {}, []
    for field, values in VOCAB.items():
        found, negative, consumed = set(), set(), set()
        phrases = sorted(((alias.split(), value) for value, aliases in values.items()
                          for alias in aliases), key=lambda pair: -len(pair[0]))
        for phrase, value in phrases:
            for i in range(len(tokens) - len(phrase) + 1):
                positions = set(range(i, i + len(phrase)))
                if positions & consumed or tokens[i:i + len(phrase)] != phrase:
                    continue
                consumed.update(positions)
                target = negative if i > 0 and tokens[i - 1] in {"not", "no", "without"} else found
                target.add(value)
        if len(found) > 1 or found & negative:
            ambiguous.append(field)
        elif found:
            positive[field] = next(iter(found))
        if negative:
            excluded[field] = sorted(negative)
    return {"positive": positive, "excluded": excluded, "ambiguous": ambiguous}
