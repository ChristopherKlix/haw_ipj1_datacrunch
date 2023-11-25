# import pandas as pd
import copy
import csv
from datetime import datetime
from datetime import date
from datetime import timedelta
from time import sleep, time
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from typing import List
import threading


REFERENCE_YEAR = 2030
RES_PATH = './static/res/'
ENERGY_PRODUCTION_CSV = 'Realisierte_Erzeugung_202001010000_202212312359_Viertelstunde.csv'
ENERGY_CONSUMPTION_CSV = 'Realisierter_Stromverbrauch_202001010000_202212312359_Viertelstunde.csv'
INSTALLED_CAPACITY_CSV = 'Installierte_Erzeugungsleistung_202001010000_202212312359_Viertelstunde.csv'
ENERGY_PRODUCTION_ROWS = 105216
ENERGY_CONSUMPTION_ROWS = 105216
INSTALLED_CAPACITY_ROWS = 105216


def main():
    # print('\033c', end='')
    os.system('cls' if os.name == 'nt' else 'clear')


    # * Load Data
    # TODO: Load data in a separate thread
    # TODO: and display a loading animation
    #
    # ! Combine all data in one single object? MAybe?!
    data: np.ndarray = load_data()
    data = load_installed_capacity(data)
    power_consumption_data: np.ndarray = load_power_consumption_data()


    # Print number of data entries
    print('Number of data entries:', data.size)

    structured_data: np.ndarray = reshape_data(data)
    structured_power_consumption_data: np.ndarray = reshape_data(power_consumption_data)

    # Print dimensions of structured data
    print('Dimensions of structured data:', structured_data.shape)

    reference_data = compute_reference_year(structured_data)
    reference_power_consumption_data = compute_reference_year(structured_power_consumption_data)

    # Print dimensions of average data
    print('Dimensions of average data:', reference_data.shape)

    # Request user input for date
    print('#' * 30)
    print('Average data tool')
    print('#' * 30)

    # Count all entries with little to no PV and Wind production
    flattened_data = data.flatten()

    dunkelflaute_count = 0
    dunkelflaute_pv_threshold = 1_000_000
    dunkelflaute_wind_threshold = 100_000_000

    entries_with_no_pv = 0
    entries_with_no_wind = 0
    entries_daytime_with_no_pv = 0
    year_count = [0, 0, 0]
    entries_nighttime_with_no_pv = 0

    for entry in flattened_data:
        pv_prod = entry.pv
        wind_prod = entry.wind_offshore + entry.wind_onshore

        if pv_prod < dunkelflaute_pv_threshold and wind_prod < dunkelflaute_wind_threshold:
            dunkelflaute_count += 1

        if pv_prod < dunkelflaute_pv_threshold:
            entries_with_no_pv += 1

            if entry.start.hour >= 6 and entry.start.hour <= 18:
                entries_daytime_with_no_pv += 1

                if entry.start.year == 2020:
                    year_count[0] += 1
                elif entry.start.year == 2021:
                    year_count[1] += 1
                elif entry.start.year == 2022:
                    year_count[2] += 1
            else:
                entries_nighttime_with_no_pv += 1

        if wind_prod < dunkelflaute_wind_threshold:
            entries_with_no_wind += 1

    print(f'Number of entries with little to no PV and Wind production: {dunkelflaute_count}')
    print(f'Number of entries with no PV production: {entries_with_no_pv}')
    print(f'Number of entries with no PV production during daytime: {entries_daytime_with_no_pv}')
    print(f'                                                  2020: {year_count[0]}')
    print(f'                                                  2021: {year_count[1]}')
    print(f'                                                  2022: {year_count[2]}')
    print(f'Number of entries with no PV production during nighttime: {entries_nighttime_with_no_pv}')
    print(f'Number of entries with less than 100 MWh Wind production: {entries_with_no_wind}')

    # Compute commulative energy production of PV per month in 2020
    pv_per_month_2020 = np.empty(12, dtype=int)
    pv_per_month_2021 = np.empty(12, dtype=int)
    pv_per_month_2022 = np.empty(12, dtype=int)

    installed_pv_per_month_2020 = np.empty(12, dtype=int)
    installed_pv_per_month_2021 = np.empty(12, dtype=int)
    installed_pv_per_month_2022 = np.empty(12, dtype=int)

    print(f'#' * 100)
    print(f'# PV production and installed PV per month')
    print(f'~' * 100)
    print(f'                   2020        2021        2022                           2020        2021        2022')

    for month in range(0, 12):
        for day in range(0, 31):
            for hour in range(0, 24):
                for quarter in range(0, 4):
                    pv_per_month_2020[month] += structured_data[0, month, day, hour, quarter].pv
                    pv_per_month_2021[month] += structured_data[1, month, day, hour, quarter].pv
                    pv_per_month_2022[month] += structured_data[2, month, day, hour, quarter].pv
                    installed_pv_per_month_2020[month] = structured_data[0, month, 0, 0, 0].installed_pv
                    installed_pv_per_month_2021[month] = structured_data[1, month, 0, 0, 0].installed_pv
                    installed_pv_per_month_2022[month] = structured_data[2, month, 0, 0, 0].installed_pv

    for i in range(0, 12):
        print(f'PV Production:    {pv_per_month_2020[i] / 1_000_000_000_000:6.2f} TWh    {pv_per_month_2021[i] / 1_000_000_000_000:6.2f} TWh    {pv_per_month_2022[i] / 1_000_000_000_000:6.2f} TWh', end='')
        print(f' │ Installed PV:    {installed_pv_per_month_2020[i] / 1_000_000_000:6.2f} GW    {installed_pv_per_month_2021[i] / 1_000_000_000:6.2f} GW    {installed_pv_per_month_2022[i] / 1_000_000_000:6.2f} GW')

    # Compute commulative energy production of PV per month in 2020
    wind_offshore_per_month_2020 = np.empty(12, dtype=int)
    wind_offshore_per_month_2021 = np.empty(12, dtype=int)
    wind_offshore_per_month_2022 = np.empty(12, dtype=int)

    installed_wind_offshore_per_month_2020 = np.empty(12, dtype=int)
    installed_wind_offshore_per_month_2021 = np.empty(12, dtype=int)
    installed_wind_offshore_per_month_2022 = np.empty(12, dtype=int)

    print(f'#' * 100)
    print(f'# Wind Offshore production and installed Wind Offshore per month')
    print(f'~' * 100)
    print(f'                   2020        2021        2022                           2020        2021        2022')

    for month in range(0, 12):
        for day in range(0, 31):
            for hour in range(0, 24):
                for quarter in range(0, 4):
                    wind_offshore_per_month_2020[month] += structured_data[0, month, day, hour, quarter].wind_offshore
                    wind_offshore_per_month_2021[month] += structured_data[1, month, day, hour, quarter].wind_offshore
                    wind_offshore_per_month_2022[month] += structured_data[2, month, day, hour, quarter].wind_offshore
                    installed_wind_offshore_per_month_2020[month] = structured_data[0, month, 0, 0, 0].installed_wind_offshore
                    installed_wind_offshore_per_month_2021[month] = structured_data[1, month, 0, 0, 0].installed_wind_offshore
                    installed_wind_offshore_per_month_2022[month] = structured_data[2, month, 0, 0, 0].installed_wind_offshore

    for i in range(0, 12):
        print(f'Wind Offshore Production:    {wind_offshore_per_month_2020[i] / 1_000_000_000_000:6.2f} TWh    {wind_offshore_per_month_2021[i] / 1_000_000_000_000:6.2f} TWh    {wind_offshore_per_month_2022[i] / 1_000_000_000_000:6.2f} TWh', end='')
        print(f' │ Installed Wind Offshore:    {installed_wind_offshore_per_month_2020[i] / 1_000_000_000:6.2f} GW    {installed_wind_offshore_per_month_2021[i] / 1_000_000_000:6.2f} GW    {installed_wind_offshore_per_month_2022[i] / 1_000_000_000:6.2f} GW')

    wind_onshore_per_month_2020 = np.empty(12, dtype=int)
    wind_onshore_per_month_2021 = np.empty(12, dtype=int)
    wind_onshore_per_month_2022 = np.empty(12, dtype=int)

    installed_wind_onshore_per_month_2020 = np.empty(12, dtype=int)
    installed_wind_onshore_per_month_2021 = np.empty(12, dtype=int)
    installed_wind_onshore_per_month_2022 = np.empty(12, dtype=int)

    print(f'#' * 100)
    print(f'# Wind Onshore production and installed Wind Onshore per month')
    print(f'~' * 100)
    print(f'                   2020        2021        2022                           2020        2021        2022')

    for month in range(0, 12):
        for day in range(0, 31):
            for hour in range(0, 24):
                for quarter in range(0, 4):
                    wind_onshore_per_month_2020[month] += structured_data[0, month, day, hour, quarter].wind_onshore
                    wind_onshore_per_month_2021[month] += structured_data[1, month, day, hour, quarter].wind_onshore
                    wind_onshore_per_month_2022[month] += structured_data[2, month, day, hour, quarter].wind_onshore
                    installed_wind_onshore_per_month_2020[month] = structured_data[0, month, 0, 0, 0].installed_wind_onshore
                    installed_wind_onshore_per_month_2021[month] = structured_data[1, month, 0, 0, 0].installed_wind_onshore
                    installed_wind_onshore_per_month_2022[month] = structured_data[2, month, 0, 0, 0].installed_wind_onshore

    for i in range(0, 12):
        print(f'Wind Onshore Production:    {wind_onshore_per_month_2020[i] / 1_000_000_000_000:6.2f} TWh    {wind_onshore_per_month_2021[i] / 1_000_000_000_000:6.2f} TWh    {wind_onshore_per_month_2022[i] / 1_000_000_000_000:6.2f} TWh', end='')
        print(f' │ Installed Wind Onshore:    {installed_wind_onshore_per_month_2020[i] / 1_000_000_000:6.2f} GW    {installed_wind_onshore_per_month_2021[i] / 1_000_000_000:6.2f} GW    {installed_wind_onshore_per_month_2022[i] / 1_000_000_000:6.2f} GW')


    # Compute total energy balance of 2020, 2021, and 2022

    # 2020
    years = [2020, 2021, 2022]

    for i, year in enumerate(years):
        production_fossil_fuels = 0
        production_renewables = 0
        production_nuclear = 0
        production_total = 0
        total_load = 0
        net_balance = 0

        for month in range(0, 12):
            for day in range(0, 31):
                for hour in range(0, 24):
                    for quarter in range(0, 4):
                        total_load += structured_power_consumption_data[i, month, day, hour, quarter].total_load
                        production_fossil_fuels += structured_data[i, month, day, hour, quarter].total_fossil_fuels()
                        production_renewables += structured_data[i, month, day, hour, quarter].total_renewables()
                        production_nuclear += structured_data[i, month, day, hour, quarter].nuclear
                        production_total += structured_data[i, month, day, hour, quarter].total_production()

        net_balance = production_total - total_load

        print('#' * 40)
        print(f'Net energy balance of {year}')
        print('~' * 40)
        print(f'Production from fossil fuels: {production_fossil_fuels / 1_000_000 / 1_000_000:6.2f} TWh')
        print(f'Production from renewables:   {production_renewables / 1_000_000 / 1_000_000:6.2f} TWh')
        print(f'Production from nuclear:      {production_nuclear / 1_000_000 / 1_000_000:6.2f} TWh')
        print(f'Total production:             {production_total / 1_000_000 / 1_000_000:6.2f} TWh')
        print(f'Total load:                   {total_load / 1_000_000 / 1_000_000:6.2f} TWh')
        print('-' * 40)
        print(f'Net balance:                  ', end='')

        if net_balance < 0:
            # Make ASCII red
            print('\033[91m', end='')
        elif net_balance > 0:
            # Make ASCII green
            print('\033[92m', end='')

        print(f'{net_balance / 1_000_000 / 1_000_000:6.2f} TWh')

        # Reset ASCII color
        print('\033[0m', end='')

    # Comnpute maximum PV production per hour relative to installed capacity
    print('#' * 40)
    print(f'Maximum PV production per hour relative to installed capacity')
    print('~' * 40)

    max_percentage = 0.0
    max_timestamp = (None, None)

    for year in range(0, 3):
        for month in range(0, 12):
            for day in range(0, 31):
                for hour in range(0, 24):
                    for quarter in range(0, 4):
                        pv_production = structured_data[year, month, day, hour, quarter].pv
                        interpolated_pv_production = pv_production * 4
                        installed_pv = structured_data[year, month, 0, 0, 0].installed_pv
                        percentage = interpolated_pv_production / installed_pv * 100

                        start_time = structured_data[year, month, day, hour, quarter].start
                        end_time = structured_data[year, month, day, hour, quarter].end

                        max_timestamp = (start_time, end_time) if percentage >= max_percentage else max_timestamp
                        max_percentage = max(max_percentage, percentage)


    print(f'Maximum PV production: {max_percentage:.2f}%')
    print(f'At: {max_timestamp[0]} - {max_timestamp[1]}')
    print('#' * 40)

    return structured_data, structured_power_consumption_data

    sys.exit(0)

    month = int(input('Enter month: '))
    day = int(input('Enter day: '))

    # Print average data
    print(f'Computing average data for the {day}{ordinal_suffix(day)} of {month}...')

    # Plot average data for the 15th of March
    # elements = reference_data[0, month-1, day-1, :, :]
    energy_production = reference_data[0, month-1, day-1, :, :]
    energy_consumption = reference_power_consumption_data[0, month-1, day-1, :, :]

    # Compute best month for pv production
    best_month = compute_best_pv_month(reference_data)

    print(f'Best month for pv production: {best_month + 1}')

    # plot_day(energy_production, energy_consumption)

    # Compute deviation from reference year to 2020, 2021, and 2022
    day = 1
    month = 1

    pv_2020 = structured_data[0, month, day, 11, 0].pv
    pv_2021 = structured_data[1, month, day, 11, 0].pv
    pv_2022 = structured_data[2, month, day, 11, 0].pv
    pv_2030 = reference_data[0, month, day, 11, 0].pv

    print(f'PV production on the {day}{ordinal_suffix(day)} of {month} in 2020: {pv_2020 / 1_000_000:.2f} MWh')
    print(f'PV production on the {day}{ordinal_suffix(day)} of {month} in 2021: {pv_2021 / 1_000_000:.2f} MWh')
    print(f'PV production on the {day}{ordinal_suffix(day)} of {month} in 2022: {pv_2022 / 1_000_000:.2f} MWh')
    print(f'PV production on the {day}{ordinal_suffix(day)} of {month} in 2030: {pv_2030 / 1_000_000:.2f} MWh')

    print(f'Deviation from 2020: {(pv_2020 - pv_2030) / pv_2020 * 100:.2f}%')
    print(f'Deviation from 2021: {(pv_2021 - pv_2030) / pv_2021 * 100:.2f}%')
    print(f'Deviation from 2022: {(pv_2022 - pv_2030) / pv_2022 * 100:.2f}%')

    # Compute the average deviation of total_load and residual_load from the reference year
    deviation_sum = 0.0
    deviation_count = 0

    for month in range(0, 12):
        for day in range(0, 31):
            for hour in range(0, 24):
                for quarter in range(0, 4):
                    # print(f'{deviation_count}' + ': ' + f'{month + 1}, {day + 1}, {hour + 1}, {quarter}')
                    total_load = structured_power_consumption_data[0, month, day, hour, quarter].total_load
                    residual_load = structured_power_consumption_data[0, month, day, hour, quarter].residual_load
                    if (total_load == 0.0):
                        continue
                    deviation = residual_load / total_load * 100
                    deviation_sum += deviation
                    deviation_count += 1

    average_deviation = deviation_sum / deviation_count

    print(f'Average deviation of residual_load from total_load: {average_deviation:.2f}%')


