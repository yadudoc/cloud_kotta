// This code is borrowed from -> http://www.randomsnippets.com/2008/02/21/how-to-dynamically-add-form-elements-via-javascript/
// It has obviously been cleaned up for this application
var icounter = 1;
var ilimit = 10;
var ocounter = 1;
var olimit = 10;

function addInput(divName){
     if (icounter == ilimit)  {
          alert("You have reached the limit of adding " + icounter + " inputs");
     }
     else {
          var newdiv = document.createElement('div');
          newdiv.innerHTML = "Input " + " <br><input type='text' name='input_url" + icounter + "'>";
          document.getElementById(divName).appendChild(newdiv);
          icounter++;
     }
}


function addOutput(divName){
     if (ocounter == olimit)  {
          alert("You have reached the limit of adding " + ocounter + " outputs");
     }
     else {
          var newdiv = document.createElement('div');
          newdiv.innerHTML = "Output " + " <br><input type='text' name='output_file" + ocounter + "'>";
          document.getElementById(divName).appendChild(newdiv);
          ocounter++;
     }
}
