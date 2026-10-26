import streamlit as st
from filelock import Timeout
from finder_core.storage import add_item
from finder_core.ui import fields, records
from finder_core.dashboard import hero, bars, color_pie

hero('02 / CONTRIBUTE', 'Found something? Make it findable.',
     'A few clear details can help someone find their belongings. Add the facts you can see.')
left, right = st.columns([1.55, 1], gap='large')
with left:
    st.subheader('Report a found item')
    st.caption('Use synthetic records for the class demo. No names, contacts or photos are collected.')
    with st.form('report'):
        values = fields()
        st.caption('Brand and mark are optional. Choose “Not supplied” when unknown.')
        submit = st.form_submit_button('Save found item', type='primary', icon=':material/add:')
    if submit:
        try:
            item = add_item(values)
        except (OSError, ValueError, Timeout):
            st.error('The item could not be saved. Check the data file and try again; no success is claimed.')
        else:
            st.success(f'Item #{item["id"]} saved and available for search.')
with right:
    with st.container(border=True):
        st.markdown('### Small details matter')
        st.markdown('**01 · Identify it**  \nChoose the closest supported category and color.')
        st.markdown('**02 · Add a clue**  \nA brand or visible mark helps distinguish similar items.')
        st.markdown('**03 · Note the place**  \nSelect where the item was found, then save its record.')
        st.caption('No ownership decisions are made here. Returns are verified in person.')
    items = records()
    st.metric('Items recorded', len(items))
    st.markdown('#### Reporting snapshot')
    st.caption('All recorded items, including those already returned.')
    locations, colors = st.tabs(['Found locations', 'Color mix'])
    with locations:
        bars(items, 'location', 'Location', 'report_locations')
    with colors:
        color_pie(items, 'report_colors')
