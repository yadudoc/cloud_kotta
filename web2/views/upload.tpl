<div class="container">
<div class="page-header">
  <h2>{{title}}</h2>
</div>

<p>You file will be uploaded and stored encrypted in your folder.</p>
<div class="form-wrapper">

    <form action="http://klab-webofscience.s3.amazonaws.com/" method="post" enctype="multipart/form-data">
        <input type="hidden" name="key" value="uploads/{{session["user_id"]}}/${filename}" />
	<input type="hidden" name="acl" value="private"/>
        <input type="hidden" name="success_action_redirect" value="{{redirect_url}}">
        <input type="hidden" name="X-Amz-Credential" value="{{aws_key_id}}/20151212/us-east-1/s3/aws4_request" />
        <input type="hidden" name="X-Amz-Algorithm" value="AWS4-HMAC-SHA256" />
        <input type="hidden" name="X-Amz-Server-Side-Encryption" value="AES256" />
        <!-- User: <input type="text" name="x-amz-meta-username"/><br /> -->

	<input type="hidden" type="text" name="x-amz-meta-username" value="{{session["user_id"]}}" placeholder="Enter a username" />

        <input type="hidden" name="x-amz-meta-filename" value="${filename}" />
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

        <!-- <input type="submit" name="submit" value="Upload to Amazon S3" /> -->
	<div class="form-actions">
	  <input class="btn btn-lg btn-primary" type="submit" value="Upload" />
	</div>

    </form>

</div>

%end

</div>
%rebase('views/base', title='Turing - Upload')

