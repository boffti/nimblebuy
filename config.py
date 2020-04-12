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
DATABASE_URI = 'postgres://hauqoqqdyajftq:28ca4ee1d28fba345ffcc74d6fc72804955eb4957ecc4d8f4b9cd742f1267dd0@ec2-3-234-109-123.compute-1.amazonaws.com:5432/df5gld6qit5fva'