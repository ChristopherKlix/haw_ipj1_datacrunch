import math
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from time import sleep, time
import altair as alt
from vega_datasets import data as vega_data
from streamlit_option_menu import option_menu

from init_page import PageManager

# Import data.py
import data as data_loader
import gpt as GPT

# Define colors
clr_wind_offshore = '#3454D1'
clr_wind_onshore = '#17B890'
clr_photovoltaic = '#ffc300'
clr_hydro = '#63D2FF'
clr_biomass = '#7DDF64'
clr_charcoal = '#8A6552'
clr_coal = '#CDD4DF'
clr_gas = '#FFE0B5'
clr_other_conventional = '#6D5F6D'
clr_nuclear = '#0CCA4A'
clr_fossil_fuels = '#6D5F6D'

global prompt
global msg

min_date = dt.date(2020, 1, 1)
max_date = dt.date(2022, 12, 31)

selected_date = dt.date(2020, 1, 1)

production_data, consumption_data = None, None

# Get the data
# @st.cache_resource
# def get_data():
#     with st.spinner('Loading data...'):
#         data_0, data_1 = data_loader.main()

#         if data_0 is None:
#             toast = st.error('Data could not be loaded!', icon="❌")
#             return None, None, toast
#         else:
#         #     toast = st.success('Data loaded successfully!', icon="✅")
#             return data_0, data_1, None

# production_data, consumption_data, toast = get_data()

# if toast is not None:
#     toast.empty()

# Create a enum for the different power sources
class PowerSource:
    def __init__(self, name, id, color, display_name=None):
        self.name = name
        self.id = id
        self.color = color
        self.display_name = display_name

    def get_id(self):
        return self.id

    def get_display_name(self):
        if self.display_name is None:
            return self.name
        else:
            return self.display_name

    def __str__(self):
        return self.name


# Create a list of power sources
power_sources = {
    'w-off': PowerSource('Wind Offshore','w-off', clr_wind_offshore, '🌊 Wind Offshore'),
    'w-on': PowerSource('Wind Onshore','w-on', clr_wind_onshore, '🌴 Wind Onshore'),
    'pv': PowerSource('Photovoltaic','pv', clr_photovoltaic, '☀️ Photovoltaic'),
    'hy': PowerSource('Hydro','hy', clr_hydro, '💧 Hydro'),
    'bm': PowerSource('Biomass','bm', clr_biomass, '🌽 Biomass'),
    'coal': PowerSource('Coal','coal', clr_coal, '⛽ Coal'),
    'charcoal': PowerSource('Charcoal','charcoal', clr_charcoal, '🪨 Charcoal'),
    'gas': PowerSource('Gas','gas', clr_gas, '⛽ Gas'),
    'other': PowerSource('Other Conventional','other', clr_other_conventional, '⛽🪨 Other Conventional'),
    'nuclear': PowerSource('Nuclear','nuclear', clr_nuclear, '☢️ Nuclear')
}

def main():
    print('Launching app...')

    page = PageManager()

    # global production_data
    # global consumption_data
    # production_data, consumption_data = page.get_data()

    st.title('Energy Dashboard')

    st.warning('⚠️ This is a prototype!')

    st.error('A breaking change has been made to the data. Page could not load.')

    # render_view_dashboard()


def ask_bot_btn_clicked():
    st.session_state.selected = 'Ask GPT'


class ChatMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content


@st.cache_resource
def get_init_prompts():
    prompts: list = [
        ChatMessage("assistant", "Moin 👋"),
        ChatMessage("assistant", "Was möchtest du über erneuerbare Energien wissen?")
    ]

    return prompts


def calculate_net_balance(year: int, metric_prefix: str = 'tera', round_to: int = 2):
    total_renewables = 0
    total_fossil_fuels = 0
    total_production = 0
    total_consumption = 0

    for month in range(0, 12):
        for day in range(0, 31):
            for hour in range(0, 24):
                for quarter in range(0, 4):
                    total_renewables += production_data[year-2020, month, day, hour, quarter].total_renewables()
                    total_fossil_fuels += production_data[year-2020, month, day, hour, quarter].total_fossil_fuels()
                    total_production += production_data[year-2020, month, day, hour, quarter].total_production()
                    total_consumption += consumption_data[year-2020, month, day, hour, quarter].total_load

    prefixes = {
        'tera': 1_000_000_000_000,
        'giga': 1_000_000_000,
        'mega': 1_000_000,
        'kilo': 1_000
    }

    if metric_prefix == 'tera':
        total_renewables /= prefixes.get('tera')
        total_fossil_fuels /= prefixes.get('tera')
        total_production /= prefixes.get('tera')
        total_consumption /= prefixes.get('tera')
    elif metric_prefix == 'giga':
        total_renewables /= prefixes.get('giga')
        total_fossil_fuels /= prefixes.get('giga')
        total_production /= prefixes.get('giga')
        total_consumption /= prefixes.get('giga')
    elif metric_prefix == 'mega':
        total_renewables /= prefixes.get('mega')
        total_fossil_fuels /= prefixes.get('mega')
        total_production /= prefixes.get('mega')
        total_consumption /= prefixes.get('mega')
    elif metric_prefix == 'kilo':
        total_renewables /= prefixes.get('kilo')
        total_fossil_fuels /= prefixes.get('kilo')
        total_production /= prefixes.get('kilo')
        total_consumption /= prefixes.get('kilo')

    # Round to 2 decimals
    if round_to > 0:
        total_renewables = round(total_renewables, round_to)
        total_fossil_fuels = round(total_fossil_fuels, round_to)
        total_production = round(total_production, round_to)
        total_consumption = round(total_consumption, round_to)
    elif round_to == 0:
        total_renewables = int(total_renewables)
        total_fossil_fuels = int(total_fossil_fuels)
        total_production = int(total_production)
        total_consumption = int(total_consumption)

    return {
        'total-renewables': total_renewables,
        'total-fossil-fuels': total_fossil_fuels,
        'total-production': total_production,
        'total-load': total_consumption
    }


def render_view_ask_gpt():
    # prompts: list = []

    with st.chat_message("assistant"):
        st.write("Moin 👋")
        st.write("Was möchtest du über erneuerbare Energien wissen?")

    prompt = st.chat_input("Stell eine Frage...", key='chat_input', on_submit=processPrompt)

    if prompt:
        st.empty()
        chat_message = ChatMessage("user", prompt)

        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner('Hmmm...'):
            msg = GPT.ask(prompt)

            with st.chat_message("assistant"):
                st.write(msg)
        # prompts.append(chat_message)

    # for prompt in prompts:
    #     with st.chat_message(prompt.role):
    #         st.write(prompt.content)

    # with st.spinner('Hmmm...'):
    #     question = prompts[-1].content

    #     msg = GPT.ask(question)

    #     if msg is not None:  # Add a check for None
    #         bot_response = ChatMessage("assistant", msg)
    #         prompts.append(bot_response)


