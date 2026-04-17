from pymongo import MongoClient

client = MongoClient("mongodb+srv://anand_11:anand@cluster0.k9fsamf.mongodb.net/?appName=Cluster0"
)

db = client["notes_app"]

users = db["users"]
notes = db["notes"]