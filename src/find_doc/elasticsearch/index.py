from find_doc.core.config import settings
from find_doc.elasticsearch.client import es_client

INDEX_NAME = settings.INDEX_NAME

INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "russian_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "russian_stop", "russian_stemmer"],
                }
            },
            "filter": {
                "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                "russian_stemmer": {"type": "stemmer", "language": "russian"},
            },
        },
    },
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "text": {
                "type": "text",
                "analyzer": "russian_analyzer",
            },
        }
    },
}


async def init_index():
    exists = await es_client.indices.exists(index=INDEX_NAME)
    if not exists:
        await es_client.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS)
