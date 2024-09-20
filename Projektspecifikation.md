# Projektspecifikation
***
# Användarflöde
![Användarflöde](./User%20flow.drawio.png)

# Algoritmer


# Datastrukturer

## Train
Lagrar ett tåg, dess avgångstid, ankomsttid, startstation, destination och en lista med vagnar.

### Attribut
- `train_number: int` - unikt tågnummer
- `start_station: str` - startstation
- `destination: str` - destination
- `departure_time: datetime` - avgångstid
- `arrival_time: datetime` - ankomsttid
- `carriages: list[Carriage]` - lista med vagnar


## Carriage
Lagrar en vagn, dess stolar och alla passagerare.

### Attribut
- `seats: list[tuple[list[Seat], list[Seat]]]` - lista med alla par av stolsrader separerade av en gång. Varje element innehåller en tuple av två listor med stolar, en för varje sida av gången.
- `seating_configuration: str` - sittkonfiguration (ex. "2+2", "3+2" etc.)


## Seat
Innehåller information om en stol, dess position och om den är upptagen.

### Attribut
- `number: int` - stolsnummer i vagnen
- `passenger: Passenger` - passagerare som sitter i stolen


## Passenger
Lagrar information om en passagerare.

### Attribut
- `seat_number: int | None` - stolsnummer som den sitter på. `None` om inte placerad än.