"""Unit tests for solana.system_program."""
import solana.name_program as name_prog
from solana.account import Account
from solana.publickey import PublicKey


def test_create():
    """Test creating a name account."""
    params = name_prog.CreateNameParams(
        funding_account=Account().public_key(),
        hashed_name=name_prog.get_hashed_name("", "some_name12348364567"),
        lamports=123,
        space=1,
    )
    assert name_prog.decode_create_name(name_prog.create_name(params)) == params
