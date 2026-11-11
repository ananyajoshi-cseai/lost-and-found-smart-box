import difflib
import re
from .vocabulary import VOCAB

NEGATORS = {"not", "no", "without"}
# Words that may sit between a negator and what it negates: "not a blue bottle".
FILLERS = {"a", "an", "the", "any", "my", "one"}

ALIAS_TOKENS = {token for values in VOCAB.values()
                for aliases in values.values() for alias in aliases for token in alias.split()}

# Ordinary words that must never be "corrected" into a vocabulary word.
COMMON_WORDS = {
    "lost", "left", "near", "found", "with", "from", "that", "this", "have", "some", "there",
    "about", "around", "inside", "outside", "next", "last", "small", "large", "big", "pink",
    "yellow", "orange", "purple", "color", "colour", "brand", "item", "thing", "please",
}


def singular(token):
    """Plural -> singular, but only when the result is a word we know ("bottles" -> "bottle")."""
    if token in ALIAS_TOKENS:
        return token
    candidates = []
    if token.endswith("ies"):
        candidates.append(token[:-3] + "y")
    if token.endswith("es"):
        candidates.append(token[:-2])
    if token.endswith("s"):
        candidates.append(token[:-1])
    return next((c for c in candidates if c in ALIAS_TOKENS), token)


def _words(text):
    return re.findall(r"[a-z0-9]+", text.lower().replace("'", ""))


def _negated(tokens, i):
    """True when a negator precedes position i, optionally through fillers ("not a ...")."""
    j = i - 1
    while j >= 0 and tokens[j] in FILLERS:
        j -= 1
    return j >= 0 and tokens[j] in NEGATORS


def parse(text):
    """Longest phrase first; plurals folded; negation reaches past "a/an/the"."""
    tokens = [singular(t) for t in _words(text)]
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
                target = negative if _negated(tokens, i) else found
                target.add(value)
        if len(found) > 1 or found & negative:
            ambiguous.append(field)
        elif found:
            positive[field] = next(iter(found))
        if negative:
            excluded[field] = sorted(negative)
    return {"positive": positive, "excluded": excluded, "ambiguous": ambiguous}


# --- Spelling suggestions -------------------------------------------------------
# Kept separate from parse(): a guess is never applied silently, the app asks first.

_TARGETS = {}
for _field, _values in VOCAB.items():
    for _value, _aliases in _values.items():
        for _alias in _aliases:
            if " " not in _alias and len(_alias) >= 4:
                _TARGETS.setdefault(_alias, _field)


def suggest_corrections(text, cutoff=0.8):
    """Unknown words that look like a misspelled vocabulary word.

    Returns [{"typed", "suggestion", "field"}], e.g. "Miltn" -> "milton" (brand).
    Short words and ordinary English words are left alone, and a suggestion must
    start with the same letter, to avoid wild guesses.
    """
    out, seen = [], set()
    for token in _words(text):
        if (len(token) < 4 or token in seen or token in COMMON_WORDS or token.isdigit()
                or singular(token) in ALIAS_TOKENS):
            continue
        seen.add(token)
        pool = [word for word in _TARGETS if word[0] == token[0]]
        best = difflib.get_close_matches(token, pool, n=1, cutoff=cutoff)
        if best:
            out.append({"typed": token, "suggestion": best[0], "field": _TARGETS[best[0]]})
    return out


def apply_correction(text, typed, suggestion):
    """Replace the misspelled word in the user's original text."""
    return re.sub(rf"\b{re.escape(typed)}\b", suggestion, text, flags=re.IGNORECASE)
