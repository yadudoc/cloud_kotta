<div class="container">
<div class="page-header">
  <h2>Submit Task</h2>
</div>


<p>Please provide the information below to submit a generic script for execution</p>
<div class="form-wrapper">
  <form role="form" action="{{get_url('submit_task')}}" method="post" name="submit_task">

    <input type="hidden" name="jobtype" id="jobtype" value="{{jobtype}}" /><br/>
    
    <input type="hidden" name="username" value="{{session["user_id"]}}"/>

    <input type="hidden" name="email" value="{{session["email"]}}"/>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="jobname">Job Name</label>
	%if prefill and 'jobname' in prefill:
	        <input class="form-control input-lg input_url required" type="text" id="executable" name="jobname" value="{{prefill['jobname']}}" />
	%else:
	        <input class="form-control input-lg input_url required" type="text" id="executable" name="jobname" placeholder="A friendly name" />
	%end
      </div>
    </div>


    <div class="row">
      <div class="form-group col-md-4">
        <label for="executable">Command</label>
	%if prefill :
	        <input class="form-control input-lg input_url required" type="text" id="executable" name="executable" value="{{prefill['executable']}}" />
	%else:
	        <input class="form-control input-lg input_url required" type="text" id="executable" name="executable" value="/bin/bash myscript.sh" />
	%end
      </div>
    </div>

    <div class="row">
       <div class="form-group col-md-8">
          <label for="script">Script (Script will run as root)</label>
	%if prefill :
          <textarea class="form-control input_lg" rows="5" name="script" id="script" >{{prefill['i_script']}}</textarea>
	%else:
          <textarea class="form-control input_lg" rows="5" name="script" id="script" >
#!/bin/bash
echo "Hello World"
</textarea>

	%end
       </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="script_name">Filename for script</label>
	%if prefill :
		<input class="form-control input-lg input_url required" type="text" name="script_name" id="args" value="{{prefill['i_script_name']}}"/>
	%else:
		<input class="form-control input-lg input_url required" type="text" name="script_name" id="args" value='myscript.sh'/>
	%end
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-10">
        <label for="inputs">Inputs</label>
	%if prefill :
		<input class="form-control input-lg input_url" type="text" name="inputs" value="{{prefill['inputs']}}"/>
	%else:
	        <input class="form-control input-lg input_url" type="text" name="inputs" placeholder="Comma separated list of input URLs"/>
	%end
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-10">
        <label for="outputs">Outputs</label>
	%if prefill :
	        <input class="form-control input-lg input_url" type="text" name="outputs" value="{{prefill['outputs']}}"/>
	%else:
	        <input class="form-control input-lg input_url" type="text" name="outputs" placeholder="Comma separated list of output files"/>	
	%end
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <input class="form-control input-lg uneditable-input" type="text" name="output_file_stdout" id="output_file" value="STDOUT.txt"/>
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <input class="form-control input-lg input_url " type="text" name="output_file_stderr" id="output_file" value="STDERR.txt"/>
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="walltime">Walltime in minutes</label>
	%if prefill :
	        <input class="form-control input-lg required" type="text" name="walltime" id="walltime" value="{{prefill['walltime']/60}}"/>
	%else:
	        <input class="form-control input-lg required" type="text" name="walltime" id="walltime" value="5"/>
	%end

      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-4">
        <label for="queue">Deployment Type</label>
	%if prefill :
	    %if prefill["queue"] == "Test" :
 	    <select class="form-control input-lg required" id="queue" name="queue" default="{{prefill['queue']}}">
    	       <option value="Test">Testing/Dev</option>
	       <option value="Prod">Production</option>
            </select>
	    %elif prefill["queue"] == "Prod" :
 	    <select class="form-control input-lg required" id="queue" name="queue" default="{{prefill['queue']}}">
	       <option value="Prod">Production</option>
    	       <option value="Test">Testing/Dev</option>
            </select>
	    %else:
 	    <select class="form-control input-lg required" id="queue" name="queue" default="{{prefill['queue']}}">
    	       <option value="Test">Testing/Dev</option>
	       <option value="Prod">Production</option>
            </select>
	    %end
	%else:
	    <select class="form-control input-lg required" id="queue" name="queue" default="Test">
    	       <option value="Test">Testing/Dev</option>
	       <option value="Prod">Production</option>
            </select>
	%end


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
