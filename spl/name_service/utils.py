from hashlib import sha256

from solana.publickey import PublicKey

def get_hashed_name(hash_prefix: str, name: str) -> bytes:
    """
    Get name-based hash used in seeding the derivation of a program address.
    """
    return sha256((hash_prefix + name).encode()).digest()


def get_name_account_address(seeds: list[bytes], program_id: PublicKey) -> bytes:
    """
    Get name account address in deterministic fashion based on provided seeds and program ID.
    """
    name_record_pubkey, _ = PublicKey.find_program_address(
        seeds,
        program_id
    )
    return name_record_pubkey