def compute_best_pv_month(data):
    # Compute average pv production per month
    pv_per_month = np.empty(12, dtype=int)

    for month in range(0, 12):
        for day in range(0, 31):
            for hour in range(0, 24):
                for quarter in range(0, 4):
                    pv_per_month[month] += data[0, month, day, hour, quarter].pv


    # Find month with highest pv production
    best_month = 0
    for month in range(0, 12):
        if pv_per_month[month] > pv_per_month[best_month]:
            best_month = month

    return best_month


def plot_day(p_data, c_data):
    # Merge data array into one array
    p_data = p_data.flatten()
    p_data /= 1_000_000

    c_data = c_data.flatten()
    c_data /= 1_000_000

    # Duplicate last element to make the plot look nicer
    p_data = np.append(p_data, p_data[-1])
    c_data = np.append(c_data, c_data[-1])

    # hours = [d.start.hour for d in data]
    hours = np.arange(0, 24, 0.25)
    # Add the quarter of the next day
    hours = np.append(hours, 24.0)

    pv = [d.pv for d in p_data]
    wind_offshore = [d.wind_offshore for d in p_data]
    wind_onshore = [d.wind_onshore for d in p_data]
    biomass = [d.biomass for d in p_data]
    hydro = [d.hydro for d in p_data]

    total_load = [d.total_load for d in c_data]
    residual_load = [d.residual_load for d in c_data]

    fossil_fuels = [d.charcoal + d.coal + d.gas + d.other_conventional for d in p_data]

    clr_biomass = '#a7c957'
    clr_hydro = '#6184D8'
    clr_wind_offshore = '#0F0326'
    clr_wind_onshore = '#6a994e'
    clr_pv = '#EEA243'
    clr_dark = '#6a994e'
    clr_darker = '#386641'

    colors = [
        '#232C2E',
        clr_pv,
        clr_wind_onshore,
        clr_wind_offshore,
        clr_biomass,
        clr_hydro
    ]


    plt.style.use('dark_background')
    plt.figure(figsize=(20, 6))
    plt.plot([],[],color=colors[0], label='Fossil Fuels', linewidth=3)
    plt.plot([],[],color=colors[1], label='PV', linewidth=3)
    plt.plot([],[],color=colors[2], label='Wind Offshore', linewidth=3)
    plt.plot([],[],color=colors[3], label='Wind Onshore', linewidth=3)
    plt.plot([],[],color=colors[4], label='Biomass', linewidth=3)
    plt.plot([],[],color=colors[5], label='Hydro', linewidth=3)


    plt.stackplot(hours, fossil_fuels, pv, wind_offshore, wind_onshore, biomass, hydro, colors=colors, interpolate='cubic')

    plt.plot(hours, total_load, color='red', label='Total Load', linewidth=3)
    plt.plot(hours, residual_load, color='orange', label='Residual Load', linewidth=3)

    plt.xlabel('Hour of day')
    plt.ylabel('Power [MWh]')
    plt.xticks(np.arange(0, 25, 1))
    plt.xlim([0, 24])
    plt.title(f'Average energy production on the {p_data[0].get_day_f()} of {p_data[0].get_month_f()}.')
    plt.legend()
    plt.show()


