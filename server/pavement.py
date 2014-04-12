import os, re, shutil, sys, time, urllib, zipfile, \
    glob, fileinput
    
from paver.easy import task, options, cmdopts, needs
from paver.easy import path, sh, info, call_task
from paver.easy import BuildFailure

try:
    from paver.path import pushd
except ImportError:
    from paver.easy import pushd

assert sys.version_info >= (2, 6), \
    SystemError("WebSAFE requires python 2.6 or better")
    
GEOSERVER_URL="http://build.geonode.org/geoserver/latest/geoserver.war"
DATA_DIR_URL="http://build.geonode.org/geoserver/latest/data.zip"
JETTY_RUNNER_URL="http://repo2.maven.org/maven2/org/mortbay/jetty/jetty-runner/8.1.8.v20121106/jetty-runner-8.1.8.v20121106.jar"

def grab(src, dest, name):
    download = True
    if not dest.exists():
        print 'Downloading %s' % name
    elif not zipfile.is_zipfile(dest):
        print 'Downloading %s (corrupt file)' % name
    else:
        download = False
    if download:
        urllib.urlretrieve(str(src), str(dest))
        
@task
@cmdopts([
    ('fast', 'f', 'Fast. Skip some operations for speed.'),
])
def setup_geoserver(options):
    """Prepare a testing instance of GeoServer."""
    fast = options.get('fast', False)
    download_dir = path('downloaded')
    if not download_dir.exists():
        download_dir.makedirs()

    geoserver_dir = path('geoserver')

    geoserver_bin = download_dir / os.path.basename(GEOSERVER_URL)
    jetty_runner = download_dir / os.path.basename(JETTY_RUNNER_URL)

    grab(GEOSERVER_URL, geoserver_bin, "geoserver binary")
    grab(JETTY_RUNNER_URL, jetty_runner, "jetty runner")

    if not geoserver_dir.exists():
        geoserver_dir.makedirs()

        webapp_dir = geoserver_dir / 'geoserver'
        if not webapp_dir:
            webapp_dir.makedirs()

        print 'extracting geoserver'
        z = zipfile.ZipFile(geoserver_bin, "r")
        z.extractall(webapp_dir)

    _install_data_dir()

def _install_data_dir():
    target_data_dir = path('geoserver/data')
    if target_data_dir.exists():
        target_data_dir.rmtree()

    original_data_dir = path('geoserver/geoserver/data')
    justcopy(original_data_dir, target_data_dir)

    config = path('geoserver/data/security/auth/geonodeAuthProvider/config.xml')
    with open(config) as f:
        xml = f.read()
        m = re.search('baseUrl>([^<]+)', xml)
        xml = xml[:m.start(1)] + "http://localhost:8000/" + xml[m.end(1):]
        with open(config, 'w') as f: f.write(xml)
        
@task
def start_geoserver(options):
    """
    Start GeoServer with GeoNode extensions
    """

    #from geonode.settings import OGC_SERVER 
    #GEOSERVER_BASE_URL = OGC_SERVER['default']['LOCATION']

    url = "http://localhost:8080/geoserver/"
    #if GEOSERVER_BASE_URL != url:
    #    print 'your GEOSERVER_BASE_URL does not match %s' % url
    #    sys.exit(1)

    download_dir = path('downloaded').abspath()
    jetty_runner = download_dir / os.path.basename(JETTY_RUNNER_URL)
    data_dir = path('geoserver/data').abspath()
    web_app = path('geoserver/geoserver').abspath()
    log_file = path('geoserver/jetty.log').abspath()
    config = path('scripts/jetty-runner.xml').abspath()
    # @todo - we should not have set workdir to the datadir but a bug in geoserver
    # prevents geonode security from initializing correctly otherwise
    with pushd(data_dir):
        sh(('java -Xmx512m -XX:MaxPermSize=256m'
            ' -DGEOSERVER_DATA_DIR=%(data_dir)s'
            # workaround for JAI sealed jar issue and jetty classloader
            ' -Dorg.eclipse.jetty.server.webapp.parentLoaderPriority=true'
            ' -jar %(jetty_runner)s'
            ' --log %(log_file)s'
            ' %(config)s'
            ' > /dev/null &' % locals()
          ))

    info('Starting GeoServer on %s' % url)

    # wait for GeoServer to start
    started = waitfor(url)
    info('The logs are available at %s' % log_file)

    if not started:
        # If applications did not start in time we will give the user a chance
        # to inspect them and stop them manually.
        info(('GeoServer never started properly or timed out.'
              'It may still be running in the background.'))
        sys.exit(1)
        
@task
def stop_geoserver():
    """
    Stop GeoServer
    """
    kill('java', 'geoserver')
        
def kill(arg1, arg2):
    """Stops a process that contains arg1 and is filtered by arg2
    """
    from subprocess import Popen, PIPE

    # Wait until ready
    t0 = time.time()
    # Wait no more than these many seconds
    time_out = 30
    running = True

    while running and time.time() - t0 < time_out:
        p = Popen('ps aux | grep %s' % arg1, shell=True,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)

        lines = p.stdout.readlines()

        running = False
        for line in lines:

            if '%s' % arg2 in line:
                running = True

                # Get pid
                fields = line.strip().split()

                info('Stopping %s (process number %s)' % (arg1, fields[1]))
                kill = 'kill -9 %s 2> /dev/null' % fields[1]
                os.system(kill)

        # Give it a little more time
        time.sleep(1)
    else:
        pass

    if running:
        raise Exception('Could not stop %s: '
                        'Running processes are\n%s'
                        % (arg1, '\n'.join([l.strip() for l in lines])))


def waitfor(url, timeout=300):
    started = False
    for a in xrange(timeout):
        try:
            resp = urllib.urlopen(url)
        except IOError, e:
            pass
        else:
            if resp.getcode() == 200:
                started = True
                break
        time.sleep(1)
    return started


def justcopy(origin, target):
    import shutil
    if os.path.isdir(origin):
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(origin, target)
    elif os.path.isfile(origin):
        if not os.path.exists(target):
            os.makedirs(target)
        shutil.copy(origin, target)