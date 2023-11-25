import streamlit as st
import datetime as dt
import pandas as pd
import numpy as np
import altair as alt


class Source:
    def __init__(self, title: str, author: str, date: str, url: str, is_gov_source: bool = False, government_locality: str = None):
        self.title = title
        self.author = author
        self.date = dt.datetime.strptime(date, "%Y-%m-%d")
        self.url = url
        self.is_gov_source = is_gov_source
        self.government_locality = government_locality

    def get_date_APA7(self) -> str:
        return self.date.strftime("%Y, %B %d").replace(" 0", " ")

    def get_gov_local_icon (self) -> str:
        if self.government_locality == "de":
            return "🇩🇪"
        elif self.government_locality == "eu":
            return "🇪🇺"
        else:
            return "🌍"

class URLImage:
    def __init__(self, url: str, alt: str = None, width: int | None = None):
        self.url = url
        self.alt = alt
        self.width = width

    def __str__(self) -> str:
        return self.get_html()

    def get_html(self) -> str:
        width = f'{self.width}' if self.width is not None else '100%'
        return f'<img src=\"{self.url}\" alt=\"{self.alt}\" class=\"image__img\" width="{width}"/>'


class View:
    @staticmethod
    def image(image: URLImage):
        st.markdown(f'{image.get_html()}<div class="image__caption"><a href=\"{image.url}\">Source: {image.alt}</a></div>', unsafe_allow_html=True)

    @staticmethod
    def demo_chart():
        df = pd.DataFrame({
            'index': [1, 2, 3, 4, 5],
            'wheat': [10, 20, 30, 40, 50],
            'barley': [20, 10, 40, 30, 60]
        })

        chart = alt.Chart(df).mark_area().encode(
            x='index',
            y='count()',
            color='wheat'
        )

        st.altair_chart(chart, use_container_width=True)

    @staticmethod
    def background():
        st.markdown(
            '''
            <div id="background-image">
                <div id="background-image__content">
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

        with open("./static/background.css", "r") as file:
            css = file.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
