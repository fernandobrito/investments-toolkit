# Investments toolkit

My personal collection of scripts and automations to help me handle my equity investments.

Currently, it only has features related to calculating the correlation of a list of assets.

## Portfolio correlation

Features:

* Caches the results of data feeds API requests
* Calculates a correlation matrix and plots it
* Uses clustering to order the correlation matrix

## Architecture

### Data feeds

Clients to retrieve asset information and historical prices from different sources. Currently, the following (
minimalist) clients are implemented:

* [Avanza](https://www.avanza.se): a Swedish broker
* [CMC Markets](https://www.cmcmarkets.com/sv-se/): an international CFD broker

## Development

* `make type`
* `make lint`

## License

This project is licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.