def render_view_settings():
    st.header('Settings')
    st.write('There are no settings yet.')




def render_view_dashboard():
    st.markdown("""
                The data shown is based on quarter hour intervals.
                Since the data is in GWh (Gigawatt hours), the values are divided by 1 billion and rounded to 2 decimals.
                Therefore, manual calculations may not exactly match the values shown here.
                """)

    global selected_date

    columns = st.columns(3)

    interval_selection = None

    with columns[0]:
        interval_selection = st.selectbox('Interval',
                                          options=["Gesamt", "Jahr", "Month", "Tag"])

    with columns[1]:
        selected_date = st.date_input(
            label="Select a date to plot",
            value=selected_date,
            min_value=min_date,
            max_value=max_date,
            format="DD.MM.YYYY",
            key='date_input',
            help="The data is available from 01.01.2020 to 31.12.2022."
        )

    with columns[2]:
        st.selectbox('Data source',
                    options=["SMARD.de", "Frauenhofer", "Agora Energiewende"])

    plot_selection = st.selectbox('Plots',
                   options=["Produktion", "Installierte Leistung", "Verbrauch"])

    if plot_selection != "Verbrauch":
        st.multiselect('Sources',
                        options=["Wind Offshore", "Wind Onshore", "Photovoltaic", "Hydro", "Biomass", "Coal", "Charcoal", "Gas", "Other Conventional", "Nuclear"])

    render_tabs()

    st.markdown("""
                Source: [SMARD Stromarktdaten der Bundesnetzagentur](https://www.smard.de/)
                """)


def processPrompt():
    global prompt
    global msg


def render_tabs():
    tab_init, tab_weather, tab_all, tab0, tab1, tab2, tab3, tab4, tab_fossil_fuels, tab_nuclear = st.tabs(["Overview","Weather", "⚡ All Sources", "🌊 Wind Offshore", "🌴 Wind Onshore", "☀️ Photovoltaic", "💧 Hydro", "🌽 Biomass", "⛽🪨 Fossil Fuels", "☢️ Nuclear"])

    with tab_init:
        render_view_overview()

    with tab_all:
        render_view_all()
    with tab_weather:
        source = vega_data.seattle_weather()

        scale = alt.Scale(
            domain=["sun", "fog", "drizzle", "rain", "snow"],
            range=["#e7ba52", "#a7a7a7", "#aec7e8", "#1f77b4", "#9467bd"],
        )
        color = alt.Color("weather:N", scale=scale)

        brush = alt.selection_interval(encodings=["x"])
        click = alt.selection_multi(encodings=["color"])

        points = (
            alt.Chart()
            .mark_point()
            .encode(
                alt.X("monthdate(date):T", title="Date"),
                alt.Y(
                    "temp_max:Q",
                    title="Maximum Daily Temperature (C)",
                    scale=alt.Scale(domain=[-5, 40]),
                ),
                color=alt.condition(brush, color, alt.value("lightgray")),
                size=alt.Size("precipitation:Q", scale=alt.Scale(range=[5, 200])),
            )
            .properties(width=550, height=300)
            .add_selection(brush)
            .transform_filter(click)
        )

        bars = (
            alt.Chart()
            .mark_bar()
            .encode(
                x="count()",
                y="weather:N",
                color=alt.condition(click, color, alt.value("lightgray")),
            )
            .transform_filter(brush)
            .properties(
                width=550,
            )
            .add_selection(click)
        )

        chart = alt.vconcat(points, bars, data=source, title="Seattle Weather: 2012-2015")

        st.altair_chart(chart, theme="streamlit", use_container_width=True)



        iowa_source = vega_data.iowa_electricity()

        chart_iowa = alt.Chart(iowa_source).mark_area().encode(
            alt.X("year:T", title="Year"),
            alt.Y(
                "net_generation:Q",
                title="Net Generation",
                # scale=alt.Scale(domain=[-5, 40]),
            ),
            # x="year:T",
            # y="net_generation:Q",
            color="source:N"
        )

        st.altair_chart(chart_iowa, theme="streamlit", use_container_width=True)
    with tab0:
        render_view_individual(power_sources.get('w-off'))
    with tab1:
        render_view_individual(power_sources.get('w-on'))
    with tab2:
        render_view_individual(power_sources.get('pv'))
    with tab3:
        render_view_individual(power_sources.get('hy'))
    with tab4:
        render_view_individual(power_sources.get('bm'))
    with tab_fossil_fuels:
        render_view_fossil_fuels()
    with tab_nuclear:
        render_view_individual(power_sources.get('nuclear'))


