<div class="container">
<div class="page-header">
  <h2>Submit Task</h2>
</div>

<p>Please provide the information below to submit a Document2Vector task.</p>
<div class="form-wrapper">

<!-- 
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  </head>
  <body>
    -->
    <form action="http://klab-webofscience.s3.amazonaws.com/" method="post" enctype="multipart/form-data">
        <input type="hidden" name="key" value="uploads/${username}/${filename}" /><br/>
        <input type="hidden" name="acl" value="private"/>
        <input type="hidden" name="success_action_redirect" value="{{redirect_url}}">
        <input type="hidden" name="X-Amz-Credential" value="{{aws_key_id}}/20151212/us-east-1/s3/aws4_request" />
        <input type="hidden" name="X-Amz-Algorithm" value="AWS4-HMAC-SHA256" />
        <input type="hidden" name="X-Amz-Server-Side-Encryption" value="AES256" />
        <!-- User: <input type="text" name="x-amz-meta-username"/><br /> -->
	<div class="row">
	  <div class="form-group col-md-4">
            <label for="name">Username</label>
	    <input class="form-control input-lg required" type="text" name="x-amz-meta-username" id="username" placeholder="Enter a username" />

	  </div>
	</div>

        <input type="hidden" name="x-amz-meta-filename" value="${filename}" /><br />
        <input type="hidden" name="AWSAccessKeyId" value="{{aws_key_id}}" />
        <input type="hidden" name="Policy" value="{{policy}}" />
        <input type="hidden" name="Signature" value="{{signature}}" />

        <!-- File: <input type="file" name="file" /> <br /> -->
	<div class="row">
	  <div class="form-group col-md-4">
            <label for="name">File</label>
	         <input class="form-control input-lg required" type="file" name="file" id="filename" />
	  </div>
	</div>

</br>
<div class="dropdown">
     <label for="dropdown">Access ACL</label></br>
  <button class="btn btn-default dropdown-toggle" type="button" id="dropdownMenu1" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
    Dropdown
    <span class="caret"></span>
  </button>
  <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
    <li><a href="#">Action</a></li>
    <li><a href="#">Another action</a></li>
    <li><a href="#">Something else here</a></li>
    <li role="separator" class="divider"></li>
    <li><a href="#">Separated link</a></li>
  </ul>
</div>

        <!-- <input type="submit" name="submit" value="Upload to Amazon S3" /> -->
	<div class="form-actions">
	  <input class="btn btn-lg btn-primary" type="submit" value="Upload" />
	</div>

    </form>

<!-- </html> -->
</div>

%end

</div>
%rebase('views/base', title='Turing - Upload')

