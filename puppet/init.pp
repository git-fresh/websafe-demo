class update {
  # There seems to be a problem with apt-get update without this.
  exec {'dpkg-configure':
    command => '/usr/bin/dpkg --configure -a',
    before => Exec['apt-initialize']
  }
  
  exec {'apt-initialize':
    command => '/usr/bin/apt-get update',
    before => Package['python-software-properties']
  }

  package {'python-software-properties':
    ensure => present,
    before => Exec['apt-update']
  }

  exec {'add-python-software':
    path => ["/usr/bin/","/usr/sbin/","/bin"],
    command => 'sudo apt-get install python-software-properties',
    before => Exec['add-ubuntugis'],
    logoutput => "on_failure"
  }

  exec {'add-ubuntugis':
    path => ["/usr/bin/","/usr/sbin/","/bin"],
    command => 'sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable',
    before => Exec['apt-update'],
    logoutput => "on_failure"
  }
  
  exec {'apt-update':
    command => '/usr/bin/apt-get update'
  }
}

class server_dependencies {
  package {['python-pip', 'python-setuptools', 'python-dev', 'build-essential',
            'python-numpy', 'python-nose', 'git']:
    ensure => present,
    provider => 'apt'
  }
}

class inasafe {
  
  package {['python-sphinx', 'pyqt4-dev-tools', 'python-gdal', 'curl', 'libpq-dev', 
            'gdal-bin', 'python-qgis']:
    ensure => present,
    provider => 'apt'
  }
  
  package { ['tornado', 'Paver', 'requests', 'gsconfig', 'python-sld']:
    ensure  => installed,
    provider => pip
  }
}

class weasyprint {
  package {[ 'libcairo2-dev', 'libxslt1-dev', 'libpango1.0-0', 'libgdk-pixbuf2.0-0', 'libffi-dev']:
    ensure => present,
    provider => 'apt'
  }
  
  package { 'cffi':
    ensure  => '0.6',
    provider => pip
  }
  
  package { ['html5lib', 'cairosvg', 'tinycss', 'cssselect', 'pyphen', 'cairocffi', 'weasyprint']:
    ensure  => installed,
    provider => pip
  }
}

class {'update':}
class {'server_dependencies':}
class {'inasafe':}
class {'weasyprint':}

Class['update'] -> Class['server_dependencies'] -> Class['inasafe'] -> Class['weasyprint']