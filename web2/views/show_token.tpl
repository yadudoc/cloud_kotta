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

<script src="https://cdn.jsdelivr.net/clipboard.js/1.5.16/clipboard.min.js"></script>

<div id="main">
     
     <div class="table-responsive">
     <table class="table table-hover">
     
     <div style="width:100%">
	    <label>Credentials as JSON</label>
	    </br>
            <div>

	    <pre><code id="creds">{{credentials}}</code></pre>

	    <!--
	    <button class="btn" data-clipboard-action="cut" data-clipboard-target="code#creds">
		    Cut to clipboard
	    </button> 
	    -->
            </div>
     </div>

     
     </table>
     </div>
</div>
</div>
%rebase('views/base', title='Turing-Credentials')
