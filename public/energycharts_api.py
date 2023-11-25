# Example:
# 'https://api.energy-charts.info/total_power?country=de&start=2023-01-01T00%3A00%2B01%3A00&end=2023-01-01T23%3A45%2B01%3A00'

from dataclasses import dataclass, field
from io import TextIOWrapper
import os
import sys
from threading import Thread
from time import sleep, time
from typing import Callable, Type, TypeAlias
import requests
import datetime as dt
import json
import pandas as pd
import csv
import numpy as np
from numpy.typing import NDArray

RES_PATH = './src/static/res/'


def main():
    # Clear screen
    print('\033[H\033[J')

    # Get CLI args
    args = sys.argv[1:]

    # Check if first argument is schema
    if len(args) > 0 and args[0] == 'schema':
        schema_test_file()
        quit(0)

    start: dt.datetime = dt.datetime(2021, 1, 1, 0, 0)
    end: dt.datetime = dt.datetime(2022, 12, 31, 23, 59)

    filename: str = 'energycharts'

    # Perform request and write response to file
    # for year in range(2015, 2023):
    #     start = dt.datetime(year, 1, 1, 0, 0)
    #     end = dt.datetime(year, 12, 31, 23, 59)

    #     res = perform_request(start, end)
    #     write_json_file(res, f'{filename}_{year}.json')

    # Create CSV file
    # for year in range(2015, 2023):
    #     create_csv(f'{filename}_{year}.json')

    # Merge CSV files
    with open(f'{RES_PATH}{filename}.csv', 'w', encoding='utf-8') as outfile:
        for year in range(2015, 2023):
            with open(f'{RES_PATH}{filename}_{year}.csv', 'r', encoding='utf-8') as infile:
                # Write header
                if year == 2015:
                    outfile.write(next(infile))
                else:
                    # Skip header
                    next(infile)

                if year < 2020:
                    for line in infile:
                        outfile.write(line)
                else:
                    for line in infile:
                        # split line into columns by comma
                        columns = line.split(',')

                        # Write columns 0 to 9
                        outfile.write(','.join(columns[:9]))

                        # Insert empty column
                        outfile.write(',')
                        outfile.write(',')

                        # Write columns 10 to last
                        outfile.write(','.join(columns[9:]))


class EnergychartsAPIManager:
    BASE_URL           = 'https://api.energy-charts.info'
    POWER              = '/total_power'
    LOCALE             = '?country=de'
    START_PREFIX       = '&start='
    END_PREFIX         = '&end='

    endpoint: str      = field(default=None, init=False)
    url: str           = field(default=None, init=False)
    start: dt.datetime = field(default=None, init=False)
    end: dt.datetime   = field(default=None, init=False)

    def set_range(self, start: dt.datetime, end: dt.datetime) -> None:
        self.start = start
        self.end = end

    def perform_request(self) -> requests.Response:
        """
        Performs a request to the energycharts API and writes the response to a file.

        Args:
            start (dt.datetime): The start datetime of the requested data.
            end (dt.datetime): The end datetime of the requested data.
            filename (str): The name of the file to write the response to.

        Returns:
            float: The time elapsed during the API request.
        """

        print(f'Requesting data from {self.BASE_URL}...')

        print(f'Endpoint: {self.POWER}')
        print(f'Locale:   {self.LOCALE}')
        print(f'Start:    {self.start}')
        print(f'End:      {self.end}')

        print('-' * 50)

        # Convert dt.datetime(2023, 01, 01, 00, 00) to '2023-01-01T00%3A00%2B01%3A00'
        start_str: str = self.start.strftime('%Y-%m-%dT%H%%3A%M%%2B01%%3A00')
        end_str: str = self.end.strftime('%Y-%m-%dT%H%%3A%M%%2B01%%3A00')

        self.endpoint = self.POWER + self.LOCALE + self.START_PREFIX + start_str + self.END_PREFIX + end_str
        self.url      = self.BASE_URL + self.endpoint

        print(f'# CURL:     {self.url}')
        print('# requesting...')

        # Perform request
        timestamp_0: dt.datetime = dt.datetime.now()

        response: requests.Response = requests.get(self.url)

        timestamp_1: dt.datetime = dt.datetime.now()

        time_elapsed: dt.timedelta = timestamp_1 - timestamp_0

        print(f'# API request time: {time_elapsed}')

        if response.status_code != 200:
            print('# API invalid request.')
            quit(1)

        print('# Data successfully received.')
        print('-' * 50)

        return response

    def write_json_file(self, response: requests.Response, filename: str):
        print('# Writing data into file...')

        # Write json into file
        with open(f'{RES_PATH}{filename}', 'w', encoding='utf-8') as file:
            json.dump(response.json(), file, ensure_ascii=False, indent=4)

        print('# Data successfully written into file.')


def schema_test_file() -> None:
    """
    Creates a schema test file by performing a request to the energy charts API and saving the response to a JSON file.
    Then, it creates a CSV file from the JSON file.

    Args:
        None

    Returns:
        None
    """

    print('#' * 50)
    print('# Creating schema test file...')

    json_filename = 'energycharts_schema_test.json'

    start: dt.datetime = dt.datetime(2023, 1, 1, 0, 0)
    end: dt.datetime = dt.datetime(2023, 1, 1, 0, 59)

    manager = EnergychartsAPIManager()
    manager.set_range(start, end)
    response = manager.perform_request()
    manager.write_json_file(response, json_filename)

    print('# Schema test file successfully created.')
    print('#' * 50)

    create_csv(json_filename)


