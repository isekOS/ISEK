import json
from typing import Optional, Dict

import etcd3gw
import base64
from ecdsa.keys import SigningKey, VerifyingKey
from ecdsa.curves import NIST256p

from isek.util.logger import logger
from isek.node.registry import Registry


class EtcdRegistry(Registry):
    def __init__(self,
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 parent_node_id: Optional[str] = "root",
                 etcd_client: Optional[etcd3gw.Etcd3Client] = None,
                 ttl: int = 30):

        if host and port and etcd_client:
            logger.warning("Both 'host/port' and 'etcd_client' provided. Using 'etcd_client'.")

        if etcd_client:
            self.etcd_client = etcd_client
        elif host and port:
            self.etcd_client = etcd3gw.client(host=host, port=port)
        else:
            raise TypeError("Either 'host' and 'port' or 'etcd_client' must be provided.")

        self.parent_node_id = parent_node_id or "root"

        if not self.etcd_client.status():
            raise ConnectionError("Failed to connect to the etcd server.")

        self.sk = SigningKey.generate(curve=NIST256p)

        self.ttl = ttl
        self.leases = {}

    def register_node(self, node_id: str, host: str, port: int, metadata: Optional[Dict[str, str]] = None):
        vk = self.sk.verifying_key
        vk_bytes = vk.to_string()
        vk_base64 = base64.b64encode(vk_bytes).decode('utf-8')

        node_info = {
            "node_id": node_id,
            "host": host,
            "port": port,
            "public_key": vk_base64,
            "metadata": metadata or {}
        }

        node_info_json = json.dumps(node_info, sort_keys=True).encode("utf-8")
        signature = base64.b64encode(self.sk.sign_deterministic(node_info_json)).decode("utf-8")

        node_entry = {
            "node_info": node_info,
            "signature": signature
        }

        lease = self.etcd_client.lease(self.ttl)
        self.leases[node_id] = lease

        key = f"/{self.parent_node_id}/{node_id}"
        self.etcd_client.put(key, json.dumps(node_entry), lease=lease)

        logger.info(f"Node {node_id} registered with info: {node_info}")

    def lease_refresh(self, node_id: str):
        lease_refresh_response = None
        try:
            self.__verify_signature(node_id)
            self.leases[node_id].refresh()
            # logger.debug(f"Lease renewed for node: {node_id}, response: {lease_refresh_response}")
        except Exception as e:
            logger.exception(f"Lease renewal failed for node {node_id}, response: {lease_refresh_response}: {e}")

    def get_available_nodes(self) -> Dict[str, dict]:
        nodes = {}
        for value, metadata in self.etcd_client.get_prefix(f"/{self.parent_node_id}/"):
            node_id = metadata.get('key').decode("utf-8").split(f"/{self.parent_node_id}/")[-1]
            try:
                nodes[node_id] = json.loads(value.decode("utf-8"))['node_info']
            except Exception as e:
                logger.exception(f"Error decoding node {node_id}: {e}")
        return nodes

    def deregister_node(self, node_id: str):
        key = f"/{self.parent_node_id}/{node_id}"
        self.__verify_signature(node_id)
        self.etcd_client.delete(key)
        if node_id in self.leases:
            self.leases[node_id].revoke()
            del self.leases[node_id]
        logger.info(f"Node {node_id} deregistered.")

    def __verify_signature(self, node_id):
        key = f"/{self.parent_node_id}/{node_id}"
        node_entry_json = self.etcd_client.get(key)[0]

        if not node_entry_json:
            raise ValueError(f"Node {node_id} not found")

        node_entry = json.loads(node_entry_json.decode("utf-8"))
        node_info = node_entry["node_info"]
        node_base64_signature = node_entry["signature"]

        vk_bytes = base64.b64decode(node_info["public_key"])
        vk = VerifyingKey.from_string(vk_bytes, curve=NIST256p)

        node_info_json = json.dumps(node_info, sort_keys=True).encode("utf-8")
        calculated_signature = self.sk.sign_deterministic(node_info_json)
        calculated_base64_signature = base64.b64encode(calculated_signature).decode("utf-8")

        if calculated_base64_signature != node_base64_signature:
            raise ValueError(f"Signature verification failed for node {node_id}!")

        if not vk.verify(calculated_signature, node_info_json):
            raise ValueError(f"Node {node_id} has an invalid signature!")
