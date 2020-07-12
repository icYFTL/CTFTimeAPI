from flask import Flask
import logging
import json
from requests import session as r_session

# Get config from config.json
config = json.load(open('config.json', 'r'))

# Flask setup
app = Flask(__name__)
app.config["APPLICATION_ROOT"] = config['url_prefix']

# Logging setup
logging.basicConfig(format='%(asctime)-15s | [%(name)s] %(levelname)s => %(message)s', level=logging.DEBUG, filename='CTFTimeAPI.log')

# Session for CTFTime requests
session = r_session()
session.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
                   'referer': 'https://ctftime.org/'}