def create_csv(srcfile: str, filename: str | None=None) -> None:
    """
    Reads a JSON file containing energy production data and converts it to a CSV file.

    Args:
        srcfile (str): The name of the JSON file to read.
        filename (str, optional): The name of the CSV file to create. If not provided, the CSV file will have the same name as the JSON file with a .csv extension.

    Returns:
        None
    """

    print('Creating CSV file...')

    with open(f'{RES_PATH}{srcfile}', 'r', encoding='utf-8') as file:
        data = json.load(file)

        # Convert the JSON data to a DataFrame
        # df = pd.json_normalize(data, )
        df_list = []

        for pt in data['production_types']:
            df = pd.DataFrame(pt['data'], columns=[pt['name']], index=data['unix_seconds'])
            df_list.append(df)

        df_final = pd.concat(df_list, axis=1)

        # Reset the index and rename the index column
        df_final.reset_index(inplace=True)
        df_final.rename(columns={'index': 'unix_seconds'}, inplace=True)

        # Save the DataFrame to a CSV file
        if filename is None:
            filename = f'{srcfile.replace(".json", ".csv")}'

        df_final.to_csv(f'{RES_PATH}{filename}', index=False)

    print('CSV file successfully created.')


@dataclass(unsafe_hash=True)
class Data:
    """
    A class representing energy data.

    Attributes:
    -----------
    start : datetime.datetime
        The start datetime of the data.
    end : datetime.datetime
        The end datetime of the data.
    production : Production
        A class representing the production data.
    power : Power
        A class representing the power data.
    consumption : Consumption
        A class representing the consumption data.
    """
    start: dt.datetime             = field(default=None, init=True, kw_only=True)
    end: dt.datetime               = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.end = self.start + dt.timedelta(minutes=15)

    @dataclass(unsafe_hash=True)
    class EnergySources:
        pv: float                  = field(default=0.0, init=True, kw_only=True)
        wind_offshore: float       = field(default=0.0, init=True, kw_only=True)
        wind_onshore: float        = field(default=0.0, init=True, kw_only=True)
        biomass: float             = field(default=0.0, init=True, kw_only=True)
        hydro: float               = field(default=0.0, init=True, kw_only=True)
        other_renewables: float    = field(default=0.0, init=True, kw_only=True)
        coal: float                = field(default=0.0, init=True, kw_only=True)
        lignite: float             = field(default=0.0, init=True, kw_only=True)
        gas: float                 = field(default=0.0, init=True, kw_only=True)
        other_conventionals: float = field(default=0.0, init=True, kw_only=True)
        nuclear: float             = field(default=0.0, init=True, kw_only=True)

        def get_total_renewables(self) -> float:
            return self.pv + self.wind_offshore + self.wind_onshore + self.biomass + self.hydro + self.other_renewables

        def get_total_fossils(self) -> float:
            return self.coal + self.lignite + self.gas + self.other_conventionals

        def __add__(self, value: float):
            return self.__class__(**{k: v + value for k, v in self.__dict__.items()})

        def __sub__(self, value: float):
            return self.__class__(**{k: v - value for k, v in self.__dict__.items()})

        def __truediv__(self, value: float):
            return self.__class__(**{k: v / value for k, v in self.__dict__.items()})

        def __mul__(self, value: float):
            return self.__class__(**{k: v * value for k, v in self.__dict__.items()})

    @dataclass(unsafe_hash=True)
    class Production(EnergySources):
        ...

    production: Production         = field(default_factory=Production, init=True)

    @dataclass(unsafe_hash=True)
    class Power(EnergySources):
        ...

    power: Power                   = field(default_factory=Power, init=True)

    @dataclass(unsafe_hash=True)
    class Consumption:
        load: float                = field(default=0.0, init=True, kw_only=True)
        residual: float            = field(default=0.0, init=True, kw_only=True)

        def __add__(self, value: float):
            return self.__class__(**{k: v + value for k, v in self.__dict__.items()})

        def __sub__(self, value: float):
            return self.__class__(**{k: v - value for k, v in self.__dict__.items()})

        def __truediv__(self, value: float):
            return self.__class__(**{k: v / value for k, v in self.__dict__.items()})

        def __mul__(self, value: float):
            return self.__class__(**{k: v * value for k, v in self.__dict__.items()})

    consumption: Consumption       = field(default_factory=Consumption, init=True)


DataArray: TypeAlias = type[np.ndarray[Data]]


