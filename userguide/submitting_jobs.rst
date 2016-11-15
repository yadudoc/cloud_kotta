Submitting Jobs
===============

We refer to a complete description of the inputs, executable, outputs and the parameters within which execution must happen as a **job**.
A script job is the most common type of job, which takes arbitrary code along with inputs and constraints. It is also possible to create
templated jobs from common jobs with a fixed pattern of inputs, executables and outputs.



Defining a Script Job
---------------------

Here's a snapshot of the Script job submission page:

.. image:: ../figures/script_job.png

A script job is the simplest, yet most flexible job type that Cloud Kotta offers.
Here are the different parameters that it provides.

Job Name
^^^^^^^^

This is simply a friendly name that could be used to identify the job. The submission system automatically issues
a unique job id to every job, that is used internally, however is not human friendly.

.. _ref_command:

Command
^^^^^^^

This is the command that is issued on a remote machine to start the execution. 
When this command is executed here are some things to keep in mind:
* The executable is invoked on a Ubuntu 14.04 machine (Linux).
* The command is being executed in a remote system with superuser privileges
  
  * This implies that you are allowed to install packages

* Always assume that your job is going to execute on a fresh machine. Do not assume to have applications installed by a previous job to be available.
* Avoid installing or leaving data in folders outside the current working directory (CWD) (This is important for the cleanup step).
* You can assume that the input files you specify in `Inputs` will be in your current working directory provided you have privileges to access them and that they exist.


.. _ref_script:

Script
^^^^^^

This is the crux of the Job. Here's where you generally write quick scripts, or in case of large pipelines, write a wrapper
for the code that you will call. Any arbitrary code could be specified here, and we have had cases with python, bash, julia,
perl, and wrappers that in turn compiled and ran c/c++ codes.

.. note::
   Go to the #cloudkotta channel for specific examples.

.. note::
   Git is installed on the compute nodes. It is common to clone code public repositories for large applications, which allows easy
   maintenance of large code bases separate from the job execution system.


jFilename for script
^^^^^^^^^^^^^^^^^^^

This is the filename underwhich the body of the script defined in the previous :ref:`ref_script` section is written
to within the current working directory on the compute node. This is useful to manage extensions of say, python .py file vs a shell script with .sh extension.
In addition naming the script file makes it easy to be invoked by the :ref:`ref_command`.


.. _ref_inputs:

Inputs
^^^^^^

This field accepts a comma separated list of URLs of the following types:

* HTTP urls for resources hosted anywhere
* S3 urls which start with s3:// prefix to resources on internal buckets.
* HTTPs urls to S3 resources of the form :
  https://s3.<region>.amazonaws.com/<bucket>/<path_to_object>

In order to access objects in S3 storage, the user must have sufficient access privileges.
If you the requisite permissions and the remote resources are reachable they will be downloaded
to the current working directory on a compute node. This is the same directory within which the
`Command` will be executed.

.. note::
   If a resource in the comma separated list could not be reached, the system will **not** emit
   an error. You have to explicitly check for missing files.

.. note::
   If you require access to Protected data-sets please contact the system administrators.

.. note::
   It is common to get large packages (eg tarballs of virtual-env for python) to the CWD via `Inputs`


Outputs
^^^^^^^

This field accepts a comma separated list of files that you wish to be retrieved from the compute node
at the end of the Job. The files that are retrieved are hosted on S3, and are server-side encrypted.
The jobs pages will provide signed URLs that are valid for 1 hour that allows you to either view, download,
or share (for a limited time as the URL expires) the output files.

The filename could also be files listed below directories in the current working directory of the Job.


STDOUT.txt and STDERR.txt
^^^^^^^^^^^^^^^^^^^^^^^^^

These are default outputs that are created for logging the output streams from the Job. The STDOUT stream is logged to STDOUT.txt and similarly STDERR to STDERR.txt.
These defaults are in place to aid debugging. 

Walltime in minutes
^^^^^^^^^^^^^^^^^^^

This is a required field, that allows the user to set an upperbound on the amount of time that the Job is allowed to run.
If the job exceeds the walltime, it is terminated and the Job will show an ERROR_CODE:1001.
In the event of an early termination of a instance, the job is automatically resubmitted for re-execution and the job is
again allotted the same walltime.



.. _ref_deployment_type:

Deployment Type
^^^^^^^^^^^^^^^

This is a required field that requires the user to choose from a dropdown of Deployment types.
Cloud Kotta currently supports two deployment types:

Testing/Dev
"""""""""""

This deployment type is suited for short (under .5 hour) tasks that require limted CPU and memory resources.
The Testing pool is a scalable pool of upto 10 `t2.small <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/t2-instances.html>`_ instances.
The max wait time when the pool is not at full load is under 4 minutes.

Production
""""""""""

This deployment type is suited for long running tasks that have large CPU and/or memory requirements.
The production pool supports upto 100 instances of generally `r3.8xlarge <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/t2-instances.html>`_ instances which 
come with 32 virtual CPUs and 244GB of RAM. These machines also have 2x320 GB of SSD storage on node.

.. note::
   Ask on the #cloudkotta channel if you are unsure about the deployment type, or if you have a specific instance type requirement.

.. note::
   Please post a note on the #cloudkotta channel before launching production jobs that take up more than 10 production instances for more than 2 hours.



Defining a Doc2Vec Job
----------------------

Doc2Vec is a packaged application, based on `Doc2Vec <https://radimrehurek.com/gensim/models/doc2vec.html>`_ from the python GenSim package.
Here's a snapshot of the Doc_to_Vec job submission page:

.. image:: ../figures/doc_to_vec.png




Document file URL
^^^^^^^^^^^^^^^^^

This is a required field. It takes a csv file with the format :

.. code-block:: xml

	<Doc_id_1>,<document text> 
	..
	<Doc_id_N>,<document text> 


Model file URL
^^^^^^^^^^^^^^

This is an optional field. This is only used when a large Doc2Vec task is run in a distributed manner.
In order to run Doc2Vec in distributed mode, initially a model is created by taking a single pass across
the corpus to generate word and document matrices that are in the pickled model file. Following this, we
run multiple independent jobs on slices of the corpus where word vectors are projected into this same high-dimensional space.

.. note::
   Contact @bartleyn for info on this.


Parameters file URL
^^^^^^

Optional field. This is a URL to a json document that defines the parameters to pass to the Doc2vec run.

.. code-block:: json

   { "epochs"    : 15, 
     "min_count" : 1,
     "window"    : 5, 
     "seed"      : 0,
     "size": 100
   }



Walltime in minutes
^^^^^^^^^^^^^^^^^^^

This is a required field, that allows the user to set an upperbound on the amount of time that the Job is allowed to run.
If the job exceeds the walltime, it is terminated and the Job will show an ERROR_CODE:1001.
In the event of an early termination of a instance, the job is automatically resubmitted for re-execution and the job is
again allotted the same walltime.


Deployment Type
^^^^^^^^^^^^^^^

Please refer to :ref:`ref_deployment_type`
