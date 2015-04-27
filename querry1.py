from pymongo import MongoClient
import pprint

def get_db(db_name):

    client = MongoClient('localhost', 27017)
    db = client[db_name]
    return db

def make_pipeline():
    
    pipeline = [{"$group" : {"_id" : "$type" , "count" : {"$sum" : 1}}},
                {"$sort" : { "count" : -1}}]
    return pipeline

def city_sources(db, pipeline):
    result = db.fullosm.aggregate(pipeline)
    print result
    return result

if __name__ == '__main__':
    db = get_db('portlandOR')
    collection = db.fullosm  
    pipeline = make_pipeline()
    result = city_sources(db, pipeline) 
    pprint.pprint(list(result))
