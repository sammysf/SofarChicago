$('#download-button').click(function() {
	$(this).fadeOut(function() {
		$('#content form').fadeIn();
	});
});

$('form').submit(function() {
	
	$('#content form').fadeOut(function() {
		$('#wait').fadeIn().delay(1000).fadeOut(function() {
			$('#success').fadeIn();
		});			
	});

	$.post("submit", {'email': $(this).find('input[name="email"]').val()}, function(data) {
		$('#success').append(data.message);
		console.log(data);
    }, 'json');


	return false;
});