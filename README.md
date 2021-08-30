# Investments toolkit

[![Tests](https://github.com/fernandobrito/investments-toolkit/actions/workflows/run-tests.yaml/badge.svg)](https://github.com/fernandobrito/investments-toolkit/actions/workflows/run-tests.yaml)
[![codecov](https://codecov.io/gh/fernandobrito/investments-toolkit/branch/main/graph/badge.svg?token=N3UOREZCI4)](https://codecov.io/gh/fernandobrito/investments-toolkit)
[![Code checks](https://github.com/fernandobrito/investments-toolkit/actions/workflows/run-code-checks.yaml/badge.svg)](https://github.com/fernandobrito/investments-toolkit/actions/workflows/run-code-checks.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Apache License 2.0](https://img.shields.io/github/license/fernandobrito/investments-toolkit)](https://github.com/voi-oss/dbt-exposures-crawler/)

My personal collection of scripts and automations to help me handle my investments.

## Summary

* Calculates the correlation matrix of the assets in my portfolio (and optionally compare it with an extra list of
  assets)
* Unified (HTTP) endpoint for getting the latest price from different sources

### Generic features

* Caches the results of HTTP requests locally (file system backend
  from [requests-cache](https://github.com/reclosedev/requests-cache)). Useful for local development
* Caches assets metadata and price history remotely ([Google Firestore](https://cloud.google.com/firestore)). Useful for
  production deployments
* Exposes some of the graphs through HTTP ([FastAPI](https://fastapi.tiangolo.com/)). Useful for creating links from my
  Google Sheets
* Exposes some of the raw outputs as CSV through HTTP (FastAPI). Useful for embedding the results in Google Sheets
* Containerized as a Docker image and ready to be deployed in the
  cloud ([Google Cloud Run](https://cloud.google.com/run))
* Interactive graphs ([Plotly](https://github.com/plotly/plotly.py))

## Portfolio correlation

### Motivation

Calculates a correlation matrix between multiple assets. As part of my trading strategy, I am interested in knowning the
current level of correlation between the assets that I already own. Additionally, when I am opening new positions, I
want to select the assets with the least correlation possible to my current portfolio.

### Specific features

* Calculates a correlation matrix and plots it on an interactive graph
* Uses clustering to order the correlation matrix, making it easier to interpret it
* Serves the output via HTTP either as a graph or as a CSV

### Usage examples

#### Programmatically (Jupyter notebook)

This graph below was generated from one of the [example files](examples/correlation_from_list.ipynb) (Jupyter notebook).

<p align="center">
    <a href="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_matrix.gif">
        <img 
          src="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_matrix.gif?raw=true" 
          alt="Correlation matrix"
          width="600px"
        />
    </a>
</p>

#### Via HTTP server (standalone graph)

The same graph as above, but returned in a standalone HTML page. Useful for creating a link with your assets from Google
Sheets while still keeping the interactivity.

<p align="center">
    <a href="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_http.png">
        <img 
          src="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_http.png?raw=true" 
          alt="Correlation interactive matrix"
          width="600px"
        />
    </a>
</p>

#### Other assets with portfolio

During the screening process before starting new positions, it is possible to provide an extra list of assets other than
the ones in your portfolio. Those assets will be appended at the end of the correlation matrix, after the clustering
step is done. This facilitates identifying which one of the extra assets have the lowest correlation to the assets in
your current portfolio.

<p align="center">
    <a href="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_extra.png">
        <img 
          src="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_extra.png?raw=true" 
          alt="Correlation interactive matrix"
          width="600px"
        />
    </a>
</p>

#### Via HTTP server (CSV)

Useful for embedding the results in Google Sheets
(using [IMPORTDATA()](https://support.google.com/docs/answer/3093335?hl=en)).

<p align="center">
    <a href="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_csv.png">
        <img 
          src="https://github.com/fernandobrito/investments-toolkit/blob/main/docs/correlation_csv.png?raw=true" 
          alt="Correlation raw results in CSV"
          width="600px"
        />
    </a>
</p>

## Latest price

First I started using `=GOOGLEFINANCE()` in my Google Sheets spreadsheet to get the latest price and a % variation for
the day for each asset. At some point, some of my new stocks were not available in Google Finance and I had to
use `=IMPORTXML()` to parse the public page from my broker to retrieve the same information. And then, I started using
multiple brokers and I had to introduce `=ImportJSON()` for those as well, which made it quite cumbersome to maintain
within the spreadsheet.

In this project, I hide this complexity from my spreadsheet by just exposing a `/price/<asset_id>` to handle all the
different data feeds.

In other words, I could replace this:

```
=GOOGLEFINANCE(CONCATENATE(D20, ":", SUBSTITUTE($F20, "_", "-")), "changepct")/100
=INDEX(ImportJSON("https://oaf.cmcmarkets.com/instruments/price/X-AASOB?key=<KEY>", "/movement_percentage"), 2, 1)/100
=VALUE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(IMPORTXML("https://www.avanza.se/aktier/gamla-aktiesidan.html/666686/swedencare","//span[contains(@class, 'changePercent')]/text()"),",","."), " %", ""), "+", ""))/100
```

With this:

```
=VALUE(ImportJSON(CONCATENATE("https://<HOST>/price/", A3, ":", C3), "/change_pct", "noHeaders"))/100
```

---

## Architecture

### Data feeds

Clients to retrieve asset information and historical prices from different sources. Currently, the following (
minimalist) clients are implemented:

* [Avanza](https://www.avanza.se): a Swedish broker
* [CMC Markets](https://www.cmcmarkets.com/sv-se/): an international CFD broker

### Persistence

Clients to interact with Google Firestore and for setting up HTTP requests local cache.

### Models

Python classes to represent assets, price bars and data sources.

## Deployment

I host an instance of the HTTP server for my personal use on [Google Cloud Run](https://cloud.google.com/run). Both my
uses of Google Cloud Run and [Google Firestore](https://cloud.google.com/firestore) for this project falls under their
free tier.

Check `.env.example` for the environment variables necessary to spin up an instance of the server.

## Development

I use [ngrok](https://ngrok.com/) when I need to connect Google Sheets with a local instance of the HTTP server.

Useful commands:

* `make lint`: runs `mypy`
* `make type`: runs `black` and `flake8`
* `make serve`: starts a `uvicorn` server with live reload enabled

## License

This project is licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.
