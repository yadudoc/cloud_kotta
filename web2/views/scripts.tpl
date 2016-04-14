<!-- Load JavaScript form validation library -->
<!--
<script type="text/javascript" src="{{get_url('static', filename='js/parsley.min.js')}}"></script>
-->

<!-- Enable some JS effects -->

<script type="text/javascript">
// Modal and alert box handling
$(document).ready(function(){
	// Add the alert div
	$("#alert-div").html('<div id="alert-fading-message" class="alert alert-info alert-block"><button type="button" class="close" data-dismiss="alert">&times;</button><h4 class="alert-headline"></h4><span class="alert-message"></span></div>');
	// Hide the alert div
	$("div#alert-fading-message").hide();
});

// Animates in-line alerts to make them fade away after a short delay (default 5 sec.)
function fadeAlertDiv(timeoutDelay, redirectUrl) {
	timeoutDelay = typeof timeoutDelay !== 'undefined' ? timeoutDelay : 5000;
	redirectUrl = typeof redirectUrl !== 'undefined' ? redirectUrl : window.location.href;
	window.setTimeout(function() {
		$('#alert-fading-message').animate({
			opacity: 0.25,
			height: 'toggle'
		}, {duration: 2000});
		window.location.href = redirectUrl;
	}, timeoutDelay);
}
</script>

</script>