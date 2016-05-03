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
</style>

<div id="main">

     <div class="row">
      <div class="form-group col-md-4">
        <label for="progress-prod">Production</label>
      </div>
     </div>

     <div class="row">
     <div class="progress">
       <div class="progress-bar progress-bar-success progress-bar-striped " style="width: {{autoscale['prod'][0]}}%">
              {{autoscale['prod'][0]}}%
       </div>
       <div class="progress-bar progress-bar-warning progress-bar-striped active" style="width: {{autoscale['prod'][1]}}%">
              {{autoscale['prod'][1]}}%
       </div>
       
       <div class="progress-bar progress-bar-danger progress-bar-striped active" style="width: {{autoscale['prod'][2]}}%">
              {{autoscale['prod'][2]}}%
       </div>
     </div>
     </div>


     <div class="row">
      <div class="form-group col-md-4">
        <label for="progress-test">Test/Development</label>
      </div>
     </div>

     <div class="row">
     <div class="progress">
       <div class="progress-bar progress-bar-success progress-bar-striped " style="width: {{autoscale['test'][0]}}%">
              {{autoscale['test'][0]}}%
       </div>
       <div class="progress-bar progress-bar-warning progress-bar-striped active" style="width: {{autoscale['test'][1]}}%">
              {{autoscale['test'][1]}}%
       </div>
       
       <div class="progress-bar progress-bar-danger progress-bar-striped active" style="width: {{autoscale['test'][2]}}%">
              {{autoscale['test'][2]}}%
       </div>
     </div>

     </div>

     <div class="table-responsive">
     <table class="table table-curved">
     <thead>
	<tr>
		<th>User</th>
		<th>Job ID</th>
        	<th>Status</th>
        	<th>Job Type</th>
        	<th>Submit time</th>
		<th>Queue</th>
      	</tr>
      </thead>
      </br>
      %for row in table:
          <tr>
        %for i,col in enumerate(row):
            %if i == 1 :
	    <td><a href="{{get_url('jobs')}}/{{col}}">{{col}}</a></td>
            %else :
            <td>{{col}}</td>
            %end
        %end	
              </tr>
          %end
     </table>
     </div>
</div>
</div>
%rebase('views/base', title='Turing-Jobs')
