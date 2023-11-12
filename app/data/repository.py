import motor.motor_asyncio
from bson import ObjectId

class Repository:
    def __init__(self, url, database_name):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self.db = self.client[database_name]

    async def insert_one(self, collection_name: str, document: dict) -> str:
        collection = self.db[collection_name]
        result = await collection.insert_one(document)
        return result.inserted_id

    async def insert_many(self, collection_name: str, documents: list) -> list:
        collection = self.db[collection_name]
        result = await collection.insert_many(documents)
        return result.inserted_ids

    async def find_one(self, collection_name, query) -> dict:
        collection = self.db[collection_name]
        document = await collection.find_one(query)
        return document
    
    async def find_by_id(self, collection_name, id) -> dict:
        collection = self.db[collection_name]
        document = await collection.find_one({"_id": ObjectId(id)})
        return document

    async def find_many(self, collection_name, query) -> list:
        collection = self.db[collection_name]
        documents = []
        async for document in collection.find(query):
            documents.append(document)
        return documents

    async def update_one(self, collection_name, query, update):
        collection = self.db[collection_name]
        result = await collection.update_one(query, {'$set': update})
        return result.modified_count

    async def delete_one(self, collection_name, query):
        collection = self.db[collection_name]
        result = await collection.delete_one(query)
        return result.deleted_count

    async def delete_many(self, collection_name, query):
        collection = self.db[collection_name]
        result = await collection.delete_many(query)
        return result.deleted_count
    
    async def delete_by_id(self, collection_name, id):
        collection = self.db[collection_name]
        result = await collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count
