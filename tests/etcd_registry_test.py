# import ecdsa
# from isek.node.etcd_registry import EtcdRegistry
#
#
# def test_etcd_registry():
#     node_a = EtcdRegistry(host="47.236.116.81", port=2379)
#     node_a.register_node("node_a", "localhost", 8080, {"name": "a"})
#
#     node_b = EtcdRegistry(host="47.236.116.81", port=2379)
#     node_b.register_node("node_b", "localhost", 8082, {"name": "b"})
#
#     node_c = EtcdRegistry(host="47.236.116.81", port=2379, parent_node_id="abc")
#     node_c.register_node("node_c", "localhost", 8082, {"name": "c"})
#
#     assert len(node_b.get_available_nodes()) == 2
#
#     try:
#         node_b.deregister_node("node_a")
#     except ValueError as e:
#         print(f"node_b can not deregister node_a: {e}")
#     assert len(node_b.get_available_nodes()) == 2
#     node_a.deregister_node("node_a")
#     print("node_a deregister node_a")
#     assert len(node_b.get_available_nodes()) == 1
#     assert len(node_c.get_available_nodes()) == 1
#
