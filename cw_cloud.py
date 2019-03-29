# ??? to resolve error caused when running in debug mode in virtual environment
#
#!/usr/bin/env python3

# flask container framework
from flask import Flask, request, jsonify, g, url_for
# flask application object [set to load configuration from file]
app = Flask(__name__, instance_relative_config=True)
#
app.config.from_object('config')
# load configuration from file
app.config.from_pyfile('config.py')

# handle http requests
import requests

# password hashing
from passlib.apps import custom_app_context as pwd_context

# token based authentication
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

# for password based authentication
from flask_httpauth import HTTPBasicAuth
#
auth = HTTPBasicAuth()

# cassandra database cluster
from cassandra.cluster import Cluster
#
cluster = Cluster(['cassandra'])
# establish connection session to cassandra cluster
session = cluster.connect()

#
# --- Global Variables
#

url_template = "{endpoint}apikey={apikey}{query}"
_endpoint = app.config['API_ENDPOINT']
_apikey = app.config['MY_API_KEY']

#
# --- Authentication
#

# get hash for user password
def hash_password(password):
	return pwd_context.encrypt(password)

# verify user password hash
def verify_password_hash(password, password_hash):
	return pwd_context.verify(password, password_hash)

# generate new token for user id
def generate_auth_token(user_id, expiration = 600):
	#
	s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
	# return new generated authentication token
	return s.dumps({ 'id': user_id })

# verify given token [static because ???]
@staticmethod
def verify_auth_token(token):
	#
	s = Serializer(app.config['SECRET_KEY'])
	# check if authentication token still valid
	try:
		# try loading token ?
		data = s.loads(token)
	except SignatureExpired:
		# valid token, but expired
		return None
	except BadSignature:
		# invalid token
		return None
	# get user data from given id
	user = session.execute("SELECT * FROM users WHERE id = '{}' LIMIT 1".format(data['id']))
	# return user data for given authentication token
	return user

# authentication with token, or username and password
@auth.verify_password
def verify_password(username_or_token, password):
    # try verify token
    user = verify_auth_token(username_or_token)
    # if token based authentication failed
    if not user:
    	# try verify with username and password
    	user = session.execute("SELECT * FROM users WHERE username = '{}' LIMIT 1".format(username_or_token))
    	# if no user found, or password hash authentication failed
    	if not user or not verify_password_hash(password, user['password_hash']):
        	# return failure
        	return False
    # store user data for authentication
    g.user = user
    # return success
    return True

# curl -u miguel:python -i -X GET http://localhost:8080/token/new
# request new token
@app.route('/token/new')
# resource requires authentication
@auth.login_required
def get_auth_token():
    # generate a new authentication token for user id
    token = generate_auth_token(g.user['user_id'])
    # return generated authentication token
    return jsonify({ 'token': token.decode('ascii') })

#
# --- External API Requests
#

# handle all unknown URLs [Uniform Resource Locator]
@app.errorhandler(404)
def page_not_found(e):
	# return error response
	return jsonify({'error':'Resource not found'}),404

# curl -u maaz:qmul -i -X GET http://localhost:8080/stock_time_series?function=XYZ
# curl -u maaz:wrongpassword -i -X GET http://localhost:8080/stock_time_series
# curl -u eyJhbGciOiJIUzI1NiIsImV4cCI6MTM4NTY2OTY1NSwiaWF0IjoxMzg1NjY5MDU1fQ.eyJpZCI6MX0.XbOEFJkhjHJ5uRINh2JA1BPzXjSohKYDRT472wGOvjc:unused -i -X GET http://localhost:8080/stock_time_series
# Stock Time Series [Intraday, Daily, Daily_Adjusted, Quote_Endpoint, Search_Endpoint]
@app.route('/stock_time_series',methods=["GET"])
# resource requires authentication
@auth.login_required
def stock_time_series():
	# set to defaults
	_function = 'TIME_SERIES_INTRADAY'
	_symbol = 'MSFT'
	_interval = '5min'
	_keywords = 'microsoft'
	# override if present
	if 'function' in request.args:
		_function = request.args['function']
	if 'symbol' in request.args:
		_symbol = request.args['symbol']
	if 'interval' in request.args:
		_interval = request.args['interval']
	if 'keywords' in request.args:
		_keywords = request.args['keywords']
	# set query based on function TYPE
	if _function == 'TIME_SERIES_INTRADAY':
		_query = '&function={function}&symbol={symbol}&interval={interval}'.format(function = _function, symbol = _symbol, interval = _interval)
	elif _function == 'TIME_SERIES_DAILY' or _function == 'TIME_SERIES_DAILY_ADJUSTED' or _function == 'GLOBAL_QUOTE':
		_query = '&function={function}&symbol={symbol}'.format(function = _function, symbol = _symbol)
	elif _function == 'SYMBOL_SEARCH':
		_query = '&function={function}&keywords={keywords}'.format(function = _function, keywords = _keywords)
	# http request to api
	response = requests.get(url_template.format(endpoint = _endpoint, apikey = _apikey, query = _query))
	# if request successful
	if response.ok:
		# return success response
		return jsonify({'success':str(response.content)}), 200
	# return failure response
	return jsonify({'error':str(response.status_code)})

