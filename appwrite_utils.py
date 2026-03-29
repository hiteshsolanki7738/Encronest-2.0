import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.id import ID

load_dotenv()

APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")
APPWRITE_COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_ID")
APPWRITE_BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID")

client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)

databases = Databases(client)
storage = Storage(client)


def upload_file(file_bytes, filename, receiver_email=None, expiry_time=None):
    # Upload file to storage
    file_response = storage.create_file(
        bucket_id=APPWRITE_BUCKET_ID,
        file_id=ID.unique(),
        file=file_bytes
    )

    file_id = file_response["$id"]

    # Save metadata in database
    databases.create_document(
        database_id=APPWRITE_DATABASE_ID,
        collection_id=APPWRITE_COLLECTION_ID,
        document_id=ID.unique(),
        data={
            "filename": filename,
            "download_url": file_id,
            "receiver_email": receiver_email,
            "expiry_time": expiry_time
        }
    )

    return file_id


def get_download_url(file_id):
    return f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{file_id}/view?project={APPWRITE_PROJECT_ID}"