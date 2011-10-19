import Globals
import os.path

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
from Products.CMFCore.DirectoryView import registerDirectory
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

import transaction
from Products.ZenModel.ZenossInfo import ZenossInfo
from Products.ZenModel.ZenPack import ZenPackBase
from Products.ZenModel.ZenMenu import ZenMenu

class ZenPack(ZenPackBase):
    """ ZenPack loader
    """
    
    profilerTab = { 'id'            : 'profileorganizer'
                   , 'name'          : 'Profiles'
                   , 'action'        : 'Profiles/viewProfileOrganizer'
                   , 'permissions'   : ( "Manage DMD", )
                   }

    def addProfilerTab(self,app):
        dmdloc = self.dmd
        finfo = dmdloc.factory_type_information
        actions = list(finfo[0]['actions'])
        for i in range(len(actions)):
            if (self.profilerTab['id'] in actions[i].values()):
                return
        actions.append(self.profilerTab)
        finfo[0]['actions'] = tuple(actions)
        dmdloc.factory_type_information = finfo
        transaction.commit()
    
    def rmvProfilerTab(self,app):
        dmdloc = self.dmd
        finfo = dmdloc.factory_type_information
        actions = list(finfo[0]['actions'])
        for i in range(len(actions)):
            if (self.profilerTab['id'] in actions[i].values()):
                actions.remove(self.profilerTab)
        finfo[0]['actions'] = tuple(actions)
        dmdloc.factory_type_information = finfo
        transaction.commit()
    
    def installMenus(self,app):
        dmdloc = self.dmd
        self.removeMenus(dmdloc)
        rulesetmenu = ZenMenu('ProfileMenu')
        dmdloc.zenMenus._setObject(rulesetmenu.id, rulesetmenu)
        rulesetmenu = dmdloc.zenMenus._getOb(rulesetmenu.id)
        rulesetmenu.manage_addZenMenuItem('addRuleset',
                                   action='dialog_addRuleset',  # page template that is called
                                   description='Add Ruleset',
                                   ordering=6.0,
                                   isdialog=True)
        rulesetmenu.manage_addZenMenuItem('removeRuleset',
                                   action='dialog_removeRuleset',  # page template that is called
                                   description='Remove Ruleset',
                                   ordering=5.0,
                                   isdialog=True)
        rulesetmenu.manage_addZenMenuItem('moveRuleset',
                                   action='dialog_moveRuleset',  # page template that is called
                                   description='Move Ruleset',
                                   ordering=4.0,
                                   isdialog=True)
        rulesetmenu.manage_addZenMenuItem('runAllMatches',
                                   action='dialog_runAllMatches',  # page template that is called
                                   description='Test All Rules',
                                   ordering=3.0,
                                   isdialog=True)
        rulesetmenu.manage_addZenMenuItem('runAllRules',
                                   action='dialog_runAllRules',  # page template that is called
                                   description='Apply All Rules',
                                   ordering=2.0,
                                   isdialog=True)
        rulesetmenu.manage_addZenMenuItem('buildAllAlerts',
                                   action='dialog_buildAllAlerts',  # page template that is called
                                   description='Generate All Alerts',
                                   ordering=1.0,
                                   isdialog=True)

        
        rulesetmenu = ZenMenu('RuleMenu')
        dmdloc.zenMenus._setObject(rulesetmenu.id, rulesetmenu)
        rulesetmenu = dmdloc.zenMenus._getOb(rulesetmenu.id)
        rulesetmenu.manage_addZenMenuItem('addRule',
                                   action='dialog_addRule',  # page template that is called
                                   description='Add Rule',
                                   ordering=2.0,
                                   isdialog=True)
        rulesetmenu.manage_addZenMenuItem('removeRule',
                                   action='dialog_removeRule',  # page template that is called
                                   description='Remove Rule',
                                   ordering=1.0,
                                   isdialog=True)
        
        rulesetmenu = ZenMenu('RulesetMenu')
        dmdloc.zenMenus._setObject(rulesetmenu.id, rulesetmenu)
        rulesetmenu = dmdloc.zenMenus._getOb(rulesetmenu.id)
        rulesetmenu.manage_addZenMenuItem('runMatches',
                                   action='dialog_runMatches',  # page template that is called
                                   description='Test Rules',
                                   ordering=3.0,
                                   isdialog=True)
        rulesetmenu.manage_addZenMenuItem('runRules',
                                   action='dialog_runRules',  # page template that is called
                                   description='Apply Rules',
                                   ordering=2.0,
                                   isdialog=True)
        rulesetmenu.manage_addZenMenuItem('buildAlerts',
                                   action='dialog_buildAlerts',  # page template that is called
                                   description='Generate Alerts',
                                   ordering=1.0,
                                   isdialog=True)

    def removeMenus(self, dmd):
        try:
            self.dmd.zenMenus._delObject('ProfileMenu')
        except:
            pass
        try:
            self.dmd.zenMenus._delObject('RuleMenu')
        except:
            pass
        try:
            self.dmd.zenMenus._delObject('RulesetMenu')
        except:
            pass

    def install(self, app):
        ZenPackBase.install(self, app)
        self.addProfilerTab(app)
        self.installMenus(app.zport.dmd)
        
    def upgrade(self, app):
        ZenPackBase.upgrade(self, app)
        self.addProfilerTab(app)
        self.installMenus(app.zport.dmd)

    def remove(self, app, junk):
        self.rmvProfilerTab(app)
        #self.dmd._delObject('Profiles')
        self.removeMenus(self.zport.dmd)
        #ZenPackBase.remove(self, app, junk)
        #ZenPackBase.remove(self.app, leaveObjects)

