<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>

<div class="row">
     <div class="row">
          <div class="form-group col-md-4">
	  Temporary keys for {{username}}
          </div>
     </div>

     <div class="row">
          <div class="form-group col-md-10">
	  	  
          Here's your temporary credentials for accessing S3 buckets <br></br>
	  AccessKey    : {{AccessKeyId}}      </br></br>
	  SecretKey    : {{SecretAccessKey}}  </br></br>
	  Token        : {{Token}}            </br></br>
	  Expiration   : {{Expiration}}       </br></br>
          </div>
     </div>

</div>

</div>

%rebase('views/base', title='Turing - Keys')