import csv
import numpy as np
import datetime as dt

import data as data_loader


def main():
    prod_data, cons_data = data_loader.main()

    for year in range(0, 3):
        for month in range(0, 12):
            for day in range(0, 31):
                for hour in range(0, 24):
                    for quarter in range(0, 4):
                        prod = prod_data[year][month][day][hour][quarter].total_renewables()
                        load = cons_data[year][month][day][hour][quarter].total_load

                        if load == 0:
                            continue

                        ratio = prod / load

                        timestamp: dt = prod_data[year][month][day][hour][quarter].start

                        if ratio >= 1.0:
                            print(f"Ratio: {ratio} at {timestamp}")

if __name__ == '__main__':
    main()