import streamlit as st
import streamlit.components.v1 as components
import datetime as dt
import sys
from data_manager.data_manager import Collections, DataManager
from dtypes import URLImage, View

from navbar import Navbar

import data as data_loader

from expire import EXPIRATION_DATE

class PageManager:
    def __init__(self, layout: str = "centered") -> None:
        self.layout = layout
        self.config()
        self.render_navbar()
        self.init_session_state()

        if self.is_expired():
            st.empty()
            st.error("Diese Demo ist abgelaufen. Die neue App ist ab Meilenstein 3 verfügbar.")
            View.image(URLImage('https://cdn.dribbble.com/users/367174/screenshots/1343487/expired-account.gif'))
            sys.exit(1)

    def is_expired(self) -> bool:
        return False
        # current_time = dt.datetime.now()

        # return current_time >= EXPIRATION_DATE

    def config(self):
        print("PageLoader config")

        # Read about.md file
        about_md = 'Error. Could not read file.'
        with open("./static/about.md", "r") as f:
            about_md = f.read()

        st.set_page_config(
            page_title="Energy Dashboard",
            page_icon="⚡",
            initial_sidebar_state='collapsed',
            layout=f'{self.layout}',
            menu_items={
                # 'Get Help': 'http://localhost:8501/',
                # 'Report a bug': 'http://localhost:8501/',
                'About': f'{about_md}',
            }
        )

        with open("./static/sources.css", "r") as file:
            style = file.read()
            st.markdown(f'<style>{style}</style>', unsafe_allow_html=True)

            # st.markdown(
            #     """
            #     <style>
            #         .st-emotion-cache-1n76uvr {
            #             top: -5rem;
            #         }
            #     </style>
            #     """,
            #     unsafe_allow_html=True
            # )

    def init_session_state(self):
        # Sidebar State
        if 'sidebar_state' not in st.session_state:
            st.session_state.sidebar_state = 'collapsed'

        # Min Coverage
        if 'min_coverage' not in st.session_state:
            st.session_state.min_coverage = 80

    def render_navbar(self):
        Navbar.render()

    @staticmethod
    @st.cache_data(show_spinner="Parsing and caching data...")
    def get_data():
        # Get the data
        # with st.spinner('Loading data...'):
        data_manager = DataManager()
        collections: Collections = data_manager.get_data()
        return collections

        # data_0, data_1 = data_loader.main()

        # if data_0 is None:
        #     # toast = st.error('Data could not be loaded!', icon="❌")
        #     return None, None
        # else:
        # #     toast = st.success('Data loaded successfully!', icon="✅")
        #     return data_0, data_1
