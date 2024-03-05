import dataclasses
import enum
import typing


@dataclasses.dataclass
class AccountInfo():
    account_hash: bytes
    action_thresholds: "ActionThresholds"
    associated_keys: typing.List["AssociatedKey"]
    main_purse: int
    named_keys: list


@dataclasses.dataclass
class ActionThresholds():
    deployment: int
    key_management: int


@dataclasses.dataclass
class AssociatedKey():
    account_hash: bytes
    weight: int


@dataclasses.dataclass
class AuctionBidByDelegator():
    bonding_purse: "URef"
    public_key: bytes
    delegatee: bytes
    staked_amount: int


@dataclasses.dataclass
class AuctionState():
    bids: typing.List["AuctionBidByValidator"]
    block_height: int
    era_validators: "EraValidators"
    state_root: bytes


@dataclasses.dataclass
class AuctionBidByValidator():
    public_key: bytes
    bid: "AuctionBidByValidatorInfo"


@dataclasses.dataclass
class AuctionBidByValidatorInfo():
    bonding_purse: "URef"
    delegation_rate: int
    delegators: typing.List["AuctionBidByDelegator"]
    inactive: bool
    staked_amount: int


@dataclasses.dataclass
class Block():
    body: "BlockBody"
    hash: bytes
    header: "BlockHeader"
    proofs: typing.List["BlockSignature"]


@dataclasses.dataclass
class BlockBody():
    proposer: bytes
    deploy_hashes: typing.List[bytes]
    transfer_hashes: typing.List[bytes]


@dataclasses.dataclass
class BlockHeader():
    accumulated_seed: bytes
    body_hash: bytes
    era_id: int
    height: int
    parent_hash: bytes
    protocol_version: str
    random_bit: bool
    state_root: bytes


@dataclasses.dataclass
class BlockSignature():
    public_key: bytes
    signature: bytes


@dataclasses.dataclass
class BlockTransfers():
    block_hash: bytes
    transfers: typing.List["Transfer"]


@dataclasses.dataclass
class Deploy():
    approvals: typing.List["DeployApproval"]
    hash: bytes
    header: dict
    payment: dict
    session: dict


@dataclasses.dataclass
class DeployApproval():
    signer: bytes
    signature: bytes


@dataclasses.dataclass
class DeployHeader():
    account: bytes
    body_hash: bytes
    chain_name: str
    dependencies: typing.List[bytes]
    gas_price: int
    timestamp: "Timestamp"
    ttl: "DeployTimeToLive"


@dataclasses.dataclass
class DeployTimeToLive():
    as_milliseconds: int
    humanized: str


@dataclasses.dataclass
class EraValidators():
    era_id: int
    validator_weights: typing.List["EraValidatorWeight"]


@dataclasses.dataclass
class EraValidatorWeight():
    public_key: bytes
    weight: int


@dataclasses.dataclass
class EraInfo():
    seigniorage_allocations: typing.List["SeigniorageAllocation"]


@dataclasses.dataclass
class EraSummary():
    block_hash: bytes
    era_id: int
    era_info: EraInfo
    merkle_proof: str
    state_root: bytes


@dataclasses.dataclass
class NamedKey():
    key: str
    name: str


@dataclasses.dataclass
class ProtocolVersion():
    major: int
    minor: int
    revision: int


@dataclasses.dataclass
class SeigniorageAllocation():
    amount: int


@dataclasses.dataclass
class SeigniorageAllocationForDelegator(SeigniorageAllocation):
    delegator_public_key: bytes
    validator_public_key: bytes


@dataclasses.dataclass
class SeigniorageAllocationForValidator(SeigniorageAllocation):
    validator_public_key: bytes


@dataclasses.dataclass
class Transfer():
    amount: int
    deploy_hash: bytes
    from_: bytes
    gas: int
    source: "URef"
    target: "URef"
    correlation_id: int = None
    to_: bytes = None


@dataclasses.dataclass
class Timestamp():
    value: float


class URefAccessRights(enum.Enum):
    NONE = 0
    READ = 1
    WRITE = 2
    ADD = 4
    READ_WRITE = 3
    READ_ADD = 5
    ADD_WRITE = 6
    READ_ADD_WRITE = 7


@dataclasses.dataclass
class URef():
    access_rights: URefAccessRights
    address: bytes


@dataclasses.dataclass
class ValidatorChanges():
    public_key: bytes
    status_changes: typing.List["ValidatorStatusChange"]


@dataclasses.dataclass
class ValidatorStatusChange():
    era_id: int
    status_change: "ValidatorStatusChangeType"


class ValidatorStatusChangeType(enum.Enum):
    Added = 0
    Removed = 1
    Banned = 2
    CannotPropose = 4
    SeenAsFaulty = 3