def merge_smard_files() -> None:
    """
    Merges the smard files into one file.

    Args:
        None

    Returns:
        None
    """
    # Step 1: Load all files
    timestamp_appendix = ('' + '2015' + '01' + '01' + '00' + '00' + '_')
    timestamp_appendix += ('2022' + '12' + '31' + '23' + '59' + '_' + 'Viertelstunde')

    production_filename = 'Realisierte_Erzeugung_'
    production_filename += timestamp_appendix
    production_filename += '.csv'

    consumption_filename = 'Realisierter_Stromverbrauch_'
    consumption_filename += timestamp_appendix
    consumption_filename += '.csv'

    power_filename = 'Installierte_Erzeugungsleistung_'
    power_filename += timestamp_appendix
    power_filename += '.csv'

    production_file  = open(f'{RES_PATH}{production_filename}', 'r', encoding='utf-8')
    consumption_file = open(f'{RES_PATH}{consumption_filename}', 'r', encoding='utf-8')
    power_file       = open(f'{RES_PATH}{power_filename}', 'r', encoding='utf-8')

    production_reader  = csv.DictReader(production_file, delimiter=';')
    consumption_reader = csv.DictReader(consumption_file, delimiter=';')
    power_reader       = csv.DictReader(power_file, delimiter=';')

    # Get headers
    production_header  = production_reader.fieldnames
    consumption_header = consumption_reader.fieldnames
    power_header       = power_reader.fieldnames

    # Write temporary files with adjusted headers
    production_outfile = open(f'{RES_PATH}_tmp_production.csv', 'w', encoding='utf-8')
    consumption_outfile = open(f'{RES_PATH}_tmp_consumption.csv', 'w', encoding='utf-8')
    power_outfile = open(f'{RES_PATH}_tmp_power.csv', 'w', encoding='utf-8')

    production_header = [
        'unix_seconds',
        'Solar',
        'Wind onshore',
        'Wind offshore',
        'Biomass',
        'Hydro',
        'Other renewables',
        'Fossil brown coal / lignite',
        'Fossil hard coal',
        'Fossil gas',
        'Other conventionals',
        'Nuclear',
        'Hydro pumped storage'
    ]

    production_outfile.write(';'.join(production_header) + '\n')

    i = 0

    print('#' * 50)
    print(f'# Writing tmp file for Production...')
    print('#' * 50)

    for row in production_reader:
        date_as_string = row['\ufeffDatum'] + ' ' + row['Anfang']
        unix_seconds = dt.datetime.strptime(date_as_string, '%d.%m.%Y %H:%M').timestamp()
        production_outfile.write(f'{round(unix_seconds)};')

        solar               = row['Photovoltaik [MWh] Originalauflösungen']
        wind_onshore        = row['Wind Onshore [MWh] Originalauflösungen']
        wind_offshore       = row['Wind Offshore [MWh] Originalauflösungen']
        biomass             = row['Biomasse [MWh] Originalauflösungen']
        hydro               = row['Wasserkraft [MWh] Originalauflösungen']
        other_renewables    = row['Sonstige Erneuerbare [MWh] Originalauflösungen']
        lignite             = row['Braunkohle [MWh] Originalauflösungen']
        coal                = row['Steinkohle [MWh] Originalauflösungen']
        gas                 = row['Erdgas [MWh] Originalauflösungen']
        other_conventionals = row['Sonstige Konventionelle [MWh] Originalauflösungen']
        nuclear             = row['Kernenergie [MWh] Originalauflösungen']
        pump_storage        = row['Pumpspeicher [MWh] Originalauflösungen']

        solar               = solar.replace('.', '').replace(',', '.')
        wind_onshore        = wind_onshore.replace('.', '').replace(',', '.')
        wind_offshore       = wind_offshore.replace('.', '').replace(',', '.')
        biomass             = biomass.replace('.', '').replace(',', '.')
        hydro               = hydro.replace('.', '').replace(',', '.')
        other_renewables    = other_renewables.replace('.', '').replace(',', '.')
        lignite             = lignite.replace('.', '').replace(',', '.')
        coal                = coal.replace('.', '').replace(',', '.')
        gas                 = gas.replace('.', '').replace(',', '.')
        other_conventionals = other_conventionals.replace('.', '').replace(',', '.')
        nuclear             = nuclear.replace('.', '').replace(',', '.')
        pump_storage        = pump_storage.replace('.', '').replace(',', '.')

        production_outfile.write(f'{solar};')
        production_outfile.write(f'{wind_onshore};')
        production_outfile.write(f'{wind_offshore};')
        production_outfile.write(f'{biomass};')
        production_outfile.write(f'{hydro};')
        production_outfile.write(f'{other_renewables};')
        production_outfile.write(f'{lignite};')
        production_outfile.write(f'{coal};')
        production_outfile.write(f'{gas};')
        production_outfile.write(f'{other_conventionals};')
        production_outfile.write(f'{nuclear};')
        production_outfile.write(f'{pump_storage}')

        production_outfile.write('\n')
        print(f'Writing row {i + 1}...', end='\r')
        i += 1

    rows = i

    print()
    print('#' * 50)
    print(f'# Writing tmp file for Power...')
    print('#' * 50)

    power_header = [
        'unix_seconds',
        'Installed solar',
        'Installed wind onshore',
        'Installed wind offshore',
        'Installed biomass',
        'Installed hydro',
        'Installed other renewables',
        'Installed fossil brown coal / lignite',
        'Installed fossil hard coal',
        'Installed fossil gas',
        'Installed other conventionals',
        'Installed nuclear'
    ]

    power_outfile.write(';'.join(power_header) + '\n')

    i = 0

    for row in power_reader:
        date_as_string = row['\ufeffDatum'] + ' ' + row['Anfang']
        unix_seconds = dt.datetime.strptime(date_as_string, '%d.%m.%Y %H:%M').timestamp()
        power_outfile.write(f'{round(unix_seconds)};')

        solar               = row['Photovoltaik [MW] Berechnete Auflösungen']
        wind_onshore        = row['Wind Onshore [MW] Berechnete Auflösungen']
        wind_offshore       = row['Wind Offshore [MW] Berechnete Auflösungen']
        biomass             = row['Biomasse [MW] Berechnete Auflösungen']
        hydro               = row['Wasserkraft [MW] Berechnete Auflösungen']
        other_renewables    = row['Sonstige Erneuerbare [MW] Berechnete Auflösungen']
        lignite             = row['Braunkohle [MW] Berechnete Auflösungen']
        coal                = row['Steinkohle [MW] Berechnete Auflösungen']
        gas                 = row['Erdgas [MW] Berechnete Auflösungen']
        other_conventionals = row['Sonstige Konventionelle [MW] Berechnete Auflösungen']
        nuclear             = row['Kernenergie [MW] Berechnete Auflösungen']

        solar              = solar.replace('.', '').replace(',', '.')
        wind_onshore       = wind_onshore.replace('.', '').replace(',', '.')
        wind_offshore      = wind_offshore.replace('.', '').replace(',', '.')
        biomass            = biomass.replace('.', '').replace(',', '.')
        hydro              = hydro.replace('.', '').replace(',', '.')
        other_renewables   = other_renewables.replace('.', '').replace(',', '.')
        lignite            = lignite.replace('.', '').replace(',', '.')
        coal               = coal.replace('.', '').replace(',', '.')
        gas                = gas.replace('.', '').replace(',', '.')
        other_conventionals = other_conventionals.replace('.', '').replace(',', '.')
        nuclear            = nuclear.replace('.', '').replace(',', '.')

        power_outfile.write(f'{solar};')
        power_outfile.write(f'{wind_onshore};')
        power_outfile.write(f'{wind_offshore};')
        power_outfile.write(f'{biomass};')
        power_outfile.write(f'{hydro};')
        power_outfile.write(f'{other_renewables};')
        power_outfile.write(f'{lignite};')
        power_outfile.write(f'{coal};')
        power_outfile.write(f'{gas};')
        power_outfile.write(f'{other_conventionals};')
        power_outfile.write(f'{nuclear}')

        power_outfile.write('\n')
        print(f'Writing row {i + 1}...', end='\r')
        i += 1

    print()
    print('#' * 50)
    print(f'# Writing tmp file for Consumption...')
    print('#' * 50)

    consumption_header = [
        'unix_seconds',
        'Load',
        'Residual load',
        'Hydro pumped storage consumption'
    ]

    consumption_outfile.write(';'.join(consumption_header) + '\n')

    i = 0

    for row in consumption_reader:
        date_as_string = row['\ufeffDatum'] + ' ' + row['Anfang']
        unix_seconds = dt.datetime.strptime(date_as_string, '%d.%m.%Y %H:%M').timestamp()
        consumption_outfile.write(f'{round(unix_seconds)};')

        load               = row['Gesamt (Netzlast) [MWh] Originalauflösungen']
        residual           = row['Residuallast [MWh] Originalauflösungen']
        pump_storage       = row['Pumpspeicher [MWh] Originalauflösungen']

        load               = load.replace('.', '').replace(',', '.')
        residual           = residual.replace('.', '').replace(',', '.')
        pump_storage       = pump_storage.replace('.', '').replace(',', '.')

        consumption_outfile.write(f'{load};')
        consumption_outfile.write(f'{residual};')
        consumption_outfile.write(f'{pump_storage}')

        consumption_outfile.write('\n')
        print(f'Writing row {i + 1}...', end='\r')
        i += 1

    print()

    production_file.close()
    production_outfile.close()
    power_file.close()
    power_outfile.close()
    consumption_file.close()
    consumption_outfile.close()

    # Reopen tmp files
    production_file  = open(f'{RES_PATH}_tmp_production.csv', 'r', encoding='utf-8')
    power_file       = open(f'{RES_PATH}_tmp_power.csv', 'r', encoding='utf-8')
    consumption_file = open(f'{RES_PATH}_tmp_consumption.csv', 'r', encoding='utf-8')

    production_file.seek(0)
    power_file.seek(0)
    consumption_file.seek(0)

    production_reader  = csv.DictReader(production_file, delimiter=';')
    power_reader       = csv.DictReader(power_file, delimiter=';')
    consumption_reader = csv.DictReader(consumption_file, delimiter=';')

    # Step 2: Generate header
    header = [
        'unix_seconds',
        'Solar',
        'Wind onshore',
        'Wind offshore',
        'Biomass',
        'Hydro',
        'Fossil brown coal / lignite',
        'Fossil hard coal',
        'Fossil gas',
        'Nuclear',
        'Other conventionals',
        'Other renewables',
        'Installed solar',
        'Installed wind onshore',
        'Installed wind offshore',
        'Installed biomass',
        'Installed hydro',
        'Installed fossil brown coal / lignite',
        'Installed fossil hard coal',
        'Installed fossil gas',
        'Installed nuclear',
        'Installed other conventionals',
        'Installed other renewables',
        'Load',
        'Residual load',
        'Hydro pumped storage consumption',
        'Hydro pumped storage'
    ]

    # Step 3: Write new file
    target_filename = 'smard.csv'

    outfile = open(f'{RES_PATH}{target_filename}', 'w', encoding='utf-8')

    writer = csv.DictWriter(outfile, fieldnames=header)

    print('#' * 50)
    print('Writing smard.csv...')
    print('#' * 50)

    writer.writeheader()

    #  Step 4: Write data

    # Skip headers
    # next(production_reader)
    # next(power_reader)
    # next(consumption_reader)

    i = 0

    while ((production_row := next(production_reader, None)) != None):
        print(f'Writing row {i + 1}...', end='\r')

        power_row = next(power_reader)
        consumption_row = next(consumption_reader)

        # Join rows
        row = {**production_row, **power_row, **consumption_row}

        writer.writerow(row)
        i += 1

    print()
    print('#' * 50)

    production_file.close()
    power_file.close()
    consumption_file.close()

    # Remove tmp files
    os.remove(f'{RES_PATH}_tmp_production.csv')
    os.remove(f'{RES_PATH}_tmp_power.csv')
    os.remove(f'{RES_PATH}_tmp_consumption.csv')

    outfile.close()


class DataNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass(unsafe_hash=True)
class TestCaseResult:
    """
    A class representing a test case result.

    Attributes:
    -----------
    description : str
        The description of the test case.
    result : bool
        The result of the test case.
    expected_value : float
        The expected value of the data to test.
    actual_value : float
        The actual value of the data to test.
    timestamp : int
        The timestamp of the data to test.

    Methods:
    --------
    None

    Raises:
    -------
    None
    """
    description: str = field(default=None, init=True)
    result: bool = field(default=None, init=True)
    expected_value: float = field(default=None, init=True)
    actual_value: float = field(default=None, init=True)
    timestamp: int = field(default=None, init=True)


@dataclass(unsafe_hash=True)
class TestCase:
    """
    A class representing a test case.

    Attributes:
    -----------
    description : str
        The description of the test case.
    timestamp : int
        The timestamp of the data to test.
    collection : Collection
        The collection to test.
    category : str
        The category of the data to test.
    value_field : str
        The value field of the data to test.
    expected_value : float
        The expected value of the data to test.
    actual_value : float
        The actual value of the data to test.

    Methods:
    --------
    evaluate() -> TestCaseResult
        Evaluates the test case and returns a TestCaseResult object.

    Raises:
    -------
    None
    """
    description: str               = field(default=None, init=True)
    timestamp: int                 = field(default=None, init=True)
    collection: Type['Collection'] = field(default=None, init=True)
    category: str                  = field(default=None, init=True)
    value_field: str               = field(default=None, init=True)
    expected_value: float          = field(default=None, init=True)
    actual_value: float            = field(default=None, init=True)

    def evaluate(self) -> TestCaseResult:
        """
        Evaluates the test case and returns a TestCaseResult object.

        Args:
            None

        Returns:
            TestCaseResult: The result of the test case.

        Raises:
            None
        """
        d = self.collection.get_by_timestamp(self.timestamp)
        value = getattr(d, self.category)
        self.actual_value = getattr(value, self.value_field)

        result = TestCaseResult()
        result.description = self.description
        result.timestamp = self.timestamp
        result.expected_value = self.expected_value
        result.actual_value = self.actual_value

        if (self.expected_value == None or self.actual_value == None):
            result.result = False

        result.result = self.expected_value == self.actual_value

        return result


