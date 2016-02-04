<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>

<div class="row">
     <hr />
     Your job has been submitted with Job_id: <a href="{{get_url('jobs')}}/{{job_id}}">{{job_id}}</a>.</br>
     Check here :<a href="{{get_url('jobs')}}">Jobs!</a>
</div>

</div>

%rebase('views/base', title='Turing-Confirm')