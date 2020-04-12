import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")


SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_URI = 'postgres://dfosuotlmrvmrc:3fa1cc4bfbe6a7a9575433324cb62be48e9d010f5b35304167e967fba615eb83@ec2-34-197-212-240.compute-1.amazonaws.com:5432/dbstsl3gvgms93'