***************
Game Design Doc
***************

Intro
=====

Open world rogue-like with multiple victory conditions similar to Civ games. The setting is technology meets fantasy similar to many Final Fantasy settings or Shadowrun.

Rough Plot
==========

N/A

Gameplay Description
====================

Overview
--------

The player generates a character that they use to explore an open world city.
They must then complete various tasks/quests/missions to work toward one of a multiple of victory conditions.

Character Control
------------------

Movement
^^^^^^^^

Typical N-directional (with respect to the ground plane) movement with jumping.
Short objects will be automatically vaulted over.
The height threshold for this automatic vaulting can be increased by the movement trait tree.

Shooting
^^^^^^^^

The player will have a reticule to be able to aim.
The projectile will jitter some random amount based on the character's Guns trait.

Mêlée
^^^^^

Mêlée combat can be handled one of two ways:

#. Re-using shooting code and bringing the distance in close
#. Add physics shapes to the model to detect hits

The first is simpler while the second is more accurate.

Camera
------

Typical third-person camera. Maybe with a first-person option.

Demonic Incursion
-----------------

Demons are taking over the city.
Throughout the game, demon portals will open and more demons will enter the city.
The number and strength of the demons will depend on the number of portals open or some other "demonic incursion metric."
When this metric is maxed out, the city is overrun and the game is over.
To close the portals, the player will have to enter them and perform some action (similar to Oblivion gates in Oblivion).

Character Creation and Progression
----------------------------------

At character creation a player will pick three traits.
The traits are:

(To be trimmed)

* Guns
* Mêlée
* Explosives
* Thievery
* Movement
* Adept/Self Magic
* Destruction Magic
* Controller Magic
* Conjuration Magic
* Divine/Demonic Magic
* Politics/Influence/Sabotage

Each trait has a tree that points can be spent on to improve the traits.
New traits can be acquired via quests.
How to unlock each trait quest will have to be determined.

.. note::

    How many upgrades should each trait have? 5?

Victory Conditions
------------------

Influence
^^^^^^^^^

Control a majority of the city.

.. note::

    How do you get more control?

Purge the Demons
^^^^^^^^^^^^^^^^

Gather artifacts from exploring/closing demon portals to force open a portal to the heart of the demonic threat to end it.

Captain Awesome
^^^^^^^^^^^^^^^

Complete three trait mastery quests.
A trait mastery test becomes available when a trait skill tree has been completed.

Artistic Style Outline
======================

Systematic Breakdown of Components
==================================

Game Engines
------------

Options:

* BGE
* Panda3D
* Godot

Requirements:

* Support for editing on Linux/OSX/Windows
* Support for publishing to Linux/OSX/Windows
* Character and vehicle physics
* Pipeline for getting assets from Blender

Physics
-------

Vehicle Physics
^^^^^^^^^^^^^^^


Character Physics
^^^^^^^^^^^^^^^^^

We will need a kinematic character controller.
Ideally we could make use of an existing KCC instead of writing one from scratch.

GUI
---

Options for BGE:

* Bgui

Options for Panda:

* DirectGui
* LUI
* CEF

Options for Godot:

* Built-in

AI
--

Asset Break Down
================

Suggested Game Flow Diagram
===========================

#. Create/Load character
#. Complete quests in the city and work toward a victory condition
#. Win when victory condition is met

Suggested Project Timeline
==========================

TODO: Generate a task dependency graph.

Additional Ideas and Possibilities
==================================

* Randomly generate cities
* Add flying vehicles
* More parkour-style movement options

