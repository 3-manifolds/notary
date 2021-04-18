import subprocess
import json
import time
import configparser

"""
This module defines the Notarizer class, which is a base class that needs to be
extended by defining the build_dmg method in a subclass.

The Notarizer expects to find a config file named notarize.cfg in the current
directory. The file should have the following format:

[developer]
username = <your app store id or email>
password = <your app-specific password>
identity = <the signing identity you used to sign your app>

[app]
app_name = <name of the app>
app_path = <path to the application bundle>
dmg_path = <path to the disk image that your build_dmg method will create>
bundle_id = <an (arbitrary) bundle identifier that you provide for the request>

"""

class Notarizer:
    """
    Base class for app notarizers.
    """
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.start = time.time()
        
    def build_dmg(self):
        #Subclasses must override this method.
        raise RuntimeError('The Notarizer.build_dmg method must be overridden.')

    def upload_dmg(self):
        config = self.config
        print('Uploading %s to Apple ...'%config['app']['dmg_path'])
        args = ['xcrun', 'altool', '--notarize-app',
                '--primary-bundle-id', '%s'%config['app']['bundle_id'],
                '-u', config['developer']['username'],
                '-p', config['developer']['password'],
                '-f', '"%s"'%config['app']['dmg_path'],
                '--output-format', 'json',
                ]
        start = time.time()
        result = subprocess.run(args, text=True, capture_output=True)
        elapsed = int(round(time.time() - start))
        if result.returncode:
            print("Upload failed:")
            print(result.stderr)
            sys.exit(1)
        info = json.loads(result.stdout)
        self.UUID = info['notarization-upload']['RequestUUID']
        print('Request UUID:', self.UUID)
        print('Uploaded in %s seconds.'%elapsed)

    def wait_for_result(self):
        print('Waiting for results ...')
        config = self.config
        args = ['xcrun', 'altool', '--notarization-info', self.UUID,
                '-u', config['developer']['username'],
                '-p', config['developer']['password'],
                '--output-format', 'json']
        status = 'in progress'
        while status == 'in progress':
            time.sleep(59)
            result = subprocess.run(args, text=True, capture_output=True)
            if result.returncode:
                print("Info request failed:")
                print(result.stderr)
                sys.exit(1)
            info = json.loads(result.stdout)
            status = info['notarization-info']['Status']
            print(status, '(%s seconds)'%int(round(time.time() - self.start)))
        if status != 'success':
            print('Notarization failed')
            sys.exit(1)

    def staple_app(self):
        config = self.config
        print('Stapling the notarization ticket to %s\n'%config['app']['app_path'])
        args = ['xcrun', 'stapler', 'staple', config['app']['app_path']]
        result = subprocess.run(args, text=True, capture_output=True)
        self.check(result, 'Stapling failed')

    def sign_dmg(self):
        print('Signing the disk image')
        config = self.config
        args = ['codesign', '-v', '-s', config['developer']['identity'],
                config['app']['dmg_path']]
        result = subprocess.run(args, text=True, capture_output=True)
        self.check(result, 'Signing failed')

    def staple_dmg(self):
        config = self.config
        print('Stapling the notarization ticket to %s\n'%config['app']['dmg_path'])
        args = ['xcrun', 'stapler', 'staple', config['app']['dmg_path']]
        result = subprocess.run(args, text=True, capture_output=True)
        self.check(result, 'Stapling failed')

    def check(self, result, message):
        if result.returncode:
            print(message + ':')
            print(result.stderr)
            sys.exit(1)
        
    def run(self):
        self.build_dmg()
        self.upload_dmg()
        self.wait_for_result()
        self.staple_app()
        print('Repackaging the stapled app ...')
        self.build_dmg()
        self.sign_dmg()
        self.upload_dmg()
        self.wait_for_result()
        self.staple_dmg()
