# import time
#
# from isek.node.isek_center_registry import IsekCenterRegistry
# from isek import isek_center
# import threading
#
#
# def test_isek_center_registry():
#     server_thread = threading.Thread(target=isek_center.main, daemon=True)
#     server_thread.start()
#     time.sleep(2)
#
#     node_a = IsekCenterRegistry()
#     node_a.register_node("node_a", "localhost", 8080, {"name": "a"})
#
#     node_b = IsekCenterRegistry()
#     node_b.register_node("node_b", "localhost", 8082, {"name": "b"})
#
#     all_nodes = node_b.get_available_nodes()
#     assert len(all_nodes) == 2
#     node_a.deregister_node("node_a")
#     all_nodes = node_b.get_available_nodes()
#     assert len(all_nodes) == 1
#     node_b.deregister_node("node_b")