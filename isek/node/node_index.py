# import faiss
# import numpy as np
# from isek.util.tools import dict_md5
# from isek.util.logger import logger
# from isek.embedding.abstract_embedding import AbstractEmbedding
#
#
# class NodeIndex(object):
#     def __init__(self, embedding: AbstractEmbedding):
#         self.node_info_dict = {}
#         self.node_ids = []
#         self.node_index = None
#         self.embedding = embedding
#         self.dim = self.embedding.dim
#
#     def compare_and_build(self, all_nodes):
#         has_vector_nodes = {}
#         not_has_vector_nodes = {}
#         not_has_vector_intros = []
#         for node_id, node_info in all_nodes.items():
#             node_md5 = dict_md5(node_info)
#             if (node_id not in self.node_info_dict
#                     or self.node_info_dict[node_id]['md5'] != node_md5):
#                 not_has_vector_nodes[node_id] = {
#                     "md5": node_md5
#                 }
#                 not_has_vector_intros.append(node_info["metadata"]["intro"])
#             else:
#                 has_vector_nodes[node_id] = self.node_info_dict[node_id]
#
#         vectors = self.embedding.embedding(not_has_vector_intros)
#         for node_id, vector in zip(not_has_vector_nodes.keys(), vectors):
#             not_has_vector_nodes[node_id]['vector'] = vector
#
#         self.node_info_dict = has_vector_nodes | not_has_vector_nodes
#         if len(not_has_vector_nodes) > 0:
#             self.rebuild()
#
#     def rebuild(self):
#         node_ids, vectors = zip(*[(node_id, n['vector']) for node_id, n in self.node_info_dict.items()])
#         vectors = np.array(vectors, dtype='float32')
#         new_index = faiss.IndexFlatL2(self.dim)
#         new_index.add(vectors)
#         self.node_index = new_index
#         self.node_ids = node_ids
#         logger.debug("Node index rebuild finished.")
#
#     def search(self, query, limit=20):
#         vector = self.embedding.embedding_one(query)
#         results = []
#         if len(self.node_ids) > limit:
#             query_vector = np.array([vector], dtype='float32')
#             distances, indices = self.node_index.search(query_vector, limit)
#             for distance, index in zip(distances[0], indices[0]):
#                 real_distance = 1 - distance / 2.0
#                 node_id = self.node_ids[index]
#                 logger.debug(f"search result index[{index}] distance[{real_distance}] node_id[{node_id}]")
#                 results.append(node_id)
#         else:
#             results = self.node_ids
#         return results