def render_view_overview():
    st.subheader('Overview')
    st.write('This is a dashboard to show energy production and consumption data.')

    st.markdown('### Bilanz')
    # st.markdown('Total change in energy production and consumption in 2022 compared to the previous year.')
    st.markdown('Gesamtänderung der Energieproduktion und des Energieverbrauchs im Jahr 2022 im Vergleich zum Vorjahr.')

    net_balance = calculate_net_balance(year=2022, round_to=0)

    col0, col1, col2, col3 = st.columns(4)
    col0.metric("☀️🌊 Erneuerbare Energien", f'{net_balance["total-renewables"]} TWh', "-10 TWh")
    col1.metric("⛽🪨 Fossile Energien", f'{net_balance["total-fossil-fuels"]} TWh', "1 TWh")
    col2.metric("⚡ Gesamt Produktion", f'{net_balance["total-production"]} TWh', "-40 TWh")
    col3.metric("🔌 Gesamt Last", f'{net_balance["total-load"]} TWh', "-22 TWh")

    st.markdown('### Relative Bilanz')
    # st.markdown('Relative change in energy production and consumption from 2021 to 2022 compared to the previous years\' change.')
    st.markdown('Relative Änderung der Energieproduktion und des Energieverbrauchs von 2021 bis 2022 im Vergleich zur Änderung des Vorjahres.')

    col0, col1, col2, col3 = st.columns(4)
    col0.metric("☀️🌊 Renewables", "-2.6%", "-5.7%")
    col1.metric("⛽🪨 Fossil Fuels", "0.46%", "13.15%")
    col2.metric("⚡ Total Production", "-5.97%", "0.6%")
    col3.metric("🔌 Total Load", "-4.36%", "3.91%")


    st.markdown('### Maximale PV-Effizienz')

    max_percentage = 0.0
    max_timestamp = (None, None)

    percentage_distribution = np.zeros(100, dtype=int)
    percentage_distribution_daytime = np.zeros(100, dtype=int)

    limit_to_daytime: bool = st.toggle('Auf Tageszeit limitieren', value=True, key='limit_to_daytime')
    global selector_start_time
    global selector_end_time
    selector_start_time = dt.time(6, 0, 0)
    selector_end_time = dt.time(18, 0, 0)
    percentage_total_count = 0

    # Time selector for the chart
    if limit_to_daytime:
        col_0, col_1 = st.columns(2)

        with col_0:
            selector_start_time = st.time_input(
                label="Select a start time",
                value=dt.time(6, 0, 0),
                key='time_input_start',
                help="The data is available from 01.01.2020 to 31.12.2022."
            )
        with col_1:
            selector_end_time = st.time_input(
                label="Select an end time",
                value=dt.time(18, 0, 0),
                key='time_input_end',
                help="The data is available from 01.01.2020 to 31.12.2022."
            )

    for year in range(0, 3):
        for month in range(0, 12):
            for day in range(0, 31):
                for hour in range(0, 24):
                    for quarter in range(0, 4):
                        if production_data[year, month, day, hour, quarter].coal == 0:
                            continue

                        pv_production = production_data[year, month, day, hour, quarter].pv
                        interpolated_pv_production = pv_production * 4
                        installed_pv = production_data[year, month, 0, 0, 0].installed_pv
                        percentage = interpolated_pv_production / installed_pv * 100

                        start_time = production_data[year, month, day, hour, quarter].start
                        end_time = production_data[year, month, day, hour, quarter].end

                        max_timestamp = (start_time, end_time) if percentage >= max_percentage else max_timestamp
                        max_percentage = max(max_percentage, percentage)

                        percentage_distribution[int(percentage)] += 1

                        current_time_iteration_start = dt.time(hour, quarter * 15, 0)

                        if current_time_iteration_start >= selector_start_time and current_time_iteration_start <= selector_end_time:
                            percentage_distribution_daytime[int(percentage)] += 1

    percentage_distribution_df = pd.DataFrame(
        {
            'Percentage': np.arange(0, 100),
            'Count': percentage_distribution
        }
    )

    percentage_distribution_daytime_df = pd.DataFrame(
        {
            'Percentage': np.arange(0, 100),
            'Count': percentage_distribution_daytime
        }
    )

    data_to_plot = percentage_distribution_daytime_df if limit_to_daytime else percentage_distribution_df

    percentage_chart = alt.Chart(data_to_plot).mark_bar().encode(
        alt.X(
            "Percentage:Q",
            title="Prozentteil",
            scale=alt.Scale(domain=[0, 100]),
        ),
        alt.Y(
            "Count:Q",
            title="Anzahl der Viertelstunden",
            scale=alt.Scale(domain=[0, 3000]),
        )
    ).interactive().properties(width=550, height=500)

    # st.markdown(f'The maximum PV effeciency is {max_percentage:.2f}% and was reached between {max_timestamp[0]} and {max_timestamp[1]}.')

    st.markdown('<div style=height: 4rem;></div>', unsafe_allow_html=True)
    st.markdown(f'##### Maximal erreichte PV-Effizienz')
    st.markdown(f'<div style="font-size: 2.25rem; padding-bottom: 0.25rem">{max_percentage:.2f}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size: 0.8rem; padding-bottom: 0.25rem; opacity: 0.8;">Between {max_timestamp[0]} and {max_timestamp[1]}</div>', unsafe_allow_html=True)

    if limit_to_daytime:
        st.markdown(f'#### Zeitraum ({selector_start_time.strftime("%H:%M")} - {selector_end_time.strftime("%H:%M")})')
    else:
        st.markdown(f'#### Alle Einträge')

    st.markdown(f'Der übliche Zeitrahmen für eine PV-Produktion von mehr als 5% liegt im Durchschnitt zwischen 10:00 und 15:00 Uhr.')

    # st.button('Set timeframe to average sunhours.', key='set_timeframe_to_average_sunhours')

    percentage_total_count = np.sum(percentage_distribution_daytime) if limit_to_daytime else np.sum(percentage_distribution)

    st.markdown(f'Gesamtanzahl an Einträgen: {percentage_total_count}')

    st.altair_chart(percentage_chart, theme="streamlit", use_container_width=True)




    st.markdown('## Abdeckung durch Erneuerbare Energien')
    # st.write("""
    #          Presented below is a comprehensive chart illustrating the power production distribution from renewable sources. This histogram-style chart has been thoughtfully designed to facilitate a clear understanding of the frequency and volume of power generated by sustainable sources.
    #          The data is meticulously sourced from quarter-hour intervals within the period spanning from 2020 to 2022. This analysis provides valuable insights into the sustained growth and impact of renewable energy sources on our power production landscape.

    #          The percentiles are floating-point values, which means that the values are rounded to two decimal places. This is done to ensure that the data is easily readable and understandable.
    #          """
    #          )

    st.markdown("""
                Im Folgenden wird eine umfassende Tabelle präsentiert, die die Verteilung der Stromerzeugung aus erneuerbaren Quellen veranschaulicht. Diese Histogramm-artige Tabelle wurde sorgfältig entworfen, um ein klares Verständnis für die Häufigkeit und das Volumen der von nachhaltigen Quellen erzeugten Energie zu erleichtern. Die Daten stammen akribisch aus Viertelstundenintervallen im Zeitraum von 2020 bis 2022. Diese Analyse liefert wertvolle Einblicke in das nachhaltige Wachstum und den Einfluss erneuerbarer Energiequellen auf unsere Energieerzeugungslandschaft.

                Die Prozentwerte sind Gleitkommazahlen, was bedeutet, dass die Werte auf zwei Dezimalstellen gerundet sind. Dies wird getan, um sicherzustellen, dass die Daten leicht lesbar und verständlich sind.
                """)

    time_interval_options = ['Gesamt (2020-2022)', 2020, 2021, 2022]
    selected_interval = st.selectbox('Ausgewählter Zeitraum', options=time_interval_options, key='selectbox_year')

    data_power_from_renewables_hist = np.zeros(150, dtype=int)

    for year in range(0, 3):
        for month in range(0, 12):
            for day in range(0, 31):
                for hour in range(0, 24):
                    for quarter in range(0, 4):
                        if st.session_state.selectbox_year == time_interval_options[0]:
                            year = year
                        else:
                            year = st.session_state.selectbox_year - 2020

                        if production_data[year, month, day, hour, quarter].coal == 0:
                            continue

                        renewables_production = production_data[year, month, day, hour, quarter].total_renewables()
                        total_load = consumption_data[year, month, day, hour, quarter].total_load

                        percentage = renewables_production / total_load * 100

                        # Clamp the percentage to 100 since it is possible to have surplus energy
                        # percentage = min(percentage, 100)

                        data_power_from_renewables_hist[int(percentage)] += 1

    df_power_from_renewables_hist = pd.DataFrame(
        {
            'Percentage': np.arange(0, 150),
            'Count': data_power_from_renewables_hist
        }
    )

    selection_interval = alt.selection_interval(encodings=['x'])

    chart_power_from_renewables_hist = alt.Chart(df_power_from_renewables_hist).mark_bar().encode(
        alt.X(
            "Percentage:Q",
            title="Prozentteil",
            scale=alt.Scale(domain=[0, 150]),
        ),
        alt.Y(
            "Count:Q",
            title="Anzahl an Viertelstunden",
            scale=alt.Scale(domain=[0, 3000]),
        ),
        color=alt.condition(selection_interval, alt.value('#93C7FA'), alt.value('#2C3140'))
    ).properties(width=550, height=500).add_params(selection_interval)

    hist_count = alt.Chart(df_power_from_renewables_hist).transform_filter(
        selection_interval
    ).transform_aggregate(
        total_count='sum(Count)',
        # relative_percentage='sum(Count) / 105108:Q',
        groupby=[]
    ).mark_bar().encode(
        x=alt.X(
            'total_count:Q',
            # 'relative_percentage:Q',
            title='Gesamtanzahl der ausgewählten Viertelstunden',
            scale=alt.Scale(domain=[0, 110000])
            # axis=alt.Axis(format='%'),
            # scale=alt.Scale(domain=[0, 1])
            ),
        color=alt.value('#93C7FA'),
        tooltip=alt.Tooltip('total_count:Q', title='Accumulated Count')
        # tooltip=alt.Tooltip('relative_percentage:Q', title='Relative Percentage')
    ).properties(width=550)

    chart_power_from_renewables_hist_line = alt.Chart(df_power_from_renewables_hist).mark_rule().encode(
        x=alt.X(
            "a:Q",
            scale=alt.Scale(domain=[0, 150]),
        ),
        size=alt.value(2),
        color=alt.ColorValue('#FF4B4B')
    ).transform_calculate(
        a="100"
    )

    hist_count_line = alt.Chart(df_power_from_renewables_hist).mark_rule().encode(
        x=alt.X(
            "a:Q",
            scale=alt.Scale(domain=[0, 110000]),
            # scale=alt.Scale(domain=[0, 1]),
        ),
        size=alt.value(2),
        color=alt.ColorValue('#FF4B4B')
    ).transform_calculate(
        a="105108"
        # a="1"
    )

    first_chart = alt.vconcat(alt.layer(
        chart_power_from_renewables_hist,
        chart_power_from_renewables_hist_line
    ), alt.layer(hist_count, hist_count_line)).resolve_scale(color='independent')

    least_coverage_percentile: int = 0
    greatest_coverage_percentile: int = 0

    for index, data in enumerate(data_power_from_renewables_hist):
        if data > 0:
            least_coverage_percentile = index
            break

    for index, data in enumerate(data_power_from_renewables_hist[::-1]):
        if data > 0:
            greatest_coverage_percentile = data_power_from_renewables_hist.size - index
            break

    coverage_col0, coverage_col1 = st.columns(2)

    st.markdown('<div style=height: 40rem;></div>', unsafe_allow_html=True)

    with coverage_col0:
        st.markdown(f'<div style="font-size: 3.25rem; font-weight: 700; padding-bottom: 0.25rem; text-align: center;">{least_coverage_percentile:.0f}%</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 0.8rem; padding-bottom: 0.25rem; text-align: center; opacity: 0.8;">Geringste Abdeckung</div>', unsafe_allow_html=True)

    with coverage_col1:
        st.markdown(f'<div style="font-size: 3.25rem; font-weight: 700; padding-bottom: 0.25rem; text-align: center;">{greatest_coverage_percentile:.0f}%</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 0.8rem; padding-bottom: 0.25rem; text-align: center; opacity: 0.8;">Höchste Abdeckung</div>', unsafe_allow_html=True)

    st.markdown('<div style=height: 4rem;></div>', unsafe_allow_html=True)

    st.markdown("""
                Das Diagramm zeigt die Gesamtzahl an Viertelstunden im ausgewählten Jahr,
                in denen erneuerbare Energien einen bestimmten Prozentsatz der Gesamtlast abdecken.
                Bei Überschussproduktion steigt der Prozentsatz über 100%.
                Die überschüssige Energie wird in solchen Fällen entweder in Nachbarländer exportiert oder in Pumpspeicher gespeichert.
                """)

    st.markdown(f'Dargestellte Daten aus dem Jahr: {selected_interval}')

    st.altair_chart(first_chart, theme="streamlit", use_container_width=True)

    # Lower res chart
    year = 0
    if st.session_state.selectbox_year == time_interval_options[0]:
        year = 2030
    else:
        year = st.session_state.selectbox_year - 2020
    hist_data = compute_renewable_distribution(year, resolution=10, clamp_overshoot=True, upper_limit=100)
    lowres_chart = alt.Chart(hist_data).mark_bar(size=30).encode(
        alt.X(
            "Percentage:Q",
            title="Prozentteil",
            scale=alt.Scale(domain=[0, 110]),
            axis=alt.Axis(tickCount=11, values=list(range(0, 110, 10)))
        ),
        alt.Y(
            "Count:Q",
            title="Anzahl an Viertelstunden",
            scale=alt.Scale(domain=[0, 22000]),
        ),
        color=alt.condition(
            alt.datum.Percentage == 30,  # If the percentile is 30 this test returns True,
            alt.value('#FF4B4B'),     # which sets the bar orange.
            alt.value('#93C7FA')   # And if it's not true it sets the bar steelblue.
        )
    ).properties(height=500)

    st.markdown("""
                Das Diagramm zeigt ähnlich zu dem vorherigen die Gesamtzahl an Viertelstunden im ausgewählten Jahr,
                jedoch auf 10%-Intervalle summiert.
                Sprich, 15% Abdeckung werden als 10% gezählt, 25% als 20% usw.
                Die Anzahl der 100%-Anteile entspricht sämtlichen Produktionsintervallen mit Überschussproduktion,
                sprich, Produktion über 100% der Gesamtlast.
                """)

    st.markdown(f'Dargestellte Daten aus dem Jahr: {selected_interval}')
    st.markdown(f'Intervallgröße: 10%')
    st.markdown(f'Gesamtzahl der Viertelstunden: {np.sum(hist_data["Count"])}')

    st.altair_chart(lowres_chart, theme="streamlit", use_container_width=True)

    with st.expander('Datentabelle anzeigen'):
        st.dataframe(hist_data, height=430, use_container_width=True, hide_index=True, column_config={
            'Percentage': 'Prozentteil',
            'Count': 'Anzahl an Viertelstunden'
        })

        download_filename = st.text_input(
            'CSV-Dateiname',
            value='share_of_renewables',
            key='csv_filename',
            help='Der Dateiname der CSV-Datei, die heruntergeladen werden soll.',
            placeholder='filename.csv'
            )

        st.download_button(
            label='CSV herunterladen',
            data=hist_data.to_csv(),
            file_name=f'{download_filename}.csv'
            )


    # data_power_from_renewables_hist
    data_sumchart_x = np.arange(0, 101)
    data_sumchart_y = np.zeros(101, dtype=int)

    # for index, data in enumerate(data_power_from_renewables_hist):
    for i in range(0, data_sumchart_x.size):
        data_sumchart_x[i] = i
        data_sumchart_y[i] = np.sum(data_power_from_renewables_hist[i:]) / np.sum(data_power_from_renewables_hist) * 100
        # data_sumchart_y[i] = i

    df_sumchart = pd.DataFrame(
        {
            'Percentage': data_sumchart_x,
            'Count': data_sumchart_y
        }
    )

    sumchart = alt.Chart(df_sumchart).mark_area().encode(
        alt.X(
            "Percentage:Q",
            title="% mind. abgedeckt durch EE",
            scale=alt.Scale(domain=[0, 100]),
        ),
        alt.Y(
            "Count:Q",
            title="% der Zeit",
            scale=alt.Scale(domain=[0, 100]),
        )
    ).properties(width=550, height=300)

    st.markdown('### Renz-Diagramm')
    st.markdown("""
                Diese Diagramm zeigt die Anteile der Zeit, in der erneuerbare Energien einen bestimmten Prozentsatz der Gesamtlast abdecken.
                """)
    st.markdown('#### Wie lese ich das Diagramm?')
    st.markdown("""
                Dieser Wert ist eine Mindestabdeckung, sprich mindestens 10% sind 100% der Zeit abgedeckt.
                """)

    number_input_col = st.columns(3)

    number_clr = 'none'
    if data_sumchart_y[st.session_state.min_coverage] <= 100:
        number_clr = '#7DDF64'
    if data_sumchart_y[st.session_state.min_coverage] <= 60:
        number_clr = '#ffc300'
    if data_sumchart_y[st.session_state.min_coverage] <= 40:
        number_clr = '#FF4B4B'

    with number_input_col[0]:
            st.markdown(f'<div style="font-size: 3.25rem; font-weight: 700; color: {number_clr}; padding-bottom: 0.25rem; text-align: center;">{data_sumchart_y[st.session_state.min_coverage]:.0f}%</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.8rem; padding-bottom: 0.25rem; text-align: center; opacity: 0.8;">des Jahres durch EE abgedeckt</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="padding-bottom: 2rem;"></div>', unsafe_allow_html=True)

            st.number_input(
                'Mindestabdeckung',
                min_value=0,
                max_value=100,
                value=st.session_state.min_coverage,
                step=10,
                key='min_coverage'
                )

    with number_input_col[1]:
            st.markdown(f'<div style="font-size: 3.25rem; font-weight: 700; padding-bottom: 0.25rem; text-align: center;">10%</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.8rem; padding-bottom: 0.25rem; text-align: center; opacity: 0.8;">Immer abgedeckt</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="padding-bottom: 2rem;"></div>', unsafe_allow_html=True)

    with number_input_col[2]:
            st.markdown(f'<div style="font-size: 3.25rem; font-weight: 700; padding-bottom: 0.25rem; text-align: center;">108%</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.8rem; padding-bottom: 0.25rem; text-align: center; opacity: 0.8;">Maximale Abdeckung</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="padding-bottom: 2rem;"></div>', unsafe_allow_html=True)

            # st.number_input(
            #     'Mindestabdeckung',
            #     min_value=0,
            #     max_value=100,
            #     value=80,
            #     step=10,
            #     key='min_coverage'
            #     )

    sumchart_vertical_line = alt.Chart(df_sumchart).mark_rule().encode(
        x=alt.X(
            "a:Q",
        ),
        size=alt.value(2),
        color=alt.ColorValue('#FF4B4B')
    ).transform_calculate(
        a=f'{st.session_state.min_coverage}'
    )

    st.markdown(f'<div style="padding-bottom: 2rem;"></div>', unsafe_allow_html=True)

    st.altair_chart(sumchart + sumchart_vertical_line, theme="streamlit", use_container_width=True)

    with st.expander('Datentabelle anzeigen'):
        st.dataframe(df_sumchart, height=430, use_container_width=True, hide_index=True, column_config={
            'Percentage': 'Prozentteil',
            'Count': 'Anzahl an Viertelstunden'
        })

        download_filename = st.text_input(
            'CSV-Dateiname',
            value='share_of_renewables',
            key='csv_filename_sumchart',
            help='Der Dateiname der CSV-Datei, die heruntergeladen werden soll.',
            placeholder='filename.csv'
            )

        st.download_button(
            label='CSV herunterladen',
            data=df_sumchart.to_csv(),
            file_name=f'{download_filename}.csv',
            key='download_button_sumchart'
            )

    st.markdown("""
                <img src=\"https://climateactiontracker.org/media/original_images/2021/5/CAT-2021-05_Deutschland_EmissionenKlimaziel.png\" alt="Power grid schematic" width="100%" style="border-radius: 6px; margin-bottom: 1rem"/>
                """, unsafe_allow_html=True)


    # ------------------------------
    # Net balance chart 2022
    # ------------------------------
    st.markdown('## Netzbilanz')

    net_balance_individual = np.zeros((1, 12, 31, 24, 4), dtype=float)
    net_balance_accumulated = np.zeros((1, 12, 31, 24, 4), dtype=float)

    net_balance_cols = st.columns(2)

    # Parameters
    net_balance_year = 2022
    with net_balance_cols[0]:
        net_balance_year = st.selectbox('Jahr', options=[2020, 2021, 2022], index=2, key='net-balance-year')

    time_range_resolution = 20
    with st.expander('⚙️ Zeitbereich Auflösung'):
        time_range_resolution = st.select_slider('Data Point Auflösung (jeder n-th data point wird angezeigt)',
                                                options=[1, 10, 20, 50, 100, 200, 500, 1_000, 10_000],
                                                value=20,
                                                key='time_range_resolution',
                                                help='The resolution of the time range. The higher the value, the less data points are displayed. This can help with performance issues.')
        st.caption(f'The time range resolution determines how many data points are displayed. The higher the value, the less data points are displayed. This can help with performance issues but also reduces the accuracy of the data.')

    if time_range_resolution >= 100:
        st.warning('The time range resolution is set to a high value. This greatly affects to accuracy of the data.')

    for y, m, d, h, q in get_iterator():
        # Skip the entries with no data (invalid dates)
        # This takes care of leap years and
        # the lack of a 31st of a month
        if production_data[net_balance_year-2020, m, d, h, q].start == None:
            net_balance_individual[0, m, d, h, q] = 3.1415
            continue

        # Calculate the net balance
        balance = production_data[net_balance_year-2020, m, d, h, q].total_production() - consumption_data[net_balance_year-2020, m, d, h, q].total_load

        # Convert from Wh to GWh
        balance /= 1_000_000_000

        # Store the balance
        net_balance_individual[0, m, d, h, q] = balance

    # Flatten the arrays to 1D
    net_balance_individual = net_balance_individual.flatten()
    net_balance_accumulated = net_balance_accumulated.flatten()

    # Create the x-axis time range
    time_range = pd.date_range(start='2022-01-01 00:00', end='2022-12-31 23:59', freq='15min', tz='Europe/Berlin')

    # Store the data in a new array
    # with only the valid entries
    _net_balance_individual = np.zeros(time_range.size)

    # Filter out the invalid entries
    i = 0
    for elem in net_balance_individual:
        if elem != 3.1415:
            _net_balance_individual[i] = elem
            i += 1

    # Override the old array
    net_balance_individual = _net_balance_individual

    # Cumulative sum
    net_balance_accumulated = np.cumsum(net_balance_individual)

    # UI - Initial balance
    with net_balance_cols[1]:
        initial_balance = st.number_input('Speicher aus dem letzten Jahr [GWh]',
                        value=10_000)

    # Add the initial balance to the net balance
    net_balance_accumulated += initial_balance

    # Generate the dataframes
    net_balance_individual_df = pd.DataFrame(
        {
            'time': time_range[0::time_range_resolution],
            'balance': net_balance_individual[0::time_range_resolution]
        }
    )

    net_balance_accumulated_df = pd.DataFrame(
        {
            'time': time_range[0::time_range_resolution],
            'balance': net_balance_accumulated[0::time_range_resolution]
        }
    )

    # Generate the charts
    net_balance_brush = alt.selection_interval(encodings=['x'])

    net_balance_individual_chart = alt.Chart(net_balance_individual_df).mark_bar().encode(
        alt.X(
            "time:T",
            title="Time",
        ),
        alt.Y(
            "balance:Q",
            title="Bilanz [GWh]",
        ),
        color=alt.condition(
            alt.datum.balance >= 0,  # If the balance is positive this test returns True,
            alt.value('#7DDF64'),     # which sets the bar orange.
            alt.value('#FF4B4B')   # And if it's not true it sets the bar steelblue.
        )
    ).properties(width=550, height=500)

    net_balance_accumulated_chart = alt.Chart(net_balance_accumulated_df).mark_area().encode(
        alt.X(
            "time:T",
            title="Time",
        ),
        y=alt.Y(
            "balance:Q",
            title="Bilanz [GWh]",
        ),
        color=alt.condition(
            alt.datum.balance >= 0,  # If the balance is positive this test returns True,
            alt.value('#7DDF64'),     # which sets the bar orange.
            alt.value('#FF4B4B')   # And if it's not true it sets the bar steelblue.
        )
    ).properties(width=550, height=500)

    # Render the charts
    st.markdown('#### Zeitaufgelöste Bilanz')

    st.markdown('###### Formel:')
    st.latex(r'''
                \text{net balance}_{day} = \text{production}_{day} - \text{consumption}_{day}
            ''')
    st.altair_chart(net_balance_individual_chart, theme="streamlit", use_container_width=True)

    st.markdown('#### Akkumulierte Bilanz')
    st.latex(r'''
                \sum_{day=0}^{total} \sum_{day'=0}^{day} \text{net balance}_{day'}
            ''')
    st.altair_chart(net_balance_accumulated_chart, theme="streamlit", use_container_width=True)

    st.markdown('### Datenquellen')

    st.markdown('''
                [SMARD | Marktdaten visualisieren](https://www.smard.de/home/marktdaten?marketDataAttributes=%7B%22resolution%22:%22month%22,%22from%22:1580511600000,%22to%22:1672527599999,%22moduleIds%22:%5B1004066,1001226,1001225,1004067,1004068,1001228,1001224,1001223,1004069,1004071,1004070,1001227,5000410%5D,%22selectedCategory%22:null,%22activeChart%22:true,%22style%22:%22color%22,%22categoriesModuleOrder%22:%7B%7D,%22region%22:%22DE%22%7D)
             ''')


