from solana.publickey import PublicKey

MAINNET_NAME_PROGRAM_ID: PublicKey = PublicKey("namesLPneVptA9Z5rqUDD9tMTWEJwofgaYwp8cawRkX")
"""Public key that identifies the mainnet-beta Solana SPL Name Service program."""

DEVNET_NAME_PROGRAM_ID: PublicKey = PublicKey("Gh9eN9nDuS3ysmAkKf4QJ6yBzf3YNqsn6MD8Ms3TsXmA")
"""Public key that identifies the devnet Solana SPL Name Service program."""

NAME_PROGRAM_HASH_PREFIX = "SPL Name Service"
"""Hardcoded in SPL Name Service program, prepended to name when generating its hash."""

# All accounts must have at least 96 bytes to store required metadata
REQ_INITIAL_ACCOUNT_BUFFER = 96

