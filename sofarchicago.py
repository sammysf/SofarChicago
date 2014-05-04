from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail, Message
import os
import datetime

app = Flask(__name__)

## Config ##
app.secret_key = '238h?8328gf@$@naweifj??.//'
app.config['PASSWORD'] = 'ilovesofar'
app.config['MINUTES_ALIVE'] = 30
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['SQLALCHEMY_POOL_RECYCLE'] = 30

# Email
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'samtoizer'
app.config['MAIL_PASSWORD'] = 'isitred!'

mail = Mail(app)
db = SQLAlchemy(app)

## Models ##
class Email(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, default=db.func.now())
	email = db.Column(db.String(120))

	def __init__(self, email):
		self.email = email

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('layout.html'), 404

# AJAX calls
@app.route('/submit', methods=['POST'])
def submit():

	# If link is still live, send an email
	if getEndTime():

		# Save their address
		newEmail = Email(request.form['email'])
		db.session.add(newEmail)
		db.session.commit()

		# Setup
		subject = 'Your Sofar Downloads'
		sender = ('Sofar Sounds', app.config['MAIL_USERNAME'] + '@gmail.com')
		recipients = [request.form['email']]
		# Email
		msg = Message(subject, sender = sender, recipients = recipients)
		msg.body = 'Thanks so much for coming to Sofar Sounds!  Please enjoy these songs, and if you like what you hear, be sure to visit their website!'
		msg.html = '<br><h1>Thank you so much for coming to Sofar Sounds!</h1><br><br>Please enjoy these songs, and if you like what you hear, be sure to visit their website!'
		# Attachment
		with app.open_resource('Sofar Songs.zip') as fp:
		    msg.attach('Sofar Songs.zip', 'application/zip', fp.read())
		# Send
		mail.send(msg)

		# Return to front-end
		return jsonify({'message': 'You should receive an email shortly.  Thanks so much for coming to Sofar Chicago.'})
	else:
		return jsonify({'message': 'Looks like the download link timed out.  Please ask a Sofar representative to restart the link.'})

# Login the admin
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

# Generate a download button
@app.route('/generate-button', methods=['POST'])
def generateButton():
	queryResponse = Generated.query.first()
	if not queryResponse:
		nowGenerate = Generated('secret')
		db.session.add(nowGenerate)
		db.session.commit()
		endTime = nowGenerate.endtime
	else:
		endTime = queryResponse.endtime
	return jsonify({'status': 'success', 'endTime': endTime})

# Stop the download button
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