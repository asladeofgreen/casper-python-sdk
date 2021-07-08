import datetime
import operator
import random



def test_create_deploy_approval(TYPES, FACTORY, vector_cl_data_1, vector_crypto_2):
    _bytes = vector_cl_data_1.get_value_as_bytes(TYPES.CLTypeKey.BYTE_ARRAY)
    for algo, pbk, pvk in [operator.itemgetter("algo", "pbk", "pvk")(i) for i in vector_crypto_2]:
        account_info = FACTORY.create_account_info(algo, pvk, pbk)
        approval = FACTORY.create_deploy_approval(account_info, _bytes)
        assert isinstance(approval, TYPES.DeployApproval)


def test_create_deploy_parameters(TYPES, FACTORY, a_test_account, a_test_chain_id):
    assert isinstance(
        FACTORY.create_deploy_parameters(
            account=FACTORY.create_public_key(
                a_test_account.algo,
                a_test_account.pbk
            ),
            chain_name=a_test_chain_id,
            dependencies=[],
            gas_price=random.randint(0, 65),
            timestamp=datetime.datetime.utcnow(),
            ttl="1day",
        ),
        TYPES.DeployStandardParameters
        )


def test_create_transfer_session(TYPES, FACTORY):
    assert isinstance(
        FACTORY.create_session_for_transfer(
            amount = random.randint(0, 1e9),
            correlation_id = random.randint(0, 1e9),
            target = bytes([]),
            ),
        TYPES.ExecutionInfo_Transfer
        )


def test_create_transfer_payment(TYPES, FACTORY):
    assert isinstance(
        FACTORY.create_standard_payment(
            amount = random.randint(0, 1e5),
        ),
        TYPES.ExecutionInfo_ModuleBytes
        )


def test_create_transfer_body(TYPES, FACTORY, deploy_params):
    payment = FACTORY.create_standard_payment(
        amount = random.randint(0, 1e5),
        )
    session = FACTORY.create_session_for_transfer(
        amount = random.randint(0, 1e9),
        correlation_id = random.randint(0, 1e9),
        target = bytes([]),
        )
    body = FACTORY.create_deploy_body(payment, session)
    assert isinstance(body, TYPES.DeployBody)
    assert isinstance(body.hash, str)
    assert len(body.hash) == 64


def test_create_transfer_header(TYPES, FACTORY, deploy_params):
    payment = FACTORY.create_standard_payment(
        amount = random.randint(0, 1e5),
        )
    session = FACTORY.create_session_for_transfer(
        amount = random.randint(0, 1e9),
        correlation_id = random.randint(0, 1e9),
        target = bytes([]),
        )
    body = FACTORY.create_deploy_body(payment, session)
    header = FACTORY.create_deploy_header(body, deploy_params)
    assert isinstance(header, TYPES.DeployHeader)
    assert isinstance(header.body_hash, str)
    assert len(header.body_hash) == 64


def test_create_transfer_deploy(TYPES, FACTORY, deploy_params, cp2):
    session = FACTORY.create_session_for_transfer(
        amount = random.randint(0, 1e9),
        correlation_id = random.randint(0, 1e9),
        target = cp2.account_hash,
        )
    payment = FACTORY.create_standard_payment(
        amount = random.randint(0, 1e5),
        )
    deploy = FACTORY.create_deploy(deploy_params, payment, session)
    assert isinstance(deploy, TYPES.Deploy)
    assert isinstance(deploy.hash, str)
    assert len(deploy.hash) == 64
