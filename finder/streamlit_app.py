import streamlit as st
from finder_core.dashboard import style

st.set_page_config(page_title='Campus Lost & Found Finder', page_icon='🔎', layout='wide')
style()
st.sidebar.markdown('## 🔎 Campus Finder')
st.sidebar.caption('LOST & FOUND · CAMPUS EDITION')
page = st.navigation([
    st.Page('views/search.py', title='Search', icon=':material/search:', default=True),
    st.Page('views/report.py', title='Report Found Item', icon=':material/add_circle:'),
    st.Page('views/staff.py', title='Staff — mark returned', icon=':material/task_alt:'),
])
st.sidebar.divider()
st.sidebar.markdown('**A little detail. A better match.**')
st.sidebar.caption('Describe the category, color and any identifying marks to narrow your search.')
st.sidebar.info('Local classroom demo · synthetic records · no login')
page.run()
st.html('<p class="finder-footnote">CAMPUS LOST & FOUND FINDER · Rule-based matching · Ownership verified in person</p>')
