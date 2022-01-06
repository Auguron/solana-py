from hashlib import sha256

from solana.publickey import PublicKey
from solana.system_program import SYS_PROGRAM_ID

from .constants import *

def get_hashed_name(hash_prefix: str, name: str) -> bytes:
    """
    Get name-based hash used in seeding the derivation of a program address.
    """
    return sha256((hash_prefix + name).encode()).digest()


def get_name_account(
    name: str,
    class_account: PublicKey=SYS_PROGRAM_ID,
    parent_account: PublicKey=SYS_PROGRAM_ID,
    program_id: PublicKey=NAME_PROGRAM_ID,
    hash_prefix: str=NAME_PROGRAM_HASH_PREFIX
    ) -> PublicKey:
    """
    Calculate the name account based on necessary parameters.
    """
    hashed_name = get_hashed_name(hash_prefix, name)
    account, _ = PublicKey.find_program_address(
        [
            hashed_name,
            bytes(class_account),
            bytes(parent_account)
        ],
        bytes(name_program_id)
    )
    return account
