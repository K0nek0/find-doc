from elasticsearch import AsyncElasticsearch

from find_doc.core.config import settings

es_client = AsyncElasticsearch(settings.ELASTICSEARCH_URL)
