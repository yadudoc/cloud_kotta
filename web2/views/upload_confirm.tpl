<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>

<div class="row">
    <div class="row">
      <div class="form-group col-md-10">
      Your file has been uploaded.
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-10">
      Use this signed link to share : </br>
      <td>{{!signed_url}}</td>
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-10">
      Use this link to run compute jobs : </br>
      <td>{{!unsigned}}</td>
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-10">
          <a href="{{get_url('submit')}}" class="btn btn-info" role="button">Browse your uploads</a>      
      </div>
    </div>


</div>

</div>

%rebase('views/base', title='Turing - Confirm')