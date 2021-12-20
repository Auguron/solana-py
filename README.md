
For the original library, [see michaelhly's repo](https://michaelhly.github.io/solana-py/).

### SPL Name Service Fork
This fork of [michaelhly's solana-py repo](https://github.com/michaelhly/solana-py.git) adds an interface to the SPL Name Service program.
It also addresses some necessary fixes and additions to program address derivation / validation.

Python version of [solana-web3.js](https://github.com/solana-labs/solana-web3.js/) for interacting with Solana.

Read the [Documentation](https://michaelhly.github.io/solana-py/).

Also check out [anchorpy](https://kevinheavey.github.io/anchorpy/), a Python client for
[Anchor](https://project-serum.github.io/anchor/getting-started/introduction.html) based programs on Solana.

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

http_client = Client("https://api.devnet.solana.com")
```

### Async API Client

```py
import asyncio
from solana.rpc.async_api import AsyncClient

async def main():
    async with AsyncClient("https://api.devnet.solana.com") as client:
        res = await client.is_connected()
    print(res)  # True

    # Alternatively, close the client explicitly instead of using a context manager:
    client = AsyncClient("https://api.devnet.solana.com")
    res = await client.is_connected()
    print(res)  # True
    await client.close()

asyncio.run(main())
```

### Websockets Client

```py
import asyncio
from asyncstdlib import enumerate
from solana.rpc.websocket_api import connect

async def main():
    async with connect("ws://api.devnet.solana.com") as websocket:
        await websocket.logs_subscribe()
        first_resp = await websocket.recv()
        subscription_id = first_resp.result
        next_resp = await websocket.recv()
        print(next_resp)
        await websocket.logs_unsubscribe(subscription_id)

    # Alternatively, use the client as an infinite asynchronous iterator:
    async with connect("ws://api.devnet.solana.com") as websocket:
        await websocket.logs_subscribe()
        first_resp = await websocket.recv()
        subscription_id = first_resp.result
        async for idx, msg in enumerate(websocket):
            if idx == 3:
                break
            print(msg)
        await websocket.logs_unsubscribe(subscription_id)

asyncio.run(main())
```

## Development

### Setup

1. Install [poetry](https://python-poetry.org/docs/#installation)
2. Install dev dependencies:
```sh
poetry install

```

3. Activate the poetry shell.

```sh
poetry shell
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
make update-localnet
# Start localnet instance
make start-localnet
```
