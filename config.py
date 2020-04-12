import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# SQLALCHEMY_DATABASE_URI = 'sqlite:///sfv_veggies.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgres://pxvtdswblsuiga:52cd888957385327482ddfeeb0ea6546a507abab0b46b3cd91505a3523dba853@ec2-18-235-97-230.compute-1.amazonaws.com:5432/dag3cksb6esvq'