<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>

<style>
      table, th, td {
      border: 2px solid grey;
      border-collapse: collapse;
      }
      th, td {
      padding: 15px;
      }
      canvas {
         margin: 35px;
	 padding: 0;
      }
</style>


<div id="main">
<div class="form-wrapper">
  <form role="form" action="{{get_url('publish_job_handle')}}" method="post" name="publish_job">

    <input type="hidden" name="jobid" value="{{jobid}}"/>

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
       <div class="form-group col-md-8">
          <label for="jobdesc">Job Description</label>
	%if prefill and 'i_script' in prefill:
          <textarea class="form-control input_lg" rows="5" name="jobdesc" id="jobdesc" >{{prefill['i_script']}}</textarea>
	%else:
          <textarea class="form-control input_lg" rows="5" name="jobdesc" id="script" >
Job Behavior: What does this job do? What are it's Compute requirements ?
Inputs: Describe the inputs and expected format.
Outputs: Describe the outputs and their formats.
</textarea>

	%end
       </div>
    </div>

    <div class="form-actions">
      <input class="btn btn-lg btn-primary" type="submit" value="Publish" />
    </div>

</div>
</div>

</div>
%rebase('views/base', title='Turing-Publish Job')