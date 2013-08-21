#!/usr/bin/env python
import logging
import sys

from gi.repository import Gtk

import bugzilla
import getpass
import yaml
import os

from bugzilla.bugzilla3 import Bugzilla34
from bugzilla.bugzilla4 import Bugzilla4
from bugzilla.rhbugzilla import RHBugzilla4
from string import rsplit

logger = logging.getLogger()

console_handler = logging.StreamHandler(stream=sys.stdout)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

default_bz_xml_rpc = 'https://bugzilla.redhat.com/xmlrpc.cgi'

bt_config = ".bugzillatracker/config.yaml"
full_path_config = os.path.join(os.path.expanduser("~"),bt_config)

class BugzillaTracker(object):

    def __init__(self, username):
        self.bzclass = bugzilla.Bugzilla
        self.bz = self.bzclass(url=default_bz_xml_rpc)
        self.username = username
        self.password = ""
        self.bz_dict = {}

    def login(self):
        #self.password = getpass.getpass("Enter bugzilla password:")
        self.password="$Oldfield;53"
        self.bz.login(self.username,self.password)

    def init_configuration(self):
        if full_path_config:
            with open(full_path_config,'r') as yaml_file:
                self.bz_dict = yaml.load(yaml_file)
        else:
            include_fields = ["name", "id"]
            include_fields.append("versions")
            products = self.bz.getproducts(include_fields=include_fields)
            prod=[]
            for name in sorted([p["name"] for p in products]):
                if "Red Hat Enterprise Linux" in name:
                    logging.info("%s" % name)
                    prod.append(name)
                if "Fedora" in name:
                    logging.info("%s" % name)
                    prod.append(name)
            self.bz_dict['product']=prod
            compList = ["amanda","bacula","screen","emacs","openldap","autoconf", "libtool"]
            print compList
            self.bz_dict['packages']=compList
            print self.bz_dict['packages']

    def run_query(self):
        bug_status = ['NEW', 'ASSIGNED', 'NEEDINFO', 'ON_DEV',
                'MODIFIED', 'POST', 'REOPENED']
        built_query = self.bz.build_query(
                component = self.bz_dict.get('packages'),
                status=bug_status)
        result = self.bz.query(built_query)
        for ret in result:
            strbug_id = "#%s" % ret.bug_id
            if ret.status != "CLOSED":
                logger.info("%s=%s" % (strbug_id,ret.status))
                logger.info("{0}={1}.{2}.{3}.{4}".format(strbug_id, ret.product, ret.version, ret.component, ret.short_desc))
    def save_options(self):
        logger.info("save_options")
        if not os.path.exists(os.path.dirname(full_path_config)):
            os.makedirs(os.path.dirname(full_path_config))
        with open(full_path_config, 'w') as yaml_file:
                yaml_file.write(yaml.dump(self.bz_dict, default_flow_style=False))


if __name__ == "__main__":
    bz = BugzillaTracker('phracek')
    bz.init_configuration()
    bz.login()
    bz.run_query()




