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


<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/1.0.2/Chart.min.js"></script> 
<script src="{{get_url('static', filename='js/d3.v3.min.js')}}"></script>

<div id="main">

	%if usage_csv != "None":
        <div style="width:100%">
	    <label>CPU Utilization</label>
            <div>
                <canvas id="canvas_cpu" height="250" width="1200"></canvas>
            </div>
        </div>

        <div style="width:100%">
	    <label>Memory Utilization</label>
            <div>
                <canvas id="canvas_mem" height="250" width="1200"></canvas>
            </div>
        </div>
	
        <script>
	 console.log("{{usage_csv}}")
	 d3.csv("{{usage_csv}}", function(data) {
	      data.forEach(function(d) {
	      d["time"] = d["time"];
	      d["cpu"] = +d["cpu"];
	      d["mem"] = +d["mem"];
	      });
	      
	      console.log(data[0]);
	      time_vals  = data.map(function(row) {return row["time"];});
	      cpu_vals   = data.map(function(row) {return row["cpu"];});
	      memmax_vals   = data.map(function(row) {return row["memmax"];});	
	      memcur_vals   = data.map(function(row) {return row["memcur"];});	
	      console.log(time_vals);
	      console.log(cpu_vals);
 	      console.log(memmax_vals); 
     	      var mem_data = {
  	  	    labels: time_vals,
		    datasets : [
          	    {
			label: "Total Available Memory",
            		fillColor: "rgba(220,220,220,0.2)",
            		strokeColor: "rgba(220,220,220,1)",
			pointColor: "rgba(220,220,220,1)",
			pointStrokeColor: "#fff",
			pointHighlightFill: "#fff",
			pointHighlightStroke: "rgba(220,220,220,1)",
			data: memmax_vals, 
		    },
		    {
			label: "Total Used Memory",
			fillColor: "rgba(151,187,205,0.2)",
			strokeColor: "rgba(151,187,205,1)",
			pointColor: "rgba(151,187,205,1)",
			pointStrokeColor: "#fff",
			pointHighlightFill: "#fff",
			pointHighlightStroke: "rgba(151,187,205,1)",
           		data: memcur_vals,
          	    }]
    		};

     	      var cpu_data = {
  	  	    labels: time_vals,
		    datasets : [
          	    {
			label: "Cpu utililization",
            		fillColor: "rgba(128,0,0,0.2)",
            		strokeColor: "rgba(128,0,0,1)",
			pointColor: "rgba(128,0,0,1)",
			pointStrokeColor: "#fff",
			pointHighlightFill: "#fff",
			pointHighlightStroke: "rgba(128,0,0,1)",
			data: cpu_vals, 
		    }]
    		};

	        var ctx_mem = document.getElementById("canvas_mem").getContext("2d");
		var myNewChart_mem = new Chart(ctx_mem).Line(mem_data, {responsive: true, y2axis: true});

		var ctx_cpu = document.getElementById("canvas_cpu").getContext("2d");
		var myNewChart_cpu = new Chart(ctx_cpu).Line(cpu_data, {responsive: true, y2axis: true});
	 });
    	</script>
	%end     
    <div class="row">
      <div class="form-group col-md-4">
       <a href="{{get_url('job_cancel')}}/{{job_id}}" class="btn btn-danger" role="button">Cancel Job</a>
      </div>
      <div class="form-group col-md-4">
       <a href="{{get_url('resubmit')}}/{{job_id}}" class="btn btn-warning" role="button">Redo Job</a>
      </div>
      <div class="form-group col-md-4">
       <a href="{{get_url('resubmit')}}/{{job_id}}" class="btn btn-success" role="button">Publish Outputs</a>
      </div>

    </div>
   
    <!--     <div class="table-responsive"> -->
     <div class="container">
     <table class="table table-hover">
     %for row in table:
     <tr>
    %for i,col in enumerate(row):
         %if col == "inputs" :
             <td>{{col}}</td>
         <td>{{!row[1]}}</a></td>
         %break
             %end

         %if col == "s3_key_log_file" :
             <td>{{col}}</td>
         <td>{{!row[1]}}</a></td>
             %break
         %end

         %if col == "outputs" :
             <td>{{col}}</td>
         <td>{{!row[1]}}</a></td>
             %break
         %end
         
         <td>{{col}}</td>
             
    %end
    </tr>   
      %end
      
      </table>
      </div>
</div>


</div>
%rebase('views/base', title='Turing-Job Info')