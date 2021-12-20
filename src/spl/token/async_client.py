# pylint: disable=too-many-arguments
"""Async SPL Token program client."""
from __future__ import annotations

from typing import List, Optional, Union, cast

import spl.token.instructions as spl_token
from solana.blockhash import Blockhash
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment, Confirmed
from solana.rpc.types import RPCResponse, TxOpts
from spl.token._layouts import ACCOUNT_LAYOUT, MINT_LAYOUT, MULTISIG_LAYOUT
from spl.token.core import AccountInfo, MintInfo, _TokenCore


class AsyncToken(_TokenCore):  # pylint: disable=too-many-public-methods
    """An ERC20-like Token."""

    def __init__(self, conn: AsyncClient, pubkey: PublicKey, program_id: PublicKey, payer: Keypair) -> None:
        """Initialize a client to a SPL-Token program."""
        super().__init__(pubkey, program_id, payer)
        self._conn = conn

    @staticmethod
    async def get_min_balance_rent_for_exempt_for_account(conn: AsyncClient) -> int:
        """Get the minimum balance for the account to be rent exempt.

        :param conn: RPC connection to a solana cluster.
        :return: Number of lamports required.
        """
        resp = await conn.get_minimum_balance_for_rent_exemption(ACCOUNT_LAYOUT.sizeof())
        return resp["result"]

    @staticmethod
    async def get_min_balance_rent_for_exempt_for_mint(conn: AsyncClient) -> int:
        """Get the minimum balance for the mint to be rent exempt.

        :param conn: RPC connection to a solana cluster.
        :return: Number of lamports required.
        """
        resp = await conn.get_minimum_balance_for_rent_exemption(MINT_LAYOUT.sizeof())
        return resp["result"]

    @staticmethod
    async def get_min_balance_rent_for_exempt_for_multisig(conn: AsyncClient) -> int:
        """Get the minimum balance for the multisig to be rent exempt.

        :param conn: RPC connection to a solana cluster.
        :return: Number of lamports required.
        """
        resp = await conn.get_minimum_balance_for_rent_exemption(MULTISIG_LAYOUT.sizeof())
        return resp["result"]

    async def get_accounts(
        self,
        owner: PublicKey,
        is_delegate: bool = False,
        commitment: Commitment = Confirmed,
        encoding: str = "jsonParsed",
    ) -> RPCResponse:
        """Get token accounts of the provided owner by the token's mint.

        :param owner: Public Key of the token account owner.
        :param is_delegate: (optional) Flag specifying if the `owner` public key is a delegate.
        :param encoding: (optional) Encoding for Account data, either "base58" (slow), "base64" or jsonParsed".
        :param commitment: (optional) Bank state to query.

        Parsed-JSON encoding attempts to use program-specific state parsers to return more
        human-readable and explicit account state data. If parsed-JSON is requested but a
        valid mint cannot be found for a particular account, that account will be filtered out
        from results. jsonParsed encoding is UNSTABLE.
        """
        args = self._get_accounts_args(owner, commitment, encoding)
        return (
            await self._conn.get_token_accounts_by_delegate(*args)
            if is_delegate
            else await self._conn.get_token_accounts_by_owner(*args)
        )

    async def get_balance(self, pubkey: PublicKey, commitment: Commitment = Confirmed) -> RPCResponse:
        """Get the balance of the provided token account.

        :param pubkey: Public Key of the token account.
        :param commitment: (optional) Bank state to query.
        """
        return await self._conn.get_token_account_balance(pubkey, commitment)

    @classmethod
    async def create_mint(
        cls,
        conn: AsyncClient,
        payer: Keypair,
        mint_authority: PublicKey,
        decimals: int,
        program_id: PublicKey,
        freeze_authority: Optional[PublicKey] = None,
        skip_confirmation: bool = False,
        recent_blockhash: Optional[Blockhash] = None,
    ) -> AsyncToken:
        """Create and initialize a token.

        :param conn: RPC connection to a solana cluster.
        :param payer: Fee payer for transaction.
        :param mint_authority: Account or multisig that will control minting.
        :param decimals: Location of the decimal place.
        :param program_id: SPL Token program account.
        :param freeze_authority: (optional) Account or multisig that can freeze token accounts.
        :param skip_confirmation: (optional) Option to skip transaction confirmation.
        :return: Token object for the newly minted token.

        If skip confirmation is set to `False`, this method will block for at most 30 seconds
        or until the transaction is confirmed.
        """
        # Allocate memory for the account
        balance_needed = await AsyncToken.get_min_balance_rent_for_exempt_for_mint(conn)
        # Construct transaction
        token, txn, payer, mint_account, opts = _TokenCore._create_mint_args(
            conn, payer, mint_authority, decimals, program_id, freeze_authority, skip_confirmation, balance_needed, cls
        )
        # Send the two instructions
        await conn.send_transaction(txn, payer, mint_account, opts=opts, recent_blockhash=recent_blockhash)
        return cast(AsyncToken, token)

    async def create_account(
        self,
        owner: PublicKey,
        skip_confirmation: bool = False,
        recent_blockhash: Optional[Blockhash] = None,
    ) -> PublicKey:
        """Create and initialize a new account.

        This account may then be used as a `transfer()` or `approve()` destination.

        :param owner: User account that will own the new account.
        :param skip_confirmation: (optional) Option to skip transaction confirmation.
        :return: Public key of the new empty account.

        If skip confirmation is set to `False`, this method will block for at most 30 seconds
        or until the transaction is confirmed.
        """
        balance_needed = await AsyncToken.get_min_balance_rent_for_exempt_for_account(self._conn)
        new_account_pk, txn, payer, new_account, opts = self._create_account_args(
            owner, skip_confirmation, balance_needed
        )
        # Send the two instructions
        await self._conn.send_transaction(txn, payer, new_account, opts=opts, recent_blockhash=recent_blockhash)
        return new_account_pk

    async def create_associated_token_account(
        self,
        owner: PublicKey,
        skip_confirmation: bool = False,
        recent_blockhash: Optional[Blockhash] = None,
    ) -> PublicKey:
        """Create an associated token account.

        :param owner: User account that will own the associated token account.
        :param skip_confirmation: (optional) Option to skip transaction confirmation.
        :return: Public key of the new associated account.

        If skip confirmation is set to `False`, this method will block for at most 30 seconds
        or until the transaction is confirmed.
        """
        # Construct transaction
        public_key, txn, payer, opts = self._create_associated_token_account_args(owner, skip_confirmation)
        await self._conn.send_transaction(txn, payer, opts=opts, recent_blockhash=recent_blockhash)
        return public_key

    @staticmethod
    async def create_wrapped_native_account(
        conn: AsyncClient,
        program_id: PublicKey,
        owner: PublicKey,
        payer: Keypair,
        amount: int,
        skip_confirmation: bool = False,
        recent_blockhash: Optional[Blockhash] = None,
    ) -> PublicKey:
        """Create and initialize a new account on the special native token mint.

        :param conn: RPC connection to a solana cluster.
        :param program_id: SPL Token program account.
        :param owner: The owner of the new token account.
        :param payer: The source of the lamports to initialize, and payer of the initialization fees.
        :param amount: The amount of lamports to wrap.
        :param skip_confirmation: (optional) Option to skip transaction confirmation.
        :return: The new token account.

        If skip confirmation is set to `False`, this method will block for at most 30 seconds
        or until the transaction is confirmed.
        """
        # Allocate memory for the account
        balance_needed = await AsyncToken.get_min_balance_rent_for_exempt_for_account(conn)
        new_account_public_key, txn, payer, new_account, opts = _TokenCore._create_wrapped_native_account_args(
            program_id, owner, payer, amount, skip_confirmation, balance_needed
        )
        await conn.send_transaction(txn, payer, new_account, opts=opts, recent_blockhash=recent_blockhash)
        return new_account_public_key

    async def create_multisig(
        self,
        m: int,
        multi_signers: List[PublicKey],
        opts: TxOpts = TxOpts(skip_preflight=True, skip_confirmation=False),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> PublicKey:  # pylint: disable=invalid-name
        """Create and initialize a new multisig.

        :param m: Number of required signatures.
        :param signers: Full set of signers.
        :return: Public key of the new multisig account.
        """
        balance_needed = await AsyncToken.get_min_balance_rent_for_exempt_for_multisig(self._conn)
        txn, payer, multisig = self._create_multisig_args(m, multi_signers, balance_needed)
        await self._conn.send_transaction(txn, payer, multisig, opts=opts, recent_blockhash=recent_blockhash)
        return multisig.public_key

    async def get_mint_info(self) -> MintInfo:
        """Retrieve mint information."""
        info = await self._conn.get_account_info(self.pubkey)
        return self._create_mint_info(info)

    async def get_account_info(self, account: PublicKey, commitment: Optional[Commitment] = None) -> AccountInfo:
        """Retrieve account information."""
        info = await self._conn.get_account_info(account, commitment)
        return self._create_account_info(info)

    async def transfer(
        self,
        source: PublicKey,
        dest: PublicKey,
        owner: Union[Keypair, PublicKey],
        amount: int,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Transfer tokens to another account.

        :param source: Public key of account to transfer tokens from.
        :param dest: Public key of account to transfer tokens to.
        :param owner: Owner of the source account.
        :param amount: Number of tokens to transfer.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, signers, opts = self._transfer_args(source, dest, owner, amount, multi_signers, opts)
        return await self._conn.send_transaction(txn, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def approve(
        self,
        source: PublicKey,
        delegate: PublicKey,
        owner: PublicKey,
        amount: int,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Grant a third-party permission to transfer up the specified number of tokens from an account.

        :param source: Public key of the source account.
        :param delegate: Account authorized to perform a transfer tokens from the source account.
        :param owner: Owner of the source account.
        :param amount: Maximum number of tokens the delegate may transfer.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, payer, signers, opts = self._approve_args(source, delegate, owner, amount, multi_signers, opts)
        return await self._conn.send_transaction(txn, payer, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def revoke(
        self,
        account: PublicKey,
        owner: PublicKey,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Revoke transfer authority for a given account.

        :param account: Source account for which transfer authority is being revoked.
        :param owner: Owner of the source account.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, payer, signers, opts = self._revoke_args(account, owner, multi_signers, opts)
        return await self._conn.send_transaction(txn, payer, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def set_authority(
        self,
        account: PublicKey,
        current_authority: Union[Keypair, PublicKey],
        authority_type: spl_token.AuthorityType,
        new_authority: Optional[PublicKey] = None,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Assign a new authority to the account.

        :param account: Public key of the token account.
        :param current_authority: Current authority of the account.
        :param authority_type: Type of authority to set.
        :param new_authority: (optional) New authority of the account.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, payer, signers, opts = self._set_authority_args(
            account, current_authority, authority_type, new_authority, multi_signers, opts
        )
        return await self._conn.send_transaction(txn, payer, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def mint_to(
        self,
        dest: PublicKey,
        mint_authority: Union[Keypair, PublicKey],
        amount: int,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Mint new tokens.

        :param dest: Public key of the account to mint to.
        :param mint_authority: Public key of the minting authority.
        :param amount: Amount to mint.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.

        If skip confirmation is set to `False`, this method will block for at most 30 seconds
        or until the transaction is confirmed.
        """
        txn, signers, opts = self._mint_to_args(dest, mint_authority, amount, multi_signers, opts)
        return await self._conn.send_transaction(txn, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def burn(
        self,
        account: PublicKey,
        owner: PublicKey,
        amount: int,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Burn tokens.

        :param account: Account to burn tokens from.
        :param owner: Owner of the account.
        :param amount: Amount to burn.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, signers, opts = self._burn_args(account, owner, amount, multi_signers, opts)
        return await self._conn.send_transaction(txn, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def close_account(
        self,
        account: PublicKey,
        dest: PublicKey,
        authority: PublicKey,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Remove approval for the transfer of any remaining tokens.

        :param account: Account to close.
        :param dest: Account to receive the remaining balance of the closed account.
        :param authority: Authority which is allowed to close the account.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, signers, opts = self._close_account_args(account, dest, authority, multi_signers)
        return await self._conn.send_transaction(txn, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def freeze_account(
        self,
        account: PublicKey,
        authority: PublicKey,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Freeze account.

        :param account: Account to freeze.
        :param authority: The mint freeze authority.
        :param multi_signers: (optional) Signing accounts if `authority` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, signers, opts = self._freeze_account_args(account, authority, multi_signers)
        return await self._conn.send_transaction(txn, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def thaw_account(
        self,
        account: PublicKey,
        authority: PublicKey,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Thaw account.

        :param account: Account to thaw.
        :param authority: The mint freeze authority.
        :param multi_signers: (optional) Signing accounts if `authority` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, signers, opts = self._thaw_account_args(account, authority, multi_signers)
        return await self._conn.send_transaction(txn, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def transfer_checked(
        self,
        source: PublicKey,
        dest: PublicKey,
        owner: PublicKey,
        amount: int,
        decimals: int,
        multi_signers: Optional[List[Keypair]],
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Transfer tokens to another account, asserting the token mint and decimals.

        :param source: Public key of account to transfer tokens from.
        :param dest: Public key of account to transfer tokens to.
        :param owner: Owner of the source account.
        :param amount: Number of tokens to transfer.
        :param decimals: Number of decimals in transfer amount.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, signers, opts = self._transfer_checked_args(source, dest, owner, amount, decimals, multi_signers, opts)
        return await self._conn.send_transaction(txn, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def approve_checked(
        self,
        source: PublicKey,
        delegate: PublicKey,
        owner: PublicKey,
        amount: int,
        decimals: int,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Grant a third-party permission to transfer up the specified number of tokens from an account.

        This method also asserts the token mint and decimals.

        :param source: Public key of the source account.
        :param delegate: Account authorized to perform a transfer tokens from the source account.
        :param owner: Owner of the source account.
        :param amount: Maximum number of tokens the delegate may transfer.
        :param decimals: Number of decimals in approve amount.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, payer, signers, opts = self._approve_checked_args(
            source, delegate, owner, amount, decimals, multi_signers, opts
        )
        return await self._conn.send_transaction(txn, payer, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def mint_to_checked(
        self,
        dest: PublicKey,
        mint_authority: PublicKey,
        amount: int,
        decimals: int,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Mint new tokens, asserting the token mint and decimals.

        :param dest: Public key of the account to mint to.
        :param mint_authority: Public key of the minting authority.
        :param amount: Amount to mint.
        :param decimals: Number of decimals in amount to mint.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, signers, opts = self._mint_to_checked_args(dest, mint_authority, amount, decimals, multi_signers, opts)
        return await self._conn.send_transaction(txn, *signers, opts=opts, recent_blockhash=recent_blockhash)

    async def burn_checked(
        self,
        account: PublicKey,
        owner: PublicKey,
        amount: int,
        decimals: int,
        multi_signers: Optional[List[Keypair]] = None,
        opts: TxOpts = TxOpts(),
        recent_blockhash: Optional[Blockhash] = None,
    ) -> RPCResponse:
        """Burn tokens, asserting the token mint and decimals.

        :param account: Account to burn tokens from.
        :param owner: Owner of the account.
        :param amount: Amount to burn.
        :param decimals: Number of decimals in amount to burn.
        :param multi_signers: (optional) Signing accounts if `owner` is a multiSig.
        :param opts: (optional) Transaction options.
        """
        txn, signers, opts = self._burn_checked_args(account, owner, amount, decimals, multi_signers, opts)
        return await self._conn.send_transaction(txn, *signers, opts=opts, recent_blockhash=recent_blockhash)
