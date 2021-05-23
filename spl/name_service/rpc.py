
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.system_program import SYS_PROGRAM_ID

from spl.name_service.utils import get_hashed_name, get_name_account_address
from spl.name_service.name_program import NAME_PROGRAM_ID


def fetch_account_data(
        client: Client,
        name_account: PublicKey,
        encoding='jsonParsed'):
    account_info = client.get_account_info(
            name_account, encoding=encoding)['result']
    data = account_info['value']['data']
    return tuple(data)


#def retrieve_name_data(
#        client: Client,
#        name: str,
#        hash_prefix: str="SPL Name Service",
#        name_class: PublicKey=SYS_PROGRAM_ID,
#        name_owner: PublicKey=SYS_PROGRAM_ID,
#        encoding: str='jsonParsed',
#        ):
#    hashed_name = get_hashed_name(hash_prefix, name)
#    account_key = get_name_account_address(
#        [hashed_name, bytes(name_class), bytes(name_owner)],
#        NAME_PROGRAM_ID
#        )
#    account_info = client.get_account_info(
#            account_key, encoding=encoding)['result']
#    data = account_info['value']['data']
#    return data[0], data[1]
