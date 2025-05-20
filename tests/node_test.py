# import uuid
# import time
# import threading
# from isek.node.isek_center_registry import IsekCenterRegistry
# from isek.node.node import Node
# from isek import isek_center
#
#
# class DefaultNode(Node):
#
#     def build_node_id(self) -> str:
#         return uuid.uuid1().hex
#
#     def metadata(self):
#         return {}
#
#     def on_message(self, sender, message):
#         return f"{self.node_id}"
#
#
# def test_node():
#     server_thread = threading.Thread(target=isek_center.main, daemon=True)
#     server_thread.start()
#     time.sleep(2)
#     registry = IsekCenterRegistry()
#
#     def build_node(port):
#         node = DefaultNode(host="localhost", port=port, registry=registry)
#         node_thread = threading.Thread(target=node.build_server, daemon=True)
#         node_thread.start()
#         return node
#
#     node_a = build_node(8080)
#     node_b = build_node(8081)
#     time.sleep(2)
#     for n in node_a.registry.get_available_nodes():
#         print(n)
#     assert len(node_a.registry.get_available_nodes()) == 2
#     assert len(node_b.registry.get_available_nodes()) == 2
#     node_a.registry.deregister_node(node_a.node_id)
#     node_b.registry.deregister_node(node_b.node_id)
#
#
