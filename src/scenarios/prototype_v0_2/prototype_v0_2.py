import calendar
import os
import datetime as dt
from threading import Event, Thread
from pytz import timezone
from time import sleep

from functools import lru_cache

import numpy as np
from numpy.typing import NDArray
import pandas as pd
import streamlit as st
import altair as alt

from dtypes import Unit

from data_manager.data_manager import Collections, Collection, Data, DataArray


class Prototype_v0_2:
    def __init__(self, view):
        self.view = view
        self.params = {}

        try:
            self.params['reference_year'] = st.session_state.reference_year
            self.params['load'] = st.session_state.total_consumption_2030
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

        INITIAL_BALANCE: int = Unit.TWh(10)
        RESERVE_BALANCE: int = Unit.TWh(1)


        # Debug
        # st.debug(f'POWER_FACTOR_PV     : {POWER_FACTOR_PV}')
        # st.debug(f'POWER_FACTOR_WINDOFF: {POWER_FACTOR_WINDOFF}')
        # st.debug(f'POWER_FACTOR_WINDON : {POWER_FACTOR_WINDON}')
        # st.debug(f'POWER_FACTOR_BIOMASS: {POWER_FACTOR_BIOMASS}')
        # st.debug(f'POWER_FACTOR_HYDRO  : {POWER_FACTOR_HYDRO}')
        # st.debug(f'LOAD_FACTOR         : {LOAD_FACTOR}')


        # st.debug('Prototype_v0_2 works!')


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

        # ----------------------------------------
        # Apply ramp factor
        # ----------------------------------------
        _summer_factor = 0.5
        SUMMER_FACTOR = _summer_factor
        WINTER_FACTOR = 1.0

        x_W = lambda S, W, x_S: (1 - ((S/(S+W)) * x_S)) / (W/(S+W))

        WINTER_FACTOR = x_W(7, 5, SUMMER_FACTOR)

        st.debug(f'Summer Factor: {SUMMER_FACTOR}')
        st.debug(f'Winter Factor: {WINTER_FACTOR}')

        ramp_factor = np.ones(collection_2030.get_length(), dtype=float)

        # Winter End Fade Start
        w_e_0 = dt.datetime(2030, 3, 1, 0, 0)
        w_e_0 = timezone('Europe/Berlin').localize(w_e_0)
        # Winter End Fade End
        w_e_1 = dt.datetime(2030, 3, 31, 23, 45)
        w_e_1 = timezone('Europe/Berlin').localize(w_e_1)
        # Winter Beginning Fade Start
        w_b_0 = dt.datetime(2030, 10, 1, 0, 0)
        w_b_0 = timezone('Europe/Berlin').localize(w_b_0)
        # Winter Beginning Fade End
        w_b_1 = dt.datetime(2030, 10, 31, 23, 45)
        w_b_1 = timezone('Europe/Berlin').localize(w_b_1)

        # Winter 1. Jan - 28. Feb
        winter_0 = w_e_0 - timezone('Europe/Berlin').localize(dt.datetime(2030, 1, 1))
        winter_0 = winter_0.total_seconds() / (60 * 15)
        ramp_factor[:int(winter_0)] = WINTER_FACTOR

        # Ramping down 1. Mar - 31. Mar
        td_ramp_down = w_e_1 - w_e_0
        td_ramp_down = td_ramp_down.total_seconds() / (60 * 15)
        td_ramp_down = round(td_ramp_down)
        ramp_down = np.linspace(WINTER_FACTOR, SUMMER_FACTOR, td_ramp_down)

        ramp_factor[int(winter_0):int(winter_0 + td_ramp_down)] = ramp_down

        # Summer 1. Apr - 30. Sep
        summer = w_b_0 - w_e_1
        summer = summer.total_seconds() / (60 * 15)
        summer = round(summer)

        ramp_factor[int(winter_0 + td_ramp_down):int(winter_0 + td_ramp_down + summer)] = SUMMER_FACTOR

        # Ramping up 1. Oct - 31. Oct
        td_ramp_up = w_b_1 - w_b_0
        td_ramp_up = td_ramp_up.total_seconds() / (60 * 15)
        td_ramp_up = round(td_ramp_up)
        ramp_up = np.linspace(SUMMER_FACTOR, WINTER_FACTOR, td_ramp_up)

        ramp_factor[int(winter_0 + td_ramp_down + summer):int(winter_0 + td_ramp_down + summer + td_ramp_up)] = ramp_up

        # Winter 1. Nov - 31. Dec
        winter_1: dt.timedelta = timezone('Europe/Berlin').localize(dt.datetime(2030, 12, 31, 23, 45)) - w_b_1
        winter_1: float = winter_1.total_seconds() / (60 * 15)
        winter_1: int = round(winter_1)

        ramp_factor[int(winter_0 + td_ramp_down + summer + td_ramp_up):] = WINTER_FACTOR

        for i in range(collection_2030.get_length()):
            collection_2030.data[i].production.gas *= ramp_factor[i]

        recalculated_sum = sum(d.production.gas for d in collection_2030)
        st.debug(f'Recalculated Sum: {round(recalculated_sum / 1_000_000_000_000, 2)} TWh')

        st.success('Done!')

        # # Create a start and end date
        # # ! tzinfo does not work correctly with pytz
        # start = dt.datetime(2030, 3, 31,  0,  0)
        # end   = dt.datetime(2030, 3, 31, 23, 45)

        # # Localize to Europe/Berlin
        # start = timezone('Europe/Berlin').localize(start)
        # end   = timezone('Europe/Berlin').localize(end)

        # # Get the data for the given date range
        # _test = collection_2030.get_range(start, end)




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
        lowest_point = np.iinfo(np.int64).max

        storage_balance: NDArray   = np.zeros(collection_2030.get_length(), dtype=int)
        renewable_share_percentage = np.zeros(collection_2030.get_length(), dtype=float)

        simulation_successfull = False

        with st.spinner('Simulating...'):
            while not simulation_stop:
                iterations += 1

                print(f'----------------------------------------')
                print(f'iteration: {iterations}')
                print(f'----------------------------------------')

                lowest_point = np.iinfo(np.int64).max

                # ----------------------------------------
                # Setup storage
                # ----------------------------------------
                storage = MagicStorage(initial_energy=INITIAL_BALANCE)
                # storage.start_electrolysis()

                # ----------------------------------------
                # Calculate the net balance
                # ----------------------------------------
                net_balance: NDArray   = np.zeros(collection_2030.get_length(), dtype=int)
                balance_is_negative = False

                # ----------------------------------------
                # Iterate over the year 2030
                # ----------------------------------------
                for i, d in enumerate(collection_2030):
                    d: Data = d
                    net_balance[i] = d.production.total - d.consumption.load

                    discharge: int = 0
                    charge: int    = 0

                    # ----------------------------------------
                    # Charge or discharge the storage
                    # ----------------------------------------
                    if net_balance[i] > 0:
                        # Putting energy into a temporary battery
                        discharge = net_balance[i]
                        storage.charge(discharge)
                    elif net_balance[i] < 0:
                        # Taking energy from a hydrogen gas turbine
                        try:
                            charge = abs(net_balance[i])
                            storage.discharge(charge)
                        except StorageEmptyException as e:
                            print('Storage is empty. Stopping iteration.')
                            balance_is_negative = True
                            break

                    storage_balance[i] = storage.hydrogen
                    lowest_point = min(lowest_point, storage.hydrogen * storage.H_TO_W)

                    numerator = (d.production.total_renewables + discharge)
                    denominator = (d.consumption.load + charge)

                    renewable_share_percentage[i] = numerator / denominator

                # ----------------------------------------
                # Calculate the total balance (cumulative)
                # ----------------------------------------
                total_balance: NDArray = net_balance.cumsum()

                total_balance += initial_balance

                # ----------------------------------------
                # Iterate over the year 2030
                # and stop if the balance is negative
                # ----------------------------------------

                remaining_storage = storage_balance[-1] * storage.H_TO_W
                storage_less_than_initial = remaining_storage <= INITIAL_BALANCE
                reverse_storage_less = lowest_point <= RESERVE_BALANCE

                if balance_is_negative or storage_less_than_initial or reverse_storage_less:
                    for i in range(collection_2030.get_length()):
                        collection_2030.data[i].production.gas *= 1.01
                else:
                    simulation_stop = True
                    simulation_successfull = True

                if iterations > 200:
                    simulation_stop = True

        if not simulation_successfull:
            st.warning('Maximum number of iterations reached.')
            st.error('Simulation failed!')
            return

        st.success(f'Simulation succeeded after {iterations} iterations.')
        st.subheader('Results')
        st.code(f'Initial Storage Energy = {round(initial_balance / 1_000_000_000_000, 2)} TWh')

        total_gas = sum(d.production.gas for d in collection_2030)
        _base_load_coverage = round(total_gas / 1_000_000_000_000, 2)
        _per_quarter = round(_base_load_coverage * 1_000 / collection_2030.get_length(), 2)
        st.code(f'Required Base Load Coverage = {_base_load_coverage} TWh - {_per_quarter} GWh/quarter')

        base_load_overshoot = total_gas / deficit
        st.code(f'Base Load Overproduction = {round(base_load_overshoot * 100, 2)} %')
        st.code(f'Base Load Share (Consumption) = {round(total_gas / total_consumption * 100, 2)} %')

        remaining_storage = storage_balance[-1] * storage.H_TO_W
        st.code(f'Remaining Storage Energy = {round(remaining_storage / 1_000_000_000_000, 2)} TWh')

        st.code(f'Lowest Point = {round(lowest_point / 1_000_000_000_000, 2)} TWh')

        # ----------------------------------------
        # Calculate storage power
        # ----------------------------------------

        # Get the largest deficit
        differences = np.diff(storage_balance)

        # Find the maximum difference
        largest_charge = np.max(differences) * storage.W_TO_H
        largest_discharge = np.min(differences) * storage.H_TO_W

        largest_charge_power = largest_charge * 4
        largest_discharge_power = largest_discharge * 4

        st.code(f'Largest Charge = {round(largest_charge / 1_000_000_000, 2)} GWh - {round(largest_charge_power / 1_000_000_000, 2)} GW')
        st.code(f'Largest Discharge = {round(largest_discharge / 1_000_000_000, 2)} GWh - {round(largest_discharge_power / 1_000_000_000, 2)} GW')

        total_hydrogen_required = np.trapz(storage_balance)
        st.code(f'Total Hydrogen Required = {round(total_hydrogen_required / 1_000_000_000_000, 2)} Gt')


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
                        axis=alt.Axis(title=f'Erzeugung [TWh]'),
                        scale=alt.Scale(domain=[0, 3_500])
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
                        axis=alt.Axis(title=f'Verbrauch [TWh]'),
                        scale=alt.Scale(domain=[0, 3_500])
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
            'Storage Balance': np.copy(storage_balance) / 1_000_000,
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
                    axis=alt.Axis(title=f'Hydrogen [kt]'),
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
                title='Wasserstoff Speicher Gesamtenergie'
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
            'Storage Balance': np.copy(storage_balance)[start_index:end_index+1] / 1_000_000,
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
                    axis=alt.Axis(title=f'Hydrogen [kt]'),
                    scale=alt.Scale(domain=[0, 400])
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
                title=f'Wasserstoff Speicher am {selected_date.strftime("%d.%m.%Y")}'
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
        end_date   = dt.datetime(selected_date.year, selected_date.month + 1, 1, 0, 0)

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
            'Storage Balance': np.copy(storage_balance)[start_index:end_index+1] / 1_000_000,
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
                    axis=alt.Axis(title=f'Hydrogen [kt]'),
                    scale=alt.Scale(domain=[0, 400])
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
                title=f'Wasserstoff Speicher am {selected_date.strftime("%B %Y")}'
            ).configure_legend(
                orient='bottom'  # Position the legend underneath the chart
            ),
            use_container_width=True,
        )


