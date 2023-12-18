import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

from init_page import PageManager
from dtypes import View, URLImage

from scenarios.prototype_v0_1 import Prototype_v0_1
from scenarios.prototype_v0_2 import Prototype_v0_2
from scenarios.prototype_v0_2 import Prototype_v0_2_Snapshot_1
from scenarios.prototype_v0_2 import Prototype_v0_2_Snapshot_2

class Szenarien_View:
    def __init__(self):
        print("Szenarien_View init")

        if not 'current_view' in st.session_state:
            st.session_state.current_view = 'main'

        self.page = PageManager(layout="wide")

    # ---------------
    # ! Entry Point
    # ---------------
    def render(self):
        if st.session_state.current_view == 'main':
            self.main_view()
        elif st.session_state.current_view == 'result':
            self.render_result_view()

    def render_result_view(self):
        # ---------------
        # ! Header
        # ---------------
        st.title(f"Szenario {st.session_state.scenario}")

        # ---------------
        # ! Back button
        # ---------------
        st.button(
            label="Zurück",
            help="Zurück zur Szenario Auswahl.",
            on_click=lambda: st.session_state.update(current_view='main'),
        )

        # ---------------
        # ! Run simulation
        # ---------------
        if st.session_state.scenario == 'prototype-v0.1':
            self.simulate_prototype_v0_1()
        elif st.session_state.scenario == 'prototype-v0.2':
            self.simulate_prototype_v0_2()
        elif st.session_state.scenario == 'prototype-v0.2-snapshot-1':
            self.simulate_prototype_v0_2_snapshot_1()
        elif st.session_state.scenario == 'prototype-v0.2-snapshot-2':
            self.simulate_prototype_v0_2_snapshot_2()

    def on_simulate_btn_pressed(self):
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
            'prototype-v0.2-snapshot-1': 'prototype-v0.2-SNAPSHOT-1',
            'prototype-v0.2-snapshot-2': 'prototype-v0.2-SNAPSHOT-2',
            'prototype-v0.2': 'Prototyp v0.2',
            # 'default': "📊 Referenz Szenario (empfohlen)",
            # 'best-case': "☀️ Szenario \"Best Case\"",
            # 'worst-case': "🌧️ Szenario \"Worst Case\"",
            # 'custom': "⚙️ Benuzterdefiniertes Szenario"
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
                    label="Simulation",
                    options=self.scenarios.values(),
                    index=3,
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
                            Der Verbrauch wird mittels eines Faktors in Bezug auf ein Referenzjahr proportional hochskaliert.
                            Die Produktion wird mittels der Ausbauziele im Verhältnis zu der Installierten Leistung im Referenzjahr hochskaliert.
                            Mehr nicht.
                            ''')
                st.caption('''
                           Die Parameter können im Abschnitt "Szenario Parameter" angepasst werden.
                            ''')
            elif param_scenario == self.scenarios.get('prototype-v0.2'):
                st.markdown('''
                            Der Prototyp v0.2 ermöglicht eine genauere Simulation der Produktion,
                            des Verbrauchs und der Speicher des Jahres 2030.
                            Als Speichertechnologie wird eine Hybrid-Lösung simuliert,
                            welche Batteriespeicher nutzt als Kurzzeitspeicher für
                            die Wasserstoffelektrolyse.
                            ''')
                st.caption('''
                           Die Parameter können im Abschnitt "Szenario Parameter" angepasst werden.
                            ''')
            elif param_scenario == self.scenarios.get('prototype-v0.2-snapshot-1'):
                st.warning('This is a SNAPSHOT version.')
                st.caption('''
                           Die Parameter können im Abschnitt "Szenario Parameter" angepasst werden.
                            ''')
            elif param_scenario == self.scenarios.get('prototype-v0.2-snapshot-2'):
                st.warning('This is a SNAPSHOT version.')
                st.caption('''
                           Die Parameter können im Abschnitt "Szenario Parameter" angepasst werden.
                            ''')

            # ---------------
            # ! Simulation Button
            # ---------------
            st.button(
                label="Simulation starten",
                help="Simulate the energy production and consumption for the selected scenario.",
                on_click=self.on_simulate_btn_pressed,
                type="primary",
            )


        # ---------------
        # ! Parameters
        # ---------------

        if param_scenario == self.scenarios.get('custom'):
            self.render_parameter_view()
        elif param_scenario == self.scenarios.get('prototype-v0.1'):
            self.render_prototype_v0_1_view()
        elif param_scenario == self.scenarios.get('prototype-v0.2'):
            self.render_prototype_v0_2_view()
        elif param_scenario == self.scenarios.get('prototype-v0.2-snapshot-1'):
            self.render_prototype_v0_2_snapshot_1_view()
        elif param_scenario == self.scenarios.get('prototype-v0.2-snapshot-2'):
            self.render_prototype_v0_2_snapshot_2_view()

        # ---------------
        # ! Footer
        # ---------------
        self.render_footer_view()

    # ---------------
    # ! Parameter Views
    # ---------------
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

    def render_prototype_v0_2_view(self):
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
            st.divider()
            container_inital_storage = st.container()
            st.divider()
            container_hydrogen_turbine = st.container()

        with cols_params_row0[1]:
            container_reference_year = st.container()
            st.divider()
            container_simulation_limit = st.container()
            st.divider()
            container_skew_factor = st.container()

        with container_consumption:
            st.markdown('#### 🔌 Stromverbrauch')

            st.markdown('''
                        Der Stromverbrauch gibt an, wie viel Strom im Jahr 2030 gesamt verbraucht wird.
                        Dies beinhaltet Netzverluste und Verbrauch der Kraftwerke.
                        Nicht beinhaltet sind Importe und Exporte.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.caption('''
                        Bei dem Stromverbrauch handelt es sich um eine proportionale Skalierung
                        der Verbrauchsprofile aus dem Referenzjahr, welches ebenfalls als Parameter
                        festgelegt werden kann.
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
                    value=650,
                    step=10
                )

        with container_inital_storage:
            st.markdown('#### 🔋 Speicher')

            st.markdown('''
                        Generell soll ein Speichersystem die Überproduktion erneuerbarer Energien
                        über das Jahr hinweg verteilen. Das vorgesehene Speichersystem
                        ist wie folgt strukturiert: Die Überschussproduktion wird zunächst
                        in einen vorgeschalteten idealen Batteriespeicher eingespeist.
                        Daraufhin erfolgt eine Wasserstoffelektrolyse, gefolgt von der
                        Speicherung des erzeugten Wasserstoffs in Kilogramm.
                        Bei Bedarf an Strom aus dem Speicher wird der Wasserstoff mithilfe
                        von Gasturbinen in elektrische Energie umgewandelt.
                        Anschließend wird diese Energie wieder in den idealen Batteriespeicher
                        und zurück ins Netz eingespeist.
                        Der Batteriespeicher dient dazu, schnell (< 15 Minuten)
                        auf kurzfristige Netzänderungen zu reagieren und
                        die An- und Abfahrtszeiten der Turbinen und Elektrolyse auszugleichen.
                        ''')
            with st.expander(label="Wie beeinflussen diese Parameter die Simulation?"):
                st.caption('''
                        Die Beschränkung der zu speichernden Wasserstoffmenge resultiert
                           in einer optimaleren Nutzung des Speichervolumens,
                           führt jedoch gleichzeitig zu einer Erhöhung der Grundlast,
                           da Teile der Überproduktion nunmehr nur noch exportiert werden können.
                           Durch das Ansetzen eines bereits teilweise gefüllten
                           Speichers kann die Grundlast effektiv reduziert werden.
                           Konsequenterweise bedarf es am Ende des Jahres der Rückgabe dieses "Speicherkredits".
                        ''')


            st.markdown('<h5>Initialer Speicher</h5>', unsafe_allow_html=True)
            st.markdown('''
                    Der Initiale Speicher simuliert eine Speicherung
                    an Wasserstoff aus dem Vorjahr (2029).
                    ''')
            st.markdown('''
                    Zu Beginn der Simulation wird die Menge an TWh dem Speicher
                    für die Elektrolyse zur Verfügung gestellt,
                    welcher aus dieser Energiemenge eine Zahl
                    an Kilotonnen Wasserstoff produziert und speichert.
                    Zum Ende des Jahres muss dieser Speicher mindestens wieder
                    gefülllt sein, damit die Simulation
                    erfolgreich ist.
                    ''')

            with st.columns(2, gap='medium')[0]:
                st.session_state.initial_storage = st.number_input(
                    label="Initialer Speicher [TWh]",
                    min_value=0,
                    max_value=100,
                    value=10,
                    step=1
                )

            st.markdown('<h5>Speicher Kapazität</h5>', unsafe_allow_html=True)
            st.markdown('''
                        Die Speicherkapazität definiert die maximale Menge an Wasserstoff,
                        die gespeichert werden kann, unter Berücksichtigung
                        potenzieller Ausbaukapazitäten. Diese Begrenzung zielt darauf ab,
                        die vorhandenen Speicherressourcen effizienter zu nutzen
                        und eine breitere Nutzung des Speichers zu ermöglichen.
                        ''')

            with st.columns(2, gap='medium')[0]:
                st.session_state.storage_cap = st.number_input(
                    label="Speicher Kapazität [kt]",
                    min_value=0,
                    max_value=2000,
                    value=800,
                    step=100
                )

        with container_hydrogen_turbine:
            st.markdown('#### ⚡ H2 Turbinen-Technologie')

            st.markdown('''
                        Die Wasserstoffspeicher speisen den gespeicherten Wasserstoff über Pipelines
                        in die Gaskraftwerke ein. Die Kraftwerke nutzen hybride Gasturbinen,
                        welche von Erdgas auf Wasserstoff wechseln können und ebenfalls
                        mit Mischgas laufen können.
                        ''')
            st.markdown('''
                        Die Simulation nutzt eine virtuelle Gasturbine von General Electric,
                        die 9HA.02 in 2x1 CC Konfiguration mit einer Leistung von 1680 MW.
                        Pro Stunde werden dabei 77,712 Tonnen an Wasserstoff verbrannt.
                        ''')
            st.markdown('''
                        Diese Turbinen können übergangslos von Erdgas auf 100% Wasserstoff
                        wechseln. Nach eigener Aussage von General Electric können
                        die H2-Ready Turbinen innerhalb von 5min von Stillstand
                        auf 100% Leistung hochfahren.
                        Die Neuinstallation einer solcher Anlage kann innerhalb
                        von nur 2 Wochen erfolgen.
                        ''')
            st.markdown('''
                        Quelle: <a href="https://www.ge.com/gas-power/products/gas-turbines">https://www.ge.com/gas-power/products/gas-turbines</a>
                        ''',
                        unsafe_allow_html=True)

            with st.expander('Wie genau funktioniert die 9HA.02 in 2x1 CC Konfiguration?'):
                View.image(
                    URLImage(
                        url='https://www.ge.com/content/dam/gepower-new/global/en_US/images/gas-new-site/products/gas-turbines/9ha/hero-9ha-gas-turbine.png',
                        alt='https://www.ge.com/gas-power/products/gas-turbines'
                    )
                )
                st.markdown('''
                            The General Electric 9HA.02 gas turbine is a high-efficiency, heavy-duty turbine used in combined cycle power plants. In a 2x1 combined cycle (CC) configuration, two gas turbines are combined with one steam turbine. Here's a basic explanation of how this configuration works:

                            1. **Gas Turbines (2 units - 9HA.02):**
                            - The two GE 9HA.02 gas turbines operate in parallel to generate electricity. They burn natural gas or another fuel to produce high-temperature exhaust gases.

                            2. **Heat Recovery Steam Generators (HRSGs - 2 units):**
                            - The hot exhaust gases from each 9HA.02 gas turbine pass through a Heat Recovery Steam Generator (HRSG). The HRSG extracts heat from the exhaust gases to generate steam.

                            3. **Steam Turbine (1 unit):**
                            - The steam generated in the HRSGs is directed to a steam turbine. The steam turbine converts the thermal energy of the steam into additional mechanical power, which is used to generate more electricity.

                            4. **Combined Cycle Operation:**
                            - The combination of gas turbine and steam turbine operation in a 2x1 configuration maximizes the overall efficiency of the power plant. The exhaust heat from the gas turbines, which would otherwise be wasted, is utilized to generate additional electricity through the steam turbine.

                            The 2x1 CC configuration is a common design for large-scale combined cycle power plants, offering high efficiency and improved overall performance compared to single-cycle configurations.

                            For more detailed and specific information about the GE 9HA.02 gas turbine in a 2x1 CC configuration, you may want to refer to GE's technical documentation, performance specifications, or contact GE's technical support for the most accurate and up-to-date details.
                            ''')

            with st.expander('Wieso wird die General Electric Turbine für die Simulation genutzt?'):
                st.todo()

        with container_reference_year:
            st.markdown('''
                        #### 📅 Referenzjahr
                        ''')

            st.markdown('''
                        Der Parameter "Referenzjahr" ermöglicht die Auswahl eines Jahres
                        im Zeitraum von 2015 bis 2022. Er bezieht sich auf
                        reale historische Daten zur Stromproduktion und -verbrauch.
                        Diese dienen als Referenzgrundlage zur Erstellung einer Prognose bzw.
                        Hochrechnung bezüglich der zukünftigen Produktion und des Verbrauchs.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.caption('''
                            Durch die Anwendung des Parameters "Gesamtverbrauch 2030" in Verbindung
                           mit dem tatsächlichen Gesamtverbrauch aus dem Referenzjahr wird ein
                           Skalierungsfaktor ermittelt. Dieser Faktor ermöglicht die Hochskalierung
                           des aktuellen Verbrauchs des Referenzjahres auf das Jahr 2030.
                           Parallel dazu wird unter Berücksichtigung der Ausbauziele für die
                           installierte Leistung im Jahr 2030 und der installierten Leistung
                           des Referenzjahres ein weiterer Skalierungsfaktor erstellt.
                           Dieser wird auf die Erzeugungswerte der erneuerbaren Energien angewendet.
                           ''')

            st.session_state.reference_year = st.selectbox(
                label='Referenzjahr',
                options=[*range(2015, 2023)],
                index=6,
                help="Das Referenzjahr wird als Basis für die Simulation verwendet."
            )

        with container_simulation_limit:
            st.markdown('#### ❌ Simulationsiterationen')

            st.todo('''
                        Der Initiale Speicher simuliert einen idealen Energiespeicher,
                        welcher bei Bedarf mit unendlicher Leistung Energie bereitstellen kann.
                        Dieser Speicher kann nicht geladen werden.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.todo()

            with st.columns(2, gap='medium')[0]:
                st.session_state.iteration_limit = st.number_input(
                    label="Iterationslimit",
                    min_value=1,
                    max_value=400,
                    value=200,
                    step=1
                )

            with container_skew_factor:
                st.markdown('#### 📈 Skew Factor')

                st.markdown('''
                            Der Skew-Faktor ermöglicht eine effiziente Verteilung der Grundlast,
                            wodurch eine Reduzierung während ertragreicher Sommermonate
                            und eine Erhöhung in den winterlichen Perioden realisiert werden kann.
                            Dabei bleibt die Gesamtgrundlastdeckung unverändert.
                            ''')

                with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                    st.todo()

                with st.columns(2, gap='medium')[0]:
                    st.session_state.skew_factor = st.number_input(
                        label="Sommer Faktor",
                        min_value=0.1,
                        max_value=2.0,
                        value=0.5,
                        step=0.1
                    )

                if st.session_state.skew_factor:
                    SUMMER_FACTOR = st.session_state.skew_factor
                    WINTER_FACTOR = 1.0

                    x_W = lambda S, W, x_S: (1 - ((S/(S+W)) * x_S)) / (W/(S+W))

                    WINTER_FACTOR = x_W(7, 5, SUMMER_FACTOR)

                    with (cols := st.columns(2, gap='medium'))[0]:
                            st.code(f'Sommer Faktor: {round(SUMMER_FACTOR, 2)}')
                    with cols[1]:
                            st.code(f'Winter Faktor: {round(WINTER_FACTOR, 2)}')

                    data_array = np.zeros(35040, dtype=float)
                    data_array[:5664] = WINTER_FACTOR

                    ramp = np.linspace(WINTER_FACTOR, SUMMER_FACTOR, 2976)
                    data_array[5664:5664+2976] = ramp

                    data_array[5664+2976:26_112] = SUMMER_FACTOR

                    ramp = np.linspace(SUMMER_FACTOR, WINTER_FACTOR, 2976)
                    data_array[26_112:26_112+2976] = ramp

                    data_array[26_112+2976:] = WINTER_FACTOR

                    date_range = pd.date_range(
                            start='2030-01-01 00:00',
                            end='2030-12-31 23:59',
                            freq='15min',
                        )

                    skew_factor_df = pd.DataFrame({
                        'date': date_range,
                        'skew-factor': data_array
                    })

                    st.altair_chart(alt.Chart(skew_factor_df).mark_area().encode(
                        x=alt.X(
                            'date',
                            axis=alt.Axis(title='Datum')
                        ),
                        y=alt.Y(
                        'skew-factor',
                        axis=alt.Axis(title='Skew Factor'),
                        scale=alt.Scale(domain=[0.0, 2.0])
                        ),
                        color=alt.value('#6D5F6D')
                    ).properties(
                        height=300,
                    ),
                    use_container_width=True)

    def render_prototype_v0_2_snapshot_1_view(self):
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
            container_inital_storage = st.container()

        with cols_params_row0[1]:
            container_reference_year = st.container()
            container_simulation_limit = st.container()

        with container_consumption:
            st.markdown('#### 🔌 Stromverbrauch')

            st.markdown('''
                        Der Stromverbrauch gibt an, wie viel Strom im Jahr 2030 gesamt verbraucht wird.
                        Dies beinhaltet Netzverluste und Verbrauch der Kraftwerke.
                        Nicht beinhaltet sind Importe und Exporte.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.caption('''
                        Bei dem Stromverbrauch handelt es sich um eine proportionale Skalierung
                        der Verbrauchsprofile aus dem Referenzjahr, welches ebenfalls als Parameter
                        festgelegt werden kann.
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
                    value=650,
                    step=10
                )

        with container_inital_storage:
            st.markdown('#### 🔋 Initialer Speicher')

            st.markdown('''
                        Der Initiale Speicher simuliert einen idealen Energiespeicher,
                        welcher bei Bedarf mit unendlicher Leistung Energie bereitstellen kann.
                        Dieser Speicher kann nicht geladen werden.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.caption('''
                        Der Initiale Speicher ermöglicht der Simulation in Defizitphasen
                        Strom aus dem Speicher zu beziehen.
                        Nicht berechnet werden Wirkungsgerade oder realistische Speichermedien.
                        Der Strom wird sofort aus dem Speicher bezogen
                        und der Speicher hat keine Verluste über längere Zeit.
                        ''')

            cols_initial_storage_simple = st.columns(2, gap='medium')

            with cols_initial_storage_simple[0]:
                st.session_state.initial_storage = st.number_input(
                    label="Initialer Speicher [TWh]",
                    min_value=0,
                    max_value=100,
                    value=10,
                    step=1
                )

        with container_reference_year:
            st.markdown('''
                        #### 📅 Referenzjahr
                        ''')

            st.todo()
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                # st.caption()
                st.todo()

            st.session_state.reference_year = st.selectbox(
                label='Referenzjahr',
                options=[*range(2015, 2023)],
                index=6,
                help="Das Referenzjahr wird als Basis für die Simulation verwendet."
            )

        with container_simulation_limit:
            st.markdown('#### ❌ Simulationsiterationen')

            st.todo('''
                        Der Initiale Speicher simuliert einen idealen Energiespeicher,
                        welcher bei Bedarf mit unendlicher Leistung Energie bereitstellen kann.
                        Dieser Speicher kann nicht geladen werden.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.todo()

            with st.columns(2, gap='medium')[0]:
                st.session_state.iteration_limit = st.number_input(
                    label="Iterationslimit",
                    min_value=1,
                    max_value=400,
                    value=200,
                    step=1
                )

    def render_prototype_v0_2_snapshot_2_view(self):
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
            container_inital_storage = st.container()

        with cols_params_row0[1]:
            container_reference_year = st.container()
            container_simulation_limit = st.container()

        with container_consumption:
            st.markdown('#### 🔌 Stromverbrauch')

            st.markdown('''
                        Der Stromverbrauch gibt an, wie viel Strom im Jahr 2030 gesamt verbraucht wird.
                        Dies beinhaltet Netzverluste und Verbrauch der Kraftwerke.
                        Nicht beinhaltet sind Importe und Exporte.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.caption('''
                        Bei dem Stromverbrauch handelt es sich um eine proportionale Skalierung
                        der Verbrauchsprofile aus dem Referenzjahr, welches ebenfalls als Parameter
                        festgelegt werden kann.
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
                    value=650,
                    step=10
                )

        with container_inital_storage:
            st.markdown('#### 🔋 Initialer Speicher')

            st.markdown('''
                        Der Initiale Speicher simuliert einen idealen Energiespeicher,
                        welcher bei Bedarf mit unendlicher Leistung Energie bereitstellen kann.
                        Dieser Speicher kann nicht geladen werden.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.caption('''
                        Der Initiale Speicher ermöglicht der Simulation in Defizitphasen
                        Strom aus dem Speicher zu beziehen.
                        Nicht berechnet werden Wirkungsgerade oder realistische Speichermedien.
                        Der Strom wird sofort aus dem Speicher bezogen
                        und der Speicher hat keine Verluste über längere Zeit.
                        ''')

            cols_initial_storage_simple = st.columns(2, gap='medium')

            with cols_initial_storage_simple[0]:
                st.session_state.initial_storage = st.number_input(
                    label="Initialer Speicher [TWh]",
                    min_value=0,
                    max_value=100,
                    value=10,
                    step=1
                )

        with container_reference_year:
            st.markdown('''
                        #### 📅 Referenzjahr
                        ''')

            st.todo()
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                # st.caption()
                st.todo()

            st.session_state.reference_year = st.selectbox(
                label='Referenzjahr',
                options=[*range(2015, 2023)],
                index=6,
                help="Das Referenzjahr wird als Basis für die Simulation verwendet."
            )

        with container_simulation_limit:
            st.markdown('#### ❌ Simulationsiterationen')

            st.todo('''
                        Der Initiale Speicher simuliert einen idealen Energiespeicher,
                        welcher bei Bedarf mit unendlicher Leistung Energie bereitstellen kann.
                        Dieser Speicher kann nicht geladen werden.
                        ''')
            with st.expander(label="Wie beeinflusst dieser Parameter die Simulation?"):
                st.todo()

            with st.columns(2, gap='medium')[0]:
                st.session_state.iteration_limit = st.number_input(
                    label="Iterationslimit",
                    min_value=1,
                    max_value=400,
                    value=200,
                    step=1
                )


    # ---------------
    # ! Simulations
    # ---------------
    def simulate_prototype_v0_1(self):
        prototype = Prototype_v0_1(self)
        prototype.simulate()

    def simulate_prototype_v0_2(self):
        prototype = Prototype_v0_2(self)
        prototype.simulate()

    def simulate_prototype_v0_2_snapshot_1(self):
        prototype = Prototype_v0_2_Snapshot_1(self)
        prototype.simulate()

    def simulate_prototype_v0_2_snapshot_2(self):
        prototype = Prototype_v0_2_Snapshot_2(self)
        prototype.simulate()


if __name__ == "__main__":
    view = Szenarien_View()
    view.render()
