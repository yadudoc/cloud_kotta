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

<script>
var copyTextareaBtn = document.querySelector('.js-textareacopybtn');

copyTextareaBtn.addEventListener('click', function(event) {
  var copyTextarea = document.querySelector('.js-copytextarea');
  copyTextarea.select();

  try {
    var successful = document.execCommand('copy');
    var msg = successful ? 'successful' : 'unsuccessful';
    console.log('Copying text command was ' + msg);
  } catch (err) {
    console.log('Oops, unable to copy');
  }
});
</script>

<div id="main">

     <div class="table-responsive">
     <table class="table table-hover">
     <p>
       <textarea class="js-copytextarea">Hello I'm some text</textarea>
     </p>

     <p>
       <button class="js-textareacopybtn">Copy Textarea</button>
       </p>
     </table>
     </div>
</div>
</div>
%rebase('views/base', title='Turing-Credentials')