def get_iterator():
    for year in range(0, 3):
        for month in range(0, 12):
            for day in range(0, 31):
                for hour in range(0, 24):
                    for quarter in range(0, 4):
                        yield year, month, day, hour, quarter


def mark_blurred_line(chart, n_glows=10, base_opacity=0.3):
    opacity = base_opacity / n_glows
    glows = (
        chart.mark_line(opacity=opacity, strokeWidth = 2 + (1.05 * i))
        for i in range(1, n_glows + 1)
    )

    return alt.layer(*glows)


def change_page(key):
    st.session_state.selection = st.session_state[key]


def compute_renewable_distribution(
        selectbox_year: int,
        resolution: int = 1,
        clamp_overshoot: bool = False,
        upper_limit: int = 100) -> pd.DataFrame:

    slots: int = upper_limit // resolution + 1
    data = np.zeros(slots, dtype=int)

    for year in range(0, 3):
        for month in range(0, 12):
            for day in range(0, 31):
                for hour in range(0, 24):
                    for quarter in range(0, 4):
                        if selectbox_year == 2030:
                            year = year
                        else:
                            year = selectbox_year

                        # Check for empty entries, i.e., invalid dates
                        if production_data[year, month, day, hour, quarter].coal == 0:
                            continue

                        renewables_production = production_data[year, month, day, hour, quarter].total_renewables()
                        total_load = consumption_data[year, month, day, hour, quarter].total_load

                        percentage = renewables_production / total_load * 100

                        # Clamp the percentage to 100 since it is possible to have surplus energy
                        if clamp_overshoot:
                            percentage = min(percentage, upper_limit)

                        # Map percentage to slot according to the resolution
                        slot = int(percentage) // resolution

                        data[slot] += 1

    df = pd.DataFrame(
        {
            'Percentage': np.arange(0, upper_limit+1, resolution),
            'Count': data
        }
    )

    return df


