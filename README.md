SmartRoom
===============
System that uses facial recognition to unlock a dorm room door. Uses a server/client system to allow a remote system attached to the door, with the server unlocking the door with the use of the Selenium library to spoof a mobile device, login as the user, and unlock the door.

Also includes a short program to run a fireplace video (for the monitor I had in my fireplace my first year :) )

In order to increase performance, multithreaded & multiprocessing implementations were created for the server/client version.


The highest performance version is local.py, where all work is done on a single device. This version is also the most developed for creating & training new users on the fly.


<p align="center">
<img src="https://raw.githubusercontent.com/vasilzhigilei/SmartRoom/master/facialRecScreenshot.PNG" height="400px"></img>
</p>
<h6 align="center"><i>[Local version of program with working UI]</i></h6>

Changelog
---------

##### September 27th, 2019
* Committed local version of facial recognition program, added screenshot to README.md

##### February 17th, 2019
* Fireplace script that runs a loop of a fireplace video on the monitor I had in my dorm room fireplace (no real fires allowed, how sad :( )

##### February 2nd, 2019
* Created a deployment ready version for the door unlocking script so that it could run standalone

##### January 12th, 2019
* Updated server side with multithreading
* Included Selenium door unlocking script

##### November 13th, 2018
* Initial commit of server/client files
