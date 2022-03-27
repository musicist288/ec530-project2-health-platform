.. MedOps documentation master file, created by
   sphinx-quickstart on Tue Feb  8 18:06:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MedOps's documentation!
==================================

MedOps is a platform for monitoring patients at home or in hospitals. This
application is in its infancy, so abstractions and API documentations are
subject to change at any time without notice until a stable architecture
emerges. Be sure to check back for updates. The plan is for the different data
models to be loosely coupled such that each model (devices, users, data, etc.)
has its own set of REST APIs.

The source code for MedOps is hosted on `GitHub
<https://github.com/musicist288/ec530-project2-health-platform>`_.


Guides
^^^^^^
.. toctree::
   :maxdepth: 1

   hosting


API Reference
^^^^^^^^^^^^^
If you are looking for information on the data models and APIs being developed
you're in the right spot, check out the contents below.

.. toctree::
   :maxdepth: 2

   api
   demos
   chat
   devices
   data
   users
   speechtotext
