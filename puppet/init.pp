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
  
  #exec {'add-ubuntugis':
  #  command => '/usr/bin/add-apt-repository ppa:ubuntugis/ubuntugis-unstable',
  #  before => Exec['apt-update']
  #}

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
  
  package {['python-setuptools', 'python-dev', 'build-essential',
            'python-numpy', 'python-nose', 'git', ]:
    ensure => present,
    provider => 'apt'
  }
}

class inasafe {
  
  package {['python-pip', 'python-sphinx', 'pyqt4-dev-tools', 'python-gdal', 'curl', 'libpq-dev', 
            'gdal-bin', 'python-qgis' ]:
    ensure => present,
    provider => 'apt'
  }
  
  package { ['tornado', 'numpy', 'sqlalchemy', 'Paver', 'requests', 'gsconfig', 'screenutils']:
    ensure  => installed,
    provider => pip
  }
}

class weasyprint {
  package {['libxml2-dev', 'libxslt1-dev', 'libcairo2', 'libpango1.0-0', 'libgdk-pixbuf2.0-0', 'libffi-dev']:
    ensure => present,
    provider => 'apt'
  }
  
  package { 'cffi':
    ensure  => '0.6',
    provider => pip
  }
  
  package { 'lxml':
    ensure  => '3.2.3',
    provider => pip
  }
  
  package { ['tinycss', 'cssselect', 'cairosvg', 'pyphen', 'cairocffi', 'html5lib', 'weasyprint']:
    ensure  => installed,
    provider => pip
  }
}

class {'server_dependencies':}
class {'update':}
class {'inasafe':}
class {'weasyprint':}

Class['server_dependencies'] -> Class['update'] -> Class['inasafe'] -> Class['weasyprint']