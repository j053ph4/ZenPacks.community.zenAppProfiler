import Globals
from Products.ZenModel.migrate.Migrate import *
from Products.ZenModel.ZenPack import ZenPack
from Products.ZenModel.ZenPack import ZenPackMigration
from ZenPacks.community.zenAppProfiler.ProfileOrganizer import manage_addProfileOrganizer

import logging
log = logging.getLogger("zen.migrate")

class CreateProfileOrganizer(ZenPackMigration):
    version = Version(1, 8, 0)
    def migrate(self, pack):
        if hasattr(pack.dmd, 'Profiles'):
            log.info("Profiles already exists")
        else: 
            log.info("Installing Profiles")
            manage_addProfileOrganizer(pack.dmd, 'Profiles')
  
CreateProfileOrganizer()
