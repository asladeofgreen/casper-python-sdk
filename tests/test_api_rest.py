from pycspr import NodeRestClient


async def test_get_chainspec(REST_CLIENT: NodeRestClient):
    data = await REST_CLIENT.get_chainspec()
    assert isinstance(data, dict)
    assert len(data) == 3
    assert "chainspec_bytes" in data
    assert "maybe_genesis_accounts_bytes" in data
    assert "maybe_global_state_bytes" in data


async def test_get_node_metrics(REST_CLIENT: NodeRestClient):
    data = await REST_CLIENT.get_node_metrics()
    assert isinstance(data, list)
    assert len(data) > 300


async def test_get_node_metric(REST_CLIENT: NodeRestClient):
    data = await REST_CLIENT.get_node_metric("mem_deploy_gossiper")
    assert isinstance(data, list)
    assert len(data) == 1

    data = await REST_CLIENT.get_node_metric("xxxxxxxxxxxxxxxxxxxxx")
    assert isinstance(data, list)
    assert len(data) == 0


async def test_get_node_status(REST_CLIENT: NodeRestClient):
    data = await REST_CLIENT.get_node_status()
    assert isinstance(data, dict)
    assert len(data) == 14


async def test_get_node_rpc_schema(REST_CLIENT: NodeRestClient):
    data = await REST_CLIENT.get_node_rpc_schema()
    assert isinstance(data, dict)
    assert len(data) == 5


async def test_get_validator_changes(REST_CLIENT: NodeRestClient):
    data = await REST_CLIENT.get_validator_changes()
    assert isinstance(data, list)
    for item in data:
        assert isinstance(item, dict)
