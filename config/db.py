from pymongo import MongoClient
import os

# IMPORTANT: Do NOT commit your real MongoDB URI to version control.
# This module reads the URI from the MONGO_URI environment variable.
# Create a `.env` file from `.env.example` and set MONGO_URI before running.

MONGO_URI = os.getenv("MONGO_URI")

if MONGO_URI:
	conn = MongoClient(MONGO_URI)
else:
	conn = None