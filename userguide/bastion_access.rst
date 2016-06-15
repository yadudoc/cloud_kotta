Bastion Access
==============

The Bastion node is the equivalent of a login node in traditional clusters. This a machine that is hosted
with a secure network that can be reached from the external world via SSH. By default the Bastion host is 
a t2.small instance type offered by AWS and is thus a machine with a single core with limited compute capacity.
It is intended as a machine that is to be used only for managing jobs via the job management system.

Generating SSH keys:
--------------------

Generate an SSH key following this document :
https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/
Please note the following:
1.  Do *NOT* send me your private key
2.  Please send public key as an attachment rather than pasting it's contents

Creating a user on Bastion:
---------------------------
Once you have an ssh public key, 
* either mail it to "yadu@uchicago.edu" as an attachment 
* send it to @yadu on Channel:#cloudkotta under the KnowledgeLab organization.

.. note::
   Ensure that you do **not** send or share your private key with anyone else.

.. note::
   Public keys easily get mangled when copy pasted, so always send the file in its entirety.


Logging in:
-----------

.. code-block:: bash
   :linenos: 

   ssh <username>@bastion.turingcompute.net
