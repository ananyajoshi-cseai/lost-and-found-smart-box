import streamlit as st
from filelock import Timeout
from finder_core.storage import mark_returned
from finder_core.ui import records
from finder_core.dashboard import hero, metrics, status_donut, bars

hero('03 / REUNITE', 'Close the loop.',
     'Check the item, verify the return in person, then update its status. Returned items leave the search results.')
st.warning('Demo control only — there is no staff authentication. Use on a supervised local computer.')
if 'return_notice' in st.session_state:
    st.success(st.session_state.pop('return_notice'))
items = records()
metrics(items)
st.write('')
left, right = st.columns([1.55, 1], gap='large')
with left:
    st.subheader('Mark an item returned')
    available = [i for i in items if i['status'] == 'available']
    if not available:
        st.info('No available items remain.')
    else:
        labels = {i['id']:f'#{i["id"]} · {i["color"]} {i["category"]} · {i["location"]}' for i in available}
        with st.form('return'):
            item_id = st.selectbox('Item', list(labels), format_func=labels.get, key='return_id')
            # Details live in the selector and inventory below; form changes submit together.
            st.caption('Match the ID and details in the inventory before confirming the return.')
            confirmed = st.checkbox('I have independently verified the return', key='confirmed')
            submit = st.form_submit_button('Mark returned', type='primary', icon=':material/task_alt:')
        if submit:
            if not confirmed:
                st.error('Confirm the human verification before marking returned.')
            else:
                try:
                    mark_returned(item_id)
                except (OSError, ValueError, Timeout):
                    st.error('Return could not be saved. The item may already be returned; refresh and check the record.')
                else:
                    st.session_state['return_notice'] = f'Item #{item_id} is returned and will no longer appear in search.'
                    st.session_state.pop('confirmed', None)
                    st.rerun()
with right:
    with st.container(border=True):
        st.markdown('#### Inventory status')
        status_donut(items, 'staff_status')

st.divider()
st.subheader('Inventory at a glance')
listing, distribution = st.tabs(['Item register', 'Available by location'])
with listing:
    status = st.selectbox('Show status', ['All', 'Available', 'Returned'], key='inventory_status')
    shown = [i for i in items if status == 'All' or i['status'] == status.lower()]
    if shown:
        st.dataframe(shown, hide_index=True, width='stretch',
                     column_order=['id','category','color','brand','location','mark','status'])
        st.caption(f'{len(shown)} records shown. Use the item ID when verifying a return.')
    else:
        st.info('No items with this status yet.')
with distribution:
    bars([i for i in items if i['status']=='available'], 'location', 'Location', 'staff_locations')
