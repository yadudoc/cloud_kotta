<div class="container">
<div class="page-header">
  <h2>Submit Task</h2>
</div>

<p>Please provide the information below to submit a Document2Vector task.</p>
<div class="form-wrapper">
  <form role="form" action="{{get_url('submit_task')}}" method="post" name="submit_task">

    <input type="hidden" name="jobtype" id="jobtype" value="{{jobtype}}" /><br/>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="name">Username</label>
        <input class="form-control input-lg required" type="text" name="username" id="username"
               value="{{username}}" placeholder="Enter a username" />
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-5">
        <label for="name">E-mail Address</label>
        <input class="form-control input-lg required" type="text" name="email" id="email"
               value="{{email}}" placeholder="Enter your e-mail address" />
      </div>
    </div>

    <!--
    <div class="dropdown">
      <button class="btn btn-default dropdown-toggle" type="button" id="dropdownMenu1" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
        Dropdown
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
        <li><a href="#">Action</a></li>
        <li><a href="#">Another action</a></li>
        <li><a href="#">Something else here</a></li>
        <li><a href="#">Separated link</a></li>
      </ul>
    </div>
    -->

    <div class="row">
      <div class="form-group col-md-4">
        <label for="input_url">Input URL</label>
        <input class="form-control input-lg input_url required" type="URL" name="input_url" id="input_url" placeholder="http://" />
      </div>
    </div>


    <div class="form-actions">
      <input class="btn btn-lg btn-primary" type="submit" value="submit" />
    </div>
  </form>
</div>

%end

</div>
%rebase('views/base', title='JES - Submit')
