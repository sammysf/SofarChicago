$('#download-button').click(function() {
	$(this).fadeOut(function() {
		$('#content form').fadeIn();
	});
});

// Remember the interval
var animInterval;

$('form').submit(function() {
	
	$('#content form').fadeOut(function() {
		$('#wait').fadeIn();
		animInterval = setInterval(animateProgress, 125);
	});

	$.post("submit", {'email': $(this).find('input[name="email"]').val()}, function(data) {
		// Stop current progress animation and animate it to 100%
		clearInterval(animInterval);
		$('.progress-bar').stop().width('100%');

		// Fade out wait, fade in response
		$('#response').append(data.message);			
		$('#wait').delay(2000).fadeOut(function() {
			$('#response').fadeIn();
		});
    }, 'json')
    .fail(function(data) {
    	$('#response').append('Looks like the request timed out.  Please try refreshing the page and starting over.');
    	clearInterval(animInterval);
    	$('#wait').fadeOut(function() {
			$('#response').fadeIn();
		});
    });

	return false;
});

function animateProgress() {
	var currWidth = $('.progress-bar').width() / $('.progress').width() * 100; // Get width as percentage
	currWidth += 1/8;
	$('.progress-bar').width(currWidth + '%').attr('aria-valuenow', currWidth);
	if (currWidth > 100) {
		clearInterval(animInterval);
	}
}