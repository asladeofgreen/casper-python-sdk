from pycspr.api import constants
from pycspr.api.servers.rpc.utils import Proxy


def exec(proxy: Proxy) -> dict:
    """Returns canonical network state information.

    :param proxy: Remote RPC server proxy. 
    :returns: Chain spec, genesis accounts and global state information.

    """
    response = proxy.get_response(constants.RPC_INFO_GET_CHAINSPEC)

    return response["chainspec_bytes"]
