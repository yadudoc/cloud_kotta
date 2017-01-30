Kotta Notebooks
===============

One of the simplest ways to work with Kotta is from the jupyter notebook. Jupyter notebooks allow you to do interactive data science and scientific computing from the browser. To read more about jupyter notebooks `go here <https://jupyter.readthedocs.io/en/latest/index.html>`_ . Once logged in, jupyter provides a simple development environment that is persistent which means that your notebooks are always available to you even after your browser session is closed.

The Kotta extensions to Jupyterhub enable computation to be offloaded to Kotta's elastic compute pools.
The just in time offloading of compute tasks, allow kotta to offer virtually infinite CPU/Mem/Disk resources at minimal cost.

Access
------

The Jupyter notebooks are available at `<https://books.cloudkotta.org>`_.
Please contact the :ref:`ref_admins` for username, password pair for login to the Jupyter notebooks.

Please refer to the extensive documentation `here <https://jupyter.readthedocs.io/en/latest/index.html>`_ to learn more about using Jupyter notebooks most effectively.

.. note::
   The login system for Kotta notebooks are not yet integrated with the rest of Kotta. This means that for the time being, there is a separate username/password pair used to login to the notebook environment.

To get the Oath2 refresh tokens that are required to authenticate with Kotta follow these steps:

1. First login at the `turingcompute webpage <https://turingcompute.net/login>`_

2. Click the Credentials tab under your name

   .. image:: ../figures/kotta_creds.png
              :width: 800pt

3. Login once again with Amazon, and you will be forwarded to a page which contains a refresh token in json format. Copy the json string in the box to a txt file.

   .. image:: ../figures/creds.png
              :width: 800pt


4. Upload the file to your home folder on Bastion either via ssh, or via the Jupyter notebook upload feature.

   .. image:: ../figures/jupyter_upload.png
              :width: 800pt



Environment
-----------

The notebooks are currently hosted on bastion (`a t2.large AWS machine <https://aws.amazon.com/blogs/aws/new-t2-large-instances/>`_). Each user is currently throttled to 2vCPUs and 2GB of RAM. The notebooks support Python3 as a backend kernel.

.. note::
   For specific use cases that require other kernels (eg R, python2) please contact the :ref:`ref_admins`

