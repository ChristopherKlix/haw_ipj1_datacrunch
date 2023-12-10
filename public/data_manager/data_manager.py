from dataclasses import dataclass, field
from io import TextIOWrapper
import os
import sys
from threading import Thread
from time import sleep, time, perf_counter
from typing import Callable, Type, TypeAlias
import datetime as dt
from pytz import timezone
import csv
import numpy as np
from numpy.typing import NDArray

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
        @property
        def total(self) -> float:
            return sum([v for v in self.__dict__.values()])

        @property
        def total_renewables(self) -> float:
            return self.get_total_renewables()

        @property
        def total_fossils(self) -> float:
            return self.get_total_fossils()

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

    def __add__(self, value: float):
        raise NotImplementedError('Addition is not supported for Data objects.')

    def __sub__(self, value: float):
        raise NotImplementedError('Subtraction is not supported for Data objects.')

    def __truediv__(self, value: float):
        # Call the __truediv__ of production, power, and consumption
        # and return a new Data object
        return self.__class__(
            start=self.start,
            production=self.production / value,
            power=self.power / value,
            consumption=self.consumption / value
        )

    def __mul__(self, value: float):
        raise NotImplementedError('Multiplication is not supported for Data objects.')


DataArray: TypeAlias = type[np.ndarray[Data]]


