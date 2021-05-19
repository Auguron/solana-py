"""Library to interface with system programs."""
from __future__ import annotations

from typing import Any, NamedTuple
from hashlib import sha256

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


def get_hashed_name(hash_prefix: str, name: str) -> bytes:
    return sha256((hash_prefix + name).encode()).digest()


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
    """Generate an instruction that creates and funds a new name account.
    """
    # hashed_name = sha256((params.hash_prefix + params.name).encode()).digest()
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
    name_record_pubkey = PublicKey.create_program_address(
        [params.hashed_name, bytes(params.class_account), bytes(params.parent_account)],
        NAME_PROGRAM_ID
    )
    # Enforce specified parent owner account.
    if params.parent_account != SYS_PROGRAM_ID and \
            params.parent_owner_account == SYS_PROGRAM_ID:
        raise ValueError("Must specify the supplied parent name account's owner account")

    keys = [
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=params.funding_account, is_signer=True, is_writable=True),
        AccountMeta(pubkey=name_record_pubkey, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.owner_account or params.funding_account, is_signer=False, is_writable=False),
        AccountMeta(pubkey=params.class_account, is_signer=True, is_writable=False),
        AccountMeta(pubkey=params.parent_account, is_signer=False, is_writable=False),
    ]
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
