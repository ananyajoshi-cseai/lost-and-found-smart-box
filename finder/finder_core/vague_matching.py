
import re

# Descriptions that users might use instead of an item's actual name.
VAGUE_DESCRIPTIONS = {
    "bottle": [
        "something to drink from",
        "something to drink water from",
        "something to store water",
        "water container",
        "thing used for drinking water"
         "something for drinking",
         "something to carry water",
         "container for water"
    ],

    "pen": [
        "something to write with",
        "thing used for writing",
        "writing instrument"
        "something for writing",
        "tool for writing",
        "used to write"
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
        "something for unlocking",
        "used to unlock doors"
    ],

    "umbrella": [
        "something to protect from rain",
        "something to use in rainy weather",
        "rain protection"
        "something for rainy days",
        "used during rain"
    ],

    "backpack": [
        "something to carry books",
        "something to carry things",
        "bag used to carry books"
        "something to carry my books",
        "something for carrying books"
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
