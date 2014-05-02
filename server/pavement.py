import os, re, shutil, sys, time, urllib, zipfile
    
from paver.easy import task, options, needs
from paver.easy import path, sh, info, call_task

from geoserver.catalog import Catalog


'''
Define all Geoserver and file directory constants
'''
ROOT = os.path.dirname(__file__)

DATA_PATH = os.path.join(ROOT, 'data')

GS_USERNAME = "root"
GS_PASSWORD = "projectnoah"

GEOSERVER_BASE_URL = 'http://localhost:8080/geoserver/'
GEOSERVER_REST_URL = GEOSERVER_BASE_URL + 'rest'

GEOSERVER_WORKSPACE = 'websafe'
GEOSERVER_STORE = 'impact'

try:
    from paver.path import pushd
except ImportError:
    from paver.easy import pushd

assert sys.version_info >= (2, 6), \
    SystemError("WebSAFE requires python 2.6 or better")
    
GEOSERVER_URL="http://build.geonode.org/geoserver/latest/geoserver.war"
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
def setup_geoserver():
    download_dir = path('downloaded')
    if not download_dir.exists():
        download_dir.makedirs()

    geoserver_bin = download_dir / os.path.basename(GEOSERVER_URL)
    jetty_runner = download_dir / os.path.basename(JETTY_RUNNER_URL)

    grab(GEOSERVER_URL, geoserver_bin, "geoserver binary")
    grab(JETTY_RUNNER_URL, jetty_runner, "jetty runner")

    geoserver_dir = path('geoserver')
    if not geoserver_dir.exists():
        geoserver_dir.makedirs()

        webapp_dir = geoserver_dir / 'geoserver'
        if not webapp_dir:
            webapp_dir.makedirs()

        print 'extracting geoserver'
        z = zipfile.ZipFile(geoserver_bin, "r")
        z.extractall(webapp_dir)


    target_data_dir = path('geoserver/data')
    if not target_data_dir.exists():
        target_data_dir.makedirs()

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
@needs([
    'setup_geoserver',
    'start_geoserver'
])
def setup():
    try:
        impact_dir = path('data/impact')
        if not impact_dir.exists():
            impact_dir.makedirs()

        info('Geoserver is now up at %s' % GEOSERVER_BASE_URL)
        info('Please change the password for the root user. '
             'The default password is found in: '
             '/vagrant/server/geoserver/data/security/masterpw.info')
    except:
        raise

@task
def setup_data():
    haz_conn_params =  {
        'cache and reuse memory maps': 'true', 
        'namespace': 'http://inasafe.org', 
        'filetype': 'shapefile', 
        'charset': 'ISO-8859-1', 
        'create spatial index': 'true', 
        'fstype': 'shape', 
        'url': 'file:///vagrant/server/data/hazard', 
        'enable spatial index': 'true', 
        'memory mapped buffer': 'false', 
        'timezone': 'Etc/UTC'
    }
    exp_conn_params =  {
        'cache and reuse memory maps': 'true', 
        'namespace': 'http://inasafe.org', 
        'filetype': 'shapefile', 
        'charset': 'ISO-8859-1', 
        'create spatial index': 'true', 
        'fstype': 'shape', 
        'url': 'file:///vagrant/server/data/exposure', 
        'enable spatial index': 'true', 
        'memory mapped buffer': 'false', 
        'timezone': 'Etc/UTC'
    }
    impact_conn_params =  {
        'cache and reuse memory maps': 'true', 
        'namespace': 'http://inasafe.org', 
        'filetype': 'shapefile', 
        'charset': 'ISO-8859-1', 
        'create spatial index': 'true', 
        'fstype': 'shape', 
        'url': 'file:///vagrant/server/data/impact', 
        'enable spatial index': 'true', 
        'memory mapped buffer': 'false', 
        'timezone': 'Etc/UTC'
    }

    try:
        cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
        cat.create_workspace(GEOSERVER_WORKSPACE, 'http://inasafe.org')
        cat.set_default_workspace(GEOSERVER_WORKSPACE)

        haz_store = cat.create_datastore('hazard')
        haz_store.type = 'Directory of spatial files (shapefiles)'
        haz_store.connection_parameters = haz_conn_params
        cat.save(haz_store)

        exp_store = cat.create_datastore('exposure')
        exp_store.type = 'Directory of spatial files (shapefiles)'
        exp_store.connection_parameters = exp_conn_params
        cat.save(exp_store)

        impact_store = cat.create_datastore('impact')
        impact_store.type = 'Directory of spatial files (shapefiles)'
        impact_store.connection_parameters = impact_conn_params
        cat.save(impact_store)

        exposure_dir = os.path.join(DATA_PATH, 'exposure')
        hazard_dir = os.path.join(DATA_PATH, 'hazard')

        upload_layer(str(os.path.join(exposure_dir, 'quiapo_bldgs.shp')), 'exposure')
        upload_layer(str(os.path.join(exposure_dir, 'tacloban_bldgs.shp')), 'exposure')
        upload_raster(str(os.path.join(exposure_dir, 'tacloban_pop.tif')), 'exposure')

        upload_layer(str(os.path.join(hazard_dir, 'quiapo_flood.shp')), 'hazard')
        upload_layer(str(os.path.join(hazard_dir, 'tacloban_flood.shp')), 'hazard')
        
        '''
        # upload the styles in data/styles folder
        upload_style('Building Footprints')
        upload_style('Flood Hazard Quiapo')
        upload_style('Flood Hazard')
        upload_style('Flood-Building')
        upload_style('Population Exposure')

        # set styles for each layer uploaded
        set_style('quiapo_flood', "Flood Hazard Quiapo")
        set_style('tacloban_flood', "Flood Hazard")
        set_style('quiapo_bldgs', "Building Footprints")
        set_style('tacloban_bldgs', "Building Footprints")
        set_style('tacloban_pop', "Population Exposure")
        '''

    except:
        print 'Error in setting up geoserver test environment.'
        raise

