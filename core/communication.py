# core/communication.py

import yaml
from kafka import KafkaProducer, KafkaConsumer

class PubSubConfig:
    @staticmethod
    def load(path="../messaging/pubsub_config.py") -> dict:
        return yaml.safe_load(open(path, 'r'))

class EventBus:
    def __init__(self, config: dict):
        servers = config['bootstrap_servers']
        self.producer = KafkaProducer(bootstrap_servers=servers)
        self.consumer = KafkaConsumer(bootstrap_servers=servers)

    def publish(self, topic: str, message: bytes):
        self.producer.send(topic, message)

    def subscribe(self, topic: str):
        self.consumer.subscribe([topic])
        return self.consumer
