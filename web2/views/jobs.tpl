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
     <!-- 
     <div class="table-responsive">     
     <table class="table">
     -->
     <div class="table-responsive">
     <table class="table table-hover">
     <thead>
	<tr>
		<th>Job Name/ID</th>
        	<th>Status</th>
        	<th>Job Type</th>
        	<th>Submit time</th>
      	</tr>
      </thead>
      </br>
      %for row in table:
          <tr>
        %for i,col in enumerate(row):
            <td>{{!col}}</td>
	     <!--
            %if i == 0 :
	    <td><a href="{{get_url('jobs')}}/{{col}}">{{col}}</a></td>
            %else :
            <td>{{col}}</td>
            %end
	    -->
        %end	
              </tr>
          %end
     </table>
     </div>
</div>
</div>
%rebase('views/base', title='Turing-Jobs')
