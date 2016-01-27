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
     <div class="table-responsive">
     <table class="table">
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