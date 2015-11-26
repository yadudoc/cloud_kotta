<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>


<div id="main">
     <div class="table-responsive">
     <table class="table">
      </br>
      </br>
      %for row in table:
          <tr>
        %for i,col in enumerate(row):
            %if i == 0 :
	    <td><a href="{{get_url('tasks')}}/{{col}}">{{col}}</a></td>
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
%rebase('views/base', title='JES - Status')