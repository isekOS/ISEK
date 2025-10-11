import os
import json
import time
from typing import Tuple, Optional
from pathlib import Path

from dotenv import load_dotenv
from eth_account import Account
from web3 import Web3

from isek.utils.log import log
from isek.web3.wallet_manager import IsekWalletManager


load_dotenv()


def _get_w3() -> Web3:
    rpc_url = os.getenv("ISEK_RPC_URL")
    if not rpc_url:
        raise ValueError("ISEK_RPC_URL not set")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    try:
        if hasattr(w3, "is_connected"):
            if not w3.is_connected():
                raise ConnectionError(f"Failed to connect to RPC: {rpc_url}")
        else:
            _ = w3.eth.block_number
    except Exception as e:
        raise ConnectionError(f"RPC connection error ({rpc_url}): {e}")
    return w3


def _load_abi(abi_path: Optional[str] = None) -> list:
    path_str = abi_path or os.getenv("ISEK_IDENTITY_ABI_PATH")
    if not path_str:
        raise ValueError("ISEK_IDENTITY_ABI_PATH is not set")

    # Support relative paths: try as-is (cwd), then relative to this module directory
    candidates = [Path(path_str)]
    candidates.append(Path(__file__).parent / path_str)
    file_path: Optional[Path] = None
    for candidate in candidates:
        try_path = candidate.resolve() if not candidate.exists() else candidate
        if try_path.exists():
            file_path = try_path
            break
    if file_path is None:
        raise FileNotFoundError(f"ABI file not found: {path_str}")

    with open(file_path, "r") as f:
        data = json.load(f)
    if isinstance(data, dict) and "abi" in data:
        return data["abi"]
    if isinstance(data, list):
        return data
    raise ValueError("Invalid ABI file format; expected array or object with 'abi'")


def _identity_contract(w3: Web3):
    addr = os.getenv("ISEK_IDENTITY_REGISTRY_ADDRESS")

    if not addr:
        raise ValueError("Missing registry address. Set ISEK_IDENTITY_REGISTRY_ADDRESS")
    return w3.eth.contract(address=w3.to_checksum_address(addr), abi=_load_abi())


def _resolve_info(contract, address: str) -> tuple[int, Optional[str], Optional[str]]:
    try:
        res = contract.functions.resolveByAddress(address).call()
        if res and int(res[0]) > 0:
            agent_id = int(res[0])
            domain = res[1] if len(res) > 1 else None
            addr_out = res[2] if len(res) > 2 else None
            return agent_id, domain, addr_out
    except Exception:
        pass
    return 0, None, None


def _eip1559_fees(w3: Web3) -> dict:
    latest = w3.eth.get_block("latest")
    base = latest.get("baseFeePerGas")
    if base is None:
        return {"gasPrice": w3.eth.gas_price}
    max_priority = int(os.getenv("ISEK_MAX_PRIORITY_FEE_GWEI", "1")) * 10**9
    max_fee = base * 2 + max_priority
    return {"maxFeePerGas": max_fee, "maxPriorityFeePerGas": max_priority}


def _register(contract, w3: Web3, acct: Account, domain: str) -> tuple[int, str]:
    fn = contract.functions.newAgent(domain, acct.address)
    gas = fn.estimate_gas({"from": acct.address})
    chain_id = int(os.getenv("ISEK_CHAIN_ID") or "84532")
    tx = fn.build_transaction(
        {
            "from": acct.address,
            "nonce": w3.eth.get_transaction_count(acct.address),
            "chainId": chain_id,
            "gas": int(gas * 1.2),
            **_eip1559_fees(w3),
        }
    )
    signed = Account.sign_transaction(tx, acct.key)
    raw = getattr(signed, "rawTransaction", getattr(signed, "raw_transaction", None))
    if raw is None:
        raise RuntimeError("Could not extract raw transaction bytes")
    txh = w3.eth.send_raw_transaction(raw)
    tx_hex = txh.hex()
    log.info(f"Submitted registration tx: {tx_hex} ({_tx_link(tx_hex)})")
    rcpt = w3.eth.wait_for_transaction_receipt(txh)
    if rcpt.status != 1:
        log.error("Identity registration transaction reverted")
        raise RuntimeError("Registration failed (transaction reverted)")
    try:
        logs = contract.events.AgentRegistered().process_receipt(rcpt)
        if logs:
            return int(logs[0]["args"]["agentId"]), tx_hex
    except Exception:
        pass
    for _ in range(12):
        time.sleep(1.0)
        res = contract.functions.resolveByAddress(acct.address).call()
        if res and int(res[0]) > 0:
            return int(res[0]), tx_hex
    log.error("Registration succeeded but agentId could not be resolved after retries")
    return 0, tx_hex


def resolve_identity_by_address(
    address: str,
) -> tuple[int, Optional[str], Optional[str]]:
    w3 = _get_w3()
    c = _identity_contract(w3)
    return _resolve_info(c, address)


def resolve_identity_for_card(agent_card) -> tuple[int, Optional[str], Optional[str]]:
    wm = IsekWalletManager()
    address = wm.get_wallet_address(agent_card.name)
    return resolve_identity_by_address(address)


def ensure_identity(agent_card) -> Tuple[str, Optional[int], Optional[str]]:
    network_name = os.getenv("ISEK_NETWORK_NAME", "ISEK test network")
    wm = IsekWalletManager()
    wm.create_or_load_wallet(
        agent_card.name,
        agent_url=getattr(agent_card, "domain", None)
        or getattr(agent_card, "url", None),
    )
    address = wm.get_wallet_address(agent_card.name)

    try:
        w3 = _get_w3()
        c = _identity_contract(w3)
    except Exception as e:
        log.info(f"Registry not configured: {e}. Using wallet {address}")
        return address, None, None

    agent_id, reg_domain, reg_addr = _resolve_info(c, address)
    if agent_id > 0:
        log.info(
            f"Already registered on {network_name}. Agent ID: {agent_id}, Address: {reg_addr or address}, Domain: {reg_domain}"
        )
        return address, agent_id, None

    agent_domain = getattr(agent_card, "domain", None) or getattr(
        agent_card, "url", None
    )
    if not agent_domain:
        raise ValueError("Agent domain/url is required for registration")

    acct = wm.get_signing_account(agent_card.name)
    if acct is None:
        raise ValueError(
            "Registration requires local signing. Set ISEK_WALLET_BACKEND=local."
        )

    log.info(
        f"Registering {agent_card.name} with domain {agent_domain} on {network_name}"
    )
    agent_id, tx_hex = _register(c, w3, acct, agent_domain)
    if agent_id > 0:
        log.info(
            f"Registered on {network_name}. Agent ID: {agent_id}, Address: {address}, Domain: {agent_domain}, Tx: {tx_hex}"
        )
        return address, agent_id, tx_hex

    # Final resolve attempt
    time.sleep(2.0)
    final = _resolve_info(c, address)
    if final[0] > 0:
        log.info(
            f"Registered on {network_name}. Agent ID: {final[0]}, Address: {address}, Domain: {agent_domain}, Tx: {tx_hex}"
        )
        return address, final[0], tx_hex
    log.error(
        "Proceeding without resolved agentId. Registration tx was sent; will resolve later."
    )
    return address, None, tx_hex


def _tx_link(tx_hex: str) -> str:
    template = os.getenv(
        "ISEK_EXPLORER_TX_URL_TEMPLATE", "https://sepolia.basescan.org/tx/{tx_hash}"
    )
    return template.format(tx_hash=tx_hex)