def upload_layer(file_path, store):
    data = dict()
    try:
        cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
        ws = cat.get_workspace(GEOSERVER_WORKSPACE)
        ds = cat.get_store(store)

        base = str(os.path.splitext(file_path)[0])
        name = str(os.path.splitext(os.path.basename(base))[0])

        shp = file_path
        shx = base + '.shx'
        dbf = base + '.dbf'
        prj = base + '.prj'
        data = { 
                 'shp' : shp,
                 'shx' : shx,
                 'dbf' : dbf,
                 'prj' : prj
               }
        cat.add_data_to_store(ds, name, data, ws, True)
    except:
        raise

def upload_raster(file_path, store):
    data = dict()
    try:
        cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
        ws = cat.get_workspace(GEOSERVER_WORKSPACE)
        ds = cat.get_store(store)

        base = str(os.path.splitext(file_path)[0])
        name = str(os.path.splitext(os.path.basename(base))[0])

        cat.create_coveragestore(name, file_path, ws, True)
    except:
        raise

def upload_style(style_name):
    try:
        cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
        style_dir = path('data/styles')
        style_filename = style_name + '.sld'
        style_file_path = str(os.path.join(DATA_PATH, 'styles', style_filename))

        with open(style_file_path, 'r') as style:
            cat.create_style(style_name, style.read(), workspace=GEOSERVER_WORKSPACE, overwrite=True)
            style.close()
    except:
        raise
        
@task
def start_geoserver(options):
    download_dir = path('downloaded').abspath()
    jetty_runner = download_dir / os.path.basename(JETTY_RUNNER_URL)
    data_dir = path('geoserver/data').abspath()
    web_app = path('geoserver/geoserver').abspath()
    log_file = path('geoserver/jetty.log').abspath()
    config = path('scripts/jetty-runner.xml').abspath()

    with pushd(data_dir):
        sh(('java -Xmx512m -XX:MaxPermSize=256m'
            ' -DGEOSERVER_DATA_DIR=%(data_dir)s'
            ' -Dorg.eclipse.jetty.server.webapp.parentLoaderPriority=true'
            ' -jar %(jetty_runner)s'
            ' --log %(log_file)s'
            ' %(config)s'
            ' > /dev/null &' % locals()
          ))

    info('Starting GeoServer on %s' % GEOSERVER_BASE_URL)

    # wait for GeoServer to start
    started = waitfor(GEOSERVER_BASE_URL)
    info('The logs are available at %s' % log_file)

    if not started:
        # If applications did not start in time we will give the user a chance
        # to inspect them and stop them manually.
        info(('GeoServer never started properly or timed out.'
              'It may still be running in the background.'))
        sys.exit(1)
        
@task
def stop_geoserver():
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

def set_style(layer_name, style):
    cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
    layer = cat.get_layer(layer_name)

    if style is None:
        print 'No style specified!'
        return
    
    style = cat.get_style(style, GEOSERVER_WORKSPACE)
    layer.default_style = style
    cat.save(layer)