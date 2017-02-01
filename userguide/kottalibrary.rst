Kotta Library
=============

The Kotta library provides you a simple interface to manage your jobs on Kotta. The library allows you to submit regular script style jobs as well as pure functions in python to provide a cleaner ways to express workflows. Here we will first explore using the Kotta library to run pure python functions, and then cover a brief set of examples with submitting scripts using the script interface.


Python on Kotta
---------------

The Kotta library allows you to run pure python functions on Kotta. To authenticate with the Kotta a Kotta connection object is created which takes the json credentials string.

.. code-block:: python

     # Import the Kotta module
     from kotta import Kotta, KottaJob
     from kotta.kotta_functions import *

     # Create a Kotta Connection using Login with Amazon credentials
     # The token from Kotta is stored in the auth.file
     konn = Kotta(open('../auth.file').read())

The kotta library offers a convenient ``@kottajob`` decorator that packages a python function to run on Kotta's compute nodes. The ``@kottajob`` decorator takes three arguments:

1. The Kotta object created using the credentials.
2. The queue that should run the python function.

   * The 'Test' queue provides machines with 2vCPUs and 4GB or RAM.

   * The 'Prod' queue has machines with 32vCPUs+ and 256GB of RAM.
3. The walltime in minutes. This options is required to avoid infinite loops and stuck codes.

Let's see an example:

.. code-block:: python

     @kottajob(konn, 'Test', 5)
     def my_sum(items):
          return sum(items)

     result = my_sum (range(0,100))
     print(result)


By default ``@kottajob`` is set to blocking mode. This means that the python interpreter waits while the function is evaluated remotely and results are fetched.
The decorated function can be called in non-blocking mode, by calling ``@kottajob`` with the keyword argument ``block=False``. When called in non-blocking mode,
the function invocation returns a `future job object <https://en.wikipedia.org/wiki/Futures_and_promises>`_.

Here's an example:

.. code-block:: python

    @kottajob(konn, 'Test', 5, block=False)
    def my_sum(items):
        # Here, my_sum sleeps for 5 secs, and does not return immediately
        import time
        time.sleep(5)
        return sum(items)

    job_hndl = my_sum (range(0,100))
    print(job_hndl)

    # Prints:  <kotta.kotta_job.KottaJob object at 0x7fb78cc73b70>

    # Wait a few seconds and then
    status = job_hndl.status(konn)
    print("Status : ", status)
    # Prints:  Status :  completed

    result = job_hndl.get_results(konn)
    print("Result : ", result)
    # Prints:  Result :  4950

KOut class
----------

    Represents the outputs created via the execution of a task on Kotta.


kotta.KOut(filestring)
^^^^^^^^^^^^^^^^

   Args:
     * filestring(string) : A url string

   Returns:
     KOut object

kotta.KOut.url
^^^

   A Property

   Returns:
      The url string

kotta.KOut.s3_url
^^^^^^

   Property. The S3 url of an output object which has resolved, meaning the job has completed and the output is available.

   Returns:
      Returns the s3 url of an output object.

kotta.KOut.file
^^^^

   Property. The base filename of the resource.

   Returns:
       Returns the string filename of the object

kotta.KOut.get_data()
^^^^^^^^^^

   Args:
       None

   Returns:
       If this is a data object with a resolved `url` property, download the
       data to a file specified in the `file` property.

kotta.KOut.read()
^^^^^^

   Args:
       None

   Returns:
       String. Opens the remote URL, reads the data and returns the *utf-8* decoded string.


KottaJob class
--------------


A job object once submitted to Kotta, behaves as a future. Here's a list of methods exposed by the job object.


kotta.KottaJob(kwargs...)
^^^^^^^^

    Args:
        None

    Kwargs:
        * inputs (string) : Comma separated list of urls
        * outputs (string): Comma separated list of output files
        * walltime (int): Walltime in minutes (Default = 300)
        * queue  (string) : queue to submit the job to. Valid options are:
           * 'Test' : Test queue
           * 'Prod' : Production queue
        * output_file_stdout (string): Filename to capture STDOUT stream (Default = STDOUT.txt)
        * output_file_stderr (string): Filename to capture STDERR stream (Default = STDERR.txt)
        * jobtype (string): The type of job being submitted (Default = 'script')
        * jobname (string): A user friendly name for the job
        * script (string): String text of a script to be executed on the worker side.
        * script_name (string): Name to be assigned to the script text on the worker side.

   Returns:
        kotta.KottaJob object.



kotta.KottaJob.submit(Kotta_conn)
^^^^^^^^^^^^^^^^^^

Submits the job to Kotta. Once submitted the job object goes from status 'pending' to the terminal states.

Args:

* Kotta connection object.


Returns:

* True : Submit succeeded
* False : Submit failed

Eg.

>>> konn = Kotta(open('/path/to/auth.file').read())
>>> job  = KottaJob(<job description>)
>>> job.submit(konn)
True


kotta.KottaJob.wait(Kotta_conn, maxwait=600, sleep=2, silent=True)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This function waits for the job to complete by polling for status after every sleep duration for a maximum of maxwait duration.

Args:

* Kotta connection object

Kwargs:

* maxwait : Default=600s. Maximum time to wait for the task.
* sleep   : Default=2s. Poll interval.
* silent  : Default=True. Emit print messages about the wait status

Eg.


kotta.KottaJob.cancel(Kotta_conn)
^^^^^^^^^^^^^^^^^^

Not Implemented


kotta.KottaJob.status(Kotta_conn)
^^^^^^^^^^^^^^^^^^^^

Args:

* Kotta connection object.

Returns:

* 'unsubmitted' : Not submitted to Kotta
* 'pending' : Waiting in queue to be picked up for execution
* 'staging_inputs' : Staging input files to remote worker
* 'cancelled' : Task was cancelled by user
* 'completed' : Task completed without errors
* 'failed' : Task failed with an error
* 'processing': Task execution in progress
* 'staging_outputs' : Outputs from the task are being staged out to persistent storage(S3)

Eg.

>>> job_obj.status(konn)
completed

kotta.KottaJob.jobname
^^^^^^^

Property.

Returns:
* String, name of the job.

Eg.

>>> job_obj.jobname
Python test job

kotta.KottaJob.outputs
^^^^^^^

Property.

Returns:
* A list of Kotta output objects.

kotta.KottaJob.desc
^^^^

Property.








Running Script using Kotta Library
----------------------------------

Here is a simple Hello World example written in bash

.. code-block:: python

      hello = KottaJob( jobtype       = 'script',
                        jobname       = 'hello',
                        executable    = '/bin/bash myscript.sh',
                        script_name   = 'myscript.sh',
                        script        = '#!/bin/bash \n echo "Hello World!"'
                      )


