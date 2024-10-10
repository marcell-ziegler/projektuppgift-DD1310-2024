# Projektuppgift DD1310 HT24 - Marcell Ziegler
Jag har valt uppgiften [127 Platsbokning på SJ](https://people.kth.se/~dbosk/prgx24.d/platsbokning.pdf)


# Projektspecifikation
***
# Användarflöde
![Användarflöde](./User%20flow.drawio.png)

# Algoritmer

## Hitta stol med nummer

För ett stolsnummer $n$, i en vagn med $n_l$ stolar till vänster om gånger och $n_r$ stolar till höger, låt
$$\left\{\begin{array}{l}b_r = n_l + n_r \\ r = \left\lceil n / b_r \right\rceil \\ i = n - b_r \cdot (r - 1) \end{array}\right.$$
där $r$ är stolens radnummer och $i$ är stolens index i raden. Detta innebär att man kommer åt stol nr $n$ med uttrycket `Carriage.seats[r - 1][0][i - 1]` om den befinner sig på vänster sida om gånger, dvs $i < n_l$ annars med uttrycker `Carriage.seats[r - 1][1][i - 1 - n_l]`.

# Datastrukturer

## Train
Lagrar ett tåg, dess avgångstid, ankomsttid, startstation, destination och en lista med vagnar.

### Attribut
- `train_number: int` - unikt tågnummer
- `start: str` - startstation
- `destination: str` - destination
- `departure_time: datetime` - avgångstid
- `arrival_time: datetime` - ankomsttid
- `carriages: list[Carriage]` - lista med vagnar


## Carriage
Lagrar en vagn, dess stolar och alla passagerare.

### Attribut
- `seats: list[tuple[list[Seat], list[Seat]]]` - lista med alla par av stolsrader separerade av en gång. Varje element innehåller en tuple av två listor med stolar, en för varje sida av gången.
- `seating_configuration: str` - sittkonfiguration (ex. "2+2", "3+2" etc.)
- `number: int` - vagnnummer

### Metoder
- `get_seat(number: int) -> Seat` - returnerar en specifik stol baserat på nummer

## Seat
Innehåller information om en stol, dess position och om den är upptagen.

### Attribut
- `number: int` - stolsnummer i vagnen
- `passenger_name: str` - passagerare som sitter i stolen