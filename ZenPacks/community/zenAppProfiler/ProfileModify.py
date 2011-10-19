import re
import os
import string
import Globals
from Products.ZenModel.ZenPackable import ZenPackable
from transaction import commit

class ProfileModify(ZenPackable):
    """ Class to modify device properties
    """
    def __init__(self,dmd,groupname=None,bindTemplate=None):
        self.dmd = dmd
        self.allTemplates = self.dmd.Devices.getAllRRDTemplates()
        self.groupname = groupname
        self.bindTemplate = bindTemplate

    def initDevice(self,device):
        """ retrieve device info 
        """
        self.device = device
        self.groups = self.device.getDeviceGroupNames()
        self.systems = self.device.getSystemNames()
        self.deviceTemplates = self.device.getRRDTemplates()

    def modifyMemberships(self,ruleset,remove):
        """ modify device system/group memberships 
        """
        for system in ruleset.rulesetSystemOrganizers:
            self.groupname = system
            for rule in ruleset.rules():
                if rule.ruleKey == 'System' and rule.ruleValue == self.groupname:
                    if rule.enabled == False:
                        if remove == True:
                            self.removeSystemFromDevice()
                        else:
                            self.addSystemToDevice()
        for group in ruleset.rulesetGroupOrganizers:
            self.groupname = group
            for rule in ruleset.rules():
                if rule.ruleKey == 'Group' and rule.ruleValue == self.groupname:
                    if rule.enabled == False:
                        if remove == True:
                            self.removeGroupFromDevice()
                        else:
                            self.addGroupToDevice()
                
    def modifyTemplateBindings(self,ruleset,remove):
        """ modify template bindings
        """
        for template in ruleset.rulesetTemplates:
            self.bindTemplate = template
            if remove == True:
                self.removeTemplateFromDevice()
            else:
                self.addTemplateToDevice()

    def addSystemToDevice(self):
        """ add a system organizer to a device
        """
        groups = self.systems
        if self.groupname not in groups:
            groups.append(self.groupname)
            groups.sort()
            self.device.setSystems(groups)
            commit()

    def removeSystemFromDevice(self):
        """ remove a system organizer from a device
        """
        groups = self.systems
        if self.groupname in groups:
            groups.remove(self.groupname)
            groups.sort()
            self.device.setSystems(groups)
            commit()

    def addGroupToDevice(self):
        """ add a group organizer to a device
        """
        groups = self.groups
        if self.groupname not in groups:
            groups.append(self.groupname)
            groups.sort()
            self.device.setGroups(groups)
            commit()
            
    def removeGroupFromDevice(self):
        """ remove a group organizer from a device
        """
        groups = self.groups
        if self.groupname in groups:
            groups.remove(self.groupname)
            groups.sort()
            self.device.setGroups(groups)
            commit()
        
    def getTemplate(self):
        """ get the template object based on ID
        """
        for template in self.allTemplates:
            if template.id == self.bindTemplate:
                return template
    
    def getTemplateNames(self,templates):
        """ return names of all templates
        """
        names = []
        for t in templates:
            names.append(t.id)
        return names
        
    def addTemplateToDevice(self):
        """ add a system organizer to a device
        """
        devTemplates = self.getTemplateNames(self.deviceTemplates)
        template = self.getTemplate()
        if self.bindTemplate not in devTemplates:
            devTemplates.append(self.bindTemplate)
            devTemplates.sort()
            self.device.bindTemplates(devTemplates)
            commit()

    def removeTemplateFromDevice(self):
        """ remove a system organizer from a device
        """
        devTemplates = self.getTemplateNames(self.deviceTemplates)
        if self.bindTemplate in devTemplates:
            devTemplates.remove(self.bindTemplate)
            devTemplates.sort()
            self.device.bindTemplates(devTemplates)
            commit()
