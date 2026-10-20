import streamlit as st
from filelock import Timeout
from finder_core.storage import add_item
from finder_core.ui import fields

st.header('Report a found item')
st.caption('Use synthetic records for the class demo. No names, contacts or photos are collected.')
with st.form('report'):
    values = fields()
    submit = st.form_submit_button('Save found item')
if submit:
    try:
        item = add_item(values)
    except (OSError, ValueError, Timeout):
        st.error('The item could not be saved. Check the data file and try again; no success is claimed.')
    else:
        st.success(f'Item #{item["id"]} saved and available for search.')
