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
      </br>
      </br>
      %for row in table:
          <tr>
        %for i, col in enumerate(row):

	    <td>{{!col}}</td>
        %end	
           </tr>
          %end
     </table>
     </div>
</div>
</div>

%rebase('views/base', title='Turing-Browse')
