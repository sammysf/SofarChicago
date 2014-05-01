from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import os
import datetime

app = Flask(__name__)

## Config ##
app.secret_key = '238h?8328gf@$@naweifj??.//'
app.config['PASSWORD'] = 'ilovesofar'
app.config['MINUTES_ALIVE'] = 2
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['SQLALCHEMY_POOL_RECYCLE'] = 30

## Models ##
db = SQLAlchemy(app)

class Email(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, default=db.func.now())
	email = db.Column(db.String(120))

class Generated(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	isGenerated = db.Column(db.Boolean, default=True)
	endtime = db.Column(db.DateTime)
	address = db.Column(db.String(120))

	def __init__(self, address=None):
		self.endtime = datetime.datetime.now() + datetime.timedelta(minutes = app.config['MINUTES_ALIVE'])
		self.address = address

db.create_all()

## Helper functions ##
# Get the endtime of the button
def getEndTime():
	queryResponse = Generated.query.first()

	# Check if button is still alive
	if queryResponse:
		timeDiff = datetime.datetime.now() - queryResponse.endtime
		if timeDiff.days < 0: # Should we kill it?
			return queryResponse.endtime
		else:
			db.session.delete(queryResponse)
			db.session.commit()
	return False

## Routes ##
# Pages
@app.route('/')
def index():
	return render_template('index.html', endTime = getEndTime())

@app.route('/admin')
def admin():
	return render_template('admin.html', endTime = getEndTime())

@app.route('/admin-logout', methods=['GET'])
def admin_logout():
	session.pop('loggedIn', None)
	return redirect(url_for('admin'))

# AJAX calls
@app.route('/submit', methods=['POST'])
def submit():
	return jsonify({'message': 'You should receive an email shortly.  Thanks so much for coming to Sofar Chicago.'})

@app.route('/admin-login', methods=['POST'])
def admin_login():
	if request.form['password'] == app.config['PASSWORD']:
		data = {
			'status': 'success',
			'message': 'Correct password',
			'endTime': getEndTime()
		}		
		session['loggedIn'] = True
	else:
		data = {
			'status': 'error',
			'message': 'Incorrect password'
		}
	return jsonify(data)

@app.route('/generate-button', methods=['POST'])
def generateButton():
	queryResponse = Generated.query.first()
	if not queryResponse:
		nowGenerate = Generated()
		db.session.add(nowGenerate)
		db.session.commit()
	return jsonify({'status': 'success', 'endTime': nowGenerate.endtime})

@app.route('/stop-button', methods=['POST'])
def stopButton():
	queryResponse = Generated.query.first()
	if queryResponse:
		db.session.delete(queryResponse)
		db.session.commit()
	return jsonify({'status': 'success'})

## Main ##
if __name__ == '__main__':	
	app.run(host='0.0.0.0')