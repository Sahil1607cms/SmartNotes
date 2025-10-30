
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import certifi
import os

load_dotenv()
PASS  = os.getenv("PASS")

uri = f"mongodb+srv://sahil16072004_db_user:{PASS}@cluster0.cvrmksw.mongodb.net/?retryWrites=true&w=majority&tls=true"

# Create a new client and connect to the server
client = MongoClient(
    uri,
    server_api=ServerApi('1'),
    tlsCAFile=certifi.where(),  # this ensures trusted SSL handshake
)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)