import time
import typing

from pycspr import types
from pycspr.api import constants
from pycspr.api import sse_consumer
from pycspr.api.connection import NodeConnectionInfo
from pycspr.api.sse_types import NodeEventChannel, NodeEventInfo
from pycspr.api.sse_types import NodeEventType
from pycspr.api.clients import RestServerClient
from pycspr.api.clients import RpcServerClient


class NodeClient():
    """Exposes a set of (categorised) functions for interacting  with a node.

    """
    def __init__(self, connection_info: NodeConnectionInfo):
        """Instance constructor.

        :param connection: Information required to connect to a node.

        """
        self.connection = connection_info

        self._get_rest_response = connection_info.get_rest_response
        self._get_speculative_rpc_response = connection_info.get_speculative_rpc_response

        self._rest_client = RestServerClient(connection_info)
        self._rpc_client = RpcServerClient(connection_info)
        
        # RPC server function set.
        self.get_account_balance = self._rpc_client.query_balance
        self.get_account_info = self._rpc_client.state_get_account_info
        self.get_auction_info = self._rpc_client.state_get_auction_info
        self.get_block = self._rpc_client.chain_get_block
        self.get_block_transfers = self._rpc_client.chain_get_block_transfers
        self.get_chain_spec = self._rpc_client.info_get_chainspec
        self.get_deploy = self._rpc_client.info_get_deploy
        self.get_dictionary_item = self._rpc_client.state_get_dictionary_item
        self.get_era_info = self._rpc_client.chain_get_era_info_by_switch_block
        self.get_era_info_by_switch_block = self._rpc_client.chain_get_era_info_by_switch_block
        self.get_era_summary = self._rpc_client.chain_get_era_summary
        self.get_node_peers = self._rpc_client.info_get_peers
        self.get_node_status = self._rpc_client.info_get_status
        self.get_rpc_schema = self._rpc_client.discover
        self.get_state_item = self._rpc_client.state_get_item
        self.get_state_root_hash = self._rpc_client.chain_get_state_root_hash
        self.get_validator_changes = self._rpc_client.info_get_validator_changes
        self.query_global_state = self._rpc_client.query_global_state


    async def await_n_blocks(self, offset: int):
        """Awaits until linear block chain has advanced by N blocks.

        :param offset: Number of blocks to await.

        """
        await self.await_n_events(NodeEventChannel.main, NodeEventType.BlockAdded, offset)

    async def await_n_eras(self, offset: int):
        """Awaits until consensus has advanced by N eras.

        :param offset: Number of eras to await.

        """
        await self.await_n_events(NodeEventChannel.main, NodeEventType.Step, offset)
        await self.await_n_blocks(1)

    async def await_n_events(
        self,
        event_channel: NodeEventChannel,
        event_type: NodeEventType,
        offset: int
    ) -> dict:
        """Awaits emission of N events of a certain type over a certain channel.

        :param event_channel: Type of event channel to which to bind.
        :param event_type: Type of event type to listen for (all if unspecified).
        :param offset: Number of events to await.
        :returns: Event payload N events into the future.

        """
        assert offset > 0
        count = 0
        for event_info in self.yield_events(event_channel, event_type):
            count += 1
            if count == offset:
                return event_info.payload

    async def await_until_block_n(self, block_height: int) -> dict:
        """Awaits until linear block chain has advanced to block N.

        :param block_height: Hieght of block to await.
        :returns: On-chain block information at block N blocks.

        """
        _, block_height_current = self.get_chain_heights()
        offset = block_height - block_height_current
        if offset > 0:
            await self.await_n_blocks(offset)

    async def await_until_era_n(self, era_height: int) -> dict:
        """Awaits until consensus has advanced to era N.

        :param era_height: Height of era to await.
        :returns: On-chain era information N eras in the future.

        """
        era_height_current, _ = self.get_chain_heights()
        offset = era_height - era_height_current
        if offset > 0:
            await self.await_n_eras(offset)

    def get_account_main_purse_uref(
        self,
        account_id: types.AccountID,
        block_id: types.BlockID = None
    ) -> types.CL_URef:
        """Returns an on-chain account's main purse unforgeable reference.

        :param account_id: An account holder's public key prefixed with a key type identifier.
        :param block_id: Identifier of a finalised block.
        :returns: Account main purse unforgeable reference.

        """
        account_info = self.get_account_info(account_id, block_id)

        return types.CL_URef.from_string(account_info["main_purse"])

    def get_account_named_key(
        self,
        account_id: types.AccountID,
        key_name: str,
        block_id: types.BlockID = None
    ) -> types.CL_Key:
        """Returns a key stored under an account's storage under a specific name.

        :param account_id: An account holder's public key prefixed with a key type identifier.
        :param key_name: Name of key under which account data is stored.
        :param block_id: Identifier of a finalised block.
        :returns: A CL key if found.

        """
        account_info = self.get_account_info(account_id, block_id)
        for named_key in account_info["named_keys"]:
            if named_key["name"] == key_name:
                return types.CL_Key.from_string(named_key["key"])

    def get_block_at_era_switch(
        self,
        polling_interval_seconds: float = 1.0,
        max_polling_time_seconds: float = 120.0
    ) -> dict:
        """Returns next switch block.

        :param polling_interval_seconds: Time interval time before polling for next switch block.
        :param max_polling_time_seconds: Maximum time in seconds to poll.
        :returns: On-chain block information.

        """
        elapsed = 0.0
        while True:
            block = self.get_block()
            if block["header"]["era_end"] is not None:
                return block

            elapsed += polling_interval_seconds
            if elapsed > max_polling_time_seconds:
                break
            time.sleep(polling_interval_seconds)

    def get_block_height(self) -> int:
        """Returns height of current block.

        :returns: Hieght of current block.

        """
        _, block_height = self.get_chain_heights()

        return block_height

    def get_chain_heights(self) -> int:
        """Returns height of current era & block.

        :returns: 2-ary tuple: (era height, block height).

        """
        block: dict = self.get_block()

        return block["header"]["era_id"], block["header"]["height"]

    def get_era_height(self) -> int:
        """Returns height of current era.

        :returns: Hieght of current era.

        """
        era_height, _ = self.get_chain_heights()

        return era_height

    def get_events(
        self,
        callback: typing.Callable[[NodeEventChannel, NodeEventType, int, dict], None],
        event_channel: NodeEventChannel,
        event_type: NodeEventType = None,
        event_id: int = 0
    ):
        """Binds to a node's event stream - events are passed to callback for processing.

        :param callback: Callback to invoke whenever an event of relevant type is received.
        :param event_channel: Type of event channel to which to bind.
        :param event_type: Type of event type to listen for (all if unspecified).
        :param event_id: Identifier of event from which to start stream listening.

        """
        sse_consumer.get_events(self.connection, callback, event_channel, event_type, event_id)

    def get_node_metric(self, metric_id: str) -> list:
        """Returns node metrics information filtered by a particular metric.

        :param metric_id: Identifier of node metric.
        :returns: Node metrics information filtered by a particular metric.

        """
        metrics = self.get_node_metrics()

        return [i for i in metrics if i.lower().startswith(metric_id.lower())]

    def get_node_metrics(self) -> list:
        """Returns set of node metrics.

        :returns: Node metrics information.

        """
        response = self._get_rest_response(constants.REST_GET_METRICS)
        metrics = sorted([i.strip() for i in response.split("\n") if not i.startswith("#")])

        return metrics

    def get_rpc_endpoint(self, endpoint: str) -> dict:
        """Returns RPC schema.

        :param endpoint: A specific endpoint of interest.
        :returns: A JSON-RPC schema endpoint fragment.

        """
        schema = self.get_rpc_schema()
        for obj in schema["methods"]:
            if obj["name"].lower() == endpoint.lower():
                return obj

    def get_rpc_endpoints(self) -> typing.Union[dict, list]:
        """Returns RPC schema.

        :returns: A list of all supported JSON-RPC endpoints.

        """
        schema = self.get_rpc_schema()

        return sorted([i["name"] for i in schema["methods"]])

    def yield_events(
        self,
        event_channel: NodeEventChannel,
        event_type: NodeEventType = None,
        event_id: int = 0
    ) -> typing.Generator[NodeEventInfo, None, None]:
        """Binds to a node's event stream - and yields consumed events.

        :param event_channel: Type of event channel to which to bind.
        :param event_type: Type of event type to listen for (all if unspecified).
        :param event_id: Identifier of event from which to start stream listening.

        """
        for event_info in sse_consumer.yield_events(
            self.connection,
            event_channel,
            event_type,
            event_id
            ):
            yield event_info
