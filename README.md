WebSAFE demo
============
WebSAFE for demo purposes only

Installation setup
==================
Download Vagrant:

    % http://downloads.vagrantup.com/tags/v1.2.7
    
Download VirtualBox 4.x.x:

    % https://www.virtualbox.org/wiki/Downloads
    
Clone this repository

After doing all of the above, navigate to the root of this directory and run:

    % vagrant up

...and wait until every dependency installation has finished executing...

then run:

    % vagrant provision

to install the remaining dependencies.

Running The Server
======================
    
To manually start the server, just login to the virtual machine or SSH to localhost:2222 
with the following credentials:

    % username: vagrant
    % password: vagrant
    
First, manually install Java dependencies

    % sudo apt-get install -y --force-yes openjdk-6-jdk ant maven2 --no-install-recommends

Then navigate to the server directory:

    % cd /vagrant/server

## Running for the first time

if running for the first time, type this command:
    
    % paver setup
    
the previous command will automatically start geoserver. After the geoserver starts, change the
password to `projectnoah` for the root found in:

    % /vagrant/server/geoserver/data/security/masterpw.info

after changing the password to 'projectnoah', upload all the styles in "data/styles" folder
to geoserver and then finally run this command in the command line to upload all the data for the demo:
    
    % paver setup_data
    
after setting up the data, allow the webLogin -> j_spring_security_check to create HTTP sessions.
This can be done by going in the Security -> Authentication section in the sidebar while logged in to Geoserver.

## Manually running Geoserver

To run geoserver manually next time, just type this command:
    
    % paver start_geoserver
    
then run the tornado server using this command:

    % python main.py
    
and the server is accessible in this address:
    
    % http://localhost:5000
    
to stop geoserver, just type this command:
    
    % paver stop_geoserver
    

Developer Notes
===============

All inputs and user interactions are assumed to be correct 
since this demo is only to show the basic functionalities of Web InaSAFE.