# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  module_path = ["puppet/modules"]
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  
  config.vm.network :forwarded_port, guest: 5000, host: 5000, auto_correct: true
  config.vm.network :forwarded_port, guest: 8000, host: 8000, auto_correct: true
  config.vm.network :forwarded_port, guest: 8080, host: 8080, auto_correct: true

  config.vm.provider :virtualbox do |vb|
    vb.gui = true
    vb.customize ["modifyvm", :id, "--memory", "4096"]
  end
  
  config.vm.provision :puppet, :module_path => module_path do |puppet|
    puppet.manifests_path = "puppet"
    puppet.manifest_file  = "init.pp"
  end
  
  #config.vm.provision "shell", path: "init.sh"
end
