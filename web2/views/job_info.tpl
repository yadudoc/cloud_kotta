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

<script src="{{get_url('static', filename='js/Chart.min.js')}}"></script>

<div id="main">


     <div style="width:100%">
            <div>
                <canvas id="canvas" height="450" width="1200"></canvas>
            </div>
        </div>


        <script>
          var randomScalingFactor = function(){ return Math.round(Math.random()*100)};
          var lineChartData = {
            labels : {{tdata}},
            datasets : [
                {
                    label: "CPU",
                    fillColor : "rgba(220,220,220,0.2)",
                    strokeColor : "rgba(220,220,220,1)",
                    pointColor : "rgba(220,220,220,1)",
                    pointStrokeColor : "#fff",
                    pointHighlightFill : "#fff",
                    pointHighlightStroke : "rgba(220,220,220,1)",
                    data : {{mmax}}
                },
                {
                    label: "Memory"
                    fillColor : "rgba(151,187,205,0.2)",
                    strokeColor : "rgba(151,187,205,1)",
                    pointColor : "rgba(151,187,205,1)",
                    pointStrokeColor : "#fff",
                    pointHighlightFill : "#fff",
                    pointHighlightStroke : "rgba(151,187,205,1)",
                    data : {{mcur}}
                }
            ]

        }

    window.onload = function(){
        var ctx = document.getElementById("canvas").getContext("2d");
        window.myLine = new Chart(ctx).Line(lineChartData, {
            responsive: true
        });
    }


    </script>
     
    <div class="row">
      <div class="form-group col-md-4">
       <a href="{{get_url('job_cancel')}}/{{job_id}}" class="btn btn-danger" role="button">Cancel Job</a>
      </div>
      <div class="form-group col-md-4">
       <a href="{{get_url('resubmit')}}/{{job_id}}" class="btn btn-warning" role="button">Redo Job</a>
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