class MagicStorage:
    energy: float = 0.0
    hydrogen: float = 0.0
    thread = None

    W_TO_H = 39_000
    H_TO_W = 33_000

    STORAGE_CAP: int = Unit.kt(400)

    def __init__(self, initial_energy: float = 0.0):
        self.charge(initial_energy)

    def start_electrolysis(self):
        self.thread = self.Electrolysis(self)
        self.thread.start()

    class Electrolysis(Thread):

        def __init__(self, storage):
            self.storage = storage

            name = 'Electrolysis'

            super().__init__(name=name, daemon=True)
            self._stop_event = Event()

        def run(self):
            print(f"{self.name} is powering up...")

            while not self._stop_event.is_set():
                if self.storage.energy >= self.storage.W_TO_H:

                    # Convert all possible energy into hydrogen
                    # and put it into the storage
                    possible = self.storage.energy / self.storage.W_TO_H
                    self.storage.energy -= possible * self.storage.W_TO_H
                    self.storage.hydrogen += possible

            print(f"{self.name} is stopped.")

        def stop(self):
            print(f"{self.name} is stopping...")
            self._stop_event.set()


    def stop_electrolysis(self):
        self.thread.stop()
        self.thread.join()

    def charge(self, energy: float):
        hydrogen = energy / self.W_TO_H

        self.hydrogen += hydrogen

        self.hydrogen = min(self.hydrogen, self.STORAGE_CAP)

    # def _electrolysis(self):
    #     # Wait until 39_000 of energy is available
    #     # and turn this into 1 kilogram of hydrogen
    #     print('Electrolysis started.')
    #     while True:
    #         if self.energy > self.W_TO_H:
    #             self.energy -= self.W_TO_H
    #             self.hydrogen += 1

    def discharge(self, energy: float) -> float:

        required_hydrogen = energy / self.H_TO_W

        if required_hydrogen > self.hydrogen:
            raise StorageEmptyException()
        else:
            return self.combust(required_hydrogen)

    def combust(self, hydrogen: float) -> float:
        self.hydrogen -= hydrogen
        return hydrogen * self.H_TO_W


class StorageEmptyException(Exception):
    def __init__(self, message: str = 'Storage is empty.', energy: float = 0.0):
        self.message = message
        self.energy = energy
        super().__init__(self.message)
