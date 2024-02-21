import typing

from pycspr import serialisation
from pycspr import types
from pycspr.api import constants
from pycspr.api.servers.rpc import utils
from pycspr.api.servers.rpc.chain_get_state_root_hash import exec as chain_get_state_root_hash


def exec(
    proxy: utils.Proxy,
    key: str,
    path: typing.List[str],
    state_id: types.GlobalStateID = None
) -> bytes:
    """Returns results of a query to global state at a specified block or state root hash.

    :param proxy: Remote RPC server proxy. 
    :param key: Key of an item stored within global state.
    :param path: Identifier of a path within item.
    :param state_id: Identifier of global state leaf.
    :returns: Results of a global state query.

    """
    state_id = state_id or types.GlobalStateID(
        chain_get_state_root_hash(),
        types.GlobalStateIDType.STATE_ROOT_HASH
    )

    return proxy.get_response(
        constants.RPC_QUERY_GLOBAL_STATE,
        get_params(state_id, key, path)
        )


def get_params(
    state_id: types.GlobalStateID,
    key: types.CL_Key,
    path: typing.List[str]
) -> dict:
    """Returns results of a query to global state at a specified block or state root hash.

    :param state_id: Identifier of global state leaf.
    :param key: Key of an item stored within global state.
    :param path: Identifier of a path within item.
    :returns: Parameters to be passed to endpoint.

    """
    if state_id.id_type == types.GlobalStateIDType.BLOCK_HASH:
        state_id_type = "BlockHash"
    elif state_id.id_type == types.GlobalStateIDType.BLOCK_HEIGHT:
        state_id_type = "BlockHash"
    elif state_id.id_type == types.GlobalStateIDType.STATE_ROOT_HASH:
        state_id_type = "StateRootHash"
    else:
        raise ValueError(f"Invalid global state identifier type: {state_id.id_type}")

    state_id = \
        state_id.identifier.hex() if isinstance(state_id.identifier, bytes) else \
        state_id.identifier

    return {
        "state_identifier": {
            state_id_type: state_id
        },
        "key": serialisation.cl_value_to_parsed(key),
        "path": path
    }