class DataNotFoundException(Exception):
    """
    A class representing a data not found exception.
    """
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
        result = TestCaseResult()
        result.description = self.description
        result.timestamp = self.timestamp
        result.expected_value = self.expected_value
        result.actual_value = self.actual_value

        try:
            d = self.collection.get_by_timestamp(self.timestamp)
        except DataNotFoundException as e:
            result.result = False
            return result

        value = getattr(d, self.category)
        result.actual_value = getattr(value, self.value_field)


        if (result.expected_value == None or result.actual_value == None):
            result.result = False

        result.result = result.expected_value == result.actual_value

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

    def __iter__(self) -> iter:
        """
        Returns an iterator for the data array.

        Returns:
            Data: An iterator for the data array.
        """
        return iter(self.data)

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
        data_as_list = [d for d in self.data if d.start >= start and d.start <= end]
        data_as_NDArray = np.array(data_as_list, dtype=Data)
        return data_as_NDArray


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

    def get_year(self, year: int) -> NDArray:
        """
        Returns the data for the given year.

        Args:
            year (dt.datetime): The year of the data to return.

        Returns:
            DataArray: The data for the given year.
        """
        start = dt.datetime(year, 1, 1, 0, 0)
        end = dt.datetime(year, 12, 31, 23, 59)
        return self.get_range(start, end)

    def get_month(self, year: int, month: int) -> NDArray:
        """
        Returns the data for the given month.

        Args:
            year (dt.datetime): The year of the data to return.
            month (dt.datetime): The month of the data to return.

        Returns:
            DataArray: The data for the given month.
        """
        start = dt.datetime(year, month, 1, 0, 0)
        end = dt.datetime(year, month, 31, 23, 59)
        return self.get_range(start, end)

    def get_day(self, year: int, month: int, day: int) -> NDArray:
        """
        Returns the data for the given day.

        Args:
            year (dt.datetime): The year of the data to return.
            month (dt.datetime): The month of the data to return.
            day (dt.datetime): The day of the data to return.

        Returns:
            DataArray: The data for the given day.
        """
        start = dt.datetime(year, month, day, 0, 0)
        end = dt.datetime(year, month, day, 23, 59)
        return self.get_range(start, end)

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

    def get_last_of_year(self, year: int) -> Data:
        """
        Returns the last data of the given year.

        Args:
            year (int): The year of the data to return.

        Returns:
            Data: The last data of the given year.
        """
        year: DataArray = self.get_year(year)
        return year[-1]

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
    """
    A class representing a collection of Collections.

    Attributes:
    -----------
    smard (Collection) : The smard collection.
    energycharts (Collection) : The energycharts collection.
    agora (Collection) : The agora collection.

    Methods:
    --------
    set_test_cases() -> None
        Sets the test cases for the collections.
    """
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
        """
        Sets the test cases for the collections.

        Args:
            None

        Returns:
            None
        """
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

        # Jannik
        test_cases = [
            TestCase(
                description='Production lignite',
                timestamp=int(dt.datetime(year=2022, month=12, day=13, hour=12, minute=0).timestamp()),
                collection=self.smard,
                category='production',
                value_field='lignite',
                expected_value=3931.75 * 1_000_000
            ),
            TestCase(
                description='Production PV',
                timestamp=int(dt.datetime(year=2021, month=3, day=12, hour=14, minute=15).timestamp()),
                collection=self.smard,
                category='production',
                value_field='pv',
                expected_value=3727.75 * 1_000_000
            ),
            TestCase(
                description='Production Other Renewables',
                timestamp=int(dt.datetime(year=2018, month=11, day=23, hour=22, minute=30).timestamp()),
                collection=self.smard,
                category='production',
                value_field='other_renewables',
                expected_value=38.25 * 1_000_000
            ),
            TestCase(
                description='Production On-Shore',
                timestamp=int(dt.datetime(year=2017, month=2, day=8, hour=9, minute=0).timestamp()),
                collection=self.smard,
                category='production',
                value_field='wind_onshore',
                expected_value=1836.5 * 1_000_000
            ),
            TestCase(
                description='Poduction Gas',
                timestamp=int(dt.datetime(year=2020, month=7, day=27, hour=3, minute=15).timestamp()),
                collection=self.smard,
                category='production',
                value_field='gas',
                expected_value=2108.25 * 1_000_000
            ),
            TestCase(
                description='Consumption Load',
                timestamp=int(dt.datetime(year=2020, month=9, day=15, hour=16, minute=0).timestamp()),
                collection=self.smard,
                category='consumption',
                value_field='load',
                expected_value=15560.5 * 1_000_000
            ),
            TestCase(
                description='Consumption Load',
                timestamp=int(dt.datetime(year=2019, month=2, day=25, hour=14, minute=45).timestamp()),
                collection=self.smard,
                category='consumption',
                value_field='load',
                expected_value=16548.75 * 1_000_000
            ),
            TestCase(
                description='Consumption Load',
                timestamp=int(dt.datetime(year=2016, month=5, day=3, hour=12, minute=30).timestamp()),
                collection=self.smard,
                category='consumption',
                value_field='load',
                expected_value=17392.75 * 1_000_000
            ),
        ]

        for test_case in test_cases:
            self.smard.add_test_case(test_case)

        # Adrian
        #DST Timestamp for 2015/03/29/2:00-3:00 doesn't exist
        test_cases = [
            TestCase(
                description='Power lignite DST',
                timestamp=int(dt.datetime(year=2015, month=3, day=29, hour=4, minute=0).timestamp()),
                collection=self.smard,
                category='power',
                value_field='lignite',
                expected_value=21160 * 1_000_000
            ),
            #DST 2 values -> fail ( timechange 3 -> 2)
            TestCase(
                description='Production hydro DST 25.10',
                timestamp=int(dt.datetime(year=2015, month=10, day=25, hour=2, minute=0).timestamp()),
                collection=self.smard,
                category='production',
                value_field='hydro',
                expected_value=311.75 * 1_000_000
            ),

            TestCase(
                description='Production hydro SHOULD FAIL!',
                timestamp=int(dt.datetime(year=2015, month=10, day=25, hour=2, minute=0).timestamp()),
                collection=self.smard,
                category='production',
                value_field='hydro',
                expected_value=321.25 * 1_000_000
            ),

            TestCase(
                description='Production gas DST 27.03.16',
                timestamp=int(dt.datetime(year=2016, month=3, day=27, hour=6, minute=30).timestamp()),
                collection=self.smard,
                category='production',
                value_field='gas',
                expected_value=267.5 * 1_000_000
            ),

            TestCase(
                description='Power offshore DST 30.10.16',
                timestamp=int(dt.datetime(year=2016, month=10, day=30, hour=6, minute=30).timestamp()),
                collection=self.smard,
                category='power',
                value_field='wind_offshore',
                expected_value=3283 * 1_000_000
            ),

            TestCase(
                description='Production onshore DST 27.03.17',
                timestamp=int(dt.datetime(year=2017, month=3, day=26, hour=16, minute=45).timestamp()),
                collection=self.smard,
                category='production',
                value_field='wind_onshore',
                expected_value=543.75 * 1_000_000
            ),

            TestCase(
                description='Power nuclear DST 29.10.17',
                timestamp=int(dt.datetime(year=2017, month=10, day=29, hour=16, minute=45).timestamp()),
                collection=self.smard,
                category='power',
                value_field='nuclear',
                expected_value=10793 * 1_000_000
            ),


                TestCase(
                description='Production onshore DST 28.10.18',
                timestamp=int(dt.datetime(year=2018, month=10, day=28, hour=23, minute=00).timestamp()),
                collection=self.smard,
                category='production',
                value_field='pv',
                expected_value=0 * 1_000_000
            ),

            TestCase(
                description='Power other_conventionals DST 25.3.18',
                timestamp=int(dt.datetime(year=2018, month=3, day=25, hour=23, minute=0).timestamp()),
                collection=self.smard,
                category='power',
                value_field='other_conventionals',
                expected_value=7375 * 1_000_000
            ),

                TestCase(
                description='Production onshore DST 31.3.19',
                timestamp=int(dt.datetime(year=2019, month=3, day=31, hour=15, minute=15).timestamp()),
                collection=self.smard,
                category='production',
                value_field='biomass',
                expected_value=1206.5 * 1_000_000
            ),

            TestCase(
                description='Power hydro DST 27.10.19',
                timestamp=int(dt.datetime(year=2019, month=10, day=27, hour=15, minute=15).timestamp()),
                collection=self.smard,
                category='power',
                value_field='hydro',
                expected_value=5281 * 1_000_000
            ),

                    TestCase(
                description='Production other_renewables DST 29.3.2020',
                timestamp=int(dt.datetime(year=2020, month=3, day=29, hour=8, minute=0).timestamp()),
                collection=self.smard,
                category='production',
                value_field='other_renewables',
                expected_value=42.5 * 1_000_000
            ),

            TestCase(
                description='Power other_renewables DST 25.10.20',
                timestamp=int(dt.datetime(year=2020, month=10, day=25, hour=8, minute=0).timestamp()),
                collection=self.smard,
                category='power',
                value_field='other_renewables',
                expected_value=454 * 1_000_000
            ),

                    TestCase(
                description='Production other_renewables DST 29.3.2020',
                timestamp=int(dt.datetime(year=2020, month=3, day=29, hour=8, minute=0).timestamp()),
                collection=self.smard,
                category='production',
                value_field='other_renewables',
                expected_value=42.5 * 1_000_000
            ),

            TestCase(
                description='Power other_renewables DST 25.10.20',
                timestamp=int(dt.datetime(year=2020, month=10, day=25, hour=8, minute=0).timestamp()),
                collection=self.smard,
                category='power',
                value_field='other_renewables',
                expected_value=454 * 1_000_000
            ),

                TestCase(
                description='Production onshore DST 28.3.2021',
                timestamp=int(dt.datetime(year=2021, month=3, day=28, hour=1, minute=30).timestamp()),
                collection=self.smard,
                category='production',
                value_field='wind_onshore',
                expected_value=4247.5 * 1_000_000
            ),

            TestCase(
                description='Power biomass DST 31.10.2021',
                timestamp=int(dt.datetime(year=2021, month=10, day=31, hour=1, minute=30).timestamp()),
                collection=self.smard,
                category='power',
                value_field='biomass',
                expected_value=8400 * 1_000_000
            ),

                TestCase(
                description='Production  other_conventionals DST 27.3.2022',
                timestamp=int(dt.datetime(year=2022, month=3, day=27, hour=0, minute=0).timestamp()),
                collection=self.smard,
                category='production',
                value_field='other_conventionals',
                expected_value=337.25 * 1_000_000
            ),

            TestCase(
                description='Power lignite DST 30.10.2022',
                timestamp=int(dt.datetime(year=2022, month=10, day=30, hour=0, minute=0).timestamp()),
                collection=self.smard,
                category='power',
                value_field='lignite',
                expected_value=18544 * 1_000_000
            )
        ]

        for test_case in test_cases:
            self.smard.add_test_case(test_case)

        # new year
        test_cases = [
            TestCase(
                description='Production wind onshore new year',
                timestamp=int(dt.datetime(year=2021, month=12, day=31, hour=23, minute=45).timestamp()),
                collection=self.smard,
                category='production',
                value_field='wind_onshore',
                expected_value=6424.75 * 1_000_000
            ),
            TestCase(
                description='Production wind_onshore new year',
                timestamp=int(dt.datetime(year=2022, month=1, day=1, hour=0, minute=0).timestamp()),
                collection=self.smard,
                category='production',
                value_field='wind_onshore',
                expected_value=6433.75 * 1_000_000
            ),
        ]

        for test_case in test_cases:
            self.smard.add_test_case(test_case)


