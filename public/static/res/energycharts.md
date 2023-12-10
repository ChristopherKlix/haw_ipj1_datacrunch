# Data schema

## Columns

index [0]: unix_seconds

1. Hydro pumped storage consumption
1. Cross border electricity trading
1. Nuclear
1. Hydro Run-of-River
1. Biomass
1. Fossil brown coal / lignite
1. Fossil hard coal
1. Fossil oil
1. Fossil gas
1. Geothermal
1. Hydro water reservoir
1. Hydro pumped storage
1. Others
1. Waste
1. Wind offshore
1. Wind onshore
1. Solar
1. Load
1. Residual load
1. Renewable share of generation
1. Renewable share of load

## Mapping

Definition der Quellen:

[SMARD Handbuch](https://www.smard.de/resource/blob/208546/108612cd96cc27646cb328f0ca9cb3d2/smard-benutzerhandbuch-07-2022-data.pdf)

[EnergyCharts Erläuterung](https://energy-charts.info/explanations.html?l=de&c=DE)

Die Zuweisung kann zu **100%** erfolgen. Allerdings weichen einige Quellen in der Benennung ab und andere sind in Energy Charts aufgeteilt. Zudem weichen die "Anderen" Quellen ab, bzw. sind bei SMARD detailierter aufgeschlüsselt.

Die Abweichungen in den Gesamtzahlen sollte daher also nur minimal sein.

### Time

```py
self.start = dt.datetime.fromtimestamp(unix_seconds)

self.end = self.start + dt.timedelta(minutes=15)
```

### Renewables

#### Hydro

In SMARD werden folgende Quellen spezifiziert:

- Wasserkraft

Wasserkraft beinhaltet in SMARD

- Laufwasser
- Wasserreservoir

In EnergyCharts werden folgende Quellen spezifiziert:

- Hydro Run-of-river
- Hydro water reservoir

Hydro water reservoir wird in EnergyCharts als
"Pumped storage with natural feeder" spezifiziert.

Damit stimmen die Quellen überein.

```py
self.hydro = data['Hydro Run-of-River']
self.hydro += data['Hydro water reservoir']

# Usage in storage not hydro
data['Hydro pumped storage']
data['Hydro pumped storage consumption']
```

#### Wind

```py
self.wind_onshore = data['Wind onshore']
self.wind_offshore = data['Wind offshore']
```

#### Solar

```py
self.pv = data['Solar']
```

#### Biomass

```py
self.biomass = data['Biomass']
```

#### Others Renewables

In SMARD werden folgende Quellen spezifiziert:

- Erdwärme (Geothermie)
- Deponiegas
- Klärgas
- Grubengas

In EnergyCharts werden folgende Quellen spezifiziert:

- Geothermal (Erdwärme)

∴ Es wird eine leichte Diskrepanz zwischen den beiden Quellen erwartet, da SMARD mehr Quellen spezifiziert.

```py
self.other_renewables = data['Geothermal']
```

### Fossil

#### Coal

```py
self.coal = data['Fossil hard coal']
```

```py
# ! Will be renamed to self.lignite in next version
self.charcoal = data['Fossil brown coal / lignite']
```

#### Gas

```py
self.gas = data['Fossil gas']
```

#### Other Conventional

In SMARD werden folgende Quellen spezifiziert:

- Abgeleitetes Gas aus Kohle
- Mineralöl
- Abfall
- Gichtgas
- Hochofengas
- Raffineriegas
- Gas mit hohem Wasserstoffanteil
- Sonstige Reststoffe aus Produktion (bspw. Stahl- und Kokserzeugung)
- Gemisch aus mehreren Brennstoffen

In EnergyCharts werden folgende Quellen spezifiziert:

- Fossil oil
- Waste

∴ Es wird eine leichte Diskrepanz zwischen den beiden Quellen erwartet, da SMARD mehr Quellen spezifiziert.

```py
self.other_conventional = data['Fossil oil']
self.other_conventional += data['Waste']
```

#### Pump storage

#### Pump storage energy consumption

```py
# ! Will be renamed to self.pump_storage_consumption in next version
self.gravitational_energy_storage = data['Hydro pumped storage consumption']
```

#### Pump storage energy production

```py
# ! Will be renamed to self.pump_storage in next version
self.gravity_energy_storage = data['Hydro pumped storage']
```

### Nuclear

```py
self.nuclear = data['Nuclear']
```

### Load

```py
self.load = data['Load']
```
