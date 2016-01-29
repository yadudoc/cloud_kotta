<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
	  "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title or 'Turing'}}</title>
    <link rel="shortcut icon" type="image/x-icon" href="{{get_url('static', filename='/favicon.ico')}}" />
    <link rel="icon" type="image/x-icon" href="{{get_url('static', filename='/favicon.ico')}}" />

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
	    <img src="/static/Knowledge-Lab-icon-final.png" height= "50" width="50" style="float:left;"/>
	    <a class="navbar-brand" style="float:right" href="/">Turing</a>
	  </div>
	  
	  <div class="collapse navbar-collapse">
	    <ul class="nav navbar-nav navbar-right">
	      %if session is None or session.get("logged_in") is not True :
	      <li><a href="{{get_url('login')}}">Login</a></li>

	      %else :
	      <li class="dropdown">
                <a href="#" class="dropdown-toggle" data-toggle="dropdown">Data<b class="caret"></b></a>
                <ul class="dropdown-menu">
                  <li><a href="{{get_url('submit')}}/doc_to_vec">Browse</a></li>
                  <li><a href="{{get_url('upload')}}">Upload</a></li>
                </ul>
              </li>

	      <li class="dropdown">
                <a href="#" class="dropdown-toggle" data-toggle="dropdown">Submit Job<b class="caret"></b></a>
                <ul class="dropdown-menu">
                  <li><a href="{{get_url('submit')}}/doc_to_vec">Doc To Vector</a></li>
                  <li><a href="{{get_url('submit')}}/generic">Generic Executable</a></li>
		  <li><a href="{{get_url('submit')}}/script">Script</a></li>
		  <li><a href="{{get_url('submit')}}/experimental">Experimental</a></li>
                </ul>
              </li>
	      <li><a href="{{get_url('jobs')}}">Previous Jobs</a></li>
	      <li class="dropdown">
		<a href="#" class="dropdown-toggle" data-toggle="dropdown">{{session["username"]}}<b class="caret"></b></a>
		<ul class="dropdown-menu">
		  <li><a href="{{get_url('logout')}}">Logout</a></li>
		</ul>
	      </li>
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
