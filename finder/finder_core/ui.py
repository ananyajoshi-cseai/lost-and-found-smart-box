import streamlit as st
from filelock import Timeout
from .storage import load_items


def records():
    try:
        return load_items()
    except (OSError, ValueError, Timeout):
        st.error('The item file could not be read. Stop the app and check the file or restore a backup; existing data has not been reset.')
        st.stop()


def fields():
    from .vocabulary import VOCAB
    result = {}
    for field in ['category', 'color', 'brand', 'location', 'mark']:
        options = list(VOCAB[field])
        if field in {'brand', 'mark'}:
            options = [None]+options
        result[field] = st.selectbox(field.title(), options, format_func=lambda x:'Not supplied' if x is None else x.title(), key=field)
    return result