@dataclass
class Collection:
    """
    A collection of Data objects.

    Attributes:
    -----------
    length (int) : The number of elements in the data array.
    data (DataArray) : The data array.
    """
    length: int                = field(default=0, init=False)
    name: str                  = field(default='n/a', init=False)
    parse_func: Callable       = field(default=None, init=False)
    test_cases: list[TestCase] = field(default_factory=list, init=False)

    def data_field() -> DataArray:
        return np.array(0, dtype=Data)

    data: DataArray = field(default_factory=data_field, init=False)

    def __init__(self, size: int=0) -> None:
        """
        Initializes a Collection object.

        Args:
            size (int, optional): The size of the data array. Defaults to 0.
        """
        self.length = size
        self.name = 'n/a'
        self.parse_func = None
        self.test_cases = list()
        self.data = np.empty(size, dtype=Data)

    def set_size(self, size: int) -> None:
        """
        Sets the size of the data array.

        Args:
            size (int): The new size of the data array.
        """
        self.data = np.empty(size, dtype=Data)

        self.length = self.data.size

    def set_name(self, name: str):
        """
        Sets the name of the collection.

        Args:
            name (str): The new name of the collection.
        """
        self.name = name

    def set_parse_func(self, func: Callable) -> None:
        """
        Sets the parse function of the collection.

        Args:
            func (Type[Data]): The new parse function of the collection.
        """
        self.parse_func = func

    def get_test_cases(self) -> list[TestCase]:
        """
        Returns the test cases of the collection.

        Returns:
            list[TestCase]: The test cases of the collection.
        """
        return self.test_cases

    def add_test_case(self, test_case: TestCase) -> None:
        """
        Adds the given test case to the collection.

        Args:
            test_case (TestCase): The test case to add to the collection.
        """
        self.test_cases.append(test_case)

    def get_all(self) -> DataArray:
        """
        Returns the entire data array.

        Returns:
            DataArray: The entire data array.
        """
        return self.data

    def get_range(self, start: dt.datetime, end: dt.datetime) -> DataArray:
        """
        Returns a subset of the data array based on the given start and end datetimes.

        Args:
            start (dt.datetime): The starting datetime of the subset.
            end (dt.datetime): The ending datetime of the subset.

        Returns:
            DataArray: A subset of the data array.
        """
        return DataArray([d for d in self.data if d.start >= start and d.end <= end])

    def get(self, start: dt.datetime, unsafe_return: bool = False) -> Data | None:
        """
        Returns the data at the given start datetime.

        Args:
            start (dt.datetime): The start datetime of the data to return.
            unsafe_return (bool, optional): If True, the function will return None if no data was found. Defaults to False.

        Returns:
            Data | None: The data at the given start datetime or None if no data was found and unsafe_return is True.

        Raises:
            DataNotFoundException: If no data was found for the given start datetime and unsafe_return is False.
        """
        data: Data | None = next((d for d in self.data if d.start == start), None)

        if data is None and not unsafe_return:
            raise DataNotFoundException(f'No data found for start datetime {start}')

        return data

    def get_by_timestamp(self, start: int, unsafe_return: bool = False) -> Data | None:
        """
        Returns the data at the given start timestamp.

        Args:
            start (int): The start timestamp of the data to return.
            unsafe_return (bool, optional): If True, the function will return None if no data was found. Defaults to False.

        Returns:
            Data | None: The data at the given start timestamp or None if no data was found and unsafe_return is True.

        Raises:
            DataNotFoundException: If no data was found for the given start timestamp and unsafe_return is False.
        """
        start = dt.datetime.fromtimestamp(start)

        data: Data | None = next((d for d in self.data if d.start == start), None)

        if data is None and not unsafe_return:
            raise DataNotFoundException(f'No data found for start datetime {start}')

        return data

    def get_by_index(self, index: int, unsafe_return: bool = False) -> Data | None:
        """
        Returns the data at the given index.

        Args:
            index (int): The index of the data to return.
            unsafe_return (bool, optional): If True, the function will return None if the index is out of range. Defaults to False.

        Returns:
            Data | None: The data at the given index or None if the index is out of range and unsafe_return is True.

        Raises:
            DataNotFoundException: If the index is out of range and unsafe_return is False.
        """
        try:
            return self.data[index]
        except IndexError as _:
            if not unsafe_return:
                raise DataNotFoundException(f'No data found for index {index}')
            else:
                return None

    def get_by_index_range(self, start: int, end: int) -> DataArray:
        """
        Returns a subset of the data array based on the given start and end indices.

        Args:
            start (int): The starting index of the subset.
            end (int): The ending index of the subset.

        Returns:
            DataArray: A subset of the data array.
        """
        return self.data[start:end]

    def get_length(self) -> int:
        """
        Returns the number of elements in the data array.

        Returns:
        int: The number of elements in the data array.
        """
        return self.data.size

    def add(self, data: Data) -> None:
        """
        Adds the given data at the end of the Collection.

        Args:
            data: The data to add to the array.
        """
        self.data = np.append(self.data, data)

        self.length = self.data.size

    def insert(self, data: Data, index: int) -> None:
        """
        Inserts the given data at the given index of the Collection.

        Args:
            data: The data to insert into the array.
            index: The index at which the data will be inserted.

        Raises:
            IndexError: If the given index is out of range.
        """
        try:
            self.data[index] = data
        except IndexError as e:
            raise IndexError(f'Index {index} is out of range. This Collection only has {self.data.size} elements.') from e

        self.length = self.data.size

    def append(self, data: DataArray) -> None:
        """
        Appends the given data to the end of the Collection.

        Args:
            data: The data to append to the array.
        """
        self.data = np.append(self.data, data)

        self.length = self.data.size

    def remove(self, data: Data) -> bool:
        """
        Removes the given data from the Collection.

        Args:
            data: The data to remove from the array.

        Returns:
            bool: True if the data was found and removed, False otherwise.
        """
        prev_length = self.data.size

        self.data = np.delete(self.data, np.where(self.data == data))

        self.length = self.data.size

        return prev_length != self.data.size

    def remove_by_start(self, start: dt.datetime) -> bool:
        """
        Removes the data with the given start datetime from the Collection.

        Args:
            start (dt.datetime): The start datetime of the data to remove.

        Returns:
            bool: True if the data was found and removed, False otherwise.
        """
        prev_length = self.data.size

        self.data = np.delete(self.data, np.where(self.data.start == start))

        self.length = self.data.size

        return prev_length != self.data.size

    def set(self, data: DataArray) -> int:
        """
        Sets the entire content of the Collection to the given data.
        All previous data will be overwritten.

        Args:
            data (DataArray): The data to set.

        Returns:
            int: The length of the new data.
        """
        self.data = data

        self.length = self.data.size

        return self.length