def render_view_individual(power_source: PowerSource):
    st.header(f'{power_source.get_display_name()} Power Production')

    key = f'{power_source.get_id()}'

    with st.spinner('Loading data...'):
        global selected_date
        global production_data
        global consumption_data

        # Get year from selected date and store 2020 as index 0, etc.
        year = selected_date.year - 2020

        # Do the same for the month
        month = selected_date.month - 1

        # Get the day of the month
        day = selected_date.day - 1

        selected_data = production_data[year, month, day, :, :].flatten()
        selected_consumption = consumption_data[year, month, day, :, :].flatten()

        data_to_plot = None
        consumption_to_plot = np.array([d.total_load / 1_000_000_000 for d in selected_consumption])

        if power_source.get_id() == 'w-off':
            data_to_plot = np.array([d.wind_offshore / 1_000_000_000 for d in selected_data])
            clr = clr_wind_offshore
        elif power_source.get_id() == 'w-on':
            data_to_plot = np.array([d.wind_onshore / 1_000_000_000 for d in selected_data])
            clr = clr_wind_onshore
        elif power_source.get_id() == 'pv':
            data_to_plot = np.array([d.pv / 1_000_000_000 for d in selected_data])
            clr = clr_photovoltaic
        elif power_source.get_id() == 'hy':
            data_to_plot = np.array([d.hydro / 1_000_000_000 for d in selected_data])
            clr = clr_hydro
        elif power_source.get_id() == 'bm':
            data_to_plot = np.array([d.biomass / 1_000_000_000 for d in selected_data])
            clr = clr_biomass
        elif power_source.get_id() == 'nuclear':
            data_to_plot = np.array([d.nuclear / 1_000_000_000 for d in selected_data])
            clr = clr_nuclear

        # Create a pandas dataframe with random values for 24 hours
        df = pd.DataFrame(
            {
                'Power [GWh]': data_to_plot,
                'Load [GWh]': consumption_to_plot
            },
            index=pd.date_range(selected_date.isoformat(), periods=96, freq='15min')
        )

    st.line_chart(df, color=['#FF0000', clr])


