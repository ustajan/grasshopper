.. _methods:

======================
Theory and Methodology
======================

.. toctree::
    :numbered:
    :maxdepth: 3


Theory
==================
Grasshopper utilizes tools in Geant4 to generate Monte Carlo (MC) particle simultions.
In computing, a Monte Carlo algorithm is a randomized algorithm whose output can be incorrect to a certain range in
probability. One such examples of an MC algorithm is the Karger–Stein algorithm.

The name refers to the grand casino in the Principality of Monaco at Monte Carlo, which is famous around the world
as an icon of gambling. The term "Monte Carlo" was first introduced in 1947 by Nicholas Metropolis.

Las Vegas algorithms are the subset of Monte Carlo algorithms that can always produce the correct answer.
Because they make random choices as part of their working, the time taken might vary between runs
even with the same input.

Given a procedure for verifying whether the answer given by a Monte Carlo algorithm is correct,
and that the analyical probability of a correct answer is bounded above zero, then with probability one
running the algorithm repeatedly while testing the answers will eventually give a correct answer.
Whether this process is a Las Vegas algorithm depends on whether halting with probability
one is considered to satisfy the definition. [1]

GDML
==================
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>

xmlns:xsi 

xsi:noNamespaceSchemaLocation

Materials section
-----------------
Consists of objects that are materials, isotopes, elements, etc.

Define section
--------------


Solids section
--------------


Structure section
-----------------


Setup
-----


References
----------

[1] https://en.wikipedia.org/wiki/Monte_Carlo_algorithm