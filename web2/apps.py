#!/usr/bin/env python

def common (request):
    data = {}
    
    user_id   = request.POST.get('username').strip() # Username in the form is the user_id
    email     = request.POST.get('email').strip()
    input_url = request.POST.get('input_url')
    jobtype   = request.POST.get('jobtype').strip()
    executable= request.POST.get('executable')
    args      = request.POST.get('args', '')
    walltime  = request.POST.get('walltime')
    walltime  = int(walltime) * 60;
    queue     = request.POST.get('queue')
    username  = session["username"]
    role      = session["user_role"]
    outputs   = request.POST.get('outputs', None)
    uid       = str(uuid.uuid1())
    


    
def doc_to_vec (request):
    print common(request)
    return 