def render_view_all():
    st.header(f'⚡ Power Production')

    with st.spinner('Loading data...'):
        global selected_date
        global production_data
        global consumption_data

        # Get year from selected date and store 2020 as index 0, etc.
        year = selected_date.year - 2020

        # Do the same for the month
        month = selected_date.month - 1

        # Get the day of the month
        day = selected_date.day - 1

        selected_data = production_data[year, month, day, :, :].flatten()
        selected_consumption = consumption_data[year, month, day, :, :].flatten()

        consumption_to_plot = np.array([d.total_load / 1_000_000_000 for d in selected_consumption])
        storage_to_plot = np.array([d.gravitational_energy_storage / 1_000_000_000 for d in selected_consumption])

        w_off_data = np.array([d.wind_offshore / 1_000_000_000 for d in selected_data])
        w_on_data = np.array([d.wind_onshore / 1_000_000_000 for d in selected_data])
        pv_data = np.array([d.pv / 1_000_000_000 for d in selected_data])
        hy_data = np.array([d.hydro / 1_000_000_000 for d in selected_data])
        bm_data = np.array([d.biomass / 1_000_000_000 for d in selected_data])
        ff_data = np.array([d.total_fossil_fuels() / 1_000_000_000 for d in selected_data])
        nu_data = np.array([d.nuclear / 1_000_000_000 for d in selected_data])
        gr_data = np.array([d.gravity_energy_storage / 1_000_000_000 for d in selected_data])

        # Create a pandas dataframe with random values for 24 hours
        df = pd.DataFrame(
            {
                'Biomass': bm_data,
                'Hydro': hy_data,
                'Load [GWh]': consumption_to_plot,
                'PV': pv_data,
                'Wind Offshore': w_off_data,
                'Wind Onshore': w_on_data
            },
            index=pd.date_range(selected_date.isoformat(), periods=96, freq='15min')
        )

    st.line_chart(df, color=[clr_biomass, clr_hydro, '#FF0000', clr_photovoltaic, clr_wind_offshore, clr_wind_onshore])

    st.divider()

    st.markdown("""
                <img src="https://cdn.pixabay.com/photo/2017/03/28/12/05/windmills-2181904_1280.jpg" alt="Power grid schematic" width="100%" style="border-radius: 6px; margin-bottom: 1rem"/>
                """, unsafe_allow_html=True)

    st.subheader(f'Kummulative Energieerzeugung und Verbrauch')

    st.markdown("""
                Kummulative Darstellung der Energieproduktion und des Verbrauchs.
                Die Auflösung beträgt 15 Minuten.
                Es handelt sich bei den Daten wie standardmäßig um den netto Produktionswert
                und den Brutto Verbrauchswert, d.h., dass die Verluste durch die Übertragung
                entstehen berücktsichtigt werden.
                In anderen Worten: Die Werte sind direkt vergleichbar. Was kommt aus den Kraftwerken
                raus und was geht ab diesem Punkt in das Netz hinein.

                ##### 🔋💧 Pumpspeicher
                Zudem wird auch die Ladekurve von Pumpspeichern geplottet.
                Diese Leistung ist ebenso in der Verbrauchskurve beinhaltet
                und erlaubt daher eine einfache Übersicht, um zu sehen,
                ob der Verbrauch steigt, um überschüssige Energie zu speichern,
                oder ob die Last steigt und der Pumpspeicher zur Unterstützung
                Energie entlädt.
                """)

    col0, col1 = st.columns(2)

    with col0:
        st.markdown('##### ⛽🌊 Energieerzeuger')
        show_ff: bool = st.toggle('🪨⛽ Fossile Quellen', value=True, key='show_fossil_fuels')
        show_nu: bool = st.toggle('☢️ Atomkraft', value=True, key='show_nuclear')
    with col1:
        st.markdown('##### 🔋💧 Pumpspeicher')
        show_gr_consumption: bool = st.toggle('Ladekurve', value=True, key='show_gr_consumption')
        show_gr_production: bool = st.toggle('Entladekurve', value=True, key='show_gr_production')



    # Create the Legend array
    entries_per_source = 24 * 4

    pv_array = np.full(entries_per_source, "g Photovoltaic")
    w_on_array = np.full(entries_per_source, "f Wind Onshore")
    w_off_array = np.full(entries_per_source, "e Wind Offshore")
    hy_array = np.full(entries_per_source, "d Hydro")
    bm_array = np.full(entries_per_source, "c Biomass")
    ff_array = np.full(entries_per_source, "a Fossil Fuels")
    nu_array = np.full(entries_per_source, "b Nuclear")
    gr_array = np.full(entries_per_source, "h Gravitational Energy Storage")

    tidy_data_source_col = np.concatenate([pv_array, w_on_array, w_off_array, hy_array, bm_array, ff_array, nu_array, gr_array])

    # Create the timestamp array
    tidy_data_timestamp_col = pd.date_range(selected_date.isoformat(), periods=96, freq='15min')
    tidy_data_timestamp_col = np.tile(tidy_data_timestamp_col, 8)

    # Create the net generation array
    if not show_ff:
        ff_data = np.zeros(entries_per_source)
    if not show_nu:
        nu_data = np.zeros(entries_per_source)
    if not show_gr_production:
        gr_data = np.zeros(entries_per_source)
    tidy_data_net_generation_col = np.concatenate([pv_data, w_on_data, w_off_data, hy_data, bm_data, ff_data, nu_data, gr_data])

    # Create the tidy data frame
    tidy_data = pd.DataFrame({
        'year': tidy_data_timestamp_col,
        'source': tidy_data_source_col,
        'net_generation': tidy_data_net_generation_col
    })

    # Create the chart
    stacked_chart = alt.Chart(tidy_data).mark_area().encode(
        x=alt.X("year:T", title="Hour of day"),
        y=alt.Y(
            "net_generation:Q",
            title="Net Generation [MWh]",
            stack="zero"
        ),
        order=alt.Order(
            'source',
            sort='ascending'
        ),
        color=alt.Color(
            'source:N',
            scale=alt.Scale(
                range=[clr_fossil_fuels, clr_nuclear, clr_biomass, clr_hydro, clr_wind_offshore, clr_wind_onshore, clr_photovoltaic, "#FFFFFF", '#FF0000', '#00FF00']
                ),
            legend=alt.Legend(
                title="Source",
                orient="bottom",
                )
        )
    ).interactive()

    consumption_array = np.full(entries_per_source, "x Consumption")

    storage_array = np.full(entries_per_source, "y Storage")

    consumption_plot = pd.DataFrame({
        'year': pd.date_range(selected_date.isoformat(), periods=96, freq='15min'),
        'source': consumption_array,
        'net_consumption': consumption_to_plot
    })

    storage_plot = pd.DataFrame({
        'year': pd.date_range(selected_date.isoformat(), periods=96, freq='15min'),
        'source': storage_array,
        'net_consumption': storage_to_plot
    })

    line_chart = alt.Chart(consumption_plot).mark_line().encode(
        x=alt.X("year:T", title="Hour of day"),
        y=alt.Y(
            "net_consumption:Q",
            title="Net Consumption [MWh]",
            stack="zero",
            scale=alt.Scale(domain=[0, 20]),
        ),
        order=alt.Order(
            'source',
            sort='ascending'
        ),
        color=alt.Color(
            'source:N',
            scale=alt.Scale(
                range=["#FF0000"]
                ),
            legend=alt.Legend(
                title="Source",
                orient="bottom",
                )
        )
    ).interactive().properties(width=550, height=500)

    storage_line_chart = alt.Chart(storage_plot).mark_line().encode(
        x=alt.X("year:T", title="Hour of day"),
        y=alt.Y(
            "net_consumption:Q",
            title="Net Consumption [MWh]",
            stack="zero",
            scale=alt.Scale(domain=[0, 20]),
        ),
        order=alt.Order(
            'source',
            sort='ascending'
        ),
        color=alt.Color(
            'source:N',
            scale=alt.Scale(
                range=["#00FF00"]
                ),
            legend=alt.Legend(
                title="Source",
                orient="bottom",
                )
        )
    ).interactive().properties(width=550, height=500)

    layered_chart = stacked_chart + line_chart
    if show_gr_consumption:
        layered_chart += storage_line_chart

    st.altair_chart(layered_chart, theme="streamlit", use_container_width=True)
    st.caption("© 2023 Science Sisters. Net Generation and Consumption.")


