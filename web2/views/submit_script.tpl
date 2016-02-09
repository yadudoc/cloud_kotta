<div class="container">
<div class="page-header">
  <h2>Submit Task</h2>
</div>


<p>Please provide the information below to submit a Document2Vector task.</p>
<div class="form-wrapper">
  <form role="form" action="{{get_url('submit_task')}}" method="post" name="submit_task">

    <input type="hidden" name="jobtype" id="jobtype" value="{{jobtype}}" /><br/>
    
    <input type="hidden" name="username" value="{{session["user_id"]}}"/>

    <input type="hidden" name="email" value="{{session["email"]}}"/>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="executable">Command</label>
        <input class="form-control input-lg input_url required" type="text" id="executable" name="executable" value="/bin/bash myscript.sh" />
      </div>
    </div>

    <div class="row">
       <div class="form-group col-md-8">
          <label for="script">Script (Script will run as root)</label>
          <textarea class="form-control input_lg" rows="5" name="script" id="script" >
#!/bin/bash
echo "Hello World"
</textarea>
       </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="script_name">Filename for script</label>
        <input class="form-control input-lg input_url required" type="text" name="script_name" id="args" value='myscript.sh'/>
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-10">
        <label for="inputs">Inputs</label>
        <input class="form-control input-lg input_url" type="text" name="inputs" placeholder="https://goo.gl/Acuznd, https://s3.amazonaws.com/klab-data/uploads/bill/heateqn1d_FTCS.m"/>
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-10">
        <label for="outputs">Outputs</label>
        <input class="form-control input-lg input_url" type="text" name="outputs" placeholder="myresult.dat, myapp.log"/>
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <input class="form-control input-lg input_url " type="text" name="output_file_stdout" id="output_file" value="STDOUT.txt" />
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <input class="form-control input-lg input_url " type="text" name="output_file_stderr" id="output_file" value="STDERR.txt" placeholder="STDERR.txt" />
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="walltime">Walltime in minutes</label>
        <input class="form-control input-lg required" type="text" name="walltime" id="walltime" value="5"/>
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="queue">Deployment Type</label>
	    <select class="form-control input-lg required" id="queue" name="queue" default="Test">
    	       <option value="Test">Testing/Dev</option>
	       <option value="Prod">Production</option>
            </select>
      </div>
    </div>

    <div class="form-actions">
      <input class="btn btn-lg btn-primary" type="submit" value="submit" />
    </div>
  </form>
</div>


%end

</div>
%rebase('views/base', title='Turing-Submit')