def ordinal_suffix(day):
    if 11 <= day <= 13:
        return 'th'
    else:
        last_digit = day % 10
        if last_digit == 1:
            return 'st'
        elif last_digit == 2:
            return 'nd'
        elif last_digit == 3:
            return 'rd'
        else:
            return 'th'


class Data:
    def __init__(self):
        self.start = None
        self.end = None
        self.biomass = 0.0
        self.hydro = 0.0
        self.wind_offshore = 0.0
        self.wind_onshore = 0.0
        self.pv = 0.0
        self.other_renewables = 0.0
        self.nuclear = 0.0
        self.charcoal = 0.0
        self.coal = 0.0
        self.gas = 0.0
        self.gravity_energy_storage = 0.0
        self.other_conventional = 0.0

        self.installed_biomass = 0.0
        self.installed_hydro = 0.0
        self.installed_wind_offshore = 0.0
        self.installed_wind_onshore = 0.0
        self.installed_pv = 0.0

    def init(self, values):
        start_date_as_string = values[0] + ' ' + values[1]
        end_date_as_string = values[0] + ' ' + values[2]

        # Parse date string in German format to date object
        self.start = datetime.strptime(start_date_as_string, '%d.%m.%Y %H:%M')
        self.end = datetime.strptime(end_date_as_string, '%d.%m.%Y %H:%M')
        self.biomass = float(values[3].replace('.', '').replace(',', '.')) * 1_000_000
        self.hydro = float(values[4].replace('.', '').replace(',', '.')) * 1_000_000
        self.wind_offshore = float(values[5].replace('.', '').replace(',', '.')) * 1_000_000
        self.wind_onshore = float(values[6].replace('.', '').replace(',', '.')) * 1_000_000
        self.pv = float(values[7].replace('.', '').replace(',', '.')) * 1_000_000
        self.other_renewables = float(values[8].replace('-', '0').replace('.', '').replace(',', '.')) * 1_000_000
        self.nuclear = float(values[9].replace('.', '').replace(',', '.')) * 1_000_000
        self.charcoal = float(values[10].replace('.', '').replace(',', '.')) * 1_000_000
        self.coal = float(values[11].replace('.', '').replace(',', '.')) * 1_000_000
        self.gas = float(values[12].replace('.', '').replace(',', '.')) * 1_000_000
        self.gravity_energy_storage = float(values[13].replace('.', '').replace(',', '.')) * 1_000_000
        self.other_conventional = float(values[14].replace('.', '').replace(',', '.')) * 1_000_000

    def init_installed_capacity(self, values):
        self.installed_biomass = float(values[3].replace('.', '').replace(',', '.')) * 1_000_000
        self.installed_hydro = float(values[4].replace('.', '').replace(',', '.')) * 1_000_000
        self.installed_wind_offshore = float(values[5].replace('.', '').replace(',', '.')) * 1_000_000
        self.installed_wind_onshore = float(values[6].replace('.', '').replace(',', '.')) * 1_000_000
        self.installed_pv = float(values[7].replace('.', '').replace(',', '.')) * 1_000_000

    def total_renewables(self):
        return self.biomass + self.hydro + self.wind_offshore + self.wind_onshore + self.pv + self.other_renewables

    def total_fossil_fuels(self):
        return self.charcoal + self.coal + self.gas + self.other_conventional

    def total_production(self):
        return self.biomass + self.hydro + self.wind_offshore + self.wind_onshore + self.pv + self.other_renewables + self.nuclear + self.charcoal + self.coal + self.gas + self.gravity_energy_storage + self.other_conventional

    def __add__(self, other):
        if type(other) == type(None):
            return self

        if type(other) != Data:
            raise Exception('Cannot add Data to non-Data. Trying to add ' + str(type(other)) + '.')

        result = Data()
        result.start = self.start
        result.end = self.end
        result.biomass = self.biomass + other.biomass
        result.hydro = self.hydro + other.hydro
        result.wind_offshore = self.wind_offshore + other.wind_offshore
        result.wind_onshore = self.wind_onshore + other.wind_onshore
        result.pv = self.pv + other.pv
        result.other_renewables = self.other_renewables + other.other_renewables
        result.nuclear = self.nuclear + other.nuclear
        result.charcoal = self.charcoal + other.charcoal
        result.coal = self.coal + other.coal
        result.gas = self.gas + other.gas
        result.gravity_energy_storage = self.gravity_energy_storage + other.gravity_energy_storage
        result.other_conventional = self.other_conventional + other.other_conventional
        return result

    def __truediv__(self, other):
        result = Data()

        if type(other) == Data:
            raise Exception('Cannot divide Data by Data')

        result.start = self.start
        result.end = self.end
        result.biomass = self.biomass / other
        result.hydro = self.hydro / other
        result.wind_offshore = self.wind_offshore / other
        result.wind_onshore = self.wind_onshore / other
        result.pv = self.pv / other
        result.other_renewables = self.other_renewables / other
        result.nuclear = self.nuclear / other
        result.charcoal = self.charcoal / other
        result.coal = self.coal / other
        result.gas = self.gas / other
        result.gravity_energy_storage = self.gravity_energy_storage / other
        result.other_conventional = self.other_conventional / other
        return result

    def __str__(self):
        values: List[str] = []
        date_str = self.start.strftime('%d.%m.%Y %H:%M')
        date_str, start_time = date_str.split(' ')
        end_time = self.end.strftime('%H:%M')

        values.append(date_str)
        values.append(start_time)
        values.append(end_time)
        values.append(format(self.biomass, '.,2f'))
        values.append(format(self.hydro, '.,2f'))
        values.append(format(self.wind_offshore, '.,2f'))
        values.append(format(self.wind_onshore, '.,2f'))
        values.append(format(self.pv, '.,2f'))
        values.append(format(self.other_renewables, '.,2f'))
        values.append(format(self.nuclear, '.,2f'))
        values.append(format(self.charcoal, '.,2f'))
        values.append(format(self.coal, '.,2f'))
        values.append(format(self.gas, '.,2f'))
        values.append(format(self.gravity_energy_storage, '.,2f'))
        values.append(format(self.other_conventional, '.,2f'))

        return ';'.join(values)

    def get_day_f(self):
        return f'{self.start.day}{ordinal_suffix(self.start.day)}'

    def get_month_f(self):
        return f'{self.start.strftime("%B")}'


class PowerConsumptionData:
    def __init__(self):
        self.start = None
        self.end = None
        self.total_load = 0.0
        self.residual_load = 0.0
        self.gravitational_energy_storage = 0.0

    def init(self, values):
        start_date_as_string = values[0] + ' ' + values[1]
        end_date_as_string = values[0] + ' ' + values[2]

        self.start = datetime.strptime(start_date_as_string, '%d.%m.%Y %H:%M')
        self.end = datetime.strptime(end_date_as_string, '%d.%m.%Y %H:%M')
        self.total_load = float(values[3].replace('.', '').replace(',', '.')) * 1_000_000
        self.residual_load = float(values[4].replace('.', '').replace(',', '.')) * 1_000_000
        self.gravitational_energy_storage = float(values[5].replace('.', '').replace(',', '.')) * 1_000_000

    def __add__(self, other):
        if type(other) == type(None):
            return self

        if type(other) != PowerConsumptionData:
            raise Exception('Cannot add PowerConsumptionData to non-PowerConsumptionData. Trying to add ' + str(type(other)) + '.')

        result = PowerConsumptionData()
        result.start = self.start
        result.end = self.end
        result.total_load = self.total_load + other.total_load
        result.residual_load = self.residual_load + other.residual_load
        result.gravitational_energy_storage = self.gravitational_energy_storage + other.gravitational_energy_storage
        return result

    def __truediv__(self, other):
        result = PowerConsumptionData()

        if type(other) == PowerConsumptionData:
            raise Exception('Cannot divide PowerConsumptionData by PowerConsumptionData')

        result.start = self.start
        result.end = self.end
        result.total_load = self.total_load / other
        result.residual_load = self.residual_load / other
        result.gravitational_energy_storage = self.gravitational_energy_storage / other
        return result

    def __str__(self):
        values: List[str] = []
        date_str = self.start.strftime('%d.%m.%Y %H:%M')
        date_str, start_time = date_str.split(' ')
        end_time = self.end.strftime('%H:%M')

        values.append(date_str)
        values.append(start_time)
        values.append(end_time)
        values.append(format(self.total_load, '.,2f'))
        values.append(format(self.residual_load, '.,2f'))
        values.append(format(self.gravitational_energy_storage, '.,2f'))

        return ';'.join(values)


def load_power_consumption_data() -> np.ndarray:
    """
    Loads data from a CSV file and returns it as a numpy array of PowerConsumptionData objects.

    Returns:
        np.ndarray: A numpy array of PowerConsumptionData objects.
    """
    data: np.ndarray = np.empty(ENERGY_CONSUMPTION_ROWS, dtype=PowerConsumptionData)

    path: str = RES_PATH + ENERGY_CONSUMPTION_CSV

    start_timestamp = time()

    print(f'╔════════════════════')
    print(f'╠ Importing data...')
    print(f'╠ Path: {path}')
    print(f'╠')
    print(f'╠ Reading row: ')
    print(f'╠ Parsing data: ', end='')
    sys.stdout.flush()

    import_success = False
    err = ''
    err_msg = ''

    i = 0

    try:
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=';')

            # Skip first row
            next(reader)

            for row in reader:
                data_entry = PowerConsumptionData()
                data_entry.init(row)
                data[i] = data_entry
                # Go one line up
                print('\033[1A', end='')
                # Set cursor to x 16
                print('\033[17G', end='')
                # Print row number
                print(f'{i+1}', end='')
                # Go one line down
                print('\033[1B', end='')
                # Set cursor to x 16
                print('\033[17G', end='')
                sys.stdout.flush()

                print(data_entry.start.strftime('%d.%m.%Y %H:%M'), end='')
                # data = np.append(data, data_entry)
                i += 1

            import_success = True
    except FileNotFoundError as e:
        err = 'File not found.'
        err_msg = str(e)
    except ValueError as e:
        err = 'Value error.'
        err_msg = str(e)
    except KeyboardInterrupt as e:
        err = 'Keyboard interrupt.'
        err_msg = str(e)
    except Exception as e:
        err = 'Unknown error.'
        err_msg = str(e)
    finally:
        print('\n', end='')
        print(f'╠')
        print(f'╠ Summary')
        print(f'╠ Imported {i} data entries.')
        print(f'╠ Type of data: {type(data)}')
        print(f'╠ Size of data: {data.size}')
        print(f'╠ Shape of data: {data.shape}')
        print(f'╠ ⌛ Time elapsed: {time() - start_timestamp:.2f}s')
        print(f'╠')
        if not import_success:
            print(f'╠ ❌ Import failed.')
            print(f'╠ Error: {err}')
            print(f'╠ Error message: {err_msg}')
        else:
            print(f'╠ ✅ Import successful.')
        print(f'╚════════════════════')

    if not import_success:
        sys.exit(1)

    return data


def load_installed_capacity(data: np.ndarray) -> np.ndarray:
    """
    Loads data from a CSV file and returns it as a numpy array of Data objects.

    Returns:
        np.ndarray: A numpy array of Data objects.

    Raises:
        ImportException: If the import failed.
    """

    # Create empty numpy array with the size of the CSV file
    # ! This is a very expensive operation
    # ! The size is a magic number, should be calculated

    path: str = RES_PATH + INSTALLED_CAPACITY_CSV

    start_timestamp = time()

    print(f'╔════════════════════')
    print(f'╠ Importing data...')
    print(f'╠ Path: {path}')
    print(f'╠')
    print(f'╠ Reading row: ')
    print(f'╠ Parsing data: ', end='')

    import_success = False
    err = ''
    err_msg = ''

    i = 0

    try:
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=';')

            # Skip first row
            next(reader)

            sys.stdout.flush()

            for row in reader:
                data[i].init_installed_capacity(row)
                # Go one line up
                print('\033[1A', end='')
                # Set cursor to x 16
                print('\033[17G', end='')
                # Print row number
                print(f'{i+1}', end='')
                # Go one line down
                print('\033[1B', end='')
                # Set cursor to x 16
                print('\033[17G', end='')
                sys.stdout.flush()

                print(data[i].start.strftime('%d.%m.%Y %H:%M'), end='')
                i += 1

            import_success = True
    except FileNotFoundError as e:
        err = 'File not found.'
        err_msg = str(e)
    except ValueError as e:
        err = 'Value error.'
        err_msg = str(e)
    except KeyboardInterrupt as e:
        err = 'Keyboard interrupt.'
        err_msg = str(e)
    except Exception as e:
        err = 'Unknown error.'
        err_msg = str(e)
    finally:
        print('\n', end='')
        print(f'╠')
        print(f'╠ Summary')
        print(f'╠ Imported {i} data entries.')
        print(f'╠ Type of data: {type(data)}')
        print(f'╠ Size of data: {data.size}')
        print(f'╠ Shape of data: {data.shape}')
        print(f'╠ ⌛ Time elapsed: {time() - start_timestamp:.2f}s')
        print(f'╠')
        if not import_success:
            print(f'╠ ❌ Import failed.')
            print(f'╠ Error: {err}')
            print(f'╠ Error message: {err_msg}')
        else:
            print(f'╠ ✅ Import successful.')
        print(f'╚════════════════════')

    if not import_success:
        raise ImportException('Import failed.')

    return data


def reshape_power_consumption_data(raw_data: np.ndarray) -> np.ndarray:
    """
    Reshapes a list of PowerConsumptionData objects into a 5-dimensional numpy array.

    Args:
        raw_data (List[PowerConsumptionData]): A list of PowerConsumptionData objects to be reshaped.

    Returns:
        np.ndarray: A 5-dimensional numpy array with dimensions (3, 12, 31, 24, 4).
            The array is filled with the PowerConsumptionData objects from the input list, with each
            object being placed in the corresponding position in the array based on
            its start time.

    Raises:
        None
    """

    matrix_dim: tuple = (3, 12, 31, 24, 4)
    reshaped_data: np.ndarray = np.empty(matrix_dim, dtype=PowerConsumptionData)

    # Fill entire array with PowerConsumptionData objects
    for i in range(0, reshaped_data.size):
        reshaped_data[i] = PowerConsumptionData()

    print('Reshaping data...')
    print(f'Type of raw_data: {type(raw_data)}')
    print(f'Size of raw_data: {raw_data.size}')

    # Fill structured data with data entries linearly
    # reshaped_data[year, month, day, hour, quarter]
    for data_entry in raw_data:
        d_y_i = data_entry.start.year - 2020
        d_m_i = data_entry.start.month - 1
        d_d_i = data_entry.start.day - 1
        d_h_i = data_entry.start.hour

        # 00:00 - 00:14 -> 0
        # 00:15 - 00:29 -> 1
        # 00:30 - 00:44 -> 2
        # 00:45 - 00:59 -> 3
        d_q_i = data_entry.start.minute // 15

        try:
            reshaped_data[d_y_i, d_m_i, d_d_i, d_h_i, d_q_i] = data_entry
        except IndexError:
            print(f'IndexError: {data_entry.start.strftime("%d.%m.%Y %H:%M")}')
        except ValueError:
            print(f'ValueError: {data_entry.start.strftime("%d.%m.%Y %H:%M")}')
        except AttributeError:
            print(f'AttributeError: {data_entry.start.strftime("%d.%m.%Y %H:%M")}')
        except Exception as e:
            print(f'Exception: {e}')

    return reshaped_data


def load_data() -> np.ndarray:
    """
    Loads data from a CSV file and returns it as a numpy array of Data objects.

    Returns:
        np.ndarray: A numpy array of Data objects.

    Raises:
        ImportException: If the import failed.
    """

    # Create empty numpy array with the size of the CSV file
    # ! This is a very expensive operation
    # ! The size is a magic number, should be calculated
    # TODO: Calculate size of CSV file
    # TODO: Optimize memory usage since this is a very expensive operation
    data: np.ndarray = np.empty(ENERGY_PRODUCTION_ROWS, dtype=Data)

    path: str = RES_PATH + ENERGY_PRODUCTION_CSV

    start_timestamp = time()

    print(f'╔════════════════════')
    print(f'╠ Importing data...')
    print(f'╠ Path: {path}')
    print(f'╠')
    print(f'╠ Reading row: ')
    print(f'╠ Parsing data: ', end='')

    import_success = False
    err = ''
    err_msg = ''

    i = 0

    try:
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=';')

            # Skip first row
            next(reader)

            sys.stdout.flush()

            for row in reader:
                data_entry = Data()
                data_entry.init(row)
                data[i] = data_entry
                # Go one line up
                print('\033[1A', end='')
                # Set cursor to x 16
                print('\033[17G', end='')
                # Print row number
                print(f'{i+1}', end='')
                # Go one line down
                print('\033[1B', end='')
                # Set cursor to x 16
                print('\033[17G', end='')
                sys.stdout.flush()

                print(data_entry.start.strftime('%d.%m.%Y %H:%M'), end='')
                i += 1

            import_success = True
    except FileNotFoundError as e:
        err = 'File not found.'
        err_msg = str(e)
    except ValueError as e:
        err = 'Value error.'
        err_msg = str(e)
    except KeyboardInterrupt as e:
        err = 'Keyboard interrupt.'
        err_msg = str(e)
    except Exception as e:
        err = 'Unknown error.'
        err_msg = str(e)
    finally:
        print('\n', end='')
        print(f'╠')
        print(f'╠ Summary')
        print(f'╠ Imported {i} data entries.')
        print(f'╠ Type of data: {type(data)}')
        print(f'╠ Size of data: {data.size}')
        print(f'╠ Shape of data: {data.shape}')
        print(f'╠ ⌛ Time elapsed: {time() - start_timestamp:.2f}s')
        print(f'╠')
        if not import_success:
            print(f'╠ ❌ Import failed.')
            print(f'╠ Error: {err}')
            print(f'╠ Error message: {err_msg}')
        else:
            print(f'╠ ✅ Import successful.')
        print(f'╚════════════════════')

    if not import_success:
        raise ImportException('Import failed.')

    return data


# Custom Import exception
class ImportException(Exception):
    def __init__(self, message):
        self.message = message


def reshape_data(raw_data: np.ndarray) -> np.ndarray:
    """
    Reshapes a list of Data objects into a 5-dimensional numpy array.

    Args:
        raw_data (List[Data]): A list of Data objects to be reshaped.

    Returns:
        np.ndarray: A 5-dimensional numpy array with dimensions (3, 12, 31, 24, 4).
            The array is filled with the Data objects from the input list, with each
            object being placed in the corresponding position in the array based on
            its start time.

    Raises:
        None
    """
    # 3 years
    # 12 months
    # 31 days
    # 24 hours
    # 4 quarters per hour
    matrix_dim: tuple = (3, 12, 31, 24, 4)
    raw_data_type = type(raw_data.flatten()[0])
    reshaped_data: np.ndarray = np.empty(matrix_dim, dtype=raw_data_type)

    reshaped_data = reshaped_data.flatten()

    # Fill entire array with Data objects
    for i in range(0, reshaped_data.size):
        reshaped_data[i] = raw_data_type()

    # Reshape back to the matrix_dim
    reshaped_data = reshaped_data.reshape(matrix_dim)

    print('Reshaping data...')
    print(f'Type of raw_data: {type(raw_data)}')
    print(f'Size of raw_data: {raw_data.size}')

    # Fill structured data with data entries linearly
    # reshaped_data[year, month, day, hour, quarter]
    for data_entry in raw_data:
        d_y_i = data_entry.start.year - 2020
        d_m_i = data_entry.start.month - 1
        d_d_i = data_entry.start.day - 1
        d_h_i = data_entry.start.hour

        # 00:00 - 00:14 -> 0
        # 00:15 - 00:29 -> 1
        # 00:30 - 00:44 -> 2
        # 00:45 - 00:59 -> 3
        d_q_i = data_entry.start.minute // 15

        try:
            reshaped_data[d_y_i, d_m_i, d_d_i, d_h_i, d_q_i] = data_entry
        except IndexError:
            print(f'IndexError: {data_entry.start.strftime("%d.%m.%Y %H:%M")}')
        except ValueError:
            print(f'ValueError: {data_entry.start.strftime("%d.%m.%Y %H:%M")}')
        except AttributeError:
            print(f'AttributeError: {data_entry.start.strftime("%d.%m.%Y %H:%M")}')

    reshaped_data = fix_daylight_saving_time(reshaped_data)

    return reshaped_data


def fix_daylight_saving_time(data: np.ndarray) -> np.ndarray:
    missing_timestamps = {
        2020: datetime(2020, 3, 29, 2, 0),
        2021: datetime(2021, 3, 28, 2, 0),
        2022: datetime(2022, 3, 27, 2, 0)
    }

    data_2020 = interpolate_data(data[0, 2, 28, 1, 3], data[0, 2, 28, 3, 0])

    for data_entry in data_2020:
        i_y = data_entry.start.year - 2020
        i_m = data_entry.start.month - 1
        i_d = data_entry.start.day - 1
        i_h = data_entry.start.hour
        i_q = data_entry.start.minute // 15

        data[i_y, i_m, i_d, i_h, i_q] = data_entry

    data_2021 = interpolate_data(data[1, 2, 27, 1, 3], data[1, 2, 27, 3, 0])

    for data_entry in data_2021:
        i_y = data_entry.start.year - 2020
        i_m = data_entry.start.month - 1
        i_d = data_entry.start.day - 1
        i_h = data_entry.start.hour
        i_q = data_entry.start.minute // 15

        data[i_y, i_m, i_d, i_h, i_q] = data_entry

    data_2022 = interpolate_data(data[2, 2, 26, 1, 3], data[2, 2, 26, 3, 0])

    for data_entry in data_2022:
        i_y = data_entry.start.year - 2020
        i_m = data_entry.start.month - 1
        i_d = data_entry.start.day - 1
        i_h = data_entry.start.hour
        i_q = data_entry.start.minute // 15

        data[i_y, i_m, i_d, i_h, i_q] = data_entry

    return data


def interpolate_data(data_before: Data, data_after: Data) -> np.ndarray:
    # Before start is at 01:45
    # After start is at 03:00
    # Interpolate 02:00, 02:15, 02:30, and 02:45

    # 02:00 - 02:14
    data_0: Data = copy.deepcopy(data_before)
    data_0.start = data_before.start + timedelta(minutes=15)
    data_0.end = data_before.end + timedelta(minutes=15)

    # 02:15 - 02:29
    data_1: Data = copy.deepcopy(data_before)
    data_1.start = data_before.start + timedelta(minutes=30)
    data_1.end = data_before.end + timedelta(minutes=30)

    # 02:30 - 02:44
    data_2: Data = copy.deepcopy(data_before)
    data_2.start = data_before.start + timedelta(minutes=45)
    data_2.end = data_before.end + timedelta(minutes=45)

    # 02:45 - 02:59
    data_3: Data = copy.deepcopy(data_before)
    data_3.start = data_before.start + timedelta(minutes=60)
    data_3.end = data_before.end + timedelta(minutes=60)

    return np.array([data_0, data_1, data_2, data_3])

def compute_reference_year(data: np.ndarray) -> np.ndarray:
    # Get data type of data array
    data_type = None

    try:
        data_type = type(data.flatten()[0])
    except IndexError:
        print('Data array is empty.')
        sys.exit(1)
    average_data = np.empty((1,12,31,24,4), dtype=object)

    # Fill average data with empty data objects
    for month in range(0, 12):
        for day in range(0, 31):
            for hour in range(0, 24):
                for quarter in range(0, 4):
                    new_obj = data_type()
                    try:
                        new_obj.start = datetime(REFERENCE_YEAR, month + 1, day + 1, hour, quarter * 15)
                        new_obj.end = datetime(REFERENCE_YEAR, month + 1, day + 1, hour, quarter * 15 + 15)
                    except ValueError:
                        # Skip invalid date
                        pass

                    average_data[0, month, day, hour, quarter] = new_obj

    # Generate average data from structured data
    for month in range(0, 12):
        for day in range(0, 31):
            for hour in range(0, 24):
                for quarter in range(0, 4):
                    for year in range(0, 3):
                        average_data[0, month, day, hour, quarter] += data[year, month, day, hour, quarter]
                    average_data[0, month, day, hour, quarter] /= 3

    return average_data


if __name__ == '__main__':
    main()
