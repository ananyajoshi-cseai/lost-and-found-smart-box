import streamlit as st
from finder_core.engine import parse, rank
from finder_core.scoring import WEIGHTS
from finder_core.ui import records

st.header('Search for a lost item')
st.caption('Try “navy Milton flask” or “bottle not blue”. We understand only the listed vocabulary; spelling and complex negation may need rephrasing.')
text = st.text_input('Describe your item', max_chars=300, key='query')
broaden = st.checkbox('Include related categories', key='broaden')
parsed = parse(text)
if text:
    st.write('Understood:', ', '.join(f'{k}: {v}' for k,v in parsed['positive'].items()) or 'No known attributes')
    if parsed['excluded']:
        st.write('Excluded:', ', '.join(f'{k}: {", ".join(v)}' for k,v in parsed['excluded'].items()))
    st.caption('Check this interpretation before searching. “not a blue bottle” has unsupported negation scope; use “bottle not blue”.')
if st.button('Find matches', key='search'):
    if parsed['ambiguous']:
        st.warning('Please clarify: '+', '.join(parsed['ambiguous']))
    elif not parsed['positive']:
        st.info('Add a known category or color to search.')
    else:
        items = records()
        matches = rank(parsed, items, broaden)
        if not matches:
            st.info('No matching available items. Try different details or include related categories.')
        for result in matches:
            item = next(i for i in items if i['id']==result['id'])
            with st.container(border=True):
                st.subheader(f'Item #{item["id"]} · {item["color"].title()} {item["category"]}')
                st.write({key:item[key] for key in ['brand','location','mark']})
                st.write(f'Score: {result["score"]:.2f} / 100 · {result["coverage_text"]}')
                st.caption('Text agreement, not ownership probability.')
                st.write('Related suggestion, different category' if result['related'] else 'Candidate match')
                if result['strong_candidate']:
                    st.caption('Category, color and brand agree. Human verification is still required.')
                st.table([{'Field':field, 'Points':points, 'Possible':WEIGHTS[field]}
                          for field,points in result['reasons'].items()])
                st.caption('Contact the campus lost-and-found desk to verify ownership; this demo does not submit claims.')
