Publishing Jobs
===============

The publish feature makes it easy to share code and results.
Published jobs are visible to all authenticated users.

How to Publish a job
--------------------

Select a particular job that you would like to publish. On the page you should be seeing
3 buttons that say **Cancel Job**, **Redo Job**, **Publish Job**.

.. image:: ../figures/publish.png

Clicking the **Publish Job** takes you to the Publish page. Here you are required to fill out
a meaningful name for the job and a short job description. At the minimum your job description must cover the following:

1. What does the job do ?
2. Is it CPU/RAM/IO intensive
3. If the application is not multi-threaded/multi-processing note that.
4. If your code accesses protected datasets, note that as a requirement.
5. Describe each input file and expected format.
6. Describe each output file and expected format.

Guidelines for Publishing
-------------------------

1. Do **NOT** publish any results that are **derived from a private dataset** (e.g. Web of Science, JSTOR) without prior approval from the :ref:`ref_admins`.
2. Do **NOT** publish results or data that are going into a manuscript prior to publication.
3. Add a complete and meaningful job description. When in doubt ask another human


Guidelines for Publishing
-------------------------

1. Do **NOT** publish any results that are **derived from a private dataset** (e.g. Web of Science, JSTOR) without prior approval from the :ref:`ref_admins`.
2. Do **NOT** publish results or data that are going into a manuscript prior to publication.
3. Add a complete and meaningful job description. When in doubt ask another human

Retracting a Published job
--------------------------

The owner/maintainer of a Published Job can retract a job from the Published jobs page by clicking the **Retract** button on the job info page.
Please note that the **Retract** button merely takes the job off the Published jobs page.
There are no group based controls on who can view your jobs, as a result if a job is published the unique job-id is known to the world and can
be used to view the job even after it has been retracted. Therefore users are adviced to make sure that critical/sensitive results are not
present in the jobs they publish.

.. note::
   The job-id based access is purely security by obscurity. While the input datasets are protected by role based models, the outputs attached to jobs are treated as objects that require much less protection.
 
