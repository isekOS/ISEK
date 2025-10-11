import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from eth_account import Account
from isek.utils.log import log

# Load environment variables from a .env file if present
load_dotenv()


class IsekWalletManager:
    """Local-only ISEK wallet manager.

    Responsibilities:
    - Create or load agent-scoped local wallets
    - Persist and restore wallet data to/from disk
    - Expose address and local signing capabilities
    """

    def __init__(self, wallet_data_file: Optional[str] = None):
        # Allow override via argument; otherwise read from env; fallback to default per NETWORK
        if wallet_data_file:
            self.wallet_data_file = wallet_data_file
        else:
            env_file = os.getenv("ISEK_WALLET_DATA_FILE")
            if env_file:
                self.wallet_data_file = env_file
            else:
                network = os.getenv("NETWORK", "").lower().strip()
                suffix = f".{network}" if network else ""
                self.wallet_data_file = str(
                    Path(__file__).parent / f"wallet{suffix}.json"
                )

    def _load_all_data(self) -> Dict[str, Any]:
        if not os.path.exists(self.wallet_data_file):
            return {}
        try:
            with open(self.wallet_data_file, "r") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_all_data(self, all_data: Dict[str, Any]) -> None:
        with open(self.wallet_data_file, "w") as f:
            json.dump(all_data, f, indent=2)

    def create_or_load_wallet(
        self, agent_name: str, agent_url: Optional[str] = None
    ) -> None:
        """Create or load a local wallet record for the agent."""
        all_data = self._load_all_data()
        record: Dict[str, Any] = (
            all_data.get(agent_name, {}) if isinstance(all_data, dict) else {}
        )
        # Ensure local key exists
        if not record or record.get("type") != "local":
            acct = Account.create()
            record = {
                "type": "local",
                "private_key": acct.key.hex(),
                "address": acct.address,
            }
            log.info(f"Created new local wallet for {agent_name}: {acct.address}")
        # Persist/refresh agent_url if provided
        if agent_url:
            record["agent_url"] = agent_url
        all_data[agent_name] = record
        self._save_all_data(all_data)
        return None

    def get_wallet_address(self, agent_name: str) -> str:
        """Return the on-chain address for the agent (local-only)."""
        record = self._load_all_data().get(agent_name, {})
        address = record.get("address")
        if not address:
            # initialize local record
            self.create_or_load_wallet(agent_name)
            address = self._load_all_data().get(agent_name, {}).get("address")
        if not address:
            raise ValueError(f"Local wallet address not found for agent '{agent_name}'")
        return address

    # Local-only manager: balance and transfer helpers are not implemented.

    def get_signing_account(self, agent_name: str) -> Optional[Account]:
        """Return a local signing Account for the agent (local-only)."""
        record = self._load_all_data().get(agent_name, {})
        private_key = record.get("private_key")
        if not private_key:
            # initialize if missing
            self.create_or_load_wallet(agent_name)
            record = self._load_all_data().get(agent_name, {})
            private_key = record.get("private_key")
        if not private_key:
            return None
        if not str(private_key).startswith("0x"):
            private_key = "0x" + str(private_key)
        return Account.from_key(private_key)

    def get_agent_url(self, agent_name: str) -> Optional[str]:
        record = self._load_all_data().get(agent_name, {})
        return record.get("agent_url")

    def _load_wallet_data(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Load wallet data for an agent from disk."""
        all_data = self._load_all_data()
        data = all_data.get(agent_name)
        return data if isinstance(data, dict) else None

    def _save_wallet_data(self, agent_name: str, wallet_data: Dict[str, Any]) -> None:
        """Persist wallet data for an agent to disk."""
        all_data: Dict[str, Any] = self._load_all_data()
        all_data[agent_name] = wallet_data
        self._save_all_data(all_data)
