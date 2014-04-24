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

Running Tornado Server
======================
    
To manually start the Tornado server, just login to the virtual machine or SSH to localhost:2222 
with the following credentials:

    % username: vagrant
    % password: vagrant

Then navigate to the server directory:

    % cd /vagrant/server

if running for the first time, type this command:
    
    % paver setup_data
    
the previous command will automatically start geoserver so the next command won't be needed this time.
    
to run geoserver next time the virtual machine is started, just type this command:
    
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