class Parser:
    """
    A class representing a parser.

    Attributes:
    -----------
    None

    Methods:
    --------
    parse_energycharts(vals: dict) -> Data
        Parses the given dictionary and returns a Data object.
    parse_smard(vals: dict) -> Data
        Parses the given dictionary and returns a Data object.
    """
    @staticmethod
    def parse_energycharts(vals: dict) -> Data:
        """
        Parses the given dictionary and returns a Data object.

        Args:
            vals (dict): The dictionary to parse.

        Returns:
            Data: The parsed Data object.
        """
        # tz = timezone('Europe/Berlin')
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
        tz = timezone('Europe/Berlin')
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

            data.power.pv                  = float(vals['Installed solar'])
            data.power.wind_offshore       = float(vals['Installed wind offshore'])
            data.power.wind_onshore        = float(vals['Installed wind onshore'])
            data.power.biomass             = float(vals['Installed biomass'])
            data.power.hydro               = float(vals['Installed hydro'])
            data.power.other_renewables    = float(vals['Installed other renewables'])
            data.power.coal                = float(vals['Installed fossil hard coal'])
            data.power.lignite             = float(vals['Installed fossil brown coal / lignite'])
            data.power.gas                 = float(vals['Installed fossil gas'])
            data.power.other_conventionals = float(vals['Installed other conventionals'])
            data.power.nuclear             = float(vals['Installed nuclear'])

            # Multiply by 1_000_000 to convert from MWh to Wh
            data.power *= 1_000_000

            data.consumption.load               = float(vals['Load'])
            data.consumption.residual           = float(vals['Residual load'])

            # Multiply by 1_000_000 to convert from MWh to Wh
            data.consumption *= 1_000_000

        except KeyError as e:
            print(f'KeyError: {e}')

        return data


