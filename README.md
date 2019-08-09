# App for storing and retrieving information about currencies exchange rates

## Installation:
```
git clone https://github.com/SirNicolas/exchange_rates.git
pip install -r requirements.txt 
```
## Fill DB with data:
```
python bin/fill_rates.py
```

## Run Server:
```
python bin/server.py
```

## Server endpoints:
```
/currencies - get all currencies
```
Example:
* localhost:8080/currencies?page_number=1

```
/rate/{currency_id} - get information about one currency exchange pair (rate, currency pair name, last ten days volume)
```
Example:
* localhost:8080/rate/1

## Run tests:

```
pytest tests
```
