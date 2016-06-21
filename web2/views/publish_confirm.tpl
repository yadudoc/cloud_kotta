<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>

<div id="main">
<div class="row">
     
     Your job has been published </br>
     Check here :<a href="{{get_url('jobs')}}/{{job_id}}">{{job_id}}</a>.</br>
</div>
</div>

</div>

%rebase('views/base', title='Turing-Publish Confirm')