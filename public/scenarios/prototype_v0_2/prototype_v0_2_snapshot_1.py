import calendar
import datetime as dt
from pytz import timezone

import numpy as np
from numpy.typing import NDArray
import pandas as pd
import streamlit as st
import altair as alt

from dtypes import Unit

from data_manager.data_manager import Collections, Collection, Data, DataArray


class Prototype_v0_2_Snapshot_1:
    def __init__(self, view):
        self.view = view
        self.params = {}

        try:
            self.params['reference_year'] = st.session_state.reference_year
            self.params['load'] = st.session_state.total_consumption_2030
            self.params['initial-storage'] = st.session_state.initial_storage
            self.params['iteration-limit'] = st.session_state.iteration_limit
        except:
            st.error('Could not parse parameters.')
            return

    def simulate(self):
        # Get data
        data: Collections = self.view.page.get_data()


        # Initialize constants
        POWER_TARGET_PV     : int = Unit.GW(215)
        POWER_TARGET_WINDOFF: int = Unit.GW(30)
        POWER_TARGET_WINDON : int = Unit.GW(115)
        POWER_TARGET_BIOMASS: int = Unit.MW(8_332)
        POWER_TARGET_HYDRO  : int = Unit.MW(4_253)

        LOAD_TARGET         : int = Unit.TWh(self.params['load'])


        # Get power data of reference year
        _d: Data = data.smard.get_last_of_year(self.params['reference_year'])

        POWER_CURRENT_PV     : int = _d.power.pv
        POWER_CURRENT_WINDOFF: int = _d.power.wind_offshore
        POWER_CURRENT_WINDON : int = _d.power.wind_onshore
        POWER_CURRENT_BIOMASS: int = _d.power.biomass
        POWER_CURRENT_HYDRO  : int = _d.power.hydro

        _data_year: DataArray      = data.smard.get_year(self.params['reference_year'])
        LOAD_CURRENT         : int = sum([d.consumption.load for d in _data_year])

        print(f'LOAD_CURRENT: {LOAD_CURRENT}')


        # Calculate power factors
        POWER_FACTOR_PV     : float = POWER_TARGET_PV      / POWER_CURRENT_PV
        POWER_FACTOR_WINDOFF: float = POWER_TARGET_WINDOFF / POWER_CURRENT_WINDOFF
        POWER_FACTOR_WINDON : float = POWER_TARGET_WINDON  / POWER_CURRENT_WINDON
        POWER_FACTOR_BIOMASS: float = POWER_TARGET_BIOMASS / POWER_CURRENT_BIOMASS
        POWER_FACTOR_HYDRO  : float = POWER_TARGET_HYDRO   / POWER_CURRENT_HYDRO

        LOAD_FACTOR         : float = LOAD_TARGET          / LOAD_CURRENT

        INITIAL_BALANCE: int = Unit.TWh(self.params['initial-storage'])
        RESERVE_BALANCE: int = Unit.TWh(1)


        st.warning('This is a SNAPSHOT version. Bugs are expected.')


        # ----------------------------------------
        # Create a Collection for the year 2030
        # ----------------------------------------

        # First, we use a pandas date_range
        date_range = pd.date_range(
            start=dt.datetime(2030, 1, 1, 0, 0),
            end=dt.datetime(2030, 12, 31, 23, 45),
            freq='15min',
            tz='Europe/Berlin'
        )

        # Create a collection for the year 2030
        collection_2030 = Collection()
        collection_2030.set_name('2030')

        # Create the data array for the year 2030
        _data = np.empty(len(date_range), dtype=Data)

        for i, d in enumerate(date_range):
            _data[i] = Data(
                start=d.to_pydatetime(),
            )

        # Set the data array to the collection
        collection_2030.set(_data)


        # ----------------------------------------
        # Compute values for the year 2030
        # ----------------------------------------

        def _create_generator(data: DataArray):
            for d in data:
                yield d

        reference_data: DataArray = data.smard.get_year(self.params['reference_year'])

        reference_data = _create_generator(reference_data)

        # Check for leap year
        ref_is_leap = calendar.isleap(self.params['reference_year'])

        if ref_is_leap:
            st.warning('Detected leap year. Skipping 29th of February.')

        # Start copying values
        copying_progress = st.progress(
            value=0,
            text='Copying values...'
        )

        # Copy values
        for i, d in enumerate(collection_2030):
            _data = next(reference_data)

            if ref_is_leap:
                while d.start.month == 2 and d.start.day == 29:
                    _data = next(reference_data)

            d.production                = Data.Production()
            d.production.pv             = _data.production.pv
            d.production.pv            *= POWER_FACTOR_PV
            d.production.wind_offshore  = _data.production.wind_offshore
            d.production.wind_offshore *= POWER_FACTOR_WINDOFF
            d.production.wind_onshore   = _data.production.wind_onshore
            d.production.wind_onshore  *= POWER_FACTOR_WINDON
            d.production.biomass        = _data.production.biomass
            d.production.biomass       *= POWER_FACTOR_BIOMASS
            d.production.hydro          = _data.production.hydro
            d.production.hydro         *= POWER_FACTOR_HYDRO

            d.power                     = _data.power
            d.power.pv                  = POWER_FACTOR_PV
            d.power.wind_offshore       = POWER_FACTOR_WINDOFF
            d.power.wind_onshore        = POWER_FACTOR_WINDON
            d.power.biomass             = POWER_FACTOR_BIOMASS
            d.power.hydro               = POWER_FACTOR_HYDRO

            d.consumption               = Data.Consumption()
            d.consumption.load          = _data.consumption.load * LOAD_FACTOR

            copying_progress.progress(i / collection_2030.get_length())

        copying_progress.progress(1.0)

        # ----------------------------------------
        # Calculate the deficit
        # ----------------------------------------
        total_production = sum(d.production.total for d in collection_2030)
        total_consumption = sum(d.consumption.load for d in collection_2030)
        deficit = abs(total_consumption - total_production)

        st.debug(f'Total Energy Production: {round(total_production / 1_000_000_000_000, 2)} TWh')
        st.debug(f'Total Energy Consumption: {round(total_consumption / 1_000_000_000_000, 2)} TWh')
        st.debug(f'Deficit: {round(deficit / 1_000_000_000_000, 2)} TWh')

        renewable_share = total_production / total_consumption
        st.debug(f'Renewable Share: {round(renewable_share * 100, 2)} %')

        for i, d in enumerate(collection_2030):
            _gas = deficit / collection_2030.get_length()
            collection_2030.data[i].production.gas = _gas

        st.success('Initial calculations completed!')

        # ----------------------------------------
        # Calculate the balance
        # ----------------------------------------
        net_balance: NDArray   = np.zeros(collection_2030.get_length(), dtype=int)

        # Start iterations
        st.warning('Starting iterations...')
        iterations = 0
        initial_balance = INITIAL_BALANCE

        simulation_stop = False

        total_balance = None

        storage_balance: NDArray   = np.zeros(collection_2030.get_length(), dtype=int)

        simulation_successfull = False

        with st.spinner('Simulating...'):
            while not simulation_stop:
                iterations += 1

                print(f'----------------------------------------')
                print(f'iteration: {iterations}')
                print(f'----------------------------------------')

                # ----------------------------------------
                # Calculate the net balance
                # ----------------------------------------
                net_balance: NDArray   = np.zeros(collection_2030.get_length(), dtype=int)
                balance_is_negative = False

                initial_balance = INITIAL_BALANCE

                # ----------------------------------------
                # Iterate over the year 2030
                # ----------------------------------------
                for i, d in enumerate(collection_2030):
                    d: Data = d
                    net_balance[i] = d.production.total - d.consumption.load

                    # ----------------------------------------
                    # Get energy from the initial balance
                    # ----------------------------------------
                    if net_balance[i] < 0:
                        initial_balance -= abs(net_balance[i])

                        # ----------------------------------------
                        # If there is no more energy in the initial balance
                        # we try again
                        # ----------------------------------------
                        if initial_balance < 0:
                            balance_is_negative = True
                            break

                    storage_balance[i] = initial_balance

                # ----------------------------------------
                # Calculate the total balance (cumulative)
                # ----------------------------------------
                total_balance: NDArray = net_balance.cumsum()

                total_balance += initial_balance

                # ----------------------------------------
                # Iterate over the year 2030
                # and stop if the balance is negative
                # ----------------------------------------

                if balance_is_negative:
                    for i in range(collection_2030.get_length()):
                        collection_2030.data[i].production.gas *= 1.01
                else:
                    simulation_stop = True
                    simulation_successfull = True

                if iterations > self.params['iteration-limit']:
                    simulation_stop = True

        if not simulation_successfull:
            st.warning('Maximum number of iterations reached.')
            st.error('Simulation failed!')
        else:
            st.success(f'Simulation succeeded after {iterations} iterations.')

        st.subheader('Results')

        total_gas = sum(d.production.gas for d in collection_2030)
        _base_load_coverage = round(total_gas / 1_000_000_000_000, 2)
        _per_quarter = round(_base_load_coverage * 1_000 / collection_2030.get_length(), 2)
        st.code(f'Required Base Load Coverage = {_base_load_coverage} TWh - {_per_quarter} GWh/quarter - Power: {_per_quarter * 4} GW')

        base_load_overshoot = total_gas / deficit
        st.code(f'Base Load Overproduction = {round(base_load_overshoot * 100, 2)} %')

        base_load_share = round(total_gas / total_consumption * 100, 2)

        if base_load_share >= 30:
            st.error(f'Base Load Share (Consumption) = {base_load_share} %', icon='⚠️')
        elif base_load_share >= 20:
            st.warning(f'Base Load Share (Consumption) = {base_load_share} %', icon='⚠️')
        else:
            st.code(f'Base Load Share (Consumption) = {base_load_share} %')


        # ----------------------------------------
        # Create a chart
        # ----------------------------------------

        production_base_load     = [d.production.gas for d in collection_2030]
        production_pv            = [d.production.pv for d in collection_2030]
        production_wind_offshore = [d.production.wind_offshore for d in collection_2030]
        production_wind_onshore  = [d.production.wind_onshore for d in collection_2030]
        production_biomass       = [d.production.biomass for d in collection_2030]
        production_hydro         = [d.production.hydro for d in collection_2030]

        consumption              = [d.consumption.load for d in collection_2030]

        plot_production_df = pd.DataFrame({
            'Date': date_range,
            '0 Fossil Base Load Coverage': np.copy(production_base_load) / 1_000_000_000,
            '1 Biomass': np.copy(production_biomass) / 1_000_000_000,
            '2 Hydro': np.copy(production_hydro) / 1_000_000_000,
            '3 Wind Offshore': np.copy(production_wind_offshore) / 1_000_000_000,
            '4 Wind Onshore': np.copy(production_wind_onshore) / 1_000_000_000,
            '5 PV': np.copy(production_pv) / 1_000_000_000,
        })

        plot_consumption_df = pd.DataFrame({
            'Date': date_range,
            'Consumption': np.copy(consumption) / 1_000_000_000,
        })

        domain_ = plot_production_df.columns.tolist()
        domain_.remove('Date')
        domain_.append('Consumption')

        plot_production_df['Date']  = pd.to_datetime(plot_production_df['Date'])
        plot_production_df['Date']  = plot_production_df['Date'].dt.strftime('%Y-%m-%d')
        plot_production_df          = plot_production_df.groupby(['Date']).sum().reset_index()

        plot_consumption_df['Date'] = pd.to_datetime(plot_consumption_df['Date'])
        plot_consumption_df['Date'] = plot_consumption_df['Date'].dt.strftime('%Y-%m-%d')
        plot_consumption_df         = plot_consumption_df.groupby(['Date']).sum().reset_index()

        plot_production_df          = pd.melt(plot_production_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")
        plot_consumption_df         = pd.melt(plot_consumption_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")

        clr_wind_offshore      = '#3454D1'
        clr_wind_onshore       = '#17B890'
        clr_pv                 = '#ffc300'
        clr_hydro              = '#63D2FF'
        clr_biomass            = '#7DDF64'
        clr_charcoal           = '#8A6552'
        clr_coal               = '#CDD4DF'
        clr_gas                = '#FFE0B5'
        clr_other_conventional = '#6D5F6D'
        clr_nuclear            = '#0CCA4A'
        clr_fossil_fuels       = '#6D5F6D'

        # Match the domain_ with the colors
        range_ = [
            clr_fossil_fuels,
            clr_biomass,
            clr_hydro,
            clr_wind_offshore,
            clr_wind_onshore,
            clr_pv,
            clr_gas,
            '#FF0000'
        ]

        scale_ = alt.Scale(
            domain=domain_,
            range=range_,
        )

        st.altair_chart(
            altair_chart=alt.layer(
                alt.Chart(
                    data=plot_production_df
                ).mark_area().encode(
                    x=alt.X(
                        'Date:O',
                        axis=alt.Axis(title='Datum [M]')
                    ),
                    y=alt.Y(
                        'Energy Value:Q',
                        axis=alt.Axis(title=f'Erzeugung [GWh]'),
                        scale=alt.Scale(domain=[0, 4_500])
                    ),
                    color=alt.Color(
                        'Energy_Source:N',
                        legend=alt.Legend(title='Energiequelle'),
                        scale=scale_,
                    ),
                    order=alt.Order(
                        'Energy_Source:N',
                        sort='ascending'
                    ),
                ),
                alt.Chart(
                    data=plot_consumption_df
                ).mark_line().encode(
                    x=alt.X(
                        'Date:O',
                        axis=alt.Axis(title='Datum [M]')
                    ),
                    y=alt.Y(
                        'Energy Value:Q',
                        axis=alt.Axis(title=f'Verbrauch [GWh]'),
                        scale=alt.Scale(domain=[0, 4_500])
                    ),
                    color=alt.value('#FF0000'),
                    order=alt.Order(
                        'Energy_Source:N',
                        sort='ascending'
                    ),
                )
            ).resolve_scale(
                y='independent'
            ).properties(
                title='Erzeugung und Gesamtverbrauch'
            ),
            use_container_width=True,
        )


        # ----------------------------------------
        # Plot total balance
        # ----------------------------------------

        plot_total_balance_df = pd.DataFrame({
            'Date': date_range,
            # 'Total Balance': np.copy(total_balance) / 1_000_000_000_000,
            'Storage Balance': np.copy(storage_balance) / 1_000_000_000_000,
        })

        plot_total_balance_df['Date'] = pd.to_datetime(plot_total_balance_df['Date'])
        plot_total_balance_df['Date'] = plot_total_balance_df['Date'].dt.strftime('%Y-%m-%d')
        plot_total_balance_df = plot_total_balance_df.groupby(['Date']).max().reset_index()

        plot_total_balance_df         = pd.melt(plot_total_balance_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")

        st.altair_chart(
            altair_chart=alt.Chart(
                data=plot_total_balance_df
            ).mark_line().encode(
                x=alt.X(
                    'Date:O',
                    axis=alt.Axis(title='Datum [M]')
                ),
                y=alt.Y(
                    'Energy Value:Q',
                    axis=alt.Axis(title=f'Energie [TWh]'),
                    # scale=alt.Scale(domain=[0, 100])
                ),
                color=alt.Color(
                    'Energy_Source:N',
                    legend=alt.Legend(title='Energiequelle'),
                    scale=alt.Scale(
                        # domain=['Total Balance', 'Storage Balance'],
                        # range=['#FF0000', '#000000']
                        domain=['Storage Balance'],
                        range=['#000000']
                    )
                ),
                order=alt.Order(
                    'Energy_Source:N',
                    sort='ascending'
                ),
            ).properties(
                title='Initialer Speicher Gesamtenergie'
            ),
            use_container_width=True,
        )

        # ----------------------------------------
        # Plot selectable day
        # ----------------------------------------

        container_plot_day = st.container()
        container_plot_day.header('Tagesansicht')

        selected_date: dt.date = container_plot_day.date_input(
            label='Select a date',
            min_value=dt.datetime(2030, 1, 1),
            max_value=dt.datetime(2030, 12, 31),
            value=dt.datetime(2030, 1, 1),
            format='DD.MM.YYYY',
        )

        container_plot_day_cols = container_plot_day.columns(2, gap='medium')

        selected_date = dt.datetime(selected_date.year, selected_date.month, selected_date.day, 0, 0)

        selected_date = timezone('Europe/Berlin').localize(selected_date)

        selected_data: DataArray = collection_2030.get_range(selected_date, selected_date + dt.timedelta(days=1) - dt.timedelta(minutes=15))

        # We now want to use the previously generated data and plot the same chart again
        # but with a different resolution. The year plots above are on a day resolution
        # and we want to plot the data on a 15 minute resolution.

        production_base_load     = [d.production.gas for d in selected_data]
        production_pv            = [d.production.pv for d in selected_data]
        production_wind_offshore = [d.production.wind_offshore for d in selected_data]
        production_wind_onshore  = [d.production.wind_onshore for d in selected_data]
        production_biomass       = [d.production.biomass for d in selected_data]
        production_hydro         = [d.production.hydro for d in selected_data]

        consumption              = [d.consumption.load for d in selected_data]

        date_range_day = pd.date_range(
            start=dt.datetime(selected_date.year, selected_date.month, selected_date.day, 0, 0),
            end=dt.datetime(selected_date.year, selected_date.month, selected_date.day, 23, 45),
            freq='15min',
            tz='Europe/Berlin'
        )

        st.debug(f'Data: {selected_data.size}')
        st.debug(f'Range: {len(date_range_day)}')

        plot_day_production_df = pd.DataFrame({
            'Date': date_range_day,
            '0 Fossil Base Load Coverage': np.copy(production_base_load) / 1_000_000_000,
            '1 Biomass': np.copy(production_biomass) / 1_000_000_000,
            '2 Hydro': np.copy(production_hydro) / 1_000_000_000,
            '3 Wind Offshore': np.copy(production_wind_offshore) / 1_000_000_000,
            '4 Wind Onshore': np.copy(production_wind_onshore) / 1_000_000_000,
            '5 PV': np.copy(production_pv) / 1_000_000_000,
        })

        plot_day_consumption_df = pd.DataFrame({
            'Date': date_range_day,
            'Consumption': np.copy(consumption) / 1_000_000_000,
        })

        domain_ = plot_day_production_df.columns.tolist()
        domain_.remove('Date')
        domain_.append('Consumption')

        plot_day_production_df['Date']  = pd.to_datetime(plot_day_production_df['Date'])
        plot_day_production_df['Date']  = plot_day_production_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
        # plot_day_production_df          = plot_day_production_df.groupby(['Date']).reset_index()

        plot_day_consumption_df['Date'] = pd.to_datetime(plot_day_consumption_df['Date'])
        plot_day_consumption_df['Date'] = plot_day_consumption_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
        # plot_day_consumption_df         = plot_day_consumption_df.groupby(['Date']).reset_index()

        plot_day_production_df          = pd.melt(plot_day_production_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")
        plot_day_consumption_df         = pd.melt(plot_day_consumption_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")


        container_plot_day_cols[0].altair_chart(
            altair_chart=alt.layer(
                alt.Chart(
                    data=plot_day_production_df
                ).mark_area().encode(
                    x=alt.X(
                        'Date:O',
                        axis=alt.Axis(title='Datum [M]')
                    ),
                    y=alt.Y(
                        'Energy Value:Q',
                        axis=alt.Axis(title=f'Erzeugung [GWh]'),
                        scale=alt.Scale(domain=[0, 60])
                    ),
                    color=alt.Color(
                        'Energy_Source:N',
                        legend=alt.Legend(title='Energiequelle'),
                        scale=scale_,
                    ),
                    order=alt.Order(
                        'Energy_Source:N',
                        sort='ascending'
                    ),
                ),
                alt.Chart(
                    data=plot_day_consumption_df
                ).mark_line().encode(
                    x=alt.X(
                        'Date:O',
                        axis=alt.Axis(title='Datum [M]')
                    ),
                    y=alt.Y(
                        'Energy Value:Q',
                        axis=alt.Axis(title=f'Verbrauch [GWh]'),
                        scale=alt.Scale(domain=[0, 60])
                    ),
                    color=alt.value('#FF0000'),
                    order=alt.Order(
                        'Energy_Source:N',
                        sort='ascending'
                    ),
                )
            ).resolve_scale(
                y='independent'
            ).properties(
                height=600,
                title=f'Erzeugung und Gesamtverbrauch am {selected_date.strftime("%d.%m.%Y")}'
            ).configure_legend(
                orient='bottom'  # Position the legend underneath the chart
            ),
            use_container_width=True,
        )

        # Now the plot for the storage

        # Get start index of storage array
        start_index = (selected_data[0].start - timezone('Europe/Berlin').localize(dt.datetime(2030, 1, 1, 0, 0))).total_seconds() / (60 * 15)
        start_index = round(start_index)

        # Get end index of storage array
        end_index = (selected_data[-1].start - timezone('Europe/Berlin').localize(dt.datetime(2030, 1, 1, 0, 0))).total_seconds() / (60 * 15)
        end_index = round(end_index)

        st.debug(f'Storage: {np.copy(storage_balance)[start_index:end_index+1].size}')

        plot_day_storage_df = pd.DataFrame({
            'Date': date_range_day,
            'Storage Balance': np.copy(storage_balance)[start_index:end_index+1] / 1_000_000_000_000,
        })

        plot_day_storage_df['Date'] = pd.to_datetime(plot_day_storage_df['Date'])
        plot_day_storage_df['Date'] = plot_day_storage_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
        # plot_day_storage_df = plot_day_storage_df.groupby(['Date']).mean().reset_index()

        plot_day_storage_df         = pd.melt(plot_day_storage_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")

        container_plot_day_cols[1].altair_chart(
            altair_chart=alt.Chart(
                data=plot_day_storage_df
            ).mark_line().encode(
                x=alt.X(
                    'Date:O',
                    axis=alt.Axis(title='Datum [M]')
                ),
                y=alt.Y(
                    'Energy Value:Q',
                    axis=alt.Axis(title=f'Energie [TWh]'),
                    # scale=alt.Scale(domain=[0, 400])
                ),
                color=alt.Color(
                    'Energy_Source:N',
                    legend=alt.Legend(title='Energiequelle'),
                    scale=alt.Scale(
                        # domain=['Total Balance', 'Storage Balance'],
                        # range=['#FF0000', '#000000']
                        domain=['Storage Balance'],
                        range=['#000000']
                    )
                ),
                order=alt.Order(
                    'Energy_Source:N',
                    sort='ascending'
                ),
            ).properties(
                height=600,
                title=f'Energie Speicher am {selected_date.strftime("%d.%m.%Y")}'
            ).configure_legend(
                orient='bottom'  # Position the legend underneath the chart
            ),
            use_container_width=True,
        )

        # ----------------------------------------
        # Plot selectable month
        # ----------------------------------------

        container_plot_day = st.container()
        container_plot_day.header('Monatsansicht')

        format_func = lambda option : option.strftime('%B %Y')

        selected_date: dt.date = container_plot_day.selectbox(
            label='Select a month',
            options=[
                dt.datetime(2030, 1, 1),
                dt.datetime(2030, 2, 1),
                dt.datetime(2030, 3, 1),
                dt.datetime(2030, 4, 1),
                dt.datetime(2030, 5, 1),
                dt.datetime(2030, 6, 1),
                dt.datetime(2030, 7, 1),
                dt.datetime(2030, 8, 1),
                dt.datetime(2030, 9, 1),
                dt.datetime(2030, 10, 1),
                dt.datetime(2030, 11, 1),
                dt.datetime(2030, 12, 1),
            ],
            index=0,
            format_func=format_func
        )

        container_plot_day_cols = container_plot_day.columns(2, gap='medium')

        start_date = dt.datetime(selected_date.year, selected_date.month, 1, 0, 0)
        end_month = selected_date.month + 1

        if end_month > 12:
            end_date   = dt.datetime(selected_date.year, selected_date.month, 31, 23, 59)
        else:
            end_date   = dt.datetime(selected_date.year, end_month, 1, 0, 0)

        start_date = timezone('Europe/Berlin').localize(start_date)
        end_date   = timezone('Europe/Berlin').localize(end_date)

        selected_data: DataArray = collection_2030.get_range(start_date, end_date)

        # We now want to use the previously generated data and plot the same chart again
        # but with a different resolution. The year plots above are on a day resolution
        # and we want to plot the data on a 15 minute resolution.

        production_base_load     = [d.production.gas for d in selected_data]
        production_pv            = [d.production.pv for d in selected_data]
        production_wind_offshore = [d.production.wind_offshore for d in selected_data]
        production_wind_onshore  = [d.production.wind_onshore for d in selected_data]
        production_biomass       = [d.production.biomass for d in selected_data]
        production_hydro         = [d.production.hydro for d in selected_data]

        consumption              = [d.consumption.load for d in selected_data]

        date_range_day = pd.date_range(
            start=dt.datetime(start_date.year, start_date.month, 1, 0, 0),
            end=dt.datetime(end_date.year, end_date.month, 1, 0, 0),
            freq='15min',
            tz='Europe/Berlin'
        )

        st.debug(f'Data: {selected_data.size}')
        st.debug(f'Range: {len(date_range_day)}')

        plot_day_production_df = pd.DataFrame({
            'Date': date_range_day,
            '0 Fossil Base Load Coverage': np.copy(production_base_load) / 1_000_000_000,
            '1 Biomass': np.copy(production_biomass) / 1_000_000_000,
            '2 Hydro': np.copy(production_hydro) / 1_000_000_000,
            '3 Wind Offshore': np.copy(production_wind_offshore) / 1_000_000_000,
            '4 Wind Onshore': np.copy(production_wind_onshore) / 1_000_000_000,
            '5 PV': np.copy(production_pv) / 1_000_000_000,
        })

        plot_day_consumption_df = pd.DataFrame({
            'Date': date_range_day,
            'Consumption': np.copy(consumption) / 1_000_000_000,
        })

        domain_ = plot_day_production_df.columns.tolist()
        domain_.remove('Date')
        domain_.append('Consumption')

        plot_day_production_df['Date']  = pd.to_datetime(plot_day_production_df['Date'])
        plot_day_production_df['Date']  = plot_day_production_df['Date'].dt.strftime('%Y-%m-%d %H')
        plot_day_production_df          = plot_day_production_df.groupby(['Date']).sum().reset_index()

        plot_day_consumption_df['Date'] = pd.to_datetime(plot_day_consumption_df['Date'])
        plot_day_consumption_df['Date'] = plot_day_consumption_df['Date'].dt.strftime('%Y-%m-%d %H')
        plot_day_consumption_df         = plot_day_consumption_df.groupby(['Date']).sum().reset_index()

        plot_day_production_df          = pd.melt(plot_day_production_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")
        plot_day_consumption_df         = pd.melt(plot_day_consumption_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")


        container_plot_day_cols[0].altair_chart(
            altair_chart=alt.layer(
                alt.Chart(
                    data=plot_day_production_df
                ).mark_area().encode(
                    x=alt.X(
                        'Date:O',
                        axis=alt.Axis(title='Datum [M]')
                    ),
                    y=alt.Y(
                        'Energy Value:Q',
                        axis=alt.Axis(title=f'Erzeugung [GWh]'),
                        scale=alt.Scale(domain=[0, 220])
                    ),
                    color=alt.Color(
                        'Energy_Source:N',
                        legend=alt.Legend(title='Energiequelle'),
                        scale=scale_,
                    ),
                    order=alt.Order(
                        'Energy_Source:N',
                        sort='ascending'
                    ),
                ),
                alt.Chart(
                    data=plot_day_consumption_df
                ).mark_line().encode(
                    x=alt.X(
                        'Date:O',
                        axis=alt.Axis(title='Datum [M]')
                    ),
                    y=alt.Y(
                        'Energy Value:Q',
                        axis=alt.Axis(title=f'Verbrauch [GWh]'),
                        scale=alt.Scale(domain=[0, 220])
                    ),
                    color=alt.value('#FF0000'),
                    order=alt.Order(
                        'Energy_Source:N',
                        sort='ascending'
                    ),
                )
            ).resolve_scale(
                y='independent'
            ).properties(
                height=600,
                title=f'Erzeugung und Gesamtverbrauch {selected_date.strftime("%B %Y")}'
            ).configure_legend(
                orient='bottom'  # Position the legend underneath the chart
            ),
            use_container_width=True,
        )

        # Now the plot for the storage

        # Get start index of storage array
        start_index = (selected_data[0].start - timezone('Europe/Berlin').localize(dt.datetime(2030, 1, 1, 0, 0))).total_seconds() / (60 * 15)
        start_index = round(start_index)

        # Get end index of storage array
        end_index = (selected_data[-1].start - timezone('Europe/Berlin').localize(dt.datetime(2030, 1, 1, 0, 0))).total_seconds() / (60 * 15)
        end_index = round(end_index)

        st.debug(f'Storage: {np.copy(storage_balance)[start_index:end_index+1].size}')

        plot_day_storage_df = pd.DataFrame({
            'Date': date_range_day,
            'Storage Balance': np.copy(storage_balance)[start_index:end_index+1] / 1_000_000_000_000,
        })

        plot_day_storage_df['Date'] = pd.to_datetime(plot_day_storage_df['Date'])
        plot_day_storage_df['Date'] = plot_day_storage_df['Date'].dt.strftime('%Y-%m-%d %H')
        plot_day_storage_df = plot_day_storage_df.groupby(['Date']).mean().reset_index()

        plot_day_storage_df         = pd.melt(plot_day_storage_df, id_vars=["Date"], var_name="Energy_Source", value_name="Energy Value")

        container_plot_day_cols[1].altair_chart(
            altair_chart=alt.Chart(
                data=plot_day_storage_df
            ).mark_line().encode(
                x=alt.X(
                    'Date:O',
                    axis=alt.Axis(title='Datum [M]')
                ),
                y=alt.Y(
                    'Energy Value:Q',
                    axis=alt.Axis(title=f'Energie [TWh]'),
                    # scale=alt.Scale(domain=[0, 400])
                ),
                color=alt.Color(
                    'Energy_Source:N',
                    legend=alt.Legend(title='Energiequelle'),
                    scale=alt.Scale(
                        # domain=['Total Balance', 'Storage Balance'],
                        # range=['#FF0000', '#000000']
                        domain=['Storage Balance'],
                        range=['#000000']
                    )
                ),
                order=alt.Order(
                    'Energy_Source:N',
                    sort='ascending'
                ),
            ).properties(
                height=600,
                title=f'Energie Speicher am {selected_date.strftime("%B %Y")}'
            ).configure_legend(
                orient='bottom'  # Position the legend underneath the chart
            ),
            use_container_width=True,
        )