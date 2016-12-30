<div class="container">
<div class="page-header">
     <h2>{{title}}</h2>
</div>

<div class="row">
     <hr />
     Your job has been retracted. </br>
     To go back to the jobs page click here :<a href="{{get_url('jobs')}}">Jobs</a>
</div>

</div>

%rebase('views/base', title='Turing-Retract Job')