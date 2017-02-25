JSTOR ngrams
============

JSTOR ngrams are indexed and stored on our secure S3 Buckets. The documents are indexed by their document ids (doi's)
on a MySQL database as well as in a collection of CSV files.


Index
-----

The Jstor ngram data is stored in a collection of 500 files (each approximately 3.2GB). These files are named n000 - n499.
The indexes contain the filename and the byte indices of each doi. The schema followed by the database is also followed by
the csv file. Here are a few lines from the jstor database.

+----------------+----------+------+-----------+----------+---------+--------+
| doi            | filename | line | byteFirst | byteLast | nNgrams | nWords |
+================+==========+======+===========+==========+=========+========+
| 10.1086/231208 | n000     | 0    | 0         | 2038709  | 5       | 26172  |
+----------------+----------+------+-----------+----------+---------+--------+
| 10.1086/233855 | n000     | 1    | 2038710   | 3517884  | 5       | 19995  |
+----------------+----------+------+-----------+----------+---------+--------+
| 10.1086/314323 | n000     | 2    | 3517885   | 4371013  | 5       | 12690  |
+----------------+----------+------+-----------+----------+---------+--------+
| 10.1086/316637 | n000     | 3    | 4371014   | 4616514  | 5       | 7770   |
+----------------+----------+------+-----------+----------+---------+--------+

To connect to the MySQL database, please contact the :ref:`ref_admins` for access.
The database is accessible at `klab.c3se0dtaabmj.us-west-2.rds.amazonaws.com`_

If you plan to use the csv index files those are accessible from within Kotta by specifying the filenames as inputs to jobs.

.. note::
   The jstor index database is accessible from within Kotta as well.

Storage bucket
--------------


The data is currently stored on S3 Storage : s3://klabjstor.

The indices for the files in csv file formats are stored under the same bucket and the filenames are:
s3://klabjstor/i{000 - 499}.csv

Since the data is organized by the data file, it is rather difficult to search for a particular doi without reading all 500 csv files. For search functions, it would be more convenient to query to external database and create a list of data files required and read out specific data items.

The datafiles are here:
s3://klabjstor/n{000 - 499} are the files that contain the ngram data.

Permissions
-----------

This data is only accessible from within the network and by users with the requisite access privileges.


Sample Jobs
-----------

Pending.
