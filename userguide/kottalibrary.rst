Kotta Library
=============

The Kotta library provides you a simple interface to manage your jobs on Kotta. The library allows you to submit regular script style jobs as well as pure functions in python to provide a cleaner ways to express workflows. Here we will first explore using the Kotta library to run pure python functions, and then cover a brief set of examples with submitting scripts using the raw interface.


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

The kotta library offers a convenient **@kottajob** decorator that packages a python function to run on Kotta's compute nodes. The **@kottajob** decorator takes three arguments:

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


