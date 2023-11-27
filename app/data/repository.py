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

    async def find_one(self, collection_name, query:dict) -> dict:
            # document = await db.test_collection.find_one({"i": {"$lt": 1}})
        collection = self.db[collection_name]
        document = await collection.find_one(query)
        return document
    
    async def find_by_id(self, collection_name, id) -> dict:
        collection = self.db[collection_name]
        document = await collection.find_one({"_id": ObjectId(id)})
        return document

    async def find_many(self, collection_name, query,projection={}) -> list:
        collection = self.db[collection_name]
        documents = []
        async for document in collection.find(query,projection):
            documents.append(document)
        return documents
    
    async def find_agregate(self,collection_name,match,lookup):
        collection=self.db[collection_name]
        res=collection.aggregate(
        [
        
            lookup,
        
            match,
        
   
    
        ])
        documents = []
        async for document in res:
            documents.append(document)
        return documents
    
    async def find_many_filter(self, collection_name, 
                        query,skip=0,limit=100) -> list:
        collection = self.db[collection_name]
        documents = []
        results=collection.aggregate([
                {'$match': query},
                {'$skip':  skip}, 
                {'$limit':  limit}
              ])
        async for document in results:
            documents.append(document)
        return documents

    async def update_one(self, collection_name, query, update:dict):
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

    async def get_count(self, collection_name, query):
        collection = self.db[collection_name]
        result = await collection.count_documents(query)
        return result