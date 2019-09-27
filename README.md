SmartRoom
===============
System that uses facial recognition to unlock a dorm room door. Uses a server/client system to allow a remote system attached to the door, with the server unlocking the door with the use of the Selenium library to spoof a mobile device, login as the user, and unlock the door.

Also includes a short program to run a fireplace video (for the monitor I had in my fireplace my first year :) )

In order to increase performance, multithreaded & multiprocessing implementations were created for the server/client version.


The highest performance version is local.py, where all work is done on a single device. This version is also the most developed for creating & training new users on the fly.
