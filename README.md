[![Actions
Status](https://github.com/michaelhly/solanapy/workflows/CI/badge.svg)](https://github.com/michaelhly/solanapy/actions?query=workflow%3ACI)
[![PyPI version](https://badge.fury.io/py/solana.svg)](https://badge.fury.io/py/solana)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/solana)](https://pypi.org/project/solana/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/michaelhly/solana-py/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


### SPL Name Service Fork
This fork adds an interface to the SPL Name Service program.
It also addresses some necessary fixes and additions to program address derivation / validation.

# Solana.py

Solana Python API built on the [JSON RPC API](https://docs.solana.com/apps/jsonrpc-api).

Python version of [solana-web3.js](https://github.com/solana-labs/solana-web3.js/) for interacting with Solana.

Read the [Documentation](https://michaelhly.github.io/solana-py/).

## Quickstart

### Installation

```sh
pip install solana
```

### General Usage

```py
import solana
```

### API Client

```py
from solana.rpc.api import Client

http_client = Client("https://devnet.solana.com")
```

## Development

### Setup

1. Install pipenv.

```sh
brew install pipenv
```

2. Install dev dependencies.

```sh
pipenv install --dev
```

3. Activate the pipenv shell.

```sh
pipenv shell
```

### Lint

```sh
make lint
```

### Tests

```sh
# All tests
make tests
# Unit tests only
make unit-tests
# Integration tests only
make int-tests
```

### Start a Solana Localnet

Install [docker](https://docs.docker.com/get-started/).

```sh
# Update/pull latest docker image
pipenv run update-localnet
# Start localnet instance
pipenv run start-localnet
```

### Using Jupyter Notebook

```sh
make notebook
```
