cw_cloud
=========

Coursework for Cloud Computing module.

API Documentation
-----------------

- GET **/stock_time_series**

    Get realtime and historical global equity data, or search for a particular equity. Optional arguments that can be passed along with the request:<br>
    - *function* - Get price and volume information for the given symbol `TIME_SERIES_INTRADAY` on intraday basis, `TIME_SERIES_DAILY` on daily basis, `TIME_SERIES_DAILY_ADJUSTED` on daily basis but cumulative for the current trading day. `GLOBAL_QUOTE` latest price and volume information for the given symbol. `SYMBOL_SEARCH` best-matching symbols and market information based on provided keywords. Default `TIME_SERIES_DAILY`.
    - *symbol* - The equity of interest. Default `MSFT`.
    - *interval* - `1min`, update`5min`, `15min`, `30min`, `60min` interval between two consecutive data points in the time series. Default `5min`.
    - *keywords* - A text string to search for. Default `microsoft`.
    Requires valid authentication *token*, or *username* and *password*, else failure status code `401` (unauthorized) is returned.

- GET **/foreign_exchange**

    Get real time exchange rates for any pair of digital currency or physical currency. Optional arguments that can be passed along with the request:<br>
    - *function* - Get exhange rate of any pair of currencies `CURRENCY_EXCHANGE_RATE`. Get intraday time series of the pair of currencies `FX_INTRADAY`. Default `CURRENCY_EXCHANGE_RATE`.
    - *from_symbol* - Currency to convert from. Three letter symbol from the [forex currency list](https://www.alphavantage.co/physical_currency_list/). Default `USD`.
    - *to_symbol* - Currency to convert to. Three letter symbol from the [forex currency list](https://www.alphavantage.co/physical_currency_list/). Default `BTC`.
    - *interval* - `1min`, `5min`, `15min`, `30min`, `60min` interval between two consecutive data points in the time series. Default `5min`.
    Requires valid authentication *token*, or *username* and *password*, else failure status code `401` (unauthorized) is returned.

- GET **/cryptocurrencies**

    Get wide range of data feed for digital and crypto currencies. Optional arguments that can be passed along with the request:<br>
    - *function* - Get exhange rate of any pair of currencies `CURRENCY_EXCHANGE_RATE`. Get intraday time series for a digital currency `DIGITAL_CURRENCY_DAILY`. Default `CURRENCY_EXCHANGE_RATE`.
    - *from_currency* - Currency to convert from which can be a [physical](https://www.alphavantage.co/physical_currency_list/) or [digital](https://www.alphavantage.co/digital_currency_list/). Default `USD`.
    - *to_currency* - Currency to convert to which can be a [physical](https://www.alphavantage.co/physical_currency_list/) or [digital](https://www.alphavantage.co/digital_currency_list/). Default `BTC`.
    Requires valid authentication *token*, or *username* and *password*, else failure status code `401` (unauthorized) is returned.

- POST **/users/new**

    Creates a new user account with given username and password. Required parameters:<br>
    - *username* - username of the new user account.
    - *password* - password for the new user account.
    If user already exists, status code `403` (forbidden) is returned.

- PUT **/users/update**

    Updates an existing user's username and/or password with given username and password. Required parameters:<br>
    - *username* - username of the existing user account.
    - *password* - password for the existing user account.
    Requires valid authentication *token*, or *username* and *password*, else failure status code `401` (unauthorized) is returned.

- DELETE **/users/delete**

    Deletes an existing user account.<br>
    Requires valid authentication *token*, or *username* and *password*, else failure status code `401` (unauthorized) is returned.

- GET **/token/new**

    Request a new authentication token for an existing user.
    Requires valid authentication *token*, or *username* and *password*, else failure status code `401` (unauthorized) is returned.

Example
-------

Using `curl` to request Stock Time Series data with *username* and *password* authentication:

    $ curl -u maaz:qmul -i -X GET http://localhost:8080/stock_time_series?function=XYZ

Using `curl` to request Stock Time Series data with authentication *token*:

    $ curl -u eyJhbGciOiJIUzI1NiIsImV4cCI6MTM4NTY2OTY1NSwiaWF0IjoxMzg1NjY5MDU1fQ.eyJpZCI6MX0.XbOEFJkhjHJ5uRINh2JA1BPzXjSohKYDRT472wGOvjc:unused -i -X GET http://localhost:8080/stock_time_series

Using `curl` to create a new user:

    $ curl -i -X POST -H "Content-Type: application/json" -d '{"username":"maaz","password":"qmul"}' http://localhost:8080/users/new

Using `curl` to update existing user's *username* and/or *password* with username and password authentication:

    $ curl -u maaz:cloud -i -X PUT -H "Content-Type: application/json" -d '{"username":"alam","password":"computing"}' http://localhost:8080/users/update

Using `curl` to delete an existing user with *username* and *password* authentication:

    $ curl -u maaz:cloud -i -X DELETE -H "Content-Type: application/json" http://localhost:8080/users/delete

Using `curl` to request a new token with *username* and *password* authentication:

    $ curl -u miguel:python -i -X GET http://localhost:8080/token/new
