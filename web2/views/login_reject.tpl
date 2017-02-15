<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>

<div class="row">
     <div class="row">
          <div class="form-group col-md-8"> Your Amazon user-id is registered with this service.</br>Please contact the admin at (yadu@uchicago.edu) with the following info for access.</div>
     </div>

     <div class="row">
          <div class="form-group col-md-8">User_ID : {{user_id}}</div>
     </div>

     <div class="row">
          <div class="form-group col-md-8">Name : {{username}}</div>
     </div>

     <div class="row">
          <div class="form-group col-md-8">Email : {{email}}</div>
     </div>

</div>

</div>

%rebase('views/base', title='Turing - Login Reject')