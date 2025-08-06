import os
from dotenv import load_dotenv

workers = 4

bind = '127.0.0.1:8080'

preload_app = True

dotenv_path = os.path.join(os.getcwd(), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
