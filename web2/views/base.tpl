<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
	  "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title or 'GAS'}}</title>
    <link rel="shortcut icon" type="image/x-icon" href="{{get_url('static', filename='img/favicon.ico')}}" />
    <link rel="icon" type="image/x-icon" href="{{get_url('static', filename='img/favicon.ico')}}" />

    <!-- CSS files -->
    <link rel="stylesheet" type="text/css" href="{{get_url('static', filename='css/bootstrap.min.css')}}" />
    <link rel="stylesheet" type="text/css" href="{{get_url('static', filename='css/style.css')}}" />

    <!-- JavaScript files -->
    <script type="text/javascript" src="{{get_url('static', filename='js/jquery.min.js')}}"></script>
    <script type="text/javascript" src="{{get_url('static', filename='js/jquery-ui.min.js')}}"></script>
    <script type="text/javascript" src="{{get_url('static', filename='js/bootstrap.min.js')}}"></script>
  </head>

  <body>
    <div id="wrap">
      <!-- Basic navigation menu; collapses for responsiveness to small screens -->
      <div class="navbar navbar-fixed-top" role="navigation">
	<div class="container">
	  <div class="navbar-header">
	    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
	      <span class="icon-bar"></span>
	      <span class="icon-bar"></span>
	      <span class="icon-bar"></span>
	    </button>
	    <a class="navbar-brand" href="/">Job Execution Service</a>
	  </div>
	  <div class="collapse navbar-collapse">
	    <ul class="nav navbar-nav navbar-right">
	      <li><a href="{{get_url('submit')}}">Submit Job</a></li>
	      <li><a href="{{get_url('tasks')}}">Previous Jobs</a></li>
	      <!-- <li class="dropdown">
	      </li> -->
	      %end
	    </ul>
	  </div> <!--/.nav-collapse -->
	</div> <!--/.container -->
      </div> <!--/.navbar -->

      <div id="main">
	<!-- Page body -->
	{{!base}}
      </div>

    </div> <!--/.wrap -->
    <!-- Page footer -->
    %include('views/footer.tpl')

  </body>
</html>
