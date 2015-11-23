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

<!-- Stripe code -->
<!-- This includes the main Stripe bindings -->
<script type="text/javascript" src="https://js.stripe.com/v2/"></script>

<script type="text/javascript">
// This identifies our web app in the createToken call below
Stripe.setPublishableKey('pk_test_W4wupSwRVgv7AkSrhT8KmOFG');

// This function adds the Stripe token to the form as a hidden field so we
// can access it in our server code. If there's an error in the payment
// details it displays the errors in the "payment-errors" class
var stripeResponseHandler = function(status, response) {
  var $form = $('#subscribe_form');
  if (response.error) {
    // Show the errors on the form
    $form.find('.payment-errors').text(response.error.message);
    $form.find('#bill-me').prop('disabled', false);
    $form.find('.payment-errors').html('<div class="alert alert-error alert-block"><button type="button" class="close" data-dismiss="alert">&times;</button><h4>We could not complete your request.</h4>' + response.error.message + '</div>');
  } else {
    // Get the Stipe token
    var token = response.id;
    // Insert the token into the form so it gets submitted to the server
    $form.append($('<input type="hidden" name="stripe_token" />').val(token));
    // Re-submit the form to our server
    $form.get(0).submit();
  }
};

// This function intercepts the form submission, calls Stripe to get a
// token and then calls the stripeResponseHandler() function to complete
// the submission.
jQuery(function($) {
  $('#subscribe_form').submit(function(e) {
    var $form = $(this);
    // Disable the submit button to prevent repeated clicks
    $form.find('#bill-me').prop('disabled', true);
    Stripe.createToken($form, stripeResponseHandler);
    // Prevent the form from submitting with the default action
    return false;
  });
});
</script>