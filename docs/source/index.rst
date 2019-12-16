.. Grasshopper documentation master file, created by
   sphinx-quickstart on Tue Dec 10 11:46:47 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=======================================
Grasshopper: A Geant4 Simulation Program!
=======================================


Current Work
==================
Current particle physics simulations take place largely within small communities developing limited tools for specific areas of study. 
These particle simulations are essential to evaluating environments outside of the realm of experimentation in the radiation sciences. 
While multi-use toolkits exist for particles simulation (such as MCNP or SRIM), these computational tools are often difficult for untrained users to adapt into their projects. 
Geant4 is one such toolkit used widely by physicists in radiology, fission reactor work, and space irradiation studies among many other fields [1]. 
Geant4 can be adapted for use in other programs using the methods supplied by the open source code provided. 
In addition, Geant4 relies on various databases shared by institutes such as NIST. 
Unfortunately, Geant4 and the related libraries are not a common program to install and use for scientific simulation users or the general public interested in this work [2]. 
However, a widely applicable simulation engine using Geant4, called Grasshopper, has been developed to allow for generating straightforward Monte Carlo simulations for engineers 
and scientists in a wide range of fields.


.. admonition:: Recommended publication for citing
   :class: tip

   Jacob N. Miske and Areg Danagoulian "`Grasshopper: A Geant4 code for
   Research and Development of Radiation Transport`"

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. only:: html

   --------
   Contents
   --------

.. toctree::
    :maxdepth: 1

    quickinstall
    examples/index
    releasenotes/index
    methods/index
    usersguide/index
    devguide/index
    pythonapi/index
    capi/index
    io_formats/index
    publications
    license