@dataclass
class Collections:
    smard: Collection            = field(default_factory=Collection, init=False)
    energycharts: Collection     = field(default_factory=Collection, init=False)
    agora: Collection            = field(default_factory=Collection, init=False)

    def __post_init__(self) -> None:
        self.smard.set_name('smard')
        self.energycharts.set_name('energycharts')
        self.agora.set_name('agora')

        self.smard.set_parse_func(Parser.parse_smard)
        self.energycharts.set_parse_func(Parser.parse_energycharts)
        # self.agora.set_parse_func(parse_agora)

        self.set_test_cases()

    def set_test_cases(self) -> None:
        test_case: TestCase = TestCase(
            description='Solar value',
            timestamp=int(dt.datetime(2016, 3, 1, 15, 15).timestamp()),
            collection=self.smard,
            category='production',
            value_field='pv',
            expected_value=1156.25 * 1_000_000
        )

        self.smard.add_test_case(test_case)

        test_case = TestCase(
            description='Load value',
            timestamp=int(dt.datetime(2022, 8, 31, 3, 45).timestamp()),
            collection=self.smard,
            category='consumption',
            value_field='load',
            expected_value=10300.5 * 1_000_000
        )

        self.smard.add_test_case(test_case)

        test_case = TestCase(
            description='Wind onshore',
            timestamp=int(dt.datetime(2022, 8, 31, 3, 45).timestamp()),
            collection=self.smard,
            category='production',
            value_field='wind_onshore',
            expected_value=1769.75 * 1_000_000
        )

        self.smard.add_test_case(test_case)


class Parser:
    @staticmethod
    def parse_energycharts(vals: dict) -> Data:
        """
        Parses the given dictionary and returns a Data object.

        Args:
            vals (dict): The dictionary to parse.

        Returns:
            Data: The parsed Data object.
        """
        start = dt.datetime.fromtimestamp(int(vals['unix_seconds']))
        data = Data(start=start)

        try:
            data.production.pv                  = float(vals['Solar'])
            data.production.wind_offshore       = float(vals['Wind offshore'])
            data.production.wind_onshore        = float(vals['Wind onshore'])
            data.production.biomass             = float(vals['Biomass'])
            data.production.hydro               = float(vals['Hydro Run-of-River']) + float(vals['Hydro water reservoir'])
            data.production.other_renewables    = float(vals['Geothermal'])
            data.production.coal                = float(vals['Fossil hard coal'])
            data.production.lignite             = float(vals['Fossil brown coal / lignite'])
            data.production.gas                 = float(vals['Fossil gas'])
            data.production.other_conventionals = float(vals['Fossil oil']) + float(vals['Others']) + float(vals['Waste'])
            data.production.nuclear             = float(vals['Nuclear'])

            # Multiply by 1_000_000 to convert from MW to W
            data.production *= 1_000_000

            # Divide by 4 to convert from MW to MW/h
            data.production /= 4

            data.consumption.load               = float(vals['Load'])
            data.consumption.residual           = float(vals['Residual load'])

            # Multiply by 1_000_000 to convert from MW to W
            data.consumption *= 1_000_000

            # Divide by 4 to convert from MW to MW/h
            data.consumption /= 4

        except KeyError as e:
            print(f'KeyError: {e}')
        finally:
            return data

    @staticmethod
    def parse_smard(vals: dict) -> Data:
        """
        Parses the given dictionary and returns a Data object.

        Args:
            vals (dict): The dictionary to parse.

        Returns:
            Data: The parsed Data object.
        """
        start = dt.datetime.fromtimestamp(int(vals['unix_seconds']))
        data = Data(start=start)

        try:
            data.production.pv                  = float(vals['Solar'])
            data.production.wind_offshore       = float(vals['Wind offshore'])
            data.production.wind_onshore        = float(vals['Wind onshore'])
            data.production.biomass             = float(vals['Biomass'])
            data.production.hydro               = float(vals['Hydro'])
            data.production.other_renewables    = float(vals['Other renewables'])
            data.production.coal                = float(vals['Fossil hard coal'])
            data.production.lignite             = float(vals['Fossil brown coal / lignite'])
            data.production.gas                 = float(vals['Fossil gas'])
            data.production.other_conventionals = float(vals['Other conventionals'])
            data.production.nuclear             = float(vals['Nuclear'])

            # Multiply by 1_000_000 to convert from MWh to Wh
            data.production *= 1_000_000

            data.power.pv                 = float(vals['Installed solar'])
            data.power.wind_offshore      = float(vals['Installed wind offshore'])
            data.power.wind_onshore       = float(vals['Installed wind onshore'])
            data.power.biomass            = float(vals['Installed biomass'])
            data.power.hydro              = float(vals['Installed hydro'])
            data.power.other_renewables   = float(vals['Installed other renewables'])
            data.power.coal               = float(vals['Installed fossil hard coal'])
            data.power.lignite            = float(vals['Installed fossil brown coal / lignite'])
            data.power.gas                = float(vals['Installed fossil gas'])
            data.power.other_conventionals = float(vals['Installed other conventionals'])
            data.power.nuclear            = float(vals['Installed nuclear'])

            # Multiply by 1_000_000 to convert from MWh to Wh
            data.power *= 1_000_000

            data.consumption.load               = float(vals['Load'])
            data.consumption.residual           = float(vals['Residual load'])

            # Multiply by 1_000_000 to convert from MWh to Wh
            data.consumption *= 1_000_000

        except KeyError as e:
            print(f'KeyError: {e}')
        finally:
            return data


@dataclass
class DataManager:
    collections: Collections     = field(default_factory=Collections, init=False)

    def load_data(self, use_cached: bool=True) -> None:
        if not use_cached:
            merge_smard_files()

        self.load_dataset(self.collections.smard)
        self.test_dataset(self.collections.smard)
        self.load_dataset(self.collections.energycharts)

    def get_filepath(self, collection: Collection) -> str:
        return f'{RES_PATH}{collection.name}.csv'

    def load_dataset(self, collection: Collection) -> None:
        try:
            file = open(self.get_filepath(collection), 'r', encoding='utf-8')
        except FileNotFoundError as e:
            print(f'FileNotFoundError: {e}')
            return

        reader = csv.DictReader(file)

        row_count = 0
        row_count = DataManager.count_rows(file)

        collection.set_size(row_count)

        load_times = np.empty(row_count, dtype=float)

        print('#' * 50)
        print(f'Loading data for {collection.name}')

        i: int = 0

        total_start_time = time()

        for row in reader:
            start_time = time()
            print(f'Parsing data for {i + 1}/{row_count}...', end='\n')
            print('[', end='')
            print('\033[94m', end='')
            print('#' * round(i / row_count * 50), end='')
            print('\033[0m', end='')
            print(' ' * (50 - round(i / row_count * 50)), end='')
            print(']', end='')

            d: Data = collection.parse_func(row)

            # Slow way
            # Takes about 4 minutes
            # self.collections.energycharts.add(d)

            # Fast way
            # Takes about 3 seconds
            collection.insert(d, i)

            end_time = time()
            # Print elapsed time in nanoseconds
            time_elapsed = (end_time - start_time) * 1_000_000
            load_times[i] = time_elapsed

            print(f' {round(time_elapsed, 2)} µs       ', end='')
            print('\033[1A', end='')
            print('\033[0G', end='')
            i += 1

        print('\033[1B', end='')
        print('\033[23G', end='')
        print(' DONE ', end='')

        print('\033[60G', end='\n')
        print('#' * 50)
        print(f'# \033[1mSummary\033[0m')
        print('#')

        total_end_time = time()

        print(f'# Loaded {row_count} rows.')
        total_elapsed_time = total_end_time - total_start_time
        print(f'# Total time:        {round(total_elapsed_time, 2)} s')


        avg_load_time = np.average(load_times)
        print(f'# Average load time: {round(avg_load_time, 2)} µs')

        print('#' * 50)

        # Get first entry
        first_entry = collection.get_by_index(0)

        print(f'# First entry: {first_entry.start}')

        # Get last entry
        last_entry = collection.get_by_index(row_count - 1)

        print(f'# Last entry:  {last_entry.start}')

        print('#' * 50)

        file.close()

    def test_dataset(self, collection: Collection) -> bool:
        print('#' * 50)
        print('# \033[1mUnit Testing\033[0m')

        # if collection == (c :=self.collections.smard):
        for test_case in collection.get_test_cases():
            self.print_test(test_case.evaluate())

            # start = dt.datetime(2016, 3, 1, 15, 15)
            # d = c.get(start=start)

            # self.print_test(
            #     label='Solar value',
            #     unix_seconds=int(start.timestamp()),
            #     test_value=d.production.pv,
            #     check_value=1156.25 * 1_000_000
            # )


            # start = dt.datetime(2022, 8, 31, 3, 45)
            # d = c.get(start=start)

            # self.print_test(
            #     label='Load value',
            #     unix_seconds=int(start.timestamp()),
            #     test_value=d.consumption.load,
            #     check_value=10300.5 * 1_000_000
            # )

            # What do I need?
            # - Data at a specific time
            # - The collection
            # - The expected value
            # - The category
            # - The value
            # start = dt.datetime(2022, 8, 31, 3, 45)
            # d = c.get(start=start)
            # test_value = getattr(d, 'production', None)
            # test_value = getattr(test_value, 'wind_onshore', None)

            # self.print_test(
            #     label='Wind onshore',
            #     unix_seconds=int(start.timestamp()),
            #     # test_value=d.production.wind_onshore,
            #     test_value=test_value,
            #     check_value=1769.75 * 1_000_000
            # )

        print('#' * 50)

    def print_test(self, test_result: TestCaseResult) -> None:
        print('#')
        print('# case:')
        print(f'# {test_result.description}')
        print(f'# unix_seconds: {test_result.timestamp}', end='')
        print(' ' * 4, end='')
        print('✅ Succeeded' if test_result.result else '❌ Failed')
        print(f'#     expected: {test_result.expected_value}')
        print(f'#           is: {test_result.actual_value}')
        print('#')

    @staticmethod
    def count_rows(file: TextIOWrapper) -> int:
        reader = csv.DictReader(file)

        row_count = 0

        for _ in reader:
            row_count += 1

        file.seek(0)

        return row_count


def show_loading_animation() -> Thread:
    # Start new thread for loading animation
    loading_thread = Thread(target=loading_animation, daemon=True)
    loading_thread.start()

    return loading_thread


def loading_animation() -> None:
    while True:
        print('[    ]', end='', flush=True)
        print('\033[5D', end='', flush=True)
        print('-   ', end='', flush=True)
        print('\033[4D', end='', flush=True)
        sleep(0.1)
        print(' -  ', end='', flush=True)
        print('\033[4D', end='', flush=True)
        sleep(0.1)
        print('  - ', end='', flush=True)
        print('\033[4D', end='', flush=True)
        sleep(0.1)
        print('   -', end='', flush=True)
        print('\033[4D', end='', flush=True)
        sleep(0.1)
        print('\033[1D', end='', flush=True)


if __name__ == "__main__":
    main()

    # merge_smard_files()

    exit(0)

    loader = DataManager()

    loader.load_data()

    energycharts_data: Collection = loader.collections.energycharts

    data = energycharts_data.get_all()

    l = energycharts_data.get_length()

    print(f'Length: {l}')

    test_data: Data = energycharts_data.get(dt.datetime(2021, 10, 5, 15, 15))

    print(f'Start:         {test_data.start}')
    print(f'Wind Offshore: {test_data.production.wind_offshore}')
    print(f'Load:          {test_data.consumption.load}')
