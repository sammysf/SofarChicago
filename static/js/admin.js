// Save expiration time and timer
var expireTime;
var timer;

// Decide what to show based on whether the user is logged in or not
function setupScreen(loggedIn, endTime) {
	if (loggedIn == 'True') {
		if (endTime != 'False') {
			$('#logged-in').css('display', 'none');
			setExpireTime(endTime);
		}
		else {
			$('#generate-live').css('display', 'none');
		}

		$('form').css('display', 'none');
	}
	else {
		$('#logged-in').css('display', 'none');
		$('#generate-live').css('display', 'none');
	}
}

$(document).ready(function() {

	// Do an ajax post when submitting the password so we can do a nice fadeout/fadein
	$('form').submit(function() {

		$.post('admin-login', {'password': $(this).find('input[name="password"]').val()}, function(data) {
			if (data.status == 'success') {
				$('#content form').fadeOut(function() {
					if (data.endTime) {
						setExpireTime(data.endTime);
						$('#generate-live').fadeIn();
					}
					else {
						$('#logged-in').fadeIn();	
					}					
				});
			}
			else {
				if ($('#error-message').length == 0){
					$('#content form').append('<br><br><p id=\'error-message\'>' + data.message + '</p>')
				}
			}		
	    }, 'json');


		return false;
	});

	// Tell server to generate download button when activate button is clicked
	$('#generate-button').click(function() {
		$.post('generate-button', {}, function(data) {
			$('#logged-in').fadeOut(function() {
				setExpireTime(data.endTime);
				$('#generate-live').fadeIn();
			});
	    }, 'json');
	});

	// Tell server to stop downloads when stop button is clicked
	$('#stop-button').click(function() {
		deactivateButton();
	});

});

// Remove the download button (send ajax call, fade in/out, clear timer)
function deactivateButton() {
	$.post('stop-button', {}, function(data) {
		$('#generate-live').fadeOut(function() {
			$('#logged-in').fadeIn();
		});

		// Clear the timer
		clearInterval(timer);
    }, 'json');
}

// Set the end time
function setExpireTime(endTime) {
	expireTime = endTime;
	updateTimer();

	// Update timer every second
	timer = setInterval(updateTimer, 1000);
}

// Update the timer
function updateTimer() {	
	var timeLeft = expireTime - (new Date()).getTime()/1000;  // In seconds

	// Deactivate button if time is up
	if (timeLeft < 0) {
		// Tell the server to close down the button
		deactivateButton();
	}
	else {
		// Calculate minutes and seconds
		var minutes = Math.floor(timeLeft/60);
		var seconds = Math.floor(timeLeft) - minutes*60;

		// Add zeroes if necessary
		if (seconds < 10) {
			seconds = '0' + seconds
		}
		if (minutes < 10) {
			minutes = '0' + minutes
		}

		$('#time-left').text(minutes + ':' + seconds);
	}
}