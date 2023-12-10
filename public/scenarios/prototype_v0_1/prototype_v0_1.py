import datetime as dt
import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
from dtypes import URLImage, View

from data_manager.data_manager import DataArray


class Prototype_v0_1:
    def __init__(self, view):
        self.view = view

    def simulate(self):
        # ---------------
        # ! Simulate
        # ---------------

        data = self.view.page.get_data()


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
        production_base_load_2030 = [70 * 1_000_000_000_000 / data_reference_year.size for d in data_reference_year]

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
            'Base Load': np.copy(production_base_load_2030) / 1_000_000_000,
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
                            domain=['PV', 'Wind Offshore', 'Wind Onshore', 'Biomass', 'Hydro', 'Base Load'],
                            range=['#ffb908', '#0898ff', '#3908ff', '#80A89C', '#53A6E4', '#000000', '#ff0000', '#00ff00'],
                        ),
                    )
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
                            range=['#ffb908', '#0898ff', '#3908ff', '#80A89C', '#53A6E4', '#000000', '#ff0000', '#00ff00'],
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
            if data_2030[i] * 0.8 <= production_renewables_2030[i]:
                surplus_80 += 1

            if data_2030[i] * 0.9 <= production_renewables_2030[i]:
                surplus_90 += 1

            if data_2030[i] <= production_renewables_2030[i]:
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


        # Count intervals with n percent coverage
        _gcp: int = 0

        for i in range(len(production_renewables_2030)):
            p: float = production_renewables_2030[i] + production_base_load_2030[i]
            c: float = data_2030[i]
            try:
                r: int   = round((p / c) * 100)
            except ZeroDivisionError:
                r: int   = 0
                # Convert beginning of selected year to datetime
                ts = dt.datetime(st.session_state.reference_year, 1, 1, 0, 0).timestamp()
                ts += i * 15 * 60
                print(f'ZeroDivisionError at {ts}, {p}, {c}, {r}')

            _gcp = r if r >= _gcp else _gcp

        # Array storing distribution
        _gcp_dist = np.zeros(_gcp + 1, dtype=int)

        for i in range(len(production_renewables_2030)):
            p: float = production_renewables_2030[i] + production_base_load_2030[i]
            c: float = data_2030[i]
            try:
                r: int   = round((p / c) * 100)
            except ZeroDivisionError:
                r: int   = 0
                print(f'ZeroDivisionError at {i}, {p}, {c}, {r}')

            _gcp_dist[r] += 1

        # Parse to pd.DataFrame
        _gcp_dist_df = pd.DataFrame({
            'x': np.arange(0, _gcp + 1, 1),
            'y': _gcp_dist,
        })

        # Send to View
        st.altair_chart(
            altair_chart=alt.Chart(
                data=_gcp_dist_df,
            ).mark_bar().encode(
                x=alt.X(
                    'x:O',
                    axis=alt.Axis(title='Prozentuale Deckung'),
                ),
                y=alt.Y(
                    'y:Q',
                    axis=alt.Axis(title='Anzahl an Intervallen'),
                ),
                color=alt.condition(
                    alt.datum.x >= 100,
                    alt.value('#00FF00'),
                    alt.value('#FF0000')
                )
            ),
            use_container_width=True,
        )

        st.write(f'GCP: {_gcp}')
        st.write(f'Count: {_gcp_dist[_gcp]}')

        net_balance = np.zeros(len(data_2030))

        for i in range(len(net_balance)):
            p: float = production_renewables_2030[i] + production_base_load_2030[i]
            c: float = data_2030[i]
            d: float = p - c

            net_balance[i] = d

        cummulative_net_balance = np.copy(net_balance)

        # Parse to pd.DataFrame
        _net_balance_df = pd.DataFrame({
            'Date': x_range,
            'y': net_balance / 1_000_000_000,
        })

        _cummulative_net_balance_df = pd.DataFrame({
            'Date': x_range,
            'y': cummulative_net_balance,
        })

        _net_balance_df['Date'] = pd.to_datetime(_net_balance_df['Date'])
        _net_balance_df['Date'] = _net_balance_df['Date'].dt.strftime('%Y-%m-%d')

        _cummulative_net_balance_df['Date'] = pd.to_datetime(_cummulative_net_balance_df['Date'])
        _cummulative_net_balance_df['Date'] = _cummulative_net_balance_df['Date'].dt.strftime('%Y-%m-%d')

        _cummulative_net_balance_df = _cummulative_net_balance_df.groupby(['Date']).sum().reset_index()

        _cummulative_net_balance_df = pd.melt(_cummulative_net_balance_df, id_vars=["Date"], var_name="Load Source", value_name="Load")

        # Generate a cummulative sum
        _cummulative_net_balance_df['Load'] = _cummulative_net_balance_df['Load'].cumsum()
        _cummulative_net_balance_df['Load'] /= 1_000_000_000_000

        # Send to View
        st.altair_chart(
            altair_chart=alt.Chart(
                data=_net_balance_df,
            ).mark_bar().encode(
                x=alt.X(
                    'Date:O',
                    axis=alt.Axis(title='Datum [M]')
                ),
                y=alt.Y(
                    'y:Q',
                    axis=alt.Axis(title='Net Balance [GWh]'),
                ),
                color=alt.condition(
                    alt.datum.y >= 0,
                    alt.value('#00FF00'),
                    alt.value('#FF0000')
                )
            ),
            use_container_width=True,
        )

        color = '#00FF00' if _cummulative_net_balance_df['Load'].iloc[-1] >= 0 else '#FF0000'

        pos_chart = alt.Chart(_cummulative_net_balance_df).mark_area(color='#00FF00').encode(
            x=alt.X(
                'Date:O',
                axis=alt.Axis(title='Datum [M]')
            ),
            y=alt.Y(
                'Load:Q',
                axis=alt.Axis(title='Net Balance [TWh]'),
                impute=alt.ImputeParams(value=0),
            ),
        ).transform_filter(
            alt.datum.Load >= 0
        )

        neg_chart = alt.Chart(_cummulative_net_balance_df).mark_area(color='#FF0000').encode(
            x=alt.X(
                'Date:O',
                axis=alt.Axis(title='Datum [M]')
            ),
            y=alt.Y(
                'Load:Q',
                axis=alt.Axis(title='Net Balance [TWh]'),
                impute=alt.ImputeParams(value=0),
            ),
        ).transform_filter(
            alt.datum.Load < 0
        )



        st.altair_chart(
            altair_chart=alt.layer(
                pos_chart,
                neg_chart,
            ).resolve_scale(
            ),
            use_container_width=True,
        )

        st.altair_chart(alt.Chart(_cummulative_net_balance_df).transform_calculate(
                negative='datum.Load < 0'
            ).mark_area().encode(
                x='Date:O',
                y=alt.Y('Load:Q', impute={'value': 0}),
                color=alt.Color('negative:N', scale=alt.Scale(domain=[False, True], range=['#00FF00', '#FF0000']), legend=None),
                tooltip=['Date', 'Load'],
            ).properties(
                title='Net Balance'
            ),
            use_container_width=True,
        )
