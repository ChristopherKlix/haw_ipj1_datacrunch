import streamlit as st
import pandas as pd
import altair as alt

import init_page


class Trash_View:
    def __init__(self):
        print("Trash_View init")

    def render(self):
        page = init_page.PageManager()
        data = page.get_data()

        st.title("Trash")
        st.write("Hier kommt der Müll hin.")

        data = {
            "Date": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "PV": [2, 5, 7, 4, 2, 7, 2],
            "Wind Offshore": [6, 3, 1, 4, 5, 6, 3],
            "Andere": [3, 2, 4, 1, 2, 5, 3],
        }

        df = pd.DataFrame(data)

        df_melted = df.melt(id_vars=["Date"], var_name="Energy Source", value_name="Energy Value")

        chart = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X(
                'Date:O',
                axis=alt.Axis(title='Date')
            ),
            y=alt.Y(
                'sum(Energy Value):Q',
                # stack="normalize",
                axis=alt.Axis(title='Energy Value')
            ),
            color=alt.Color(
                'Energy Source:N',
                legend=alt.Legend(title='Energy Source')
            ),
            tooltip=['Date', 'Energy Value']
        ).properties(
            title='Stacked Bar Chart of Energy Sources'
        )

        st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    view = Trash_View()
    view.render()
