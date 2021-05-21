
from solana.publickey import PublicKey

SYS_PROGRAM_ID = PublicKey("11111111111111111111111111111111")
"""
Public key that identifies the System program,
also the Python equivalent of `Pubkey::default()`.
"""
# Note: This constructor is same as PublicKey(b'\x00'*32)

# I've seen conflicting documentation, not sure which is which?
# This is the one from name_program Rust source code
# NAME_PROGRAM_ID: PublicKey = PublicKey("namesLPneVptA9Z5rqUDD9tMTWEJwofgaYwp8cawRkX")
# And this is the one from the JS source code
NAME_PROGRAM_ID: PublicKey = PublicKey("Gh9eN9nDuS3ysmAkKf4QJ6yBzf3YNqsn6MD8Ms3TsXmA")
"""Public key that identifies the Solana SPL Name Service program."""
