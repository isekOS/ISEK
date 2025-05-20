import yaml
import etcd3gw
from isek.util.logger import logger, LoggerManager
from isek.agent.persona import Persona
from isek.agent.single_agent import SingleAgent
from isek.agent.distributed_agent import DistributedAgent
from isek.llm.openai_model import OpenAIModel
from isek.embedding.openai_embedding import OpenAIEmbedding
from isek.node import EtcdRegistry, IsekCenterRegistry
from isek.llm import llms
from isek.embedding import embeddings


class IsekConfig:
    def __init__(self, yaml_path):
        try:
            with open(yaml_path, "r") as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Config loaded successfully from {yaml_path}")
        except Exception as e:
            logger.exception(f"Error loading IsekConfig: {e}")
            raise e

    def get(self, *keys):
        value = self.config
        for key in keys:
            value = value.get(key, None)
            if value is None:
                return None
        return value

    def get_sub_config(self, key):
        return self.config.get(key)

    def load_agent(self):
        is_dist = self.get("distributed")
        agent_config = self.get_sub_config("agent")
        persona = Persona.load(agent_config.get("persona_path"))
        debug = agent_config.get("debug")
        LoggerManager.init(debug)
        llm = self.load_llm()
        if not is_dist:
            return SingleAgent(persona=persona, model=llm)

        host = self.get("distributed.server", "host")
        port = self.get("distributed.server", "port")
        registry = self.load_registry()
        embedding = self.load_embedding()
        return DistributedAgent(
            host=host, port=port, registry=registry,
            persona=persona, model=llm, embedding=embedding
        )

    def load_registry(self):
        registry_mode = self.get("registry")
        if registry_mode == "etcd":
            return self.load_etcd_registry()
        else:
            return self.load_isek_center_registry()

    def load_etcd_registry(self):
        etcd_client = etcd3gw.Etcd3Client(**self.get_sub_config("registry.etcd"))
        return EtcdRegistry(etcd_client=etcd_client)

    def load_isek_center_registry(self):
        return IsekCenterRegistry(**self.get_sub_config("registry.isek_center"))

    def load_llm(self):
        llm_mode = self.get("llm")
        if llm_mode is None:
            return None
        return llms.get(llm_mode)(**self.get_sub_config(f"llm.{llm_mode}"))

    def load_embedding(self):
        embedding_mode = self.get("embedding")
        if embedding_mode is None:
            return None
        return embeddings.get(embedding_mode)(**self.get_sub_config(f"embedding.{embedding_mode}"))
