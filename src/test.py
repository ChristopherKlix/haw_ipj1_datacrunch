import csv
import matplotlib.pyplot as plt
from datetime import datetime

input_date = input("DD.MM.YYYY: ")

def parse_datetime(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str}", '%d.%m.%Y %H:%M')

csv_datei = '/Users/christopherklix/Code/haw_ipj1_datacrunch/res/Realisierte_Erzeugung_202001010000_202212312359_Viertelstunde.csv'
csv_datei2 = '/Users/christopherklix/Code/haw_ipj1_datacrunch/res/Realisierter_Stromverbrauch_202001010000_202212312359_Viertelstunde.csv'

energie_daten = []
energie_daten2 = []
production = []
consumption = []

with open(csv_datei, 'r') as file:
    csv_reader = csv.reader(file, delimiter=';')
    next(csv_reader)
    for row in csv_reader:
        datum = row[0]
        print(datum)
        anfang = row[1]
        ende = row[2]
        biomasse = float(row[3].replace('.', '').replace(',', '.'))
        wasserkraft = float(row[4].replace('.', '').replace(',', '.'))
        wind_offshore = float(row[5].replace('.', '').replace(',', '.'))
        wind_onshore = float(row[6].replace('.', '').replace(',', '.'))
        photovoltaik = float(row[7].replace('.', '').replace(',', '.'))
        sonstige_erneuerbare = float(row[8].replace('-', '0').replace('.', '').replace(',', '.'))
        kernenergie = float(row[9].replace('.', '').replace(',', '.'))
        braunkohle = float(row[10].replace('.', '').replace(',', '.'))
        steinkohle = float(row[11].replace('.', '').replace(',', '.'))
        erdgas = float(row[12].replace('.', '').replace(',', '.'))
        pumpspeicher = float(row[13].replace('.', '').replace(',', '.'))
        sonstige_konventionelle = float(row[14].replace('.', '').replace(',', '.'))

        datensatz = {
            'Datum': datum,
            'Anfang': anfang,
            'Ende': ende,
            'Biomasse [MWh]': biomasse,
            'Wasserkraft [MWh]': wasserkraft,
            'Wind Offshore [MWh]': wind_offshore,
            'Wind Onshore [MWh]': wind_onshore,
            'Photovoltaik [MWh]': photovoltaik,
            'Sonstige Erneuerbare [MWh]': sonstige_erneuerbare,
            'Kernenergie [MWh]': kernenergie,
            'Braunkohle [MWh]': braunkohle,
            'Steinkohle [MWh]': steinkohle,
            'Erdgas [MWh]': erdgas,
            'Pumpspeicher [MWh]': pumpspeicher,
            'Sonstige Konventionelle [MWh]': sonstige_konventionelle
        }
        energie_daten.append(datensatz)

print('First dataset done')

print('Starting second dataset')

with open(csv_datei2, 'r') as file:
    csv_reader = csv.reader(file, delimiter=';')
    next(csv_reader)
    for row in csv_reader:
        datum = row[0]
        print(datum)
        anfang = row[1]
        gesamt = float(row[3].replace('.', '').replace(',', '.'))

        datensatz1 = {
            'Datum': datum,
            'Anfang': anfang,
            'Gesamt (Netzlast) [MWh]': gesamt,
        }
        energie_daten2.append(datensatz1)

print('Second dataset done')


production = [datensatz['Biomasse [MWh]'] + datensatz['Wasserkraft [MWh]'] + datensatz['Wind Offshore [MWh]'] + datensatz['Wind Onshore [MWh]'] + datensatz['Photovoltaik [MWh]'] + datensatz['Sonstige Erneuerbare [MWh]'] for datensatz in energie_daten]

print('Production done')

consumption = [datensatz1['Gesamt (Netzlast) [MWh]'] for datensatz1 in energie_daten2]

print('Consumption done')

selected_date = datetime.strptime(input_date, '%d.%m.%Y')
filtered_data = [datensatz for datensatz in energie_daten if parse_datetime(datensatz['Datum'], datensatz['Anfang']).date() == selected_date.date()]
filtered_data2 = [datensatz1 for datensatz1 in energie_daten2 if parse_datetime(datensatz1['Datum'], datensatz1['Anfang']).date() == selected_date.date()]


hours = [parse_datetime(datensatz['Datum'], datensatz['Anfang']).hour + parse_datetime(datensatz['Datum'], datensatz['Anfang']).minute / 60 for datensatz in filtered_data]
production_day = [datensatz['Biomasse [MWh]'] + datensatz['Wasserkraft [MWh]'] + datensatz['Wind Offshore [MWh]'] + datensatz['Wind Onshore [MWh]'] + datensatz['Photovoltaik [MWh]'] + datensatz['Sonstige Erneuerbare [MWh]'] for datensatz in filtered_data]
consumption_day = [datensatz1['Gesamt (Netzlast) [MWh]'] for datensatz1 in filtered_data2]

def range1(array1, array2):
    if len(array1) != len(array2):
        raise ValueError("Arrays must be the same length")
    
    count10 = 0
    count20 = 0
    count30 =0
    count40 = 0
    count50 = 0
    count60 = 0
    count70 = 0
    count80 = 0
    count90 = 0
    count100 = 0

    for val1, val2 in zip(array1, array2):
        if 0.1 <= val1 / val2 < 0.2:
            count10 += 1
        if 0.2 <= val1 / val2 < 0.3:
            count20 +=1
        if 0.3 <= val1 / val2 < 0.4:
            count30 +=1
        if 0.4 <= val1 / val2 < 0.5:
            count40 +=1
        if 0.5 <= val1 / val2 < 0.6:
            count50 +=1
        if 0.6 <= val1 / val2 < 0.7:
            count60 +=1
        if 0.7 <= val1 / val2 < 0.8:
            count70 +=1
        if 0.8 <= val1 / val2 < 0.9:
            count80 +=1
        if 0.9 <= val1 / val2 < 1:
            count90 +=1
        if  val1 / val2  == 1:
            count100+=1

    return [count10, count20, count30, count40, count50, count60, count70, count80, count90, count100]

counts =[]
counts = range1(production, consumption)
print(counts)

plt.figure(figsize=(12, 6))
plt.plot(hours, production_day, label='Production (renewable energy)')
plt.plot(hours, consumption_day, label='Consumption')
plt.xlabel('Time [Hour]')
plt.ylabel('Power (MWh)')
plt.title(f'Energy production and consumption for {selected_date.strftime("%d.%m.%Y")}')
plt.legend()
plt.grid(True)

plt.xticks(range(0, 24))

x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
plt.figure(figsize=(6, 4)) 
plt.bar(range(len(counts)), counts)
plt.title('Anzahl der Viertelstunden mit 10-100 % EE-Anteil')
plt.xticks(x, ['10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'])

plt.show()

plt.show()



#Nach Objekten. Die Anzahl von Kästchen sofort berechnen. Mit Klassen