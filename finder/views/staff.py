import streamlit as st
from filelock import Timeout
from finder_core.storage import mark_returned
from finder_core.ui import records

st.header('Mark an item returned')
st.warning('Demo control only — there is no staff authentication. Use on a supervised local computer.')
items = [i for i in records() if i['status']=='available']
if not items:
    st.info('No available items remain.')
else:
    labels = {i['id']:f'#{i["id"]} · {i["color"]} {i["category"]} · {i["location"]}' for i in items}
    with st.form('return'):
        item_id = st.selectbox('Item', list(labels), format_func=labels.get, key='return_id')
        st.write(next(i for i in items if i['id']==item_id))
        confirmed = st.checkbox('I have independently verified the return', key='confirmed')
        submit = st.form_submit_button('Mark returned')
    if submit:
        if not confirmed:
            st.error('Confirm the human verification before marking returned.')
        else:
            try:
                mark_returned(item_id)
            except (OSError, ValueError, Timeout):
                st.error('Return could not be saved. The item may already be returned; refresh and check the record.')
            else:
                st.success(f'Item #{item_id} is returned and will no longer appear in search.')
