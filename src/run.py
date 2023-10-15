# import pandas as pd
import csv
from datetime import datetime


def main():
    data = set()

    with open('./res/Realisierte_Erzeugung_202001010000_202212312359_Viertelstunde.csv', 'r') as file:
        reader = csv.reader(file, delimiter=';')

        # Skip first row
        next(reader)

        for row in reader:
            data_entry = Data(row)
            data.add(data_entry)
    # file is automatically closed after the with block

    # Print number of data entries
    print('Number of data entries:', len(data))

    # Print average PV output
    print('Average PV Power Output in MWh:', sum([d.pv for d in data]) / len(data) / 1_000_000)

    # Print average PV output in 2020
    print('Average PV Power Output in 2020 in MWh:', sum([d.pv for d in data if d.start.year == 2020]) / len([d for d in data if d.start.year == 2020]) / 1_000_000)

    # Print average PV output in 2021
    print('Average PV Power Output in 2021 in MWh:', sum([d.pv for d in data if d.start.year == 2021]) / len([d for d in data if d.start.year == 2021]) / 1_000_000)

    # Print average PV output in 2022
    print('Average PV Power Output in 2022 in MWh:', sum([d.pv for d in data if d.start.year == 2022]) / len([d for d in data if d.start.year == 2022]) / 1_000_000)


class Data:
    def __init__(self, values):
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

        print('Data object created')


if __name__ == '__main__':
    main()
