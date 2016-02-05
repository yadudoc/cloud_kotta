<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>

<div class="row">
     <div class="row">
          <div class="form-group col-md-4">
          Logged in as {{session["username"]}}
          </div>
     </div>

     <div class="row">
          <div class="form-group col-md-4">
	  Notifications will go to {{session["email"]}}
          </div>
     </div>

     <div class="row">
          <div class="form-group col-md-4">
	  Amazon user id : {{session["user_id"]}}
          </div>
     </div>

</div>

</div>

%rebase('views/base', title='Turing - Login')