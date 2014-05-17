from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail, Message
import os
import time

app = Flask(__name__)

## Config ##
app.secret_key = '238h?8328gf@$@naweifj??.//'
app.config['ADMIN_PASSWORD'] = 'ilovesofar'
app.config['DOWNLOAD_PASSWORD'] = 'secretshow'
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
	endtime = db.Column(db.Integer)
	address = db.Column(db.String(120))

	def __init__(self, address=None):
		self.endtime = time.time() + app.config['MINUTES_ALIVE']*60
		self.address = address

db.create_all()

## Helper functions ##
# Get the endtime of the button
def getEndTime():
	queryResponse = Generated.query.first()

	# Check if button is still alive
	if queryResponse:
		timeDiff = queryResponse.endtime - time.time()
		if timeDiff >= 0: # Don't kill it
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

@app.route('/download')
def download():
	return render_template('download.html')

@app.route('/songs')
def songs():
	return send_from_directory(directory='static', filename='Sofar Songs.zip', as_attachment=True)

@app.route('/admin')
def admin():
	return render_template('admin.html', endTime = getEndTime())

@app.route('/admin-logout', methods=['GET'])
def admin_logout():
	session.pop('loggedIn', None)
	return redirect(url_for('admin'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

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
		msg.body = '''
					Thanks so much for coming to Sofar Chicago!  Please enjoy these songs, and if you like what you hear, go hear more!

					You can get your downloads at http://bit.ly/1iU372t.  The password (shh) is secretshow.

					Marrow
					http://marrowmakesmusic.com/
					https://www.facebook.com/marrowworld

					Living In Pretend
					http://www.livinginpretend.com/
					https://www.facebook.com/livinginpretend

					Future Monarchs
					http://futuremonarchsband.com/
					https://www.facebook.com/FutureMonarchs

					-- The Chicago Sofar Team
					www.sofarsounds.com
					Sofar Chicago Facebook <http://www.facebook.com/sofarsoundschicago>
					Sofar Chicago Twitter  <https://twitter.com/SofarChicago>
					Newsletter sign-up <https://bit.ly/Sofarsignup>
				   '''
		msg.html = '''
					<h2>Thank you so much for coming to Sofar Chicago!</h2><br>
					Please enjoy these songs, and if you like what you hear, go hear more!<br>
					You can get your downloads at <a href="http://bit.ly/1iU372t">http://bit.ly/1iU372t</a>.  The password (shh) is secretshow.<br>
					<br>
					<em>Marrow</em><br>
					<a href='http://marrowmakesmusic.com/'>http://marrowmakesmusic.com/</a><br>
					<a href='https://www.facebook.com/marrowworld'>https://www.facebook.com/marrowworld</a><br>
					<br>
					<em>Living In Pretend</em><br>
					<a href='http://www.livinginpretend.com/'>http://www.livinginpretend.com/</a><br>
					<a href='https://www.facebook.com/livinginpretend'>https://www.facebook.com/livinginpretend</a><br>
					<br>
					<em>Future Monarchs</em><br>
					<a href='http://futuremonarchsband.com/'>http://futuremonarchsband.com/</a><br>
					<a href='https://www.facebook.com/FutureMonarchs'>https://www.facebook.com/FutureMonarchs</a><br>
					<br>
					-- The Chicago Sofar Team<br>
					<a href='www.sofarsounds.com'>www.sofarsounds.com</a><br>
					Sofar Chicago Facebook <<a href='http://www.facebook.com/sofarsoundschicago'>http://www.facebook.com/sofarsoundschicago></a><br>
					Sofar Chicago Twitter  <<a href='https://twitter.com/SofarChicago'>https://twitter.com/SofarChicago></a><br>
					Newsletter sign-up <<a href='https://bit.ly/Sofarsignup'>https://bit.ly/Sofarsignup></a>
				   '''		
		# Send
		mail.send(msg)

		# Return to front-end
		return jsonify({'message': 'You should receive an email with information on how to obtain your downloads soon.  Thanks so much for coming to Sofar Chicago.'})
	else:
		return jsonify({'message': 'Looks like the download link timed out.  Please ask a Sofar representative to restart the link.'})

# Download login
@app.route('/download-login', methods=['POST'])
def download_login():
	if request.form['password'] == app.config['DOWNLOAD_PASSWORD']:
		data = {
			'status': 'success',
			'message': 'Correct password'
		}		
	else:
		data = {
			'status': 'error',
			'message': 'Incorrect password'
		}
	return jsonify(data)

# Login the admin
@app.route('/admin-login', methods=['POST'])
def admin_login():
	if request.form['password'] == app.config['ADMIN_PASSWORD']:
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
		nowGenerate = Generated()
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