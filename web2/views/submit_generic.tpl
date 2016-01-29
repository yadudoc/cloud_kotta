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
        <label for="executable">Executable</label>
        <input class="form-control input-lg input_url required" type="text" name="executable" id="executable" placeholder="/bin/sleep" />
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="arguments">Arguments</label>
        <input class="form-control input-lg input_url required" type="text" name="args" id="args" placeholder="60" />
      </div>
    </div>

    <script src="/static/js/add_input.js" language="Javascript" type="text/javascript"></script>

    <div id="dynamicInput">
    <div class="row">
      <div class="form-group col-md-4">
        <label for="input_url">Input</label>
        <input class="form-control input-lg input_url required" type="URL" name="input_url" id="input_url" placeholder="http://" />
      </div>
    </div>
    </div>
     <input type="button" value="Add another input URL" onClick="addInput('dynamicInput');">
     </br></br>


    <div class="row">
      <div class="form-group col-md-4">
        <input class="form-control input-lg input_url " type="text" name="stdout_file" id="output_file" value="STDOUT.txt" />
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <input class="form-control input-lg input_url " type="text" name="stderr_file" id="output_file" value="STDERR.txt" placeholder="STDERR.txt" />
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="walltime">Walltime in minutes</label>
        <input class="form-control input-lg required" type="text" name="walltime" id="walltime" placeholder="5" default="5"/>
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

    <div class="row">
      <div class="form-group col-md-4">
        <label for="queue">Deployment Type</label>
	    <select class="form-control input-lg required" id="queue" name="queue" default="Test">
    	       <option value="Test">Testing/Dev</option>
	       <option value="Prod">Production</option>
            </select>
      </div>
    </div>

    <!-- 
    <div id="dynamicOutput">
    <div class="row">
      <div class="form-group col-md-4">
        <label for="output_url">Output file</label>
        <input class="form-control input-lg input_url required" type="URL" name="output_url" id="output_file" placeholder="foo.txt" />
      </div>
    </div>
    </div>
     <input type="button" value="Add another output file" onClick="addInput('dynamicOutput');">
     </br></br>
     -->
    <div class="form-actions">
      <input class="btn btn-lg btn-primary" type="submit" value="submit" />
    </div>
  </form>
</div>

%end

</div>
%rebase('views/base', title='Turing-Submit')
