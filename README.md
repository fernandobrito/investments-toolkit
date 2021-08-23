# Investments toolkit

[![Code checks](https://github.com/fernandobrito/investments-toolkit/actions/workflows/run-code-checks.yaml/badge.svg)](https://github.com/fernandobrito/investments-toolkit/actions/workflows/run-code-checks.yaml)
[![Apache License 2.0](https://img.shields.io/github/license/fernandobrito/investments-toolkit)](https://github.com/voi-oss/dbt-exposures-crawler/)

My personal collection of scripts and automations to help me handle my equity investments.

Currently, it only has features related to calculating the correlation of a list of assets.

## Portfolio correlation

<p align="center">
    <a href="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_matrix.gif">
        <img 
          src="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_matrix.gif?raw=true" 
          alt="Correlation matrix"
          width="800px"
        />
    </a>
</p>

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