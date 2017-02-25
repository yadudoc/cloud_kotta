Wikipedia
=========

We have on our local S3 store the entire Wikipedia edit history from July 2016. This dataset consists of a set of 197 compressed 7z files which total ~112GB.
With the massive compression ratios on pure text files, each of these files expand to several tens of GBs. Estimated size of the uncompressed dataset is around
20TB.


Storage bucket
--------------

This data is currently on bucket : s3://klabwiki


Permissions
-----------

klab-public: Accessible to any user on `TuringCompute <www.turingcompute.net>`_.


Processed intermediates
-----------------------

Work done in 2015 involved splitting the 7z files from the 2015 edit history dump to smaller files making computation more efficient.
There was two different splits made which are currently stored at s3://klabwiki/splits and the second which split the 7z files honoring
page boundaries within the XML are in s3://klabwiki/splits_by_page.


Example
-------

Here's a job that demonstrates accessing a compressed 7z file for processing:
`Job <https://turingcompute.net/jobs/9decd236-9594-442d-ad19-106a62903d33>`_
