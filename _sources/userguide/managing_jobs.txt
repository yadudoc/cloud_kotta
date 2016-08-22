Managing Jobs
=============

Cloud Kotta makes it easy to keep track of your jobs by maintaining complete history of your jobs.
The `Previous Jobs <https://turingcompute.net/jobs>`_ tab allows you to view this history. The following
sections cover the different modes of interaction possible.



Job Status
==========

Jobs have the following states: 

* **Pending** : Jobs are in pending state when they are waiting in queue for execution. While wait times are generally under 5 minutes,
  depending on the configuration of the pool you are submitting to, wait times can vary.
* **Staging In** : The job has been launched on a compute node, and the input files are being fetched from remote storage to the local disks.
* **Processing** : The job is being executed on the compute node.
* **Staging Out** : The job has completed execution and the output files are being transferred from local disk to remote storage.
* **Failed** : The job has completed execution with failures.
* **Completed** : The job has completed execution without failures.


Job History
===========



