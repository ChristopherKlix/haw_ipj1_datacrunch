import streamlit as st
import datetime as dt
import pandas as pd
import numpy as np
from numpy.typing import NDArray
import altair as alt
from gpt import ask

import init_page

from dtypes import View
from data import Data

from data_manager.data_manager import Collections, DataArray, Data


class IST_View:
    def __init__(self):
        print("IST_View init")

        self.start_date = dt.datetime(2015, 1, 1, 0, 0)
        self.end_date = dt.datetime(2022, 12, 31, 0, 0)

        # Set default value for session_state dialog
        if 'dialog' not in st.session_state:
            st.session_state.dialog = IST_View.init_dialog()

        if 'dialog_input' not in st.session_state:
            st.session_state['dialog_input'] = ''

    def render(self):
        self.page = init_page.PageManager()

        st.title("Ist-Zustand")

        View.background()

        with st.expander("🛠️ Parameter", expanded=True):
            self.render_param_view()

        st.markdown('### Plot')
        plot_area = st.container()

        with st.spinner('Updating plot'):
            plot_area = self.render_plot_view_new()

        dialog_area = st.container()

        dialog_area.markdown('### Du hast ne Frage?')

        # Get the last two items in the st.session_state['dialog'] list
        dialog = st.session_state['dialog'][-2:]

        for message in dialog:
            if message['role'] == 'assistant':
                icon = '🤖'
            else:
                icon = ''

            dialog_area.markdown(
                f'''
                <div class="dialog {message["role"]}">
                    <div class="dialog-icon">{icon}</div>
                    <div class="dialog-message">{message["content"]}</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

        dialog_area.markdown(
            '''
            <style>
                .dialog {
                    margin: 0.5rem 0;
                    max-width: fit-content;
                }

                .dialog-icon {
                    display: inline-block;
                    width: 1.5rem;
                }

                .dialog-message {
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    border-radius: 0.5rem;
                    line-height: 1.6;
                }

                .system {
                    display: none;
                }

                .assistant {
                    text-align: left;
                }

                .assistant .dialog-message {
                    background-color: rgb(255, 75, 75);
                    color: #FFFFFF;
                }

                .user {
                    text-align: right;
                    max-width: fit-content;
                    margin-left: auto;
                }

                .user .dialog-message {
                    background-color: #F0F2F6;
                }
            </style>
            ''',
            unsafe_allow_html=True
        )


        dialog_input = dialog_area.text_input(
            label='User input',
            value=st.session_state['dialog_input'],
            key='dialog_input',
            help='Stelle eine Frage an den Chatbot.',
            on_change=self.perform_gpt_request,
            placeholder='Wieso ist...',
            label_visibility='collapsed'
        )

        chat_btns = dialog_area.columns([1, 1, 1])

        with chat_btns[0]:
            st.button('Clear chat', on_click=self.clear_chat)
        with chat_btns[1]:
            st.button('Play game', on_click=self.play_game)

        st.markdown(
            """
            ## Eneuerbare Energien

            Erneuerbare Energien spielen eine entscheidende Rolle in der nachhaltigen Energieversorgung und tragen maßgeblich zur Reduzierung von Emissionen bei.
            Anders als fossile Energieträger sind erneuerbare Energien nicht endlich und können somit unendlich genutzt werden.
            Die Nutzung von erneuerbaren Energien ist jedoch nicht ohne Nachteile.
            So ist die Energieerzeugung von erneuerbaren Energien stark von den Wetterbedingungen abhängig
            und bietet keine konstante Energieerzeugung, wie es traditionelle Energieträger tun.

            ### Energieträger - Erneuerbare vs. Fossile

            Anders als bei fossilen Energieträgern, werden erneuerbare Energien nicht in Form von Brennstoffen geliefert.
            Fossile Brennstoffe werden wortwörtlich verbrannt, um Wärme zu erzeugen, die dann mittels einer Turbine und Generatoren in Strom umgewandelt wird.
            Erneuerbare Energien (mit Ausnahme von Biomasse) haben einen direkteren Weg zur Stromerzeugung.
            Wind- und Wasserkraft werden direkt in mechanische Energie umgewandelt, welche dann mittels Generatoren in Strom umgewandelt wird.
            Photovoltaik nutzt die Sonnenenergie, um Licht (Photonen) direkt in Strom (Elektronen) zu umzuwandeln.
            """
        )

        st.metric(label="Photovoltaik", value="~26%", delta="~ 50%")
        st.metric(label="WEA", value="~50%", delta="+-10%")
        st.metric(label="Biomasse", value="~1%", delta="+-0.5%")
        st.metric(label="Geothermie", value="~15%", delta="+-5%")

    def perform_gpt_request(self) -> str:
        text = st.session_state['dialog_input']

        if not text == '':
            st.session_state.dialog.append({
                'role': 'user',
                'content': text,
            })

        st.session_state['dialog_input'] = ''

        response = ask(history=st.session_state['dialog'])

        st.session_state.dialog.append({
            'role': 'assistant',
            'content': response,
        })

    def clear_chat(self) -> None:
        st.session_state.dialog = IST_View.init_dialog()

    def play_game(self) -> None:
        st.session_state.dialog = [
            {
                'role': 'system',
                'content': '''
                    Spiel ein Spiel mit dem user. Du fragst etwas zum Thema erneuerbare Energien und der user muss es beantworten.
                    Wenn er es richtig beantwortet, dann bekommt er einen Punkt. Wenn er es falsch beantwortet, dann bekommt er keinen Punkt.
                    Bleibe beim Thema und lass dich nicht von der Bahn bringen. Nach der Antwort stellst du direkt immer die nächste Frage.
                    Und nutze Emojis.
                    ''',
            }
        ]

        st.session_state['dialog_input'] = ''

        self.perform_gpt_request()

    @staticmethod
    def init_dialog() -> dict:
        return [
            {
                'role': 'assistant',
                'content': 'Hi, wie kann ich dir helfen?',
            }
        ]

    def render_param_view(self):
        columns = st.columns(3)

        min_date = dt.date(2015, 1, 1)
        max_date = dt.date(2022, 12, 31)

        self.intervals = {
            'total': 'Gesamt',
            'year': 'Jahr',
            'month': 'Monat',
            'day': 'Tag',
        }

        with columns[0]:
            self.selection_interval = st.selectbox(
                label='Interval',
                options=self.intervals.values(),
                index=0,
                help="Das Interval, welches von dem Plot dargestellt werden soll."
                )

            if self.selection_interval == self.intervals.get('total'):
                self.start_date = dt.datetime(2015, 1, 1, 0, 0)
                self.end_date = dt.datetime(2022, 12, 31, 23, 59)

        with columns[1]:
            if self.selection_interval == self.intervals.get('year'):
                interval_selection_year = st.selectbox(
                    label='Jahr',
                    options=[2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
                    index=7,
                    disabled=(self.selection_interval == self.intervals.get('total'))
                )

                if interval_selection_year:
                    self.start_date = dt.datetime(interval_selection_year, 1, 1, 0, 0)
                    self.end_date = dt.datetime(interval_selection_year, 12, 31, 23, 59)
            elif self.selection_interval == self.intervals.get('month'):

                columns_month = st.columns(2)

                with columns_month[0]:
                    interval_selection_month = st.selectbox(
                        label='Monat',
                        options=['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August',
                                'September', 'Oktober', 'November', 'Dezember'],
                        index=0,
                        help="The data is available from 01.01.2020 to 31.12.2022."
                    )

                with columns_month[1]:
                    interval_selection_year = st.selectbox(
                        label='Jahr',
                        options=[2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
                        index=7,
                        disabled=(self.selection_interval == self.intervals.get('total'))
                    )

                if interval_selection_month:
                    self.start_date = dt.datetime(interval_selection_year, self.month_to_index(interval_selection_month), 1, 0, 0)

                    next_month = self.month_to_index(interval_selection_month)+1
                    if next_month > 12:
                        next_month = 1
                        interval_selection_year += 1
                    self.end_date = dt.datetime(interval_selection_year, next_month, 1, 23, 59)
            elif self.selection_interval == self.intervals.get('day'):
                selected_start_date = st.date_input(
                    label="Tag",
                    value=dt.date(2020, 1, 1),
                    min_value=min_date,
                    max_value=max_date,
                    format="DD.MM.YYYY",
                    key='date_input',
                    help="The data is available from 01.01.2015 to 31.12.2022.",
                    disabled=(self.selection_interval == self.intervals.get('total'))
                )

                if selected_start_date:
                    self.start_date = dt.datetime(selected_start_date.year, selected_start_date.month, selected_start_date.day, 0, 0)
                    self.end_date = dt.datetime(selected_start_date.year, selected_start_date.month, selected_start_date.day, 23, 59)
            else:
                st.date_input(
                    label="Gesamtzeitraum",
                    value=(dt.date(2015, 1, 1), dt.date(2022, 12, 31)),
                    format="DD.MM.YYYY",
                    key='date_input',
                    help="Die Daten sind verfügbar vom 01.01.2015 bis zum 31.12.2022.",
                    disabled=(self.selection_interval == self.intervals.get('total'))
                )

        with columns[2]:
            self.data_source_selection = st.selectbox(
                label='Data source',
                index=0,
                options=["SMARD.de", "Frauenhofer", "Agora Energiewende"]
            )

        columns_range = st.columns(3)

        with columns_range[0]:
            if self.data_source_selection == "Frauenhofer":
                self.plot_selection = st.selectbox(
                    label='Plots',
                    options=["Energieerzeugung", "Verbrauch"]
                )
            else:
                self.plot_selection = st.selectbox(
                    label='Plots',
                    options=["Energieerzeugung", "Installierte Leistung", "Verbrauch"]
                )

        with columns_range[1]:
            self.source_selection = st.selectbox(
                label='Energiequellen',
                options=["Alle", "Nur Erneuerbare", "Nur Fossile", "Benutzerdefiniert"],
                help="Only show the renewable energy sources.",
            )

        # with columns_range[2]:
        if self.data_source_selection == "Frauenhofer":
            st.warning("Installierte Leistung bei Frauenhofer nicht verfügbar.")
        elif self.data_source_selection == "Agora Energiewende":
            st.error("Daten von Agora Energiewende sind noch nicht verfügbar.")

        if self.plot_selection == 'Installierte Leistung':
            st.error('Installierte Leistung hat aktuell fehlerhafte Daten. Bugfix in Arbeit.')

        if self.source_selection == "Benutzerdefiniert":
            self.selected_energy_sources = st.multiselect(
                label='Energiequellen',
                options=["Wind Offshore", "Wind Onshore", "Photovoltaik", "Hydro", "Biomasse", "Steinkohle", "Braunkohle", "Gas", "Andere Erneuerbare", "Andere Konventionelle", "Nuclear"],
                default=["Wind Offshore", "Wind Onshore", "Photovoltaik", "Hydro", "Biomasse", "Steinkohle", "Braunkohle", "Gas", "Andere Erneuerbare", "Andere Konventionelle", "Nuclear"],
                disabled=self.plot_selection is "Verbrauch" or self.source_selection is not "Benutzerdefiniert",
                placeholder="Keine Energiequelle ausgewählt"
            )
        elif self.source_selection == "Nur Erneuerbare":
            self.selected_energy_sources = ["Wind Offshore", "Wind Onshore", "Photovoltaik", "Hydro", "Biomasse", "Andere Erneuerbare"]
        elif self.source_selection == "Nur Fossile":
            self.selected_energy_sources = ["Steinkohle", "Braunkohle", "Gas", "Andere Konventionelle"]
        else:
            self.selected_energy_sources = ["Wind Offshore", "Wind Onshore", "Photovoltaik", "Hydro", "Biomasse", "Steinkohle", "Braunkohle", "Gas", "Andere Erneuerbare", "Andere Konventionelle", "Nuclear"]

        self.time_range_resolution = 20
        # self.time_range_resolution = st.select_slider('Data Point Auflösung (jeder n-th data point wird angezeigt)',
        #                                         options=[1, 10, 20, 50, 100, 200, 500, 1_000, 10_000],
        #                                         value=20,
        #                                         key='time_range_resolution',
        #                                         help='The resolution of the time range. The higher the value, the less data points are displayed. This can help with performance issues.')
        # st.caption(f'The time range resolution determines how many data points are displayed. The higher the value, the less data points are displayed. This can help with performance issues but also reduces the accuracy of the data.')


    def render_plot_view(self):
        st.markdown('### Plot')

        # View.demo_chart()

        if self.selection_interval == self.intervals.get('total') or self.selection_interval == self.intervals.get('year') or self.selection_interval == self.intervals.get('month') or self.selection_interval == self.intervals.get('day'):
            # Bar chart with monthly data

            # Retrieve raw data
            raw_data = self.page.get_data()[0]

            # Find the start and end data
            i_y = self.start_date.year - 2020
            i_m = self.start_date.month - 1
            i_d = self.start_date.day - 1
            first_element: Data = raw_data[i_y, i_m, i_d, 0, 0]

            i_y = self.end_date.year - 2020
            i_m = self.end_date.month - 1
            i_d = self.end_date.day - 1
            last_element: Data = raw_data[i_y, i_m, i_d, 23, 3]

            # Flatten the data
            raw_data = raw_data.flatten()

            # Find the indices of the start and end data
            first_index = np.where(raw_data == first_element)
            last_index = np.where(raw_data == last_element)

            # Select the data between the start and end indices
            selected_data = raw_data[first_index[0][0]:last_index[0][0]+1]

            # Filter out the None values
            mask = np.array([item.start is not None for item in selected_data])
            filtered_data = selected_data[mask]

            # Create a time range
            energy_time_range = pd.date_range(
                start=self.start_date.strftime("%Y-%m-%d %H:%M"),
                end=self.end_date.strftime("%Y-%m-%d %H:%M"),
                freq='15min',
                tz='Europe/Berlin'
            )

            # Convert from Wh to TWh
            if self.selection_interval == self.intervals.get('day'):
                filtered_data /= 1_000_000_000
                y_axis_scale = "GWh"
            else:
                filtered_data /= 1_000_000_000_000
                y_axis_scale = "TWh"

            # Create a dataframe
            energy = {
                'Date': energy_time_range,
            }

            if 'Photovoltaik' in self.selected_energy_sources:
                energy['Photovoltaik'] = [d.pv for d in filtered_data]

            if 'Wind Offshore' in self.selected_energy_sources:
                energy['Wind Offshore'] = [d.wind_offshore for d in filtered_data]

            if 'Wind Onshore' in self.selected_energy_sources:
                energy['Wind Onshore'] = [d.wind_onshore for d in filtered_data]

            if 'Hydro' in self.selected_energy_sources:
                energy['Hydro'] = [d.hydro for d in filtered_data]

            if 'Biomasse' in self.selected_energy_sources:
                energy['Biomasse'] = [d.biomass for d in filtered_data]

            if 'Steinkohle' in self.selected_energy_sources:
                energy['Steinkohle'] = [d.coal for d in filtered_data]

            if 'Braunkohle' in self.selected_energy_sources:
                energy['Braunkohle'] = [d.charcoal for d in filtered_data]

            if 'Gas' in self.selected_energy_sources:
                energy['Gas'] = [d.gas for d in filtered_data]

            if 'Andere Erneuerbare' in self.selected_energy_sources:
                energy['Andere Erneuerbare'] = [d.other_renewables for d in filtered_data]

            if 'Andere Konventionelle' in self.selected_energy_sources:
                energy['Andere Konventionelle'] = [d.other_conventional for d in filtered_data]

            if 'Nuclear' in self.selected_energy_sources:
                energy['Atomkraft'] = [d.nuclear for d in filtered_data]

            energy_df = pd.DataFrame(energy)

            columns_mode = st.columns([2, 2, 2])

            with columns_mode[0]:
                mode = st.selectbox(
                    label='Absolut / Relativ',
                    options=["Absolut", "Relativ"],
                    index=0,
                    help="Absolut zeigt die Werte und relativ setzt diese im Vergleich zu der Gesamterzeugung pro Monat."
                )

            if self.selection_interval == self.intervals.get('total'):
                with columns_mode[1]:
                    sum_mode = st.selectbox(
                        label='Summe',
                        options=["Monat", "Jahr"],
                        index=0,
                        help="Die Summe der Energieerzeugung pro Monat oder Jahr."
                    )

            with columns_mode[2]:
                show_legend = st.selectbox(
                    label='Legende anzeigen',
                    options=["True", "False"],
                    index=0,
                    help="Zeigt die Legende an."
                )

            # Group and sum the data by month
            energy_df['Date'] = pd.to_datetime(energy_df['Date'])

            if self.selection_interval == self.intervals.get('total'):
                if sum_mode == "Monat":
                    energy_df['Date'] = energy_df['Date'].dt.strftime('%Y-%m')
                elif sum_mode == "Jahr":
                    energy_df['Date'] = energy_df['Date'].dt.strftime('%Y')
            elif self.selection_interval == self.intervals.get('year'):
                energy_df['Date'] = energy_df['Date'].dt.strftime('%Y-%m')
            elif self.selection_interval == self.intervals.get('month'):
                energy_df['Date'] = energy_df['Date'].dt.strftime('%Y-%m-%d')
            elif self.selection_interval == self.intervals.get('day'):
                energy_df['Date'] = energy_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
            energy_df = energy_df.groupby(['Date']).sum().reset_index()

            # Melt the dataframe
            energy_df_melted = pd.melt(energy_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")

            # Create the chart
            if self.selection_interval == self.intervals.get('day'):
                chart = alt.Chart(energy_df_melted).mark_area()
            else:
                chart = alt.Chart(energy_df_melted).mark_bar()

            energy_order = [
                'Andere Konventionelle',
                'Steinkohle',
                'Braunkohle',
                'Gas',
                'Atomkraft',
                'Andere Erneuerbare',
                'Hydro',
                'Biomasse',
                'Wind Offshore',
                'Wind Onshore',
                'Photovoltaik',
            ]

            energy_color = {
                'Photovoltaik': '#f2b134',
                'Wind Onshore': '#17B890',
                'Wind Offshore': '#3454D1',
                'Biomasse': '#7DDF64',
                'Hydro': '#63D2FF',
                'Andere Erneuerbare': '#00a0dc',
                'Atomkraft': '#0CCA4A',
                'Gas': '#FFE0B5',
                'Braunkohle': '#8A6552',
                'Steinkohle': '#CDD4DF',
                'Andere Konventionelle': '#6D5F6D',
            }

            custom_order = '{'

            for i, energy_source in enumerate(energy_order):
                custom_order += f"'{energy_source}': {i}, "

            custom_order += '}'

            chart = chart.transform_calculate(
                order=f'{custom_order}[datum.Energy_Source]'
            )

            chart = chart.encode(
                x=alt.X(
                    'Date:O',
                    axis=alt.Axis(title='Datum [M]')
                ),
                y=alt.Y(
                    'sum(Energy Value):Q',
                    stack=("normalize" if mode == "Relativ" else 'zero'),
                    axis=alt.Axis(title=f'Energieerzeugung [{y_axis_scale}]'),
                ),
                color=alt.Color(
                    'Energy_Source:N',
                    # sort=alt.SortField("order", "ascending"),
                    scale=alt.Scale(domain=list(energy_color.keys()), range=list(energy_color.values())),
                    legend=(alt.Legend(title='Energy Source') if show_legend == "True" else None),
                ),
                order='order:O',
                tooltip=['Energy_Source', 'Date', 'Energy Value']
            ).properties(
                height=500,
                title='Stacked Bar Chart of Energy Sources'
            ).configure_legend(
                labelFontSize=12,
                titleFontSize=14
            )

            st.altair_chart(chart, use_container_width=True)

    def render_plot_view_new(self):
        # Get collections
        collections: Collections = self.page.get_data()

        # Get range data
        if self.data_source_selection == "SMARD.de":
            filtered_data: NDArray = collections.smard.get_range(self.start_date, self.end_date)
        elif self.data_source_selection == "Frauenhofer":
            tz = 'Europe/Berlin'
            # Add tz to start and end date
            # self.start_date = self.start_date.replace(tzinfo=dt.timezone(dt.timedelta(hours=1)))
            # self.end_date = self.end_date.replace(tzinfo=dt.timezone(dt.timedelta(hours=1)))
            filtered_data: NDArray = collections.energycharts.get_range(self.start_date, self.end_date)
        elif self.data_source_selection == "Agora Energiewende":
            st.error("Daten von Agora Energiewende sind noch nicht verfügbar.")
            return

        # Create a time range
        energy_time_range = pd.date_range(
            start=self.start_date.strftime("%Y-%m-%d %H:%M"),
            end=self.end_date.strftime("%Y-%m-%d %H:%M"),
            freq='15min',
            tz='Europe/Berlin'
        )

        dummy_data_obj = collections.smard.get(start=self.start_date)

        print('%' * 50)
        print(f'Type: {type(filtered_data)}')
        print(f'Size: {filtered_data.size}')
        print('%' * 50)

        print('%' * 50)
        print(f'Type of i=0: {type(filtered_data[0])}')
        print(f'Type of Dummy: {type(dummy_data_obj)}')
        print('%' * 50)

        # Convert from Wh to GWh or TWh
        # based on view resolution
        if self.selection_interval == self.intervals.get('day'):
            filtered_data = np.copy(filtered_data) / 1_000_000_000
            y_axis_scale = "GWh"
        else:
            filtered_data = np.copy(filtered_data) / 1_000_000_000_000
            y_axis_scale = "TWh"

        # Create a dataframe
        energy = {
            'Date': energy_time_range,
        }

        consumption_load = {
            'Date': energy_time_range,
        }

        consumption_residual = {
            'Date': energy_time_range,
        }

        consumption_load_2030 = {
            'Date': energy_time_range,
        }

        count_data: int = 0
        count_none: int = 0

        print('%' * 50)
        for data in filtered_data:
            if data is not None:
                count_data += 1
            else:
                count_none += 1
            print(f'Type: {type(data)}', end='\r')
        print()
        print('%' * 50)
        print(f'Count Data: {count_data}')
        print(f'Count None: {count_none}')
        print('%' * 50)
        print(f'Length of index range: {len(energy_time_range)}')
        print(f'Length of data:        {len(filtered_data)}')
        # Check if start and end date match
        print('%' * 50)
        print(f'Start Date: {self.start_date}')
        print(f'End Date:   {self.end_date}')
        print(f'Data i=0: {filtered_data[0].start}')
        print(f'Data i=0: {filtered_data[0].end}')
        print(f'Data last: {filtered_data[-1].start}')
        print(f'Data last: {filtered_data[-1].end}')
        print('%' * 50)

        if self.plot_selection == "Energieerzeugung":
            if 'Photovoltaik' in self.selected_energy_sources:
                energy['Photovoltaik'] = [d.production.pv for d in filtered_data]

            if 'Wind Offshore' in self.selected_energy_sources:
                energy['Wind Offshore'] = [d.production.wind_offshore for d in filtered_data]

            if 'Wind Onshore' in self.selected_energy_sources:
                energy['Wind Onshore'] = [d.production.wind_onshore for d in filtered_data]

            if 'Hydro' in self.selected_energy_sources:
                energy['Hydro'] = [d.production.hydro for d in filtered_data]

            if 'Biomasse' in self.selected_energy_sources:
                energy['Biomasse'] = [d.production.biomass for d in filtered_data]

            if 'Steinkohle' in self.selected_energy_sources:
                energy['Steinkohle'] = [d.production.coal for d in filtered_data]

            if 'Braunkohle' in self.selected_energy_sources:
                energy['Braunkohle'] = [d.production.lignite for d in filtered_data]

            if 'Gas' in self.selected_energy_sources:
                energy['Gas'] = [d.production.gas for d in filtered_data]

            if 'Andere Erneuerbare' in self.selected_energy_sources:
                energy['Andere Erneuerbare'] = [d.production.other_renewables for d in filtered_data]

            if 'Andere Konventionelle' in self.selected_energy_sources:
                energy['Andere Konventionelle'] = [d.production.other_conventionals for d in filtered_data]

            if 'Nuclear' in self.selected_energy_sources:
                energy['Atomkraft'] = [d.production.nuclear for d in filtered_data]
        elif self.plot_selection == "Installierte Leistung":
            if 'Photovoltaik' in self.selected_energy_sources:
                energy['Photovoltaik'] = [d.power.pv for d in filtered_data]

            if 'Wind Offshore' in self.selected_energy_sources:
                energy['Wind Offshore'] = [d.power.wind_offshore for d in filtered_data]

            if 'Wind Onshore' in self.selected_energy_sources:
                energy['Wind Onshore'] = [d.power.wind_onshore for d in filtered_data]

            if 'Hydro' in self.selected_energy_sources:
                energy['Hydro'] = [d.power.hydro for d in filtered_data]

            if 'Biomasse' in self.selected_energy_sources:
                energy['Biomasse'] = [d.power.biomass for d in filtered_data]

            if 'Steinkohle' in self.selected_energy_sources:
                energy['Steinkohle'] = [d.power.coal for d in filtered_data]

            if 'Braunkohle' in self.selected_energy_sources:
                energy['Braunkohle'] = [d.power.lignite for d in filtered_data]

            if 'Gas' in self.selected_energy_sources:
                energy['Gas'] = [d.power.gas for d in filtered_data]

            if 'Andere Erneuerbare' in self.selected_energy_sources:
                energy['Andere Erneuerbare'] = [d.power.other_renewables for d in filtered_data]

            if 'Andere Konventionelle' in self.selected_energy_sources:
                energy['Andere Konventionelle'] = [d.power.other_conventionals for d in filtered_data]

            if 'Nuclear' in self.selected_energy_sources:
                energy['Atomkraft'] = [d.power.nuclear for d in filtered_data]
        elif self.plot_selection == "Verbrauch":
            consumption_load['Last'] = [d.consumption.load for d in filtered_data]
            consumption_residual['Residual Last'] = [d.consumption.residual for d in filtered_data]

        energy_df               = pd.DataFrame(energy)
        consumption_load_df     = pd.DataFrame(consumption_load)
        consumption_residual_df = pd.DataFrame(consumption_residual)


        # --------------------
        consumption_load_2030['Last 2030'] = [d.consumption.load * 1.56 for d in filtered_data]
        consumption_load_2030_df = pd.DataFrame(consumption_load_2030)
        # --------------------

        columns_mode = st.columns([2, 2, 2])

        with columns_mode[0]:
            mode = st.selectbox(
                label='Absolut / Relativ',
                options=["Absolut", "Relativ"],
                index=0,
                help="Absolut zeigt die Werte und relativ setzt diese im Vergleich zu der Gesamterzeugung pro Monat."
            )

        if self.selection_interval == self.intervals.get('total'):
            with columns_mode[1]:
                sum_mode = st.selectbox(
                    label='Summe',
                    options=["Monat", "Jahr"],
                    index=0,
                    help="Die Summe der Energieerzeugung pro Monat oder Jahr."
                )

        with columns_mode[2]:
            show_legend = st.selectbox(
                label='Legende anzeigen',
                options=["True", "False"],
                index=0,
                help="Zeigt die Legende an."
            )

        # Group and sum the data by month
        energy_df['Date']               = pd.to_datetime(energy_df['Date'])
        consumption_load_df['Date']     = pd.to_datetime(consumption_load_df['Date'])
        consumption_residual_df['Date'] = pd.to_datetime(consumption_residual_df['Date'])
        consumption_load_2030_df['Date'] = pd.to_datetime(consumption_load_2030_df['Date'])

        if self.selection_interval == self.intervals.get('total'):
            if sum_mode == "Monat":
                energy_df['Date'] = energy_df['Date'].dt.strftime('%Y-%m')
                consumption_load_df['Date'] = consumption_load_df['Date'].dt.strftime('%Y-%m')
                consumption_residual_df['Date'] = consumption_residual_df['Date'].dt.strftime('%Y-%m')
                consumption_load_2030_df['Date'] = consumption_load_2030_df['Date'].dt.strftime('%Y-%m')
            elif sum_mode == "Jahr":
                energy_df['Date'] = energy_df['Date'].dt.strftime('%Y')
                consumption_load_df['Date'] = consumption_load_df['Date'].dt.strftime('%Y')
                consumption_residual_df['Date'] = consumption_residual_df['Date'].dt.strftime('%Y')
                consumption_load_2030_df['Date'] = consumption_load_2030_df['Date'].dt.strftime('%Y')
        elif self.selection_interval == self.intervals.get('year'):
            energy_df['Date'] = energy_df['Date'].dt.strftime('%Y-%m')
            consumption_load_df['Date'] = consumption_load_df['Date'].dt.strftime('%Y-%m')
            consumption_residual_df['Date'] = consumption_residual_df['Date'].dt.strftime('%Y-%m')
            consumption_load_2030_df['Date'] = consumption_load_2030_df['Date'].dt.strftime('%Y-%m')
        elif self.selection_interval == self.intervals.get('month'):
            energy_df['Date'] = energy_df['Date'].dt.strftime('%Y-%m-%d')
            consumption_load_df['Date'] = consumption_load_df['Date'].dt.strftime('%Y-%m-%d')
            consumption_residual_df['Date'] = consumption_residual_df['Date'].dt.strftime('%Y-%m-%d')
            consumption_load_2030_df['Date'] = consumption_load_2030_df['Date'].dt.strftime('%Y-%m-%d')
        elif self.selection_interval == self.intervals.get('day'):
            energy_df['Date'] = energy_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
            consumption_load_df['Date'] = consumption_load_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
            consumption_residual_df['Date'] = consumption_residual_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
            consumption_load_2030_df['Date'] = consumption_load_2030_df['Date'].dt.strftime('%Y-%m-%d %H:%M')

        energy_df                = energy_df.groupby(['Date']).sum().reset_index()
        consumption_load_df      = consumption_load_df.groupby(['Date']).sum().reset_index()
        consumption_residual_df  = consumption_residual_df.groupby(['Date']).sum().reset_index()
        consumption_load_2030_df = consumption_load_2030_df.groupby(['Date']).sum().reset_index()

        # Melt the dataframe
        energy_df_melted                = pd.melt(energy_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")
        consumption_load_df_melted      = pd.melt(consumption_load_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")
        consumption_residual_df_melted  = pd.melt(consumption_residual_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")
        consumption_load_2030_df_melted = pd.melt(consumption_load_2030_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")

        energy_order = [
            'Andere Konventionelle',
            'Steinkohle',
            'Braunkohle',
            'Gas',
            'Atomkraft',
            'Andere Erneuerbare',
            'Hydro',
            'Biomasse',
            'Wind Offshore',
            'Wind Onshore',
            'Photovoltaik',
        ]

        energy_color = {
            'Photovoltaik': '#f2b134',
            'Wind Onshore': '#17B890',
            'Wind Offshore': '#3454D1',
            'Biomasse': '#7DDF64',
            'Hydro': '#63D2FF',
            'Andere Erneuerbare': '#00a0dc',
            'Atomkraft': '#0CCA4A',
            'Gas': '#FFE0B5',
            'Braunkohle': '#8A6552',
            'Steinkohle': '#CDD4DF',
            'Andere Konventionelle': '#6D5F6D',
        }

        consumption_order = [
            'Last',
            'Residual Last',
            'Last 2030',
        ]

        consumption_color = {
            'Last': '#ff0000',
            'Residual Last': '#17B890',
            'Last 2030': '#3454D1',
        }

        custom_order = '{'

        if self.plot_selection == "Verbrauch":
            for i, consumption_source in enumerate(consumption_order):
                custom_order += f"'{consumption_source}': {i}, "
            custom_color = consumption_color
        else:
            for i, energy_source in enumerate(energy_order):
                custom_order += f"'{energy_source}': {i}, "
            custom_color = energy_color

        custom_order += '}'

        # Create the chart
        if self.selection_interval == self.intervals.get('day'):
            if self.plot_selection == "Verbrauch":
                chart = alt.Chart(consumption_load_df_melted).mark_area()
            elif self.plot_selection == "Installierte Leistung":
                chart = alt.Chart(energy_df_melted).mark_bar()
            else:
                chart = alt.Chart(energy_df_melted).mark_area()
        else:
            if self.plot_selection == "Verbrauch":
                chart = alt.Chart(consumption_load_df_melted).mark_line(interpolate='monotone', point=True)
            else:
                chart = alt.Chart(energy_df_melted).mark_bar()

        chart = chart.transform_calculate(
            order=f'{custom_order}[datum.Energy_Source]'
        )

        y_schema_stacked = alt.Y(
                'sum(Energy Value):Q',
                stack=("normalize" if mode == "Relativ" else 'zero'),
                axis=alt.Axis(title=f'Energieerzeugung [{y_axis_scale}]'),
        )

        y_schema_area = alt.Y(
                'Energy Value:Q',
                axis=alt.Axis(title=f'Verbrauch [{y_axis_scale}]'),
        )

        title = ''

        if self.plot_selection == "Verbrauch":
            title = 'Verbrauch'
        elif self.plot_selection == "Energieerzeugung":
            title = 'Energieerzeugung'
        elif self.plot_selection == "Installierte Leistung":
            title = 'Installierte Leistung'

        chart = chart.encode(
            x=alt.X(
                'Date:O',
                axis=alt.Axis(title='Datum [M]')
            ),
            y=(y_schema_area if self.plot_selection == "Verbrauch" else y_schema_stacked),
            color=alt.Color(
                'Energy_Source:N',
                scale=alt.Scale(domain=list(custom_color.keys()), range=list(custom_color.values())),
                legend=(alt.Legend(title='Energy Source') if show_legend == "True" else None),
            ),
            order='order:O',
            tooltip=['Energy_Source', 'Date', 'Energy Value']
        ).properties(
            height=500,
            title=title
        ).configure_legend(
            labelFontSize=12,
            titleFontSize=14
        )

        chart_load = alt.Chart(consumption_load_df_melted).mark_line(interpolate='monotone', point=True)
        chart_residual = alt.Chart(consumption_residual_df_melted).mark_line(interpolate='monotone', point=True)
        chart_load_2030 = alt.Chart(consumption_load_2030_df_melted).mark_line(interpolate='monotone', point=True)

        chart_load = chart_load.encode(
            x=alt.X(
                'Date:O',
                axis=alt.Axis(title='Datum [M]')
            ),
            y=alt.Y(
                'Energy Value:Q',
                axis=alt.Axis(title=f'Verbrauch [{y_axis_scale}]'),
            ),
            color=alt.Color(
                'Energy_Source:N',
                scale=alt.Scale(domain=list(custom_color.keys()), range=list(custom_color.values())),
                legend=(alt.Legend(title='Energy Source') if show_legend == "True" else None),
            )
        ).properties(
            height=500,
            title='Verbrauch'
        )

        chart_residual = chart_residual.encode(
            x=alt.X(
                'Date:O',
                axis=alt.Axis(title='Datum [M]')
            ),
            y=alt.Y(
                'Energy Value:Q',
                axis=alt.Axis(title=f'Verbrauch [{y_axis_scale}]'),
            ),
            color=alt.value('#17B890')
        ).properties(
            height=500,
            title='Residual Last'
        )

        chart_load_2030 = chart_load_2030.encode(
            x=alt.X(
                'Date:O',
                axis=alt.Axis(title='Datum [M]')
            ),
            y=alt.Y(
                'Energy Value:Q',
                axis=alt.Axis(title=f'Verbrauch [{y_axis_scale}]'),
            ),
            color=alt.value('#3454D1')
        ).properties(
            height=500,
            title='Last 2030'
        )

        # Layer the charts
        load_chart = alt.layer(chart_load, chart_residual, chart_load_2030).resolve_scale(y='shared')
        load_chart = load_chart.configure_legend(
            labelFontSize=12,
            titleFontSize=14
        )

        # Render production chart
        if self.plot_selection == "Energieerzeugung":
            st.altair_chart(chart, use_container_width=True)
        elif self.plot_selection == "Installierte Leistung":
            st.altair_chart(chart, use_container_width=True)
        elif self.plot_selection == "Verbrauch":
            st.altair_chart(load_chart, use_container_width=True)

    def render_production_power_view(self):
        ...

    def render_consumption_view(self):
        ...

    def month_to_index(self, month: str) -> int:
        return {
            'Januar': 1,
            'Februar': 2,
            'März': 3,
            'April': 4,
            'Mai': 5,
            'Juni': 6,
            'Juli': 7,
            'August': 8,
            'September': 9,
            'Oktober': 10,
            'November': 11,
            'Dezember': 12
        }.get(month, 0)


if __name__ == "__main__":
    view = IST_View()
    view.render()
