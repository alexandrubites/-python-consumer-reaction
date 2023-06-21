# Import some necessary modules
# pip install kafka-python
# pip install pymongo
# pip install "pymongo[srv]"
from kafka import KafkaConsumer
from pymongo import MongoClient
from pymongo.server_api import ServerApi

import json

uri = "mongodb+srv://alexandrubites:IrvingConde@centeno.naivyqx.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection

# try:
#    client.admin.command('ping')
#    print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#    print(e)

# Connect to MongoDB and pizza_data database

try:
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

    db = client.bdnosql
    print("MongoDB Connected successfully!")
except:
    print("Could not connect to MongoDB")


consumer = KafkaConsumer('reactions', bootstrap_servers=[
'my-kafka-0.my-kafka-headless.alexandrubites.svc.cluster.local:9092'])
# Parse received data from Kafka
for msg in consumer:
    record = json.loads(msg.value)
    print(record)
    userId = record["userId"]
    objectId = record["objectId"]
    reactionId = record["reactionId"]

    # Create dictionary and ingest data into MongoDB
    try:
        reaction_rec = {
            'userId': userId,
            'objectId': objectId,
            'reactionId': reactionId
        }
        print(reaction_rec)
        reaction_id = db.bdnosql_reactions.insert_one(reaction_rec)
        print("Data inserted with record ids", reaction_id)
    except Exception as e:
        print("Could not insert into MongoDB:", e)

    # Create bdnosql_sumary and insert groups into mongodb
    try:
        agg_result = db.bdnosql_reactions.aggregate([
        {
            "$group": {
                "_id": {
                    "objectId": "$objectId",
                    "reactionId": "$reactionId"
                },
                "n": {"$sum": 1}
            }
        }
    ])
        db.bdnosql_sumaryReactions.delete_many({})
        for i in agg_result:
            print(i)
            sumary_id = db.bdnosql_sumaryReactions.insert_one(i)
            print("Sumary Reactions inserted with record ids: ", sumary_id)
    except Exception as e:
        print(f'group vy cought {type(e)}: ')
        print(e)