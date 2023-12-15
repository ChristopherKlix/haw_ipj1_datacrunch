import streamlit as st
import datetime as dt
import pandas as pd
import numpy as np
import altair as alt


def st_todo(s: str = ''):
    s = s.strip()

    lipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. At lectus urna duis convallis convallis tellus id. Diam sollicitudin tempor id eu nisl nunc mi ipsum faucibus. Ut pharetra sit amet aliquam.'

    content = s if s else lipsum

    st.markdown(
        f'''
        <div class="todo-wrapper" style="margin: 1rem 0; background-color: #FFD700; border-radius: 0.5rem;">
            <div class="todo-tag" style="display: inline-block; padding: 0.1rem 0.5rem; margin: 0.5rem; background-color: #000000; color: #FFD700; border-radius: 0.5rem;">
                TODO:
            </div>
            <div class="todo-content" style="display: inline-block; padding: 0.1rem; margin: 0.5rem;">
                {content}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

st.todo = st_todo


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


class Unit:
    # ----------
    # Energy
    # ----------
    @staticmethod
    def PWh(value) -> int:
        return value * 1_000_000_000_000_000

    @staticmethod
    def TWh(value) -> int:
        return value * 1_000_000_000_000

    @staticmethod
    def GWh(value) -> int:
        return value * 1_000_000_000

    @staticmethod
    def MWh(value) -> int:
        return value * 1_000_000

    @staticmethod
    def kWh(value) -> int:
        return value * 1_000

    # ----------
    # Power
    # ----------
    @staticmethod
    def PW(value) -> int:
        return value * 1_000_000_000_000_000

    @staticmethod
    def TW(value) -> int:
        return value * 1_000_000_000_000

    @staticmethod
    def GW(value) -> int:
        return value * 1_000_000_000

    @staticmethod
    def MW(value) -> int:
        return value * 1_000_000

    @staticmethod
    def kW(value) -> int:
        return value * 1_000

    # ----------
    # Mass
    # ----------
    @staticmethod
    def kg(value) -> int:
        return value

    @staticmethod
    def g(value) -> int:
        return value / 1_000

    @staticmethod
    def tonne(value) -> int:
        return value * 1_000

    @staticmethod
    def kt(value) -> int:
        return value * 1_000_000
