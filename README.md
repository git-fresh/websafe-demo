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
    
then for succeeding vagrant ups, just type this command:
    
    % paver start

and the server is accessible in this address:
    
    % http://localhost:5000
    
to stop the server, just type this command:
    
    % paver stop
    

Developer Notes
===============

All inputs and user interactions are assumed to be correct 
since this demo is only to show the basic functionalities of Web InaSAFE.