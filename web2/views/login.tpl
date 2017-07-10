<div class="container">
<div class="page-header">
  <h2>Login with Amazon</h2>
</div>

<body>
<div id="amazon-root"></div>
<script type="text/javascript">

  window.onAmazonLoginReady = function() {
    amazon.Login.setClientId('{{aws_client_id}}');
  };
  (function(d) {
    var a = d.createElement('script'); a.type = 'text/javascript';
    a.async = true; a.id = 'amazon-login-sdk';
    a.src = 'https://api-cdn.amazon.com/sdk/login1.js';
    d.getElementById('amazon-root').appendChild(a);
  })(document);

</script>

<p>Use a pre-approved account for Federated Access</p>
<div class="form-wrapper">

	<div class="row">
	  <div class="form-group col-md-4">
	  	  <a href="#" id="LoginWithAmazon">
	  	    <img border="0" alt="Login with Amazon"
	            src="https://images-na.ssl-images-amazon.com/images/G/01/lwa/btnLWA_gold_156x32.png"
		    width="156" height="32" />
		  </a>
	  </div>
	</div>
	  <script type="text/javascript">

	  document.getElementById('LoginWithAmazon').onclick = function() {
	      options = { scope : 'profile' };
	          amazon.Login.authorize(options, '{{handle_login}}');
		      return false;
          };

	  </script>

    </form>

</div>
</body>
%end

</div>
%rebase('views/base', title='Turing - Login')

