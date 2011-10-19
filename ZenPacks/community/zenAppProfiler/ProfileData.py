import re
import os
import string
import Globals
from Products.ZenModel.ZenPackable import ZenPackable

class ProfileData(ZenPackable):
    '''  Class containing logic for evaluating rule outcomes.
    '''
    
    def __init__(self,dmd):
        self.dmd = dmd
    
    def getAllRulesets(self):
        """ find all rulesets recursively
        """
        rulesets = []
        for org in [self.dmd.Profiles] + self.dmd.Profiles.getSubOrganizers():
            for ruleset in org.rulesets():
                rulesets.append(ruleset)
        return rulesets
    
    def findRuleset(self,rulesetName):
        """ find a ruleset by name
        """
        rulesets = self.getAllRulesets()
        for ruleset in rulesets:
            if ruleset.id == rulesetName:
                return ruleset
        return None
    
    def getDeviceObjects(self,devicelist):
        """ return dmd objects corresponding to device names
        """
        results = []
        if devicelist != None:
            for device in devicelist:
                results.append(self.dmd.Devices.findDeviceByIdOrIp(device.id))
        return results

    def getDeviceNames(self,devices):
        results = []
        if devices != None:
            for device in devices:
                results.append(device.id)
        return results
    
    def getAllComponentMetaTypes(self):
        """ return list of all unique component meta types 
        """
        metaTypeIndex = self.dmd.Devices.componentSearch.index_objects()[1]
        comptypes = []
        for mtype in metaTypeIndex.uniqueValues():
            comptypes.append(mtype.title())
        return comptypes
    
    def evalRuleOnDevice(self,rule,device):
        """ evaluate a rule, return True or False if device matches
        """
        if rule.ruleKey == 'System' or rule.ruleKey == 'Group':
            if self.findOrganizationRuleMatch(rule,device) == True:
                return True
        elif rule.ruleKey == 'Template':
            if rule.ruleset.matchAll == True: # this is so that unbound templates won't cause the match to fail
                return True
            if self.findTemplateOnDevice(rule,device,True) == True:
                return True
            elif self.findTemplateOnComponents(rule,device,True) == True:
                return True
        elif rule.ruleKey == 'Location':
            if self.findDeviceLocationMatch(rule, device) == True:
                return True
        elif rule.ruleKey == 'Device':
            if self.findDeviceNameMatch(rule, device) == True:
                return True 
        elif self.findComponentMetaTypeOnDevice(rule,device,True) == True:
            return True
        return False
 
    def evalRuleWithObjects(self,rule,device):
        """ evaluate a rule, return matching components:
        """
        objects = []
        # template-based device componnets
        if rule.ruleKey == 'Template':
            objects = self.findTemplateOnDevice(rule,device,False)
            objects += self.findTemplateOnComponents(rule,device,False)  
        # normal components
        else:
            objects =  self.findComponentMetaTypeOnDevice(rule,device,False)
        return objects
 
    def findOrganizationRuleMatch(self,rule,device):
        """ return True if a device is a member of this organizer
        """
        objects = []
        if rule.ruleKey == 'System':
            organizers = device.getSystemNames()
        elif rule.ruleKey == 'Group':
            organizers = device.getDeviceGroupNames()
        for org in organizers:
            if re.search(rule.ruleValue,org) != None:
                return True
        return False

    def findDeviceLocationMatch(self,rule,device):
        """ return True if a device location matches
        """
        try:
            location = device.getLocationName()
            if re.search(rule.ruleValue,location) != None:
                return True
        except:
            pass
        return False
    
    def findDeviceNameMatch(self,rule,device):
        """ return True if a device name matches
        """
        try:
            if re.search(rule.ruleValue,device.id) != None:
                return True
            elif re.search(rule.ruleValue,device.title) != None:
                return True
        except:
            pass
        return False

    def findTemplateOnDevice(self,rule,device,easy=True):
        """ return True if a template is used by a device
        """
        
        templates = device.getRRDTemplates()
        objects = []
        for template in templates:
            if re.search(rule.ruleValue,template.id) != None:
                if easy == True:
                    return True
                else:
                    objects.append(('deviceTemplate',(template,device)))
        if easy == True:
            return False
        else:
            return objects

    def findTemplateOnComponents(self,rule,device,easy=True):
        """ return True if a template is used by a device component
        """
        objects = []
        for c in self.dmd.Devices.componentSearch(meta_type=rule.ruleValue,getParentDeviceName=device.id):
            component = c.getObject()
            templates = component.getRRDTemplates()
            for template in templates:
                if re.search(rule.ruleValue,template.id) != None:
                    if easy == True:
                        return True
                    else:
                        objects.append(('componentTemplate',(template,component)))
        if easy == True:               
            return False
        else:
            return objects

    def findComponentMetaTypeOnDevice(self,rule,device,easy=True):
        """ return devices with a given component matching 
            the rule
        """
        objects = []
        for c in self.dmd.Devices.componentSearch(meta_type=rule.ruleKey,getParentDeviceName=device.id):
            component = c.getObject()
            if self.doesComponentMatch(rule,component) == True:
                if easy == True:
                    return True
                else:
                    objects.append(('deviceComponent',component))
        if easy == True:
            return False
        else:
            return objects

    def doesComponentMatch(self,rule,component):
        """ return True if component matches this rule
        """
        if re.search(rule.ruleValue,component.name()) != None:
            return True
        elif re.search(rule.ruleValue,component.getId()) != None:
            return True
        elif re.search(rule.ruleValue,component.getInstDescription()) != None:
            return True
        return False

    def setRuleMembers(self,rule,devices=[]):
        """ set current, potential matches for this rule:
            all submitted devcies match the rule, but not all are members of all 
            rule organizers
        """
        rule.rulePotentialMatches = []
        rule.ruleCurrentMatches = []
        for device in devices:
            isMember = self.isPotentialOrCurrent(rule,device)
            if isMember == True:
                rule.ruleCurrentMatches.append(device)
            else:
                rule.rulePotentialMatches.append(device)
                    
    def isPotentialOrCurrent(self,rule,device):
        """ return True if a device is a member of ruleset organizers
        """
        deviceOrganizers = set( device.getSystemNames() + device.getDeviceGroupNames())
        allOrgs = rule.ruleset.rulesetSystemOrganizers + rule.ruleset.rulesetGroupOrganizers
        subOrgs = []
        for org in allOrgs:
            for rule in rule.ruleset.rules():
                if rule.ruleKey == 'System' or rule.ruleKey == 'Group':
                    if rule.ruleValue == org:
                        if rule.enabled == False:
                            subOrgs.append(org)
                            
        rulesetOrganizers = set(subOrgs)
        
        return rulesetOrganizers.issubset(deviceOrganizers)

    def findLifeCycle(self,devicename):
        """ Find the lifecycle of a device
        """
        device = self.dmd.Devices.findDeviceByIdOrIp(devicename)
        for g in device.getDeviceGroupNames():
            if re.search(self.cmdbprefs.lifecycleString,g) != None:
                return g
    

