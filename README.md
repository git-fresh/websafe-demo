WebSAFE demo
=======
WebSAFE frontend + backend for demo purposes only

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

Then run:

    % python /vagrant/webapp/main.py

and the backend server is accessible in this address:
    
    % http://localhost:9090

and the frontend server is accessible in this address:
    
    % http://localhost:5000