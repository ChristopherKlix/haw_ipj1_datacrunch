# import pandas as pd
import csv
from datetime import datetime
from datetime import date
from time import sleep, time
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from typing import List
import threading


REFERENCE_YEAR = 2030
RES_PATH = './res/'
ENERGY_PRODUCTION_CSV = 'Realisierte_Erzeugung_202001010000_202212312359_Viertelstunde.csv'
ENERGY_PRODUCTION_ROWS = 105216


def main():
    # print('\033c', end='')
    os.system('cls' if os.name == 'nt' else 'clear')

    data: np.ndarray = load_data()


    print('Data imported and parsed successfully!')

    # Print number of data entries
    print('Number of data entries:', data.size)

    structured_data: np.ndarray = reshape_data(data)

    # Print dimensions of structured data
    print('Dimensions of structured data:', structured_data.shape)

    reference_data = compute_reference_year(structured_data)

    # Print dimensions of average data
    print('Dimensions of average data:', reference_data.shape)

    # Request user input for date
    print('#' * 30)
    print('Average data tool')
    print('#' * 30)
    month = int(input('Enter month: '))
    day = int(input('Enter day: '))

    # Print average data
    print(f'Computing average data for the {day}{ordinal_suffix(day)} of {month}...')
    sleep(1)
    print('Done.')
    sleep(1)
    print('Rendering plot...')
    sleep(1)
    print('Done.')
    sleep(1)
    print('Plotting...')

    # Plot average data for the 15th of March
    # elements = reference_data[0, month-1, day-1, :, :]
    elements = structured_data[0, month-1, day-1, :, :]

    # Compute best month for pv production
    best_month = compute_best_pv_month(reference_data)

    print(f'Best month for pv production: {best_month + 1}')

    plot_day(elements)


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


def plot_day(data):
    # Merge data array into one array
    data = data.flatten()
    data /= 1_000_000
    print(f'Dim: {data.size}')
    # Duplicate last element to make the plot look nicer
    data = np.append(data, data[-1])
    print(f'Dim: {data.size}')
    # hours = [d.start.hour for d in data]
    hours = np.arange(0, 24, 0.25)
    # Add the quarter of the next day
    hours = np.append(hours, 24.0)

    print(f'First timestamp: {data[0].start}')

    pv = [d.pv for d in data]
    wind_offshore = [d.wind_offshore for d in data]
    wind_onshore = [d.wind_onshore for d in data]
    biomass = [d.biomass for d in data]
    hydro = [d.hydro for d in data]

    fossil_fuels = [d.charcoal + d.coal + d.gas + d.other_conventional for d in data]

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

    plt.xlabel('Hour of day')
    plt.ylabel('Power [MWh]')
    plt.xticks(np.arange(0, 25, 1))
    plt.xlim([0, 24])
    plt.title(f'Average energy production on the {data[0].get_day_f()} of {data[0].get_month_f()}.')
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


def load_data() -> np.ndarray:
    """
    Loads data from a CSV file and returns it as a numpy array of Data objects.

    Returns:
        np.ndarray: A numpy array of Data objects.
    """
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
    reshaped_data: np.ndarray = np.empty(matrix_dim, dtype=Data)

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

    return reshaped_data


def compute_reference_year(data: np.ndarray) -> np.ndarray:
    average_data = np.empty((1,12,31,24,4), dtype=Data)

    # Fill average data with empty data objects
    for month in range(0, 12):
        for day in range(0, 31):
            for hour in range(0, 24):
                for quarter in range(0, 4):
                    new_obj = Data()
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
