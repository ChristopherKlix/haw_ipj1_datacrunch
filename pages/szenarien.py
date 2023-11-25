from time import sleep

import numpy as np
from data_manager.data_manager import Data, DataArray
import streamlit as st
import pandas as pd
import altair as alt

from init_page import PageManager
from dtypes import View, URLImage

import datetime as dt


class Szenarien_View:
    def __init__(self):
        print("Szenarien_View init")

        if not 'current_view' in st.session_state:
            st.session_state.current_view = 'main'

        self.page = PageManager(layout="wide")

    def render(self):
        if st.session_state.current_view == 'main':
            self.main_view()
        elif st.session_state.current_view == 'result':
            self.result_view()

    def result_view(self):
        st.title(f"Szenario {st.session_state.scenario}")

        st.button(
            label="Zurück",
            help="Zurück zur Szenario Auswahl.",
            on_click=lambda: st.session_state.update(current_view='main'),
        )

        if st.session_state.scenario == 'prototype-v0.1':
            self.simulate_prototype_v0_1()

    def simulate(self):
        print('Simulate')

        # Get the corresponding scenario key to value
        for key, value in self.scenarios.items():
            if value == st.session_state['scenario-selection']:
                st.session_state.scenario = key

        st.session_state.current_view = 'result'

    def main_view(self):
        st.title("Szenarien")

        self.scenarios = {
            'prototype-v0.1': 'Prototyp v0.1',
            'default': "📊 Referenz Szenario (empfohlen)",
            'best-case': "☀️ Szenario \"Best Case\"",
            'worst-case': "🌧️ Szenario \"Worst Case\"",
            'custom': "⚙️ Benuzterdefiniertes Szenario"
        }


        # ---------------
        # ! Hero
        # ---------------
        columns_hero_section = st.columns(2, gap='medium')

        with columns_hero_section[0]:
            container_hero_left = st.container()

        with columns_hero_section[1]:
            container_hero_right = st.container()

        # ---------------
        # ! Hero section left
        # ---------------
        with container_hero_left:
            View.image(
                URLImage(
                    url="https://images.pexels.com/photos/2561628/pexels-photo-2561628.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
                    alt="Climate Protest",
                )
            )

        # ---------------
        # ! Hero section right
        # ---------------
        with container_hero_right:

            cols_scenario_simulate = st.columns([3, 2])

            with cols_scenario_simulate[0]:
                st.markdown('#### Szenario auswählen')

                param_scenario = st.selectbox(
                    label="Szenario",
                    options=self.scenarios.values(),
                    key='scenario-selection',
                )

            if param_scenario == "📊 Referenz Szenario (empfohlen)":
                st.markdown('''
                            Das Referenzszenario ist das wahrscheinlichste Szenario für das Jahr 2030.
                            Es basiert auf den aktuellen politischen und wirtschaftlichen Rahmenbedingungen.
                            Zudem wird davon ausgegangen, dass die Klimaziele erreicht werden.
                            Vorgegebene installierte Leistung wie vom BMWK vorgesehen werden erreicht und die Wetterbedingungen sind durchschnittlich.
                            ''')
            elif param_scenario == "☀️ Szenario \"Best Case\"":
                st.markdown('''
                            Das Best Case Szenario ist das optimistischste Szenario für das Jahr 2030.
                            Es basiert auf den aktuellen politischen und wirtschaftlichen Rahmenbedingungen.
                            Zudem wird davon ausgegangen, dass die Klimaziele erreicht werden.
                            Vorgegebene installierte Leistung wie vom BMWK vorgesehen werden erreicht und die Wetterbedingungen sind optimal.
                            ''')
            elif param_scenario == "🌧️ Szenario \"Worst Case\"":
                st.markdown('''
                            Das Worst Case Szenario ist das pessimistischste Szenario für das Jahr 2030.
                            Es basiert auf den aktuellen politischen und wirtschaftlichen Rahmenbedingungen.
                            Zudem wird davon ausgegangen, dass die Klimaziele nicht erreicht werden.
                            Vorgegebene installierte Leistung wie vom BMWK vorgesehen werden nicht erreicht und die Wetterbedingungen sind schlecht.
                            ''')
            elif param_scenario == "⚙️ Benuzterdefiniertes Szenario":
                st.markdown('''
                            Das benutzerdefinierte Szenario ermöglicht es, die Parameter für die Simulation selbst anzupassen.
                            So kann z.B. die installierte Leistung für Photovoltaik, Wind Offshore und Wind Onshore selbst festgelegt werden.
                            Zudem kann die Erzeugungseffizienz für Photovoltaik, Wind Offshore und Wind Onshore selbst festgelegt werden.
                            ''')
                st.caption('''
                           Die Parameter können im Abschnitt "Szenario Parameter" angepasst werden.
                            ''')
            elif param_scenario == "Prototyp v0.1":
                st.markdown('''
                            FUuuuck I hate everything why is this project so stupid.
                            Der Verbrauch wird mittels eines Faktors in Bezug auf ein Referenzjahr proportional hochskaliert.
                            Die Produktion wird mittels der Ausbauziele im Verhältnis zu der Installierten Leistung im Referenzjahr hochskaliert.
                            Mehr nicht.
                            ''')
                st.caption('''
                           Die Parameter können im Abschnitt "Szenario Parameter" angepasst werden.
                            ''')

            # ---------------
            # ! Simulation Button
            # ---------------
            st.button(
                label="Simulation starten",
                help="Simulate the energy production and consumption for the selected scenario.",
                on_click=self.simulate,
                type="primary",
            )


        # ---------------
        # ! Parameters
        # ---------------

        if param_scenario == self.scenarios.get('custom'):
            self.render_parameter_view()
        elif param_scenario == self.scenarios.get('prototype-v0.1'):
            self.render_prototype_v0_1_view()

        # ---------------
        # ! Footer
        # ---------------
        self.render_footer_view()

    def render_parameter_view(self):
        st.divider()

        st.markdown('#### ⚙️ Szenario Parameter')
        st.markdown('''
                    Hier können die Parameter für das benutzerdefinierte Szenario angepasst werden.
                    ''')

        cols_params_row0 = st.columns(2, gap='medium')

        with cols_params_row0[0]:
            container_efficiency = st.container()

        with cols_params_row0[1]:
            container_capacity = st.container()

        cols_params_row1 = st.columns(2, gap='medium')

        with cols_params_row1[0]:
            container_consumption = st.container()

        with cols_params_row1[1]:
            View.image(
                URLImage(
                    url="https://images.pexels.com/photos/1473673/pexels-photo-1473673.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
                    alt="Dubai at night",
                )
            )

        st.divider()

        cols_params_row2 = st.columns(2, gap='medium')

        with cols_params_row2[0]:
            container_storage = st.container()

        with cols_params_row2[1]:
            st.write("Hier kommt der Müll hin.")

        with container_efficiency:
            self.render_efficiency_view()

        with container_capacity:
            self.render_capacity_view()

        with container_consumption:
            self.render_consumption_view()

        with container_storage:
            self.render_storage_view()

    def render_efficiency_view(self):
        st.markdown('#### ⚡ Erzeugungseffizienz')

        st.markdown('''
                    Die Erzeugungseffizienz gibt an, wie viel Prozent der installierten Leistung tatsächlich erzeugt wird.
                    Dieser Wert kann je nach Wetterbedingungen variieren.
                    Die Simulation berechnet einen erwarten Wert für das Jahr 2030.
                    Mit den Slidern kann dieser Wert prozentual nach oben oder unten angepasst werden.
                    ''')
        with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
            st.caption('''
                    Die Effizienz ist ein Kennwert, welcher in der Simulation eine Vielzahl von Faktoren berücksichtigt.
                    So beeinflusst der Faktor die simulierte Wetterbedingungen, die Anzahl der Sonnenstunden, die Anzahl der Windstunden, die Anzahl der Wolkenstunden, etc.
                    Daher dient dieser Wert als Prozentuale Angabe, mit Abweichung vom simulierten wahrscheinlichen Referenzjahr in 2030.
                    ''')

        st.caption('100% entspricht dem Refernzjahr 2030.')

        cols_efficiency = st.columns(3)

        with cols_efficiency[0]:
            param_efficiency_pv = st.slider(
                label="Photovoltaik [%]",
                min_value=0,
                max_value=200,
                value=100,
                help="100% entspricht dem Refernzjahr 2030.",
            )

            st.caption(f'Vorraussichtliche Erzeugung: {param_efficiency_pv / 100 * 196} TWh')

        with cols_efficiency[1]:
            param_efficieny_wind_off = st.slider(
                label="Wind Offshore [%]",
                min_value=0,
                max_value=200,
                value=100,
                help="100% entspricht dem Refernzjahr 2030.",
            )

            st.caption(f'Vorraussichtliche Erzeugung: {param_efficieny_wind_off / 100 * 196} TWh')

        with cols_efficiency[2]:
            param_efficieny_wind_on = st.slider(
                label="Wind Onshore [%]",
                min_value=0,
                max_value=200,
                value=100,
                help="100% entspricht dem Refernzjahr 2030.",
            )

            st.caption(f'Vorraussichtliche Erzeugung: {param_efficieny_wind_on / 100 * 196} TWh')

    def render_capacity_view(self):
        st.markdown('#### 🏗️ Installierte Leistung')

        st.markdown('''
                    Die Erzeugungseffizienz gibt an, wie viel Prozent der installierten Leistung tatsächlich erzeugt wird.
                    Dieser Wert kann je nach Wetterbedingungen variieren.
                    Die Simulation berechnet einen erwarten Wert für das Jahr 2030.
                    Mit den Slidern kann dieser Wert prozentual nach oben oder unten angepasst werden.
                    ''')
        with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
            st.caption('''
                    Die Effizienz ist ein Kennwert, welcher in der Simulation eine Vielzahl von Faktoren berücksichtigt.
                    So beeinflusst der Faktor die simulierte Wetterbedingungen, die Anzahl der Sonnenstunden, die Anzahl der Windstunden, die Anzahl der Wolkenstunden, etc.
                    Daher dient dieser Wert als Prozentuale Angabe, mit Abweichung vom simulierten wahrscheinlichen Referenzjahr in 2030.
                    ''')

        cols_capacity = st.columns(3)

        with cols_capacity[0]:
            st.number_input(
                label="Photovoltaik [GW]",
                min_value=0,
                max_value=1_000,
                value=240,
            )

        with cols_capacity[1]:
            st.number_input(
                label="Wind Offshore [GW]",
                min_value=0,
                max_value=1_000,
                value=240,
            )

        with cols_capacity[2]:
            st.number_input(
                label="Wind Onshore [GW]",
                min_value=0,
                max_value=1_000,
                value=240,
            )

    def render_consumption_view(self):
        st.markdown('#### 🔌 Stromverbrauch')

        st.markdown('''
                    Die Erzeugungseffizienz gibt an, wie viel Prozent der installierten Leistung tatsächlich erzeugt wird.
                    Dieser Wert kann je nach Wetterbedingungen variieren.
                    Die Simulation berechnet einen erwarten Wert für das Jahr 2030.
                    Mit den Slidern kann dieser Wert prozentual nach oben oder unten angepasst werden.
                    ''')
        with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
            st.caption('''
                    Die Effizienz ist ein Kennwert, welcher in der Simulation eine Vielzahl von Faktoren berücksichtigt.
                    So beeinflusst der Faktor die simulierte Wetterbedingungen, die Anzahl der Sonnenstunden, die Anzahl der Windstunden, die Anzahl der Wolkenstunden, etc.
                    Daher dient dieser Wert als Prozentuale Angabe, mit Abweichung vom simulierten wahrscheinlichen Referenzjahr in 2030.
                    ''')

        select_consumption_mode = st.selectbox(
            label="Berechnungsgrundlage",
            options=[
                "Gesamter Stromverbrauch (pauschal)",
                "Stromverbrauch basierend auf Parametern",
            ],
        )

        if select_consumption_mode == "Gesamter Stromverbrauch (pauschal)":
            st.caption('''
                    Der gesamte Stromverbrauch wird pauschal festgelegt.
                    ''')

            cols_consumption_simple = st.columns(2, gap='medium')

            with cols_consumption_simple[0]:
                st.number_input(
                    label="Gesamter Stromverbrauch [TWh]",
                    min_value=0,
                    max_value=1_000,
                    value=500,
                )
        elif select_consumption_mode == "Stromverbrauch basierend auf Parametern":
            st.caption('''
                    Der gesamte Stromverbrauch wird mittels Parametern berechnet.
                    Die Parameter werden in Verbrauchszahlen extrapoliert.
                    ''')

            cols_consumption_params = st.columns([1, 2], gap='medium')

            with cols_consumption_params[0]:
                st.slider(
                    label="E-Mobilität [Millionen]",
                    min_value=5,
                    max_value=30,
                    value=15,
                    help="Ziel E-Mobilität in 2030 beträgt 15 Millionen.",
                )

                number_heatpumps = st.number_input(
                    label="Wärmepumpen [Tausend]",
                    min_value=0,
                    max_value=2_000,
                    value=500,
                    help="Ziel Wärmepumpenzubau pro Jahr bis 2030 beträgt 500 Tausend.",
                )

                st.caption(f'Vorraussichtlicher Zubau pro Jahr: {(number_heatpumps * 1_000):,} Stück')

            with cols_consumption_params[1]:
                select_consumption_industry = st.selectbox(
                    label="Industrieverbrauch",
                    options=[
                        "Abnahme (97%)",
                        "Kein Wachstum (100%)",
                        "(Erwartet) Geringes Wachstum (103%)",
                        "Mittleres Wachstum (108%)",
                        "Hohes Wachstum (110%)",
                    ],
                    index=2,
                    help="Der Industrieverbrauch wird basierend auf den Daten des Fraunhofer ISE berechnet.",
                )

                if select_consumption_industry == "Abnahme (97%)":
                    st.caption('''
                            Der Industrieverbrauch reduziert sich in etwa auf 267 TWh.
                            ''')
                elif select_consumption_industry == "Kein Wachstum (100%)":
                    st.caption('''
                            Der Industrieverbrauch bleibt in etwa gleich und beträgt 276 TWh.
                            ''')
                elif select_consumption_industry == "(Erwartet) Geringes Wachstum (103%)":
                    st.caption('''
                            Der Industrieverbrauch wächst leicht und beträgt 284 TWh.
                            ''')
                elif select_consumption_industry == "Mittleres Wachstum (108%)":
                    st.caption('''
                            Der Industrieverbrauch wächst moderat und beträgt 291 TWh.
                            ''')
                elif select_consumption_industry == "Hohes Wachstum (110%)":
                    st.caption('''
                            Der Industrieverbrauch wächst stark und beträgt 294 TWh.
                            ''')

    def render_storage_view(self):
        st.markdown('#### 🔋 Speicher')

        st.multiselect(
            label="Auswahl der Speichertechnologien",
            options=[
                "Batteriespeicher",
                "Power-to-Gas (Wasserstoff)",
                "Power-to-Gas (Methanol)",
                "Power-to-Liquid (E-Fuels)",
                "Pumpspeicher",
            ],
            default=["Batteriespeicher"],
            help="Speicher können die Energieproduktion und den Energieverbrauch ausgleichen.",
        )

        View.image(
            URLImage(
                url="https://www.bmp-greengas.com/wp-content/uploads/2023/02/180426_bmp_PtG_InfoGrafik_2english-legende-2023-2.jpg",
                alt="Power-to-Gas Infografik",
            )
        )

        st.markdown('''
                    #### Was ist was?
                    ''')

        st.markdown('''
                    <div style="font-size: 1rem; font-weight: 700;">
                    🔋 Batteriespeicher
                    </div>

                    <div style="margin-left: 0rem; font-size: 0.8rem;">
                        Batteriespeicher können/müssen zur Netzstabilisierung eingesetzt werden.
                        Allerdings sind Batteriespeicher teuer und haben eine begrenzte Lebensdauer.
                        Daher ist es unwahrscheinlich, dass Batteriespeicher in großem Umfang eingesetzt werden,
                        um langfristig große Mengen an Energie zu speichern.
                    </div>
                    </br>
                    ''', unsafe_allow_html=True)

        st.markdown('''
                    <div style="font-size: 1rem; font-weight: 700;">
                    Power-to-Gas (Wasserstoff) - H<sub>2</sub>
                    </div>

                    <div style="margin-left: 0rem; font-size: 0.8rem;">
                        Power-to-Gas Anlagen können große Mengen an Energie speichern.
                        Strom wird in Wasserstoff umgewandelt und kann bei Bedarf
                        in Kraftwerken verbrannt werden, um Strom zu erzeugen.
                        Die Umwandlung von Wasserstoff in Strom ist allerdings ineffizient.
                        Während der Umwandlung geht ein Großteil der Energie verloren,
                        sodass von 100% eingespeister Energie nur in etwa 77% wieder zurückgewonnen werden können.
                    </div>
                    </br>
                    ''', unsafe_allow_html=True)

        st.markdown('''
                    <div style="font-size: 1rem; font-weight: 700;">
                    Power-to-Gas (Methanol) - CH<sub>3</sub>OH
                    </div>

                    <div style="margin-left: 0rem; font-size: 0.8rem;">
                        Power-to-Gas Anlagen können große Mengen an Energie speichern.
                        Wasserstoff wird weiter in Methanol umgewandelt und kann in das Erdgasnetz eingespeist werden.
                        Die Umwandlung von Strom in Wasserstoff und weiter in Methanol und wieder in Strom ist allerdings ineffizient.
                        Während der Umwandlung geht ein Großteil der Energie verloren,
                        sodass von 100% eingespeister Energie nur in etwa 50-60% wieder zurückgewonnen werden können.
                    </div>
                    </br>
                    ''', unsafe_allow_html=True)

        st.markdown('''
                    <div style="font-size: 1rem; font-weight: 700;">
                    ⛽ Power-to-Liquid (E-Fuels) - C<sub>x</sub>H<sub>x</sub>
                    </div>

                    <div style="margin-left: 0rem; font-size: 0.8rem;">
                        Power-to-liquid ist ein Sammelbegriff für verschiedene synthetische Kraftstoffe.
                        Dazu gehören die bekannten eFuel Kraftstoffe wie eMethanol, eDiesel und eKerosin.
                        Basierend auf dem Power-to-Gas Verfahren wird Wasserstoff in Methanol umgewandelt.
                        Durch das Beifügen von weiteren synthetischen Komponenten entsteht ein Kraftstoff,
                        der wie ein herkömmlicher Kraftstoff verwendet werden kann.
                        Dieser Prozess ist sehr ineffizient und benötigt viel Energie.
                        <b>Daher bleiben aus 100% eingespeister Energie nur in etwa 13% übrig.</b>
                    </div>
                    </br>
                    ''', unsafe_allow_html=True)

        st.markdown('''
                    <div style="font-size: 1rem; font-weight: 700;">
                    Pumpspeicher
                    </div>

                    <div style="margin-left: 0rem; font-size: 0.8rem;">
                        Pumpspeicher sind große Wasserbecken, in denen Wasser gepumpt werden kann.
                        Bei Bedarf kann das Wasser wieder abgelassen werden, um Strom zu erzeugen.
                        Pumpspeicher sind sehr effizient und können große Mengen an Energie speichern.
                        Allerdings sind Pumpspeicher sehr teuer und benötigen viel Platz.
                        Zudem ist die Höhe des Speicherbeckens proportional zur gespeicherten Energie.
                        Daher sind Pumpspeicher nur in bestimmten Regionen möglich.
                    </div>
                    ''', unsafe_allow_html=True)

    def render_footer_view(self):
        st.divider()

    def render_prototype_v0_1_view(self):
        st.session_state.total_consumption_2030 = None
        st.session_state.reference_year         = None

        st.divider()

        st.markdown('#### ⚙️ Szenario Parameter')
        st.markdown('''
                    Hier können die Parameter für das benutzerdefinierte Szenario angepasst werden.
                    ''')

        cols_params_row0 = st.columns(2, gap='medium')

        with cols_params_row0[0]:
            container_consumption = st.container()

        with cols_params_row0[1]:
            container_reference_year = st.container()

        with container_consumption:
            st.markdown('#### 🔌 Stromverbrauch')

            st.markdown('''
                        Die Erzeugungseffizienz gibt an, wie viel Prozent der installierten Leistung tatsächlich erzeugt wird.
                        Dieser Wert kann je nach Wetterbedingungen variieren.
                        Die Simulation berechnet einen erwarten Wert für das Jahr 2030.
                        Mit den Slidern kann dieser Wert prozentual nach oben oder unten angepasst werden.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.caption('''
                        Die Effizienz ist ein Kennwert, welcher in der Simulation eine Vielzahl von Faktoren berücksichtigt.
                        So beeinflusst der Faktor die simulierte Wetterbedingungen, die Anzahl der Sonnenstunden, die Anzahl der Windstunden, die Anzahl der Wolkenstunden, etc.
                        Daher dient dieser Wert als Prozentuale Angabe, mit Abweichung vom simulierten wahrscheinlichen Referenzjahr in 2030.
                        ''')

            st.selectbox(
                label="Berechnungsgrundlage",
                options=[
                    "Gesamter Stromverbrauch (pauschal)",
                ],
            )

            cols_consumption_simple = st.columns(2, gap='medium')

            with cols_consumption_simple[0]:
                st.session_state.total_consumption_2030 = st.number_input(
                    label="Gesamter Stromverbrauch [TWh]",
                    min_value=0,
                    max_value=1_000,
                    value=750,
                    step=10
                )

        with container_reference_year:
            st.markdown('''
                        #### 📅 Referenzjahr
                        ''')

            st.markdown('''
                    Die Erzeugungseffizienz gibt an, wie viel Prozent der installierten Leistung tatsächlich erzeugt wird.
                    Dieser Wert kann je nach Wetterbedingungen variieren.
                    Die Simulation berechnet einen erwarten Wert für das Jahr 2030.
                    Mit den Slidern kann dieser Wert prozentual nach oben oder unten angepasst werden.
                    ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.caption('''
                        Die Effizienz ist ein Kennwert, welcher in der Simulation eine Vielzahl von Faktoren berücksichtigt.
                        So beeinflusst der Faktor die simulierte Wetterbedingungen, die Anzahl der Sonnenstunden, die Anzahl der Windstunden, die Anzahl der Wolkenstunden, etc.
                        Daher dient dieser Wert als Prozentuale Angabe, mit Abweichung vom simulierten wahrscheinlichen Referenzjahr in 2030.
                        ''')

            st.session_state.reference_year = st.selectbox(
                label='Referenzjahr',
                options=[*range(2015, 2023)],
                index=5,
                help="Das Referenzjahr wird als Basis für die Simulation verwendet."
            )

            st.markdown(
                '''
                ##### Jahr mit höchster Produktion: 2020

                In diesem Jahr wurde verhältnismäßig am meisten Strom durch erneuerbare Energien erzeugt.
                Dies korrelliert mit den Wetterbedingungen, welche in diesem Jahr besonders gut waren.

                ##### Jahr mit niedrigster Produktion: 2021

                In diesem Jahr wurde verhältnismäßig am wenigsten Strom durch erneuerbare Energien erzeugt.
                Dies korrelliert mit den Wetterbedingungen, welche in diesem Jahr besonders schlecht waren.
                '''
            )

    def simulate_prototype_v0_1(self):
        # ---------------
        # ! Simulate
        # ---------------

        data = self.page.get_data()


        simulation_progress_widget = st.progress(
            value=0.0,
            text="Simulating..."
        )

        data_reference_year: DataArray = data.smard.get_year(st.session_state.reference_year)

        total_consumption_reference_year = 0

        for d in data_reference_year:
            total_consumption_reference_year += d.consumption.load

        total_consumption_2030 = st.session_state.total_consumption_2030 * 1_000_000_000_000

        simulation_progress_widget.progress(0.2)

        consumption_factor = total_consumption_2030 / total_consumption_reference_year

        st.write(f'Total consumption {st.session_state.reference_year}: {total_consumption_reference_year}')
        st.write(f'Total consumption 2030: {total_consumption_2030}')
        st.write(f'Consumption factor: {consumption_factor}')

        data_2030 = [d.consumption.load * consumption_factor for d in data_reference_year]

        simulation_progress_widget.progress(0.5)

        # Factor for PV
        total_production_pv_reference = 0
        total_production_wind_offshore_reference = 0
        total_production_wind_onshore_reference = 0

        for d in data_reference_year:
            total_production_pv_reference += d.production.pv
            total_production_wind_offshore_reference += d.production.wind_offshore
            total_production_wind_onshore_reference += d.production.wind_onshore

        simulation_progress_widget.progress(0.7)

        power_pv_reference = data_reference_year[-1].power.pv * 365 * 24
        power_wind_offshore_reference = data_reference_year[-1].power.wind_offshore * 365 * 24
        power_wind_onshore_reference = data_reference_year[-1].power.wind_onshore * 365 * 24

        simulation_progress_widget.progress(1.0)

        # ---------------
        # ! Computing ratios
        # ---------------

        ratio_pv_reference = total_production_pv_reference / power_pv_reference
        ratio_wind_offshore_reference = total_production_wind_offshore_reference / power_wind_offshore_reference
        ratio_wind_onshore_reference = total_production_wind_onshore_reference / power_wind_onshore_reference

        target_pv_power            = 215_000_000_000
        target_wind_offshore_power = 30_000_000_000
        target_wind_onshore_power  = 115_000_000_000
        target_biomass_power       = 8_332_000_000
        target_hydro_power         = 4_253_000_000

        pv_factor            = (target_pv_power / data_reference_year[-1].power.pv)
        wind_offshore_factor = (target_wind_offshore_power / data_reference_year[-1].power.wind_offshore)
        wind_onshore_factor  = (target_wind_onshore_power / data_reference_year[-1].power.wind_onshore)
        biomass_factor       = (target_biomass_power / data_reference_year[-1].power.biomass)
        hydro_factor         = (target_hydro_power / data_reference_year[-1].power.hydro)

        st.divider()
        st.write(f'Installed PV Reference:           {(data_reference_year[-1].power.pv / 1_000_000_000):.2f} GW -> {(target_pv_power / 1_000_000_000):.2f} GW : {pv_factor:.2f}x')
        st.write(f'Possible PV Output Reference:           {(power_pv_reference / 1_000_000_000_000):.0f} TWh -> {(power_pv_reference / 1_000_000_000_000_000 * pv_factor):.2f} PWh')
        st.write(f'Installed Wind Offshore Reference:           {(data_reference_year[-1].power.wind_offshore / 1_000_000_000):.2f} GW -> {(target_wind_offshore_power / 1_000_000_000):.2f} GW : {wind_offshore_factor:.2f}x')
        st.write(f'Possible Wind Offshore Output Reference:           {(power_wind_offshore_reference / 1_000_000_000_000):.0f} TWh -> {(power_wind_offshore_reference / 1_000_000_000_000_000 * wind_offshore_factor):.2f} PWh')
        st.write(f'Installed Wind Onshore Reference:           {(data_reference_year[-1].power.wind_onshore / 1_000_000_000):.2f} GW -> {(target_wind_onshore_power / 1_000_000_000):.2f} GW : {wind_onshore_factor:.2f}x')
        st.write(f'Possible Wind Onshore Output Reference:           {(power_wind_onshore_reference / 1_000_000_000_000):.0f} TWh -> {(power_wind_onshore_reference / 1_000_000_000_000_000 * wind_onshore_factor):.2f} PWh')
        st.write(f'Ratio PV:            {(ratio_pv_reference * 100):5.2f}%')
        st.write(f'Ratio Wind Offshore: {(ratio_wind_offshore_reference * 100):5.2f}%')
        st.write(f'Ratio Wind Onshore:  {(ratio_wind_onshore_reference * 100):5.2f}%')
        st.divider()

        st.subheader('Value prompt')

        columns = st.columns(5, gap='medium')

        category = columns[0].selectbox(
            label='Sum by',
            options=['Year', 'Month', 'Day'],
        )

        value_field = columns[1].selectbox(
            label='Field',
            options=['PV', 'Wind Offshore', 'Wind Onshore', 'Biomass', 'Hydro'],
        )

        selected_year = columns[2].number_input(
            label='Year',
            min_value=2015,
            max_value=2022,
            value=2022,
            step=1,
        )

        selected_month = columns[3].selectbox(
            label='Month',
            options=[*range(1, 13)],
            disabled=category == 'Year',
        )

        selected_day = columns[4].number_input(
            label='Day',
            min_value=1,
            max_value=31,
            value=1,
            step=1,
            disabled=category != 'Day',
        )

        btn = st.button(
            label='Get'
        )

        if btn:
            value_field = value_field.replace(' ', '_').lower()
            if category == 'Year':
                selected_data = data.smard.get_year(selected_year)
            elif category == 'Month':
                selected_data = data.smard.get_month(selected_year, selected_month)
            elif category == 'Day':
                selected_data = data.smard.get_day(selected_year, selected_month, selected_day)
            st.write(f'{value_field} {category} {selected_year}: {sum(getattr(d.production, value_field) for d in selected_data) / 1_000_000_000_000:.2f} TWh')

        # ---------------
        # ! Compute 2030 production
        # ---------------

        production_pv_2030 = [d.production.pv * pv_factor for d in data_reference_year]
        production_wind_offshore_2030 = [d.production.wind_offshore * wind_offshore_factor for d in data_reference_year]
        production_wind_onshore_2030 = [d.production.wind_onshore * wind_onshore_factor for d in data_reference_year]
        production_biomass_2030 = [d.production.biomass * biomass_factor for d in data_reference_year]
        production_hydro_2030 = [d.production.hydro * hydro_factor for d in data_reference_year]

        production_renewables_2030 = [
            production_pv_2030[i] +
            production_wind_offshore_2030[i] +
            production_wind_onshore_2030[i] +
            production_biomass_2030[i] +
            production_hydro_2030[i]
            for i in range(len(data_reference_year))
        ]

        sum_pv_reference = sum([d.production.pv for d in data_reference_year]) / 1_000_000_000_000
        sum_pv_2030 = sum(production_pv_2030) / 1_000_000_000_000

        with st.echo():
            sum_pv_reference
            sum_pv_2030

        st.dataframe({
            f'Load {st.session_state.reference_year}': [d.consumption.load for d in data_reference_year],
            'Load 2030': data_2030,
            f'PV {st.session_state.reference_year}': [d.production.pv for d in data_reference_year],
            'PV 2030': [d.production.pv * ratio_pv_reference for d in data_reference_year],
            f'Wind Offshore {st.session_state.reference_year}': [d.production.wind_offshore for d in data_reference_year],
            'Wind Offshore 2030': [d.production.wind_offshore * ratio_wind_offshore_reference for d in data_reference_year],
            f'Wind Onshore {st.session_state.reference_year}': [d.production.wind_onshore for d in data_reference_year],
            'Wind Onshore 2030': [d.production.wind_onshore * ratio_wind_onshore_reference for d in data_reference_year],
        })

        x_range = pd.date_range(
            start=dt.datetime(st.session_state.reference_year, 1, 1, 0, 0).strftime("%Y-%m-%d %H:%M"),
            end=dt.datetime(st.session_state.reference_year, 12, 31, 23, 59).strftime("%Y-%m-%d %H:%M"),
            freq='15min',
            tz='Europe/Berlin'
        )

        plot_data_0 = pd.DataFrame({
            'Date': x_range,
            'Load': np.copy(data_2030) / 1_000_000_000,
            'Renewables': np.copy(production_renewables_2030) / 1_000_000_000,
        })

        plot_data_1 = pd.DataFrame({
            'Date': x_range,
            'PV': np.copy(production_pv_2030) / 1_000_000_000,
            'Wind Offshore': np.copy(production_wind_offshore_2030) / 1_000_000_000,
            'Wind Onshore': np.copy(production_wind_onshore_2030) / 1_000_000_000,
            'Biomass': np.copy(production_biomass_2030) / 1_000_000_000,
            'Hydro': np.copy(production_hydro_2030) / 1_000_000_000,
        })

        plot_data_0['Date'] = pd.to_datetime(plot_data_0['Date'])
        plot_data_0['Date'] = plot_data_0['Date'].dt.strftime('%Y-%m-%d')
        plot_data_0 = plot_data_0.groupby(['Date']).sum().reset_index()
        plot_data_0 = pd.melt(plot_data_0, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")

        plot_data_1['Date'] = pd.to_datetime(plot_data_1['Date'])
        plot_data_1['Date'] = plot_data_1['Date'].dt.strftime('%Y-%m-%d')
        plot_data_1 = plot_data_1.groupby(['Date']).sum().reset_index()
        plot_data_1 = pd.melt(plot_data_1, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")

        st.altair_chart(
            altair_chart=alt.layer(
                alt.Chart(
                    data=plot_data_1,
                ).mark_area().encode(
                    x=alt.X(
                        'Date:O',
                        axis=alt.Axis(title='Datum [M]')
                    ),
                    y=alt.Y(
                        'sum(Energy Value):Q',
                        axis=alt.Axis(title=f'Verbrauch [TWh]'),
                    ),
                    color=alt.Color(
                        'Energy_Source:N',
                        legend=alt.Legend(title='Energiequelle'),
                        scale=alt.Scale(
                            domain=['PV', 'Wind Offshore', 'Wind Onshore', 'Biomass', 'Hydro'],
                            range=['#ffb908', '#0898ff', '#3908ff', '#80A89C', '#53A6E4', '#ff0000', '#00ff00'],
                        ),
                    ),
                ),
                alt.Chart(
                    data=plot_data_0,
                ).mark_line().encode(
                    x=alt.X(
                        'Date:O',
                        axis=alt.Axis(title='Datum [M]')
                    ),
                    y=alt.Y(
                        'Energy Value:Q',
                        axis=alt.Axis(title=f'Verbrauch [TWh]'),
                    ),
                    color=alt.Color(
                        'Energy_Source:N',
                        legend=alt.Legend(title='Energiequelle'),
                        scale=alt.Scale(
                            domain=['Load', 'Renewables'],
                            range=['#ffb908', '#0898ff', '#3908ff', '#80A89C', '#53A6E4', '#ff0000', '#00ff00'],
                        ),
                    ),
                )
            ),
            use_container_width=True,
        )

        # Count entries with surplus
        surplus = 0
        surplus_80 = 0
        surplus_90 = 0

        for i in range(len(data_2030)):
            if data_2030[i] * 0.8 < production_renewables_2030[i]:
                surplus_80 += 1

            if data_2030[i] * 0.9 < production_renewables_2030[i]:
                surplus_90 += 1

            if data_2030[i] < production_renewables_2030[i]:
                surplus += 1

        total_consumption_2030 = sum(data_2030)
        total_production_renewables_2030 = sum(production_renewables_2030)

        st.write(f'Total consumption 2030: {total_consumption_2030 / 1_000_000_000_000} TWh')
        st.write(f'Total production 2030: {total_production_renewables_2030 / 1_000_000_000_000} TWh')
        st.write(f'Ratio: {total_production_renewables_2030 / total_consumption_2030 * 100:.2f}%')

        if (total_production_renewables_2030 / total_consumption_2030) < 1:
            st.markdown('''
                        <h4 style="color: red;">⚠️ We are fucked!</h4>
                        <p style="color: red;">Die Klimaziele werden nicht erreicht.</p>
                        ''', unsafe_allow_html=True)
            View.image(URLImage('https://www.bgreco.net/forbidden/nedry.gif', width=300))
            View.image(URLImage('https://media.tenor.com/GElyvue_13cAAAAC/april-fools-joke.gif', width=300))

        st.write(f'Surplus 80%: {surplus_80} / {len(data_2030)} -> {surplus_80 / len(data_2030) * 100:.2f}%')
        st.write(f'Surplus 90%: {surplus_90} / {len(data_2030)} -> {surplus_90 / len(data_2030) * 100:.2f}%')
        st.write(f'Surplus: {surplus} / {len(data_2030)} -> {surplus / len(data_2030) * 100:.2f}%')


if __name__ == "__main__":
    view = Szenarien_View()
    view.render()
