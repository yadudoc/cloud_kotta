<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>

<div class="row">
     <div class="row">
          <div class="form-group col-md-4">
	  Rejecting login as {{username}}
          </div>
     </div>

     <div class="row">
          <div class="form-group col-md-10">
	  
	  Your Amazon user id has not been registed with this service. </br>
	  Please contact the admin at (yadu@uchicago.edu) with the following info. <br></br>
	  User_ID : {{user_id}}  </br></br>
	  Name    : {{username}} </br></br>
	  Email   : {{email}}    </br></br>

          </div>
     </div>

</div>

</div>

%rebase('views/base', title='Turing - Login')