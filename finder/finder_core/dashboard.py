"""Presentation helpers and charts derived only from stored records or scores."""
from collections import Counter
from html import escape
import math

import altair as alt
import pandas as pd
import streamlit as st
from .scoring import WEIGHTS

TEAL = '#087F8C'
NAVY = '#172B3A'
AMBER = '#C17A17'
PALETTE = ['#087F8C', '#42A99A', '#E5AD54', '#53768B', '#8B86B3', '#B97963', '#73A4B8']


def style():
    st.html("""<style>
    .block-container { max-width: 1280px; padding-top: 4rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { border-right: 1px solid #7d929b40; }
    [data-testid="stMetric"] { background: transparent; border: 1px solid #7d929b60;
        border-radius: 14px; padding: 14px 12px; }
    [data-testid="stMetricValue"] { color: inherit; font-weight: 700; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px; }
    h1,h2,h3 { letter-spacing: -.035em; }
    .finder-hero { background: #172b3a; border-radius: 20px; padding: 28px 32px;
        margin-bottom: 22px; border-bottom: 4px solid #42a99a; color: #fff; }
    .finder-hero h1 { color: #fff; margin: 8px 0; font-size: clamp(28px,3vw,40px); line-height: 1.2; }
    .finder-hero p { color: #d1e0e5; margin: 0; max-width: 720px; }
    .finder-eyebrow { color: #81d5c9; font-size: 12px; letter-spacing: .16em; font-weight: 700; }
    .finder-chip { display: inline-block; background: #e2f2ee; color: #155b54;
        padding: 6px 12px; border-radius: 20px; margin: 0 6px 7px 0; font-size: 13px; }
    .finder-chip.excluded { background: #fff0d8; color: #774700; }
    .finder-footnote { color: inherit; opacity: .75; font-size: 12px; margin-top: 24px; }
    @media(max-width: 1100px) { [data-testid="stHorizontalBlock"] { flex-wrap: wrap; } [data-testid="stColumn"] { min-width: min(100%, 260px); } }
    .st-key-inventory-metrics [data-testid="stColumn"] { min-width: min(100%, 170px); }
    @media(max-width: 640px) { .finder-hero { padding: 22px 18px; } .block-container { padding-top: 3.5rem; } }
    </style>""")


def hero(eyebrow, title, description):
    st.html(f'<section class="finder-hero"><span class="finder-eyebrow">{escape(eyebrow)}</span>'
            f'<h1>{escape(title)}</h1><p>{escape(description)}</p></section>')


def metrics(items):
    available = sum(i['status'] == 'available' for i in items)
    values = [('Recorded', len(items)), ('Available', available),
              ('Returned', len(items) - available),
              ('Locations', len({i['location'] for i in items}))]
    with st.container(key='inventory-metrics'):
        for col, (label, value) in zip(st.columns(4), values):
            col.metric(label, value)


def counts(items, field):
    return [{'Label': str(label).title(), 'Items': count}
            for label, count in sorted(Counter(i[field] for i in items).items(),
                                       key=lambda pair: (-pair[1], pair[0]))]


def finish(chart, height=270):
    # Streamlit applies the viewer's active theme to axes, legends and background.
    return chart.properties(height=height).configure_view(stroke=None).configure_axis(
        labelFontSize=12, titleFontSize=12)


def bars(items, field, label, key):
    if not items:
        st.info('No records yet. A saved item will appear here.')
        return
    chart = alt.Chart(pd.DataFrame(counts(items, field))).mark_bar(
        color=TEAL, cornerRadiusEnd=5, size=16).encode(
        y=alt.Y('Label:N', sort='-x', title=None, axis=alt.Axis(labelLimit=150)),
        x=alt.X('Items:Q', title='Items', axis=alt.Axis(tickMinStep=1)),
        tooltip=[alt.Tooltip('Label:N', title=label), 'Items:Q'])
    st.altair_chart(finish(chart, max(220, len(counts(items, field))*27)),
                   width='stretch', key=key, alt=f'Item counts by {label.lower()}.')


def status_donut(items, key):
    if not items:
        st.info('No records yet. Return status will appear after items are reported.')
        return
    df = pd.DataFrame([{'Status': status.title(), 'Items': sum(i['status'] == status for i in items)}
                       for status in ('available', 'returned')])
    chart = alt.Chart(df).mark_arc(innerRadius=70, outerRadius=100, cornerRadius=5).encode(
        theta=alt.Theta('Items:Q'), color=alt.Color('Status:N', scale=alt.Scale(
            domain=['Available', 'Returned'], range=[TEAL, '#E5AD54']),
            legend=alt.Legend(orient='bottom', title=None)),
        tooltip=['Status:N', 'Items:Q'])
    st.altair_chart(finish(chart, 250), width='stretch', key=key,
                   alt='Available and returned item counts.')
    st.caption('Current inventory status, not a recovery rate over time.')