@dataclass
class DataManager:
    """
    A class representing a data manager.
    It is used to load data from CSV files into the collections.

    Attributes:
    -----------
    collections (Collections) : The collections of the data manager.
    res_path (str) : The path to the resources directory.

    Methods:
    --------
    get_data() -> Collections
        Returns the collections of the data manager.
    load_data() -> None
        Loads the data from the CSV files into the collections.
    get_filepath(collection: Collection) -> str
        Returns the filepath of the given collection.
    load_dataset(collection: Collection) -> None
        Loads the data from the CSV file into the given collection.
    test_dataset(collection: Collection) -> bool
        Tests the given collection.
    print_test(test_result: TestCaseResult) -> None
        Prints the given test result.
    count_rows(file: TextIOWrapper) -> int
        Counts the number of rows in the given file.

    Raises:
    -------
    None
    """
    collections: Collections = field(default_factory=Collections, init=False)
    res_path: str            = field(default='./static/res/', init=False)
    is_cached: bool          = field(default=False, init=False)

    def get_data(self) -> Collections:
        if not self.is_cached:
            self.load_data()

        return self.collections

    def load_data(self) -> None:
        if self.is_cached:
            return

        self.load_dataset(self.collections.smard)
        self.test_dataset(self.collections.smard)
        self.load_dataset(self.collections.energycharts)

        self.is_cached = True

    def get_filepath(self, collection: Collection) -> str:
        return f'{self.res_path}{collection.name}.csv'

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

        sys.stdout.flush()

    def test_dataset(self, collection: Collection) -> bool:
        print('#' * 50)
        print('# \033[1mUnit Testing\033[0m')

        # if collection == (c :=self.collections.smard):
        for test_case in collection.get_test_cases():
            self.print_test(test_case.evaluate())

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
