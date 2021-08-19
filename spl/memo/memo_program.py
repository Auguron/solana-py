"""Library to interface with the memo program."""
from __future__ import annotations

from typing import Optional, Any, NamedTuple

from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction

from spl.memo.constants import MEMO_PROGRAM_ID

# Instruction Params
class MemoParams(NamedTuple):
    """Create name account transaction params."""
    funding_account: PublicKey  # System Address
    data: bytes
    memo_program_id: PublicKey=MEMO_PROGRAM_ID


def decode_memo_instruction(instruction: TransactionInstruction) -> MemoParams:
    """
    Decode a create name instruction and retrieve the instruction params.
    """
    parsed_data = __parse_and_validate_instruction(instruction, 6,
        InstructionType.CREATE)
    return MemoParams(
        funding_account=instruction.keys[1].pubkey,
        data=instruction.data,
        memo_program_id=instruction.program_id
        )

def memo_instruction(params: MemoParams) -> TransactionInstruction:
    """
    Generate an instruction that creates and funds a new name account.
    """
    keys = [
        AccountMeta(pubkey=params.funding_account, is_signer=True, is_writable=True),
    ]
    return TransactionInstruction(
        keys=keys,
        program_id=params.memo_program_id,
        data=data,
    )


