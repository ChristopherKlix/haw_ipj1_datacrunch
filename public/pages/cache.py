from time import perf_counter
import streamlit as st
import pandas as pd
import altair as alt
from data_manager.data_manager import DataManager

from init_page import PageManager


class Cache_View:
    def __init__(self):
        print("Cache_View init")

        self.page = PageManager(layout="centered")

    def render(self):
        st.title("Cache data")

        cols = st.columns(2, gap='medium')

        cache_btn = cols[0].button("Cache data")

        if cache_btn:
            st.code("Caching data...")
            start_time = perf_counter()

            self.page.get_data()

            caching_time = perf_counter() - start_time
            st.code(f"Caching time: {caching_time} seconds")
            st.success("Data cached!")


if __name__ == "__main__":
    view = Cache_View()
    view.render()
