"""Library to interface with system programs."""
from __future__ import annotations

from typing import Any, NamedTuple
from hashlib import sha256

from solana.rpc.api import Client
from solana._layouts.name_program_instructions import NAME_PROGRAM_INSTRUCTIONS_LAYOUT, InstructionType
from solana.publickey import PublicKey
from solana.program_pubkeys import SYS_PROGRAM_ID, NAME_PROGRAM_ID
from solana.transaction import AccountMeta, TransactionInstruction
from solana.utils.validate import validate_instruction_keys, validate_instruction_type


# Instruction Params
class CreateNameParams(NamedTuple):
    """Create name account transaction params."""
    funding_account: PublicKey  # System Address
    hashed_name: str
    lamports: int  # TODO make it optional, and default to minimum rent req for space allocated
    space: int  # Storage space for arbitrary data
    owner_account: PublicKey=None  # Default: funding account
    class_account: PublicKey=SYS_PROGRAM_ID  # Signer
    parent_account: PublicKey=SYS_PROGRAM_ID
    parent_owner_account: PublicKey=SYS_PROGRAM_ID  # Signer, optional but needed if parent_account != default


class UpdateNameParams(NamedTuple):
    """Update name account transaction params."""
    name_account: PublicKey  # Name account to modify
    offset: int
    input_data: bytes
    name_update_signer: PublicKey=None


def get_hashed_name(hash_prefix: str, name: str) -> bytes:
    """
    Get name-based hash used in seeding the derivation of a program address.
    """
    return sha256((hash_prefix + name).encode()).digest()


def get_name_account_address(seeds: list[bytes], program_id: PublicKey=NAME_PROGRAM_ID) -> bytes:
    """
    Get name account address in deterministic fashion based on provided seeds and program ID.
    """
    name_record_pubkey, _ = PublicKey.find_program_address(
        seeds,
        program_id
    )
    return name_record_pubkey


def __check_program_id(program_id: PublicKey) -> None:
    if program_id != SYS_PROGRAM_ID:
        raise ValueError("invalid instruction: programId is not SystemProgram")


def __parse_and_validate_instruction(
    instruction: TransactionInstruction,
    expected_keys: int,
    expected_type: InstructionType,
) -> Any:  # Returns a Construct container.
    validate_instruction_keys(instruction, expected_keys)
    data = NAME_PROGRAM_INSTRUCTIONS_LAYOUT.parse(instruction.data)
    validate_instruction_type(data, expected_type)
    return data


def decode_create_name(instruction: TransactionInstruction) -> CreateNameParams:
    """Decode a create name instruction and retrieve the instruction params.
    """  # noqa: E501 # pylint: disable=line-too-long
    parsed_data = __parse_and_validate_instruction(instruction, 6,
        InstructionType.CREATE)
    return CreateNameParams(
        funding_account=instruction.keys[1].pubkey,
        hashed_name=parsed_data.args.hashed_name,
        lamports=parsed_data.args.lamports,
        space=parsed_data.args.space)


def create_name(params: CreateNameParams) -> TransactionInstruction:
    """
    Generate an instruction that creates and funds a new name account.
    """
    data = NAME_PROGRAM_INSTRUCTIONS_LAYOUT.build(
        dict(
            instruction_type=InstructionType.CREATE,
            args=dict(
                hashed_name_size=len(params.hashed_name),
                hashed_name=bytes(params.hashed_name),
                lamports=params.lamports,
                space=params.space),
        )
    )
    # print([hex(i) for i in data], len(data))
    # print("seeds for hashed name", [params.hashed_name, bytes(params.class_account), bytes(params.parent_account)])
    # print(len(b"".join(
    #     [params.hashed_name,
    #     bytes(params.class_account),
    #     bytes(params.parent_account)])))
    # name_record_pubkey = PublicKey.create_program_address(
    # name_record_pubkey, _ = PublicKey.find_program_address(
    name_record_pubkey = get_name_account_address(
        [params.hashed_name, bytes(params.class_account), bytes(params.parent_account)],
        NAME_PROGRAM_ID
    )
    # print("name program id", NAME_PROGRAM_ID)
    # print("hashed name", name_record_pubkey.to_base58())
    # Enforce specified parent owner account.
    if params.parent_account != SYS_PROGRAM_ID and \
            params.parent_owner_account == SYS_PROGRAM_ID:
        raise ValueError("Must specify the supplied parent name account's owner account")

    keys = [
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=params.funding_account, is_signer=True, is_writable=True),
        AccountMeta(pubkey=name_record_pubkey, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.owner_account or params.funding_account, is_signer=False, is_writable=False)
    ]
    # Class Account?
    if params.class_account != SYS_PROGRAM_ID:
        keys.append(AccountMeta(pubkey=params.class_account, is_signer=True, is_writable=False))
    else:
        keys.append(AccountMeta(pubkey=params.class_account, is_signer=False, is_writable=False))
    # Parent Account?  If so, then owner account as well.
    keys.append(AccountMeta(pubkey=params.parent_account, is_signer=False, is_writable=False))
    if params.parent_account != SYS_PROGRAM_ID:
        keys.append(AccountMeta(
            pubkey=params.parent_owner_account,
            is_signer=True,
            is_writable=False)
        )
    return TransactionInstruction(
        keys=keys,
        program_id=NAME_PROGRAM_ID,
        data=data,
    )


def update_name(params: UpdateNameParams) -> TransactionInstruction:
    """
    Generate an instruction that creates and funds a new name account.
    """
    data = NAME_PROGRAM_INSTRUCTIONS_LAYOUT.build(
        dict(
            instruction_type=InstructionType.UPDATE,
            args=dict(
                offset=params.offset,
                size=len(params.input_data),
                input_data=params.input_data
            ),
        )
    )
    keys = [
            AccountMeta(params.name_account, is_signer=False, is_writable=True),
            AccountMeta(params.name_update_signer, is_signer=True, is_writable=False),
            ]
    return TransactionInstruction(
            keys=keys,
            program_id=NAME_PROGRAM_ID,
            data=data
            )

def retrieve_name_data(
        name: str,
        hash_prefix: str="SPL Name Service",
        name_class: PublicKey=SYS_PROGRAM_ID,
        name_owner: PublicKey=SYS_PROGRAM_ID,
        endpoint='https://devnet.solana.com'
        ):
    hashed_name = get_hashed_name(hash_prefix, name)
    account_key = get_name_account_address(
        [hashed_name, bytes(name_class), bytes(name_owner)],
        NAME_PROGRAM_ID
        )
    client = Client(endpoint)
    info = client.get_account_info(
            account_key, encoding='jsonParsed')['result']
    print(info)
    return info['value']['data']
