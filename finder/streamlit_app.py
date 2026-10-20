import streamlit as st

st.set_page_config(page_title='Campus Lost & Found Finder', page_icon='🔎', layout='centered')
st.title('Campus Lost & Found Finder')
st.caption('Describe it. Find possible matches. Verify ownership in person.')
st.sidebar.caption('Local classroom demo • synthetic records • no login')
page = st.navigation([
    st.Page('views/search.py', title='Search', default=True),
    st.Page('views/report.py', title='Report Found Item'),
    st.Page('views/staff.py', title='Staff — mark returned'),
])
page.run()
