import streamlit as st

import init_page
from dtypes import Source, View
from sources import sources


class Quellen_View:
    def __init__(self):
        print("Quellen_View init")
        self.sources = sources


    def render(self):
        self.page = init_page.PageManager()

        View.background()

        st.title("Quellen")
        st.markdown("""
                    Hier sind alle Quellen aufgelistet, die für die Erstellung dieses Dashboards verwendet wurden.
                    Offizielle Quellen von Regierungen sind mit dem Icon der jeweiligen Regierung gekennzeichnet.
                    """)

        for source in self.sources:
            self.View.source(source)

    class View:
        @staticmethod
        def source(source: Source):
            st.markdown(f"""
                <div class="source">
                    <div class="source__author {'source__governmental' if source.is_gov_source else ''}">{source.get_gov_local_icon() + ' ' if source.is_gov_source else ''}{source.author}.</div>
                    <div class="source__date">({source.get_date_APA7()}).</div>
                    <div class="source__title">{source.title}.</div>
                    <div class="source__url"><a href="{source.url}">{source.url}.</a></div>
                </div>
            """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    view = Quellen_View()
    view.render()
