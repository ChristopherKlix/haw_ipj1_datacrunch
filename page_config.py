import streamlit as st


if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

# Read about.md file
about_md = 'Error. Could not read file.'
with open("./static/about.md", "r") as f:
    about_md = f.read()

st.set_page_config(
    page_title="Energy Dashboard",
    page_icon="⚡",
    initial_sidebar_state=st.session_state.sidebar_state,
    # layout="wide",
    menu_items={
        'Get Help': 'http://localhost:8501/',
        'Report a bug': 'http://localhost:8501/',
        'About': f'{about_md}',
    }
)
