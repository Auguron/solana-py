"""Unit tests for solana.system_program."""
from spl.name_service import name_program
from solana.account import Account
from solana.publickey import PublicKey


def test_create():
    """Test creating a name account."""
    params = name_program.CreateNameParams(
        funding_account=Account().public_key(),
        hashed_name=name_program.get_hashed_name("", "some_name12348364567"),
        lamports=123,
        space=1,
    )
    assert name_program.decode_create_name(name_program.create_name(params)) == params
