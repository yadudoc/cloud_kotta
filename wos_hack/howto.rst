WoS Hackathon
=============


Please follow steps here : `http://docs.cloudkotta.org/userguide/kotta_access.html`_ to get an account.

Datasets
--------

There are two forms, the XML data and data ingested into a MySQL database.


.. note::
   Please note that the columns in the README.txt do not match the dataset and this is reflected in the MYSQL database schema

XML
^^^

The xml data is available at this url within Kotta : 

.. code-block:: json
   s3://klab-jobs/wos_hack/iu.tar

To get a better start here's a job that completed the run on Kotta on this dataset.
`https://turingcompute.net/jobs/f24e22ac-2d59-4073-828e-1e67c8f598cb`_

If you click the Redo Job button you are taken to this page `https://turingcompute.net/resubmit/f24e22ac-2d59-4073-828e-1e67c8f598cb`_ .
This shows the description of the sample job. This job runs the following script on a machine with the Kotta enclace :

.. code-block:: bash

                #!/bin/bash
                apt-get install -y gzip gunzip
                tar -xf iu.tar
                for gz in $(echo DELIMITED/*gz)
                do
                     gunzip $gz
                     head -n 10 ${gz%.gz}
                done
                ls -thor -R

Note how the dataset `s3://klab-jobs/wos_hack/iu.tar`_ is specified in the inputs field. This ensures that when the script is executed
in Kotta the input files are fetched from S3 onto the current working directory hosted on local disk. I've set the walltime to 10 minutes
since this job is very short and should be done in under a few minutes. 


The data is 732.5 MB

SQL
^^^

The XML data is highly relational, and is suited to a RDBMS environment. The xml has been ingested to a MySQL database (InnoDB engine). Please use the schema below to interact with this database, from within Kotta.

.. code-block:: json

                USE wos_hack;

                -- Publication (Publications_Delimited.txt.gz) :
                -- UID|Title|Volume|Page|DOI|CoverDate|ISSN|EISSN|PMID|Issue|DOCTYPES (SEPARATED by ,'s)

                DROP TABLE IF EXISTS publications;
                CREATE TABLE IF NOT EXISTS publications (
                uid       char(20) PRIMARY KEY,
                title     varchar(200),
                volume    varchar(5),
                page      varchar(15),
                doi       varchar(20),
                coverdate varchar(20),
                issn      varchar(20),
                eissn     varchar(20),
                pmid      varchar(20),
                issue     varchar(5),
                doctypes  varchar(100) );


                -- Authors (Author_Delimited.gz):
                -- AUTHOR_ID|Name|FullName|FirstName|LastName|EMAIL|RID|ORCID

                DROP TABLE IF EXISTS authors;
                CREATE TABLE IF NOT EXISTS authors (
                author_id  char(20) PRIMARY KEY,
                name       varchar(100),
                fullname   varchar(100),
                firstname  varchar(50),
                lastname   varchar(50),
                email      varchar(50),
                rid        varchar(20),
                orcid      varchar(20));


                -- PublicationAuthor Link (Publication_Author_Link.gz):
                -- UID|AUTHOR_ID|POSITION
                DROP TABLE IF EXISTS publication_author_link;
                CREATE TABLE IF NOT EXISTS publication_author_link (
                uid        varchar(20),
                author_id  varchar(20),
                position   varchar(3),
                primary key (uid, author_id)
                );

                -- Authors (Author_Delimited.gz):
                -- AUTHOR_ID|Name|FullName|FirstName|LastName|EMAIL|RID|ORCID

                DROP TABLE IF EXISTS authors;
                CREATE TABLE IF NOT EXISTS authors (
                author_id  char(20) PRIMARY KEY,
                name       varchar(100),
                fullname   varchar(100),
                firstname  varchar(50),
                lastname   varchar(50),
                email      varchar(50),
                rid        varchar(20),
                orcid      varchar(20));


                -- PublicationAuthor Link (Publication_Author_Link.gz):
                -- UID|AUTHOR_ID|POSITION
                DROP TABLE IF EXISTS publication_author_link;
                CREATE TABLE IF NOT EXISTS publication_author_link (
                uid        varchar(20),
                author_id  varchar(20),
                position   varchar(3),
                primary key (uid, author_id)
                );

                -- Address (Address_Delimited.gz):
                -- ADDRESS_ID|Organizarion|subOrg|Lab|Street|City|State|Country|ZipCode|fulladdress
                DROP TABLE IF EXISTS address;
                CREATE TABLE IF NOT EXISTS address (
                address_id   varchar(40) primary key,
                organization varchar(100),
                suborganization varchar(100),
                lab     varchar(100),
                street varchar(50),
                city varchar(50),
                state varchar(50),
                country varchar(50),
                zipcode varchar(10),
                fulladdress varchar(200),
                stdaddress varchar(100)
                );

                -- PublicationAddress Link (Publication_Address_Link.gz):
                -- UID|ADDRESS_ID|POSITION
                DROP TABLE IF EXISTS publication_address_link;
                CREATE TABLE IF NOT EXISTS publication_address_link (
                uid  varchar(20),
                address_id varchar(40),
                position   varchar(5)
                );

                -- Citations (Citation_Delimited.gz):
                -- CitingUID|CitedAuthor|Year|Page|CitedTitle|CitedJournal

                DROP TABLE IF EXISTS citations;
                CREATE TABLE IF NOT EXISTS citations (
                citing_uid  varchar(20),
                cited_author varchar(50),
                year      varchar(5),
                page      varchar(4),
                cited_title varchar(100),
                cited_journal varchar(100)
                );


