Overview
========

Cloud Kotta is a integrated solution for delivering web scale compute on data is a secure fashion.
The infrastructure components that provide compute-nodes, storage-disks, databases etc are provided by Amazon Web Services,
whereas a software and security layer built over these services create a simple, scalable computing solution.
Cloud Kotta is this meta description of infrastructure that can be used to create an on-demand virtual datacenter on AWS.

A particular instance of Cloud Kotta is hosted by the `KnowledgeLab <http://www.knowledgelab.org/>`_ at the `Computation Institute <https://www.ci.uchicago.edu/>`_.
This instance is available currently at `<https://turingcompute.net>`_.

Cloud Kotta primarily is a job execution system with interfaces that are reminescent of traditional cluster management systems such as Slurm, Condor etc.
The user is able to submit, monitor and terminate jobs. An instance of Cloud Kotta in addition to these offer long term storage of all results and complete
provenance of jobs executed.

There are three interfaces through which a user interacts with the system:

1. The Web UI (in our case, available over https://turingcompute.net)
2. A Commandline interface
3. A REST interface


