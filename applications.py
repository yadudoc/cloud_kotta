#!/usr/bin/env python
import sys
sys.path.append("../ncses/doc2vec/")

import pipeline2 as d2v

def bash_executor(jobtype, job_id, inputs, outputs):
    return "Done"


# Job Definitions
JOBS = { "doc2vec" : d2v.pipeline,
         "bash"    : bash_executor }

def test():
    uid="fasdsadsa"

    i = [{"src": "https://s3.amazonaws.com/klab-jobs/inputs/test.txt", "dest": "test.txt" }]
    o = [{"src": "doc_mat.pkl",  "dest": "klab-jobs/{0}/".format(uid)},
         {"src": "word_mat.pkl", "dest": "klab-jobs/{0}/".format(uid)},
         {"src": "mdl.pkl",      "dest": "klab-jobs/{0}/".format(uid)}]

    JOBS["doc2vec"](i, o)


#test()