# foreign exchange (fx) [exchange_rates, intraday]
@app.route('/foreign_exhange',methods=['GET'])
# resource requires authentication
@auth.login_required
def foreign_exchange():
	# set to defaults
	_function = 'CURRENCY_EXCHANGE_RATE'
	_from_currency = 'USD'
	_to_currency = 'BTC'
	# override if present
	if 'function' in request.args:
		_function = request.args['function']
	if 'from_currency' in request.args:
		_from_currency = request.args['from_currency']
	if 'to_currency' in request.args:
		_to_currency = request.args['to_currency']
	# set query based on function TYPE
	if _function == 'CURRENCY_EXCHANGE_RATE':
		_query = '&function={function}&from_currency={from_currency}&to_currency={to_currency}'.format(function = _function, from_currency = _from_currency, to_currency = _to_currency)
	elif _function == 'FX_INTRADAY':
		_query = '&function={function}&from_symbol={from_symbol}&to_symbol={to_symbol}'.format(function = _function, from_symbol = _from_symbol, to_symbol = _to_symbol)
	# http request to api
	response = requests.get(url_template.format(endpoint = _endpoint, apikey = _apikey, query = _query))
	# if request successful
	if response.ok:
		# return success response
		return jsonify({'success':str(response.content)}), 200
	# return failure response
	return jsonify({'error':str(response.status_code)})

# cryptocurrencies [exhange_rates, daily]
@app.route('/cryptocurrencies',methods=['GET'])
# resource requires authentication
@auth.login_required
def cryptocurrencies():
	# set to defaults
	_function = 'TIME_SERIES_INTRADAY'
	_symbol = 'MSFT'
	_interval = '5min'
	_keywords = 'microsoft'
	# override if present
	if 'function' in request.args:
		_function = request.args['function']
	if 'symbol' in request.args:
		_symbol = request.args['symbol']
	if 'interval' in request.args:
		_interval = request.args['interval']
	if 'keywords' in request.args:
		_keywords = request.args['keywords']
	# set query based on function TYPE
	if _function == 'TIME_SERIES_INTRADAY':
		_query = '&function={function}&symbol={symbol}&interval={interval}'.format(function = _function, symbol = _symbol, interval = _interval)
	elif _function == 'TIME_SERIES_DAILY' or _function == 'TIME_SERIES_DAILY_ADJUSTED' or _function == 'GLOBAL_QUOTE':
		_query = '&function={function}&symbol={symbol}'.format(function = _function, symbol = _symbol)
	elif _function == 'SYMBOL_SEARCH':
		_query = '&function={function}&keywords={keywords}'.format(function = _function, keywords = _keywords)
	# http request to api
	response = requests.get(url_template.format(endpoint = _endpoint, apikey = _apikey, query = _query))
	# if request successful
	if response.ok:
		# return success response
		return jsonify({'success':str(response.content)}), 200
	# return failure response
	return jsonify({'error':str(response.status_code)})

#
# --- User Data Requests
#

# curl -i -X POST -H "Content-Type: application/json" -d '{"username":"maaz","password":"cloud"}' http://localhost:8080/users/new
# create new user
@app.route('/users/new',methods=['POST'])
def users_new():
	#
	username = request.json.get('username')
	password = request.json.get('password')
	# missing both arguments
	if username is None or password is None:
		#
		return jsonify({'error':'User already exists'}), 403
	#
	rows = session.execute("SELECT * FROM users WHERE username = '{}'".format(username))
	# existing user
	for user in rows:
		#
		return jsonify({'error':'User already exists'}), 403
	#
	rows = session.execute("INSERT INTO users (username, password_hash) VALUES ('{}','{}')".format(username, hash_password(password)))
	#
	rows = session.execute("SELECT * FROM users WHERE username = '{}'".format(username))
	#
	for user in rows:
		#
		user_id = user['id']
		#
		return jsonify({ 'username': username }), 201, {'Location': url_for('get_user', id = user_id, _external = True)}
	#
	return jsonify({'error':'Failed to create user'}), 404

# curl -u maaz:cloud -i -X PUT -H "Content-Type: application/json" -d '{"username":"alam","password":"computing"}' http://localhost:8080/users/update
# curl -u eyJhbGciOiJIUzI1NiIsImV4cCI6MTM4NTY2OTY1NSwiaWF0IjoxMzg1NjY5MDU1fQ.eyJpZCI6MX0.XbOEFJkhjHJ5uRINh2JA1BPzXjSohKYDRT472wGOvjc:unused -i -X POST -H "Content-Type: application/json" -d '{"username":"alam","password":"computing"}' http://localhost:8080/users/update
# update existing user information
@app.route('/users/update',methods=['PUT'])
# resource requires authentication
@auth.login_required
def users_update():
	# put request variables
	username = request.json.get('username')
	password = request.json.get('password')
	# missing both arguments
	if username is None and password is None:
		#
		return jsonify({'error':'Missing arguments, Username and/or Password'}), 400
	#
	if not username is None:
		#
		# session.execute("UPDATE users SET username = '{}' WHERE user_id = '{}'".format(g.user.user_id))
		session.execute("UPDATE users SET username = '{}' WHERE user_id = '{}'".format(g.user['user_id']))
		# return jsonify({'success':'Username updated'})
	#
	if not password is None:
		#
		# session.execute("UPDATE users SET password = '{}' WHERE user_id = '{}'".format(g.user.user_id))
		session.execute("UPDATE users SET password = '{}' WHERE user_id = '{}'".format(g.user['user_id']))
		# return jsonify({'success':'Password updated'})
	#
	return jsonify({'error':'Updated Username and/or Password'}), 200

# curl -u maaz:cloud -i -X DELETE -H "Content-Type: application/json" http://localhost:8080/users/delete
# remove existing user
@app.route('/users/delete',methods=['DELETE'])
# resource requires authentication
@auth.login_required
def delete_users():
	#
	# session.execute("DELETE FROM users WHERE user_id = '{}'".format(g.user.user_id))
	session.execute("DELETE FROM users WHERE user_id = '{}'".format(g.user['user_id']))
	# g.user = None
	#
	return jsonify({'success':'User deleted'}), 200

#
# --- Flask
#

#
if __name__ == '__main__':
	#
	app.run(host='0.0.0.0',port=8080)
