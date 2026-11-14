import streamlit as st
from finder_core.engine import parse_with_vague_matching, rank, suggest_corrections, apply_correction
from finder_core.scoring import WEIGHTS
from finder_core.ui import records
from finder_core.dashboard import hero, metrics, facts_chips, bars, heatmap, score_bars, radar_svg

hero('01 / DISCOVER', 'Find your missing piece.',
     'Describe what you lost. Explore possible matches. Reunite with your belongings after an in-person check.')
items = records()
metrics(items)
st.write('')
with st.container(border=True):
    st.subheader('Search for a lost item')
    text = st.text_input('Describe your item', placeholder='Try: navy Milton flask near the library', max_chars=300, key='query')
    broaden = st.checkbox('Include related categories', key='broaden', help='Explore nearby categories only when no eligible exact-category item exists.')
    parsed = parse_with_vague_matching(text)
    if parsed.get("clarification_options"):
        choice = st.selectbox(
            "Which item do you mean?",
            ["Choose one"] + parsed["clarification_options"],
            key=f"vague_choice_{text}"
        )

        if choice != "Choose one":
            parsed["positive"]["category"] = choice
            parsed["ambiguous"] = [
                field for field in parsed["ambiguous"]
                if field != "category"
            ]
    def _accept(typed, suggestion):
        st.session_state['query'] = apply_correction(st.session_state.get('query', ''), typed, suggestion)
    for fix in suggest_corrections(text):
        word = fix['suggestion'].title() if fix['field'] == 'brand' else fix['suggestion']
        left, right = st.columns([3, 1], vertical_alignment='center')
        left.write(f'Did you mean **{word}**? You typed “{fix["typed"]}”.')
        right.button(f'Use {word}', key=f'fix_{fix["typed"]}', on_click=_accept,
                     args=(fix['typed'], fix['suggestion']))
    if text:
        st.caption('UNDERSTOOD · Check these details before searching')
        if parsed['positive'] or parsed['excluded']:
            facts_chips(parsed)
        else:
            st.caption('No known attributes yet.')
    searched = st.button('Find matches', key='search', type='primary', icon=':material/search:')
    st.caption('Plurals, short forms (bttl, chgr, earbuds, specs) and exclusions such as “not a blue bottle” or “bottle not blue” are understood. Close misspellings are offered as suggestions; unknown words are ignored.')

# Keep results visible on chart interactions, but clear them when the query changes.
signature = (text, broaden)
if searched:
    st.session_state['searched_signature'] = signature
if st.session_state.get('searched_signature') == signature:
    if parsed['ambiguous']:
        if "category" in parsed["ambiguous"] and parsed.get("clarification_options"):
            st.warning("Please choose an item from the options above.")
        else:
            st.warning('Please clarify: '+', '.join(parsed['ambiguous']))
    elif not parsed['positive']:
        st.info('Add a known category or color to search.')
    else:
        matches = rank(parsed, items, broaden)
        st.subheader('Your possible matches')
        st.caption(f'{len(matches)} shown · Up to 3 candidates · Minimum score 50 · Sorted by score, then item ID')
        if not matches:
            st.info('No matching available items. Try different details or include related categories.')
        for index, result in enumerate(matches, 1):
            item = next(i for i in items if i['id'] == result['id'])
            with st.container(border=True):
                st.caption(f'MATCH {index:02d} · '+('RELATED CATEGORY' if result['related'] else 'CANDIDATE'))
                st.subheader(f'Item #{item["id"]} · {item["color"].title()} {item["category"]}')
                st.write(f'Score: {result["score"]:.2f} / 100 · {result["coverage_text"]}')
                st.progress(result['score']/100)
                st.text('Brand: '+(item['brand'] or 'Not supplied')+' | Found at: '+item['location']+' | Mark: '+(item['mark'] or 'Not supplied'))
                st.caption('Text agreement, not ownership probability.')
                if result['related']:
                    st.info('Related suggestion, different category')
                if result['strong_candidate']:
                    st.caption('Category, color and brand agree. Human verification is still required.')
                with st.expander('Explore this match', expanded=index == 1):
                    points, agreement, table = st.tabs(['Weighted points', 'Attribute radar', 'Exact breakdown'])
                    with points:
                        score_bars(result, f'points_{item["id"]}')
                        st.caption('Only supplied attributes contribute to the score denominator.')
                    with agreement:
                        st.image(radar_svg(result), width=440)
                        st.caption('Outer edge = match. Center = mismatch or not supplied; axis labels distinguish them. This shows agreement, not confidence. Use Exact breakdown for the numbers.')
                    with table:
                        st.table([{'Field':field, 'Points':points, 'Possible':WEIGHTS[field]}
                                  for field,points in result['reasons'].items()])
                st.caption('Contact the campus lost-and-found desk to verify ownership; this demo does not submit claims.')

st.divider()
st.subheader('Explore the lost & found')
st.caption('Live snapshot of available items only. Hover over a chart for exact counts.')
available = [i for i in items if i['status'] == 'available']
category, location = st.tabs(['By category', 'Category × location'])
with category:
    bars(available, 'category', 'Category', 'search_categories')
with location:
    heatmap(available, 'search_locations')