def render_view_fossil_fuels():
    st.header(f'⚡ Fossil Fuels')

    with st.spinner('Loading data...'):
        global selected_date
        global production_data
        global consumption_data

        # Get year from selected date and store 2020 as index 0, etc.
        year = selected_date.year - 2020

        # Do the same for the month
        month = selected_date.month - 1

        # Get the day of the month
        day = selected_date.day - 1

        selected_data = production_data[year, month, day, :, :].flatten()
        selected_consumption = consumption_data[year, month, day, :, :].flatten()

        consumption_to_plot = np.array([d.total_load / 1_000_000_000 for d in selected_consumption])

        coal_data = np.array([d.coal / 1_000_000_000 for d in selected_data])
        charcoal_data = np.array([d.charcoal / 1_000_000_000 for d in selected_data])
        gas_data = np.array([d.gas / 1_000_000_000 for d in selected_data])
        other_data = np.array([d.other_conventional / 1_000_000_000 for d in selected_data])

        # Create a pandas dataframe with random values for 24 hours
        df = pd.DataFrame(
            {
                'Charcoal': charcoal_data,
                'Coal': coal_data,
                'Gas': gas_data,
                'Load [GWh]': consumption_to_plot,
                'Other Conventional': other_data
            },
            index=pd.date_range(selected_date.isoformat(), periods=96, freq='15min')
        )

    st.line_chart(df, color=[clr_charcoal, clr_coal, clr_gas, '#FF0000', clr_other_conventional])


if __name__ == '__main__':
    main()
