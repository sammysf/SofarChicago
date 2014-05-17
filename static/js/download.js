$(document).ready(function() {

	// Do an ajax post when submitting the password so we can do a nice fadeout/fadein
	$('form').submit(function() {

		$.post('download-login', {'password': $(this).find('input[name="password"]').val()}, function(data) {
			if (data.status == 'success') {
				$('#content form').fadeOut(function() {
					$('#download-button').fadeIn();
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