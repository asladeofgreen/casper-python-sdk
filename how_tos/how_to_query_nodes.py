import argparse
import os
import pathlib
import typing

import pycspr
from pycspr import NodeClient
from pycspr import NodeConnection
from pycspr.types import CL_URef


# Path to CCTL assets.
_PATH_TO_CCTL_ASSETS = pathlib.Path(os.getenv("CCTL")) / "assets"

# CLI argument parser.
_ARGS = argparse.ArgumentParser("Demo illustrating how to execute native transfers with pycspr.")

# CLI argument: path to cp2 account key - defaults to CCTL user 2.
_ARGS.add_argument(
    "--account-key-path",
    default=_PATH_TO_CCTL_ASSETS / "users" / "user-1" / "public_key_hex",
    dest="path_to_account_key",
    help="Path to a test user's public_key_hex file.",
    type=str,
    )

# CLI argument: host address of target node - defaults to CCTL node 1.
_ARGS.add_argument(
    "--node-host",
    default="localhost",
    dest="node_host",
    help="Host address of target node.",
    type=str,
    )

# CLI argument: Node API REST port - defaults to 14101 @ CCTL node 1.
_ARGS.add_argument(
    "--node-port-rest",
    default=14101,
    dest="node_port_rest",
    help="Node API REST port.  Typically 8888 on most nodes.",
    type=int,
    )

# CLI argument: Node API JSON-RPC port - defaults to 11101 @ CCTL node 1.
_ARGS.add_argument(
    "--node-port-rpc",
    default=11101,
    dest="node_port_rpc",
    help="Node API JSON-RPC port.  Typically 7777 on most nodes.",
    type=int,
    )

# CLI argument: Node API SSE port - defaults to 18101 @ CCTL node 1.
_ARGS.add_argument(
    "--node-port-sse",
    default=18101,
    dest="node_port_sse",
    help="Node API SSE port.  Typically 9999 on most nodes.",
    type=int,
    )


def _main(args: argparse.Namespace):
    """Main entry point.

    :param args: Parsed command line arguments.

    """
    print("-" * 74)
    print("PYCSPR :: How To Query A Node")
    print("-" * 74)

    # Set client.
    client = _get_client(args)

    # Set account key of test user.
    user_public_key = pycspr.parse_public_key(args.path_to_account_key)

    # Query 0.1: get_rpc_schema.
    rpc_schema: dict = client.get_rpc_schema()
    assert isinstance(rpc_schema, dict)
    print("SUCCESS :: Query 0.1: get_rpc_schema")

    # Query 0.2: get_rpc_endpoints.
    rpc_endpoints: typing.List[str] = client.get_rpc_endpoints()
    assert isinstance(rpc_endpoints, list)
    print("SUCCESS :: Query 0.2: get_rpc_endpoints")

    # Query 0.3: get_rpc_endpoint.
    rpc_endpoint: dict = client.get_rpc_endpoint("account_put_deploy")
    assert isinstance(rpc_endpoint, dict)
    print("SUCCESS :: Query 0.3: get_rpc_endpoint")

    # Query 1.1: get_node_metrics.
    node_metrics: typing.List[str] = client.get_node_metrics()
    assert isinstance(node_metrics, list)
    print("SUCCESS :: Query 1.1: get_node_metrics")

    # Query 1.2: get_node_metric.
    node_metric: typing.List[str] = client.get_node_metric("mem_deploy_gossiper")
    assert isinstance(node_metric, list)
    print("SUCCESS :: Query 1.2: get_node_metric")

    # Query 1.3: get_node_peers.
    node_peers: typing.List[dict] = client.get_node_peers()
    assert isinstance(node_peers, list)
    print("SUCCESS :: Query 1.3: get_node_peers")

    # Query 1.4: get_node_status.
    node_status: dict = client.get_node_status()
    assert isinstance(node_status, dict)
    print("SUCCESS :: Query 1.4: get_node_status")

    # Query 1.5: get_validator_changes.
    validator_changes: typing.List[dict] = client.get_validator_changes()
    assert isinstance(validator_changes, list)
    print("SUCCESS :: Query 1.5: get_validator_changes")

    # Query 2.1: get_state_root_hash - required for global state related queries.
    state_root_hash: bytes = client.get_state_root_hash()
    assert isinstance(state_root_hash, bytes)
    print("SUCCESS :: Query 2.1: get_state_root_hash")

    # Query 2.2: get_account_info.
    account_info: dict = client.get_account_info(user_public_key.account_key)
    assert isinstance(account_info, dict)
    print("SUCCESS :: Query 2.2: get_account_info")

    # Query 2.3: get_account_main_purse_uref.
    account_main_purse: CL_URef = \
        client.get_account_main_purse_uref(user_public_key.account_key)
    assert isinstance(account_main_purse, CL_URef)
    print("SUCCESS :: Query 2.3: get_account_main_purse_uref")

    # Query 2.4: get_account_balance.
    account_balance: int = client.get_account_balance(account_main_purse, state_root_hash)
    assert isinstance(account_balance, int)
    print("SUCCESS :: Query 2.4: get_account_balance")

    # Query 3.1: get_block_at_era_switch - will poll until switch block.
    print("POLLING :: Query 3.1: get_block_at_era_switch - may take some time")
    block: dict = client.get_block_at_era_switch()
    assert isinstance(block, dict)
    print("SUCCESS :: Query 3.1: get_block_at_era_switch")

    # Query 3.2: get_block - by hash & by height.
    assert client.get_block(block["hash"]) == \
           client.get_block(block["header"]["height"])
    print("SUCCESS :: Query 3.2: get_block - by hash & by height")

    # Query 3.3: get_block_transfers - by hash & by height.
    block_transfers: tuple = client.get_block_transfers(block["hash"])
    assert isinstance(block_transfers, tuple)
    assert isinstance(block_transfers[0], str)      # black hash
    assert isinstance(block_transfers[1], list)     # set of transfers
    assert block_transfers == client.get_block_transfers(block["header"]["height"])
    print("SUCCESS :: Query 3.3: get_block_transfers - by hash & by height")

    # Query 4.1: get_auction_info.
    auction_info: dict = client.get_auction_info()
    assert isinstance(auction_info, dict)
    print("SUCCESS :: Query 4.1: get_auction_info")

    # Query 4.2: get_era_info - by switch block hash.
    era_info: dict = client.get_era_info(block["hash"])
    assert isinstance(era_info, dict)
    print("SUCCESS :: Query 4.2: get_era_info - by switch block hash")

    # Query 4.3: get_era_info - by switch block height.
    assert client.get_era_info(block["hash"]) == \
           client.get_era_info(block["header"]["height"])
    print("SUCCESS :: Query 4.3: get_era_info - by switch block height")


def _get_client(args: argparse.Namespace) -> NodeClient:
    """Returns a pycspr client instance.

    """
    return NodeClient(NodeConnection(
        host=args.node_host,
        port_rest=args.node_port_rest,
        port_rpc=args.node_port_rpc,
        port_sse=args.node_port_sse
    ))


# Entry point.
if __name__ == "__main__":
    _main(_ARGS.parse_args())