def heatmap(items, key):
    if not items:
        st.info('No available items to map yet.')
        return
    categories = sorted({i['category'] for i in items})
    locations = sorted({i['location'] for i in items})
    totals = Counter((i['category'], i['location']) for i in items)
    df = pd.DataFrame([{'Category': c.title(), 'Location': l.title(), 'Items': totals[c, l]}
                       for c in categories for l in locations])
    base = alt.Chart(df).encode(x=alt.X('Location:N', title=None, axis=alt.Axis(labelAngle=-30)),
        y=alt.Y('Category:N', title=None, axis=alt.Axis(labelOverlap=False)), tooltip=['Category:N', 'Location:N', 'Items:Q'])
    rect = base.mark_rect(cornerRadius=3, stroke='white', strokeWidth=3).encode(
        color=alt.Color('Items:Q', scale=alt.Scale(range=['#EAF3F3', TEAL], domainMin=0),
                        legend=alt.Legend(title='Items', orient='bottom')))
    text = base.mark_text(fontSize=12).encode(text='Items:Q',
        color=alt.condition(alt.datum.Items > max(totals.values())/2, alt.value('white'), alt.value(NAVY)))
    st.altair_chart(finish(rect + text, max(220, len(categories)*29)), width='stretch', key=key,
                   alt='Available items by category and found location; each cell gives a count.')


def score_bars(result, key):
    rows = []
    for field, earned in result['reasons'].items():
        rows.extend([{'Attribute': field.title(), 'Points': earned, 'Part': 'Matched'},
                     {'Attribute': field.title(), 'Points': WEIGHTS[field]-earned, 'Part': 'Unmatched'}])
    chart = alt.Chart(pd.DataFrame(rows)).mark_bar(cornerRadiusEnd=4).encode(
        y=alt.Y('Attribute:N', sort=[f.title() for f in WEIGHTS], title=None, axis=alt.Axis(labelOverlap=False)),
        x=alt.X('Points:Q', stack='zero', scale=alt.Scale(domain=[0,40]), title='Weighted points'),
        color=alt.Color('Part:N', scale=alt.Scale(domain=['Matched','Unmatched'],range=[TEAL,'#DCE5E8']),
                        legend=alt.Legend(orient='bottom',title=None)),
        tooltip=['Attribute:N','Part:N','Points:Q'])
    st.altair_chart(finish(chart, 200),width='stretch',key=key,
                   alt='Matched and unmatched weighted points for supplied attributes.')


def radar_svg(result):
    # Agreement per axis is binary. Missing evidence is labelled, not treated as a mismatch.
    cx, cy, radius = 220, 175, 105
    fields = list(WEIGHTS)
    def point(index, scale):
        angle = -math.pi/2 + index*2*math.pi/5
        return cx + math.cos(angle)*radius*scale, cy + math.sin(angle)*radius*scale
    def polygon(scales):
        return ' '.join(f'{x:.1f},{y:.1f}' for x,y in (point(i,s) for i,s in enumerate(scales)))
    # SVG images do not inherit Streamlit's theme. Use a self-contained dark panel
    # with high-contrast labels, readable in either application theme.
    shapes = ['<rect width="440" height="340" rx="16" fill="#172B3A"/>']
    for scale in (.25,.5,.75,1):
        shapes.append(f'<polygon points="{polygon([scale]*5)}" fill="none" stroke="#537080"/>')
    for i, field in enumerate(fields):
        x,y = point(i,1)
        lx,ly = point(i,1.38)
        state = 'Not supplied' if field not in result['reasons'] else ('Match' if result['reasons'][field] else 'Mismatch')
        shapes.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="#537080"/>')
        shapes.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" fill="#E6EFF3" font-size="12">{field.title()}</text>')
        shapes.append(f'<text x="{lx}" y="{ly+16}" text-anchor="middle" fill="#B5C9D3" font-size="10">{state}</text>')
    scales = [1 if result['reasons'].get(field,0) else 0 for field in fields]
    shapes.append(f'<polygon points="{polygon(scales)}" fill="#5DD6C5" fill-opacity="0.25" stroke="#5DD6C5" stroke-width="2.5"/>')
    for i,scale in enumerate(scales):
        x,y=point(i,scale)
        shapes.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#5DD6C5"/>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 340" role="img" aria-label="Attribute agreement radar; outer points indicate matches. Read labels for missing attributes." style="width:100%;max-height:290px;font-family:Arial,sans-serif">'+''.join(shapes)+'</svg>'


def facts_chips(parsed):
    pieces = [f'<span class="finder-chip">{escape(field.title())}: {escape(value.title())}</span>'
              for field,value in parsed['positive'].items()]
    pieces += [f'<span class="finder-chip excluded">Exclude {escape(field)}: {escape(", ".join(values))}</span>'
               for field,values in parsed['excluded'].items()]
    st.html(''.join(pieces))


def color_pie(items, key):
    if not items:
        st.info('No records yet. Color distribution will appear after reporting.')
        return
    rows = counts(items, 'color')
    if len(rows) > 5:
        rows = rows[:5] + [{'Label': 'Other colors', 'Items': sum(row['Items'] for row in rows[5:])}]
    chart = alt.Chart(pd.DataFrame(rows)).mark_arc(outerRadius=80, stroke='white', strokeWidth=2).encode(
        theta=alt.Theta('Items:Q'), color=alt.Color('Label:N', scale=alt.Scale(range=PALETTE),
        legend=alt.Legend(orient='bottom', title=None, columns=2)), tooltip=['Label:N','Items:Q'])
    st.altair_chart(finish(chart, 230),width='stretch',key=key,
                   alt='Reported item colors: five most common colors, with the rest grouped together.')
    st.caption('Five most common colors; remaining colors are grouped as Other colors.')
