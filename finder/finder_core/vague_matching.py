
import re

# Descriptions that users might use instead of an item's actual name.
VAGUE_DESCRIPTIONS = {
    "bottle": [
        "something to drink from",
        "something to drink water from",
        "something to store water",
        "water container",
        "thing used for drinking water"
    ],

    "pen": [
        "something to write with",
        "thing used for writing",
        "writing instrument"
    ],

    "earphones": [
        "something to listen to music with",
        "something to listen to audio with",
        "small headphones",
        "wireless earbuds"
    ],

    "headphones": [
        "something to listen to music with",
        "something to listen to audio with",
        "headphones for listening"
    ],

    "keys": [
        "something to open a lock",
        "something to unlock a door",
        "thing used to open doors"
    ],

    "umbrella": [
        "something to protect from rain",
        "something to use in rainy weather",
        "rain protection"
    ],

    "backpack": [
        "something to carry books",
        "something to carry things",
        "bag used to carry books"
    ],

    "glasses": [
        "something to improve eyesight",
        "something to see clearly",
        "something worn on the eyes"
    ]
}


def match_vague_description(text):
    """
    Find categories matching a user's vague description.

    Returns a list of matching categories.
    An empty list means no description was recognized.
    Multiple categories mean clarification is needed.
    """

    text = text.lower().strip()
    matches = []

    for category, descriptions in VAGUE_DESCRIPTIONS.items():

        for phrase in descriptions:
            pattern = r"\b" + re.escape(phrase) + r"\b"

            if re.search(pattern, text):
                matches.append(category)
                break

    return matches
