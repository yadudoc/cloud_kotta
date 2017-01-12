Medline
======

Medline contains a variety of datasets relating to medical research, including papers from PubMed, which are indexed and stored on a MySQL database. PubMed papers are indexed by their paper ids (pmid's).

Connecting
__________

After receiving permission, enter the following line in terminal:

mysql -h klab.c3se0dtaabmj.us-west-2.rds.amazonaws.com -u username -p

with the correct username. The initial password will be the same as the username, which should be changed by entering:

set password=PASSWORD('xxxx');

at the mySQL prompt, with the x's representing the new password.

Index
_____

Different datasets are stored in 16 separate tables within the database.

+-----------------------------+
| Tables_in_medline           |
+=============================+
| abstract                    |
+-----------------------------+
| affiliation                 |
+-----------------------------+
| authorId                    |
+-----------------------------+
| authorInitialsId            |
+-----------------------------+
| authority09_articlesMedline |
+-----------------------------+
| authors                     |
+-----------------------------+
| cell_docs                   |
+-----------------------------+
| doc                         |
+-----------------------------+
| grants                      |
+-----------------------------+
| mesh                        |
+-----------------------------+
| nAuthorHistogram            |
+-----------------------------+
| patent_docs                 |
+-----------------------------+
| pmidAuthId                  |
+-----------------------------+
| pmidNumAuthors              |
+-----------------------------+
| pmid_ext_metadata           |
+-----------------------------+
| yearPmidNumAuthors          |
+-----------------------------+

Each of these tables relating to PubMed papers is linked by the paper's pmid number, with a secondary database id - these do not line up as PubMed starts the numbering in 1975 while the paper with id 1 in the database is from 1865. 

Here is a sample of the affiliation table:

+---------+-------+------------+-----------------+-----------------------------------------------------------------------------------------+
| id      | pmid  | authorRank | affiliationRank | affiliation                                                                             |
+=========+=======+============+=================+=========================================================================================+
| 4733359 | 12265 |          1 |               1 | Pharmaceutical Research Department, Allen and Hanburys Research Ltd., Ware, Herts, U.K. |
+---------+-------+------------+-----------------+-----------------------------------------------------------------------------------------+
| 5139674 | 26707 |          1 |               1 | Industrial Toxicology Research Centre, Lucknow, India.                                  |
+---------+-------+------------+-----------------+-----------------------------------------------------------------------------------------+
| 5331998 | 45516 |          1 |               1 | Department of Biochemistry, University of Mississippi Medical Center, Jackson 29216.    |
+---------+-------+------------+-----------------+-----------------------------------------------------------------------------------------+
| 4554496 | 45517 |          1 |               1 | Physiology Laboratory, College of Optometry, Ohio State University, Columbus 43210.     |
+---------+-------+------------+-----------------+-----------------------------------------------------------------------------------------+
| 4554497 | 45518 |          1 |               1 | Physiology Laboratory, College of Optometry, Ohio State University, Columbus 43210.     |
+---------+-------+------------+-----------------+-----------------------------------------------------------------------------------------+

id is the database id as explained above, and pmid is the PubMed id. authorRank is the order in which the author was listed for the paper, while affiliationRank is the order in which the affiliation is listed for the author (currently there are none above 1 for either rank in this table).

The breakdown of the other tables is as follows:

**abstract**

+----------+---------+------+-----+---------+-------+
| Field    | Type    | Null | Key | Default | Extra |
+==========+=========+======+=====+=========+=======+
| pmid     | int(11) | YES  | MUL | NULL    |       |
+----------+---------+------+-----+---------+-------+
| rank     | int(11) | YES  |     | NULL    |       |
+----------+---------+------+-----+---------+-------+
| abstract | text    | YES  |     | NULL    |       |
+----------+---------+------+-----+---------+-------+

pmid is the PubMed ID number for each paper, abstract is the text abstract from the paper. Some papers have multiple sections to their abstracts, and these are numbered in rank.

**authorId**

+--------+---------+------+-----+---------+----------------+
| Field  | Type    | Null | Key | Default | Extra          |
+========+=========+======+=====+=========+================+
| id     | int(11) | NO   | PRI | NULL    | auto_increment |
+--------+---------+------+-----+---------+----------------+
| author | text    | YES  | MUL | NULL    |                |
+--------+---------+------+-----+---------+----------------+

**authorInitialsId**

+--------+---------+------+-----+---------+----------------+
| Field  | Type    | Null | Key | Default | Extra          |
+========+=========+======+=====+=========+================+
| id     | int(11) | NO   | PRI | NULL    | auto_increment |
+--------+---------+------+-----+---------+----------------+
| author | text    | YES  | MUL | NULL    |                |
+--------+---------+------+-----+---------+----------------+

These two tables are structured identically, where all authors found in the database are ordered alphabetically by last name and are given an ID number accordingly. The authorId table lists authors full names, last first, while the authorInitialsId table lists only a first initial with the last name.
The two databases do not, however, align with their numbering, as the full name table does have some duplicates, as authors may appear in some papers with their name listed in initial form, and in another with their full name.

**authority09_articlesMedline**
+----------+-------------+------+-----+---------+-------+
| Field    | Type        | Null | Key | Default | Extra |
+==========+=============+======+=====+=========+=======+
| ID       | int(11)     | YES  |     | NULL    |       |
+----------+-------------+------+-----+---------+-------+
| pmid     | int(11)     | YES  |     | NULL    |       |
+----------+-------------+------+-----+---------+-------+
| aorder   | smallint(6) | YES  |     | NULL    |       |
+----------+-------------+------+-----+---------+-------+
| LastName | varchar(64) | YES  |     | NULL    |       |
+----------+-------------+------+-----+---------+-------+

In this table, ID is an id given to a given author, whose LastName is listed, and the pmid of all papers they are listed on, as well as the author order in which they are listed on that paper.

**authors**

+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+===========+=============+======+=====+=========+=======+
| id        | int(11)     | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
| pmid      | int(11)     | YES  | MUL | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
| rank      | int(2)      | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
| LastName  | varchar(64) | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
| FirstName | varchar(64) | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
| initials  | varchar(64) | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+

In this table, id is the database id number while pmid is the PubMed id. Rank is the author rank on the paper, and LastName, FirstName, and initials are those properties of each author's name.

**cell_docs**

+--------------------+-------------+------+-----+---------+----------------+
| Field              | Type        | Null | Key | Default | Extra          |
+====================+=============+======+=====+=========+================+
| instance_id        | int(11)     | NO   | PRI | NULL    | auto_increment |
+--------------------+-------------+------+-----+---------+----------------+
| cell_number        | varchar(30) | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| pmid               | int(11)     | YES  | MUL | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| example            | text        | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| cell_names_version | int(11)     | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| suppliers          | text        | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| observed_form      | varchar(30) | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+



**doc**

+----------------+--------------+------+-----+---------+----------------+
| Field          | Type         | Null | Key | Default | Extra          |
+================+==============+======+=====+=========+================+
| id             | int(11)      | NO   | PRI | NULL    | auto_increment |
+----------------+--------------+------+-----+---------+----------------+
| pmid           | int(11)      | YES  | MUL | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
| issn           | varchar(64)  | YES  |     | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
| year           | text         | YES  |     | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
| vol            | varchar(64)  | YES  |     | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
| issue          | varchar(64)  | YES  |     | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
| journal        | text         | YES  |     | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
| journalAbbrev  | text         | YES  |     | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
| journalCountry | varchar(255) | YES  |     | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
| journalNlmID   | varchar(64)  | YES  |     | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
| articleTitle   | text         | YES  |     | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+

This table contains all relevant information about an article's original journal publication.

**grants**

+---------+-------------+------+-----+---------+-------+
| Field   | Type        | Null | Key | Default | Extra |
+=========+=============+======+=====+=========+=======+
| id      | int(11)     | YES  |     | NULL    |       |
+---------+-------------+------+-----+---------+-------+
| pmid    | int(11)     | YES  |     | NULL    |       |
+---------+-------------+------+-----+---------+-------+
| grantId | varchar(64) | YES  |     | NULL    |       |
+---------+-------------+------+-----+---------+-------+
| acronym | varchar(64) | YES  |     | NULL    |       |
+---------+-------------+------+-----+---------+-------+
| agency  | varchar(64) | YES  |     | NULL    |       |
+---------+-------------+------+-----+---------+-------+
| country | varchar(64) | YES  |     | NULL    |       |
+---------+-------------+------+-----+---------+-------+

This table contains all relevant information about grants used to fund papers, with acronyms corresponding to the grantId acronym and the organization funding the grant. Many papers have multiple grants, and similarly some grants fund several papers.

**mesh**

+----------------+--------------+------+-----+---------+-------+
| Field          | Type         | Null | Key | Default | Extra |
+================+==============+======+=====+=========+=======+
| id             | int(11)      | YES  |     | NULL    |       |
+----------------+--------------+------+-----+---------+-------+
| pmid           | int(11)      | YES  | MUL | NULL    |       |
+----------------+--------------+------+-----+---------+-------+
| descriptorUI   | varchar(16)  | YES  |     | NULL    |       |
+----------------+--------------+------+-----+---------+-------+
| descriptorName | varchar(255) | YES  |     | NULL    |       |
+----------------+--------------+------+-----+---------+-------+
| qualifier1UI   | varchar(16)  | YES  |     | NULL    |       |
+----------------+--------------+------+-----+---------+-------+
| qualifier1Name | varchar(255) | YES  |     | NULL    |       |
+----------------+--------------+------+-----+---------+-------+
| qualifier2UI   | varchar(16)  | YES  |     | NULL    |       |
+----------------+--------------+------+-----+---------+-------+
| qualifier2Name | varchar(255) | YES  |     | NULL    |       |
+----------------+--------------+------+-----+---------+-------+

The MeSH database is a list of terms that are important and prevalant in many PubMed papers. Each of these terms has a distinct identifier, listed in descriptorUI, and often has subcategories present in a paper, which have their own UI and name. This table contains the information on MeSH terms which are found in papers, as they are in the PubMed database.

**nAuthorHistogram**

+----------+------------+------+-----+---------+-------+
| Field    | Type       | Null | Key | Default | Extra |
+==========+============+======+=====+=========+=======+
| year     | text       | YES  |     | NULL    |       |
+----------+------------+------+-----+---------+-------+
| nAuthors | bigint(21) | NO   |     | 0       |       |
+----------+------------+------+-----+---------+-------+
| nPmids   | bigint(21) | NO   |     | 0       |       |
+----------+------------+------+-----+---------+-------+

This is a histogram of the number of papers with a given number of authors by year.
For example,

+------+----------+--------+
| year | nAuthors | nPmids |
+======+==========+========+
| 1992 |        5 |  37357 |
+------+----------+--------+

this result shows that in 1992, there were 37,357 PubMed papers with 5 authors.

**patent_docs**

+--------------------+-------------+------+-----+---------+----------------+
| Field              | Type        | Null | Key | Default | Extra          |
+====================+=============+======+=====+=========+================+
| instance_id        | int(11)     | NO   | PRI | NULL    | auto_increment |
+--------------------+-------------+------+-----+---------+----------------+
| cell_number        | varchar(30) | YES  | MUL | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| usptoid            | varchar(20) | YES  | MUL | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| example            | text        | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| cell_names_version | int(11)     | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| suppliers          | text        | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| date               | int(11)     | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+
| observed_form      | varchar(30) | YES  |     | NULL    |                |
+--------------------+-------------+------+-----+---------+----------------+

**pmidAuthId**

+-------+---------+------+-----+---------+-------+
| Field | Type    | Null | Key | Default | Extra |
+=======+=========+======+=====+=========+=======+
| pmid  | int(11) | YES  |     | NULL    |       |
+-------+---------+------+-----+---------+-------+
| id    | int(11) | NO   |     | 0       |       |
+-------+---------+------+-----+---------+-------+

The id corresponds to the id given to each author on that paper based on the id in the authorId table.

**pmidNumAuthors**

+----------+------------+------+-----+---------+-------+
| Field    | Type       | Null | Key | Default | Extra |
+==========+============+======+=====+=========+=======+
| pmid     | int(11)    | YES  |     | NULL    |       |
+----------+------------+------+-----+---------+-------+
| nAuthors | bigint(21) | NO   |     | 0       |       |
+----------+------------+------+-----+---------+-------+

Number of authors for each paper.

**pmid_ext_metadata**

+---------+---------+------+-----+---------+-------+
| Field   | Type    | Null | Key | Default | Extra |
+=========+=========+======+=====+=========+=======+
| pmid    | int(11) | NO   |     | NULL    |       |
+---------+---------+------+-----+---------+-------+
| date    | int(11) | YES  |     | NULL    |       |
+---------+---------+------+-----+---------+-------+
| journal | text    | YES  |     | NULL    |       |
+---------+---------+------+-----+---------+-------+

External publication dates and journals for PubMed papers.

**yearPmidNumAuthor**

+----------+------------+------+-----+---------+-------+
| Field    | Type       | Null | Key | Default | Extra |
+==========+============+======+=====+=========+=======+
| year     | text       | YES  |     | NULL    |       |
+----------+------------+------+-----+---------+-------+
| pmid     | int(11)    | YES  |     | NULL    |       |
+----------+------------+------+-----+---------+-------+
| nAuthors | bigint(21) | NO   |     | 0       |       |
+----------+------------+------+-----+---------+-------+

Each PubMed paper is listed by pmid by year and with the number of authors on the paper.
