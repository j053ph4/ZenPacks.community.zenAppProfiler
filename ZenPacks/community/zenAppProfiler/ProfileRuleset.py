from Globals import *
from AccessControl import ClassSecurityInfo
from AccessControl import Permissions
from zope.interface import implements
from Products.ZenRelations.RelSchema import *
from Products.ZenWidgets import messaging
from Products.ZenModel.interfaces import IIndexed
from Products.ZenModel.ZenossSecurity import *
from Products.ZenModel.ZenModelRM import ZenModelRM
from Products.ZenModel.ZenPackable import ZenPackable
from ProfileData import ProfileData
from ProfileSets import ProfileSets
from ProfileModify import ProfileModify

class ProfileRuleset(ZenModelRM, ZenPackable):
    """ Class ProfileRuleset is a container for a set of rules
    """
    implements(IIndexed)
    rulesetAlerts = []
    rulesetGroups = []
    rulesetUsers = []
    rulesetTemplates = []
    rulesetGroupOrganizers = []
    rulesetSystemOrganizers = []
    rulesetAlertWhere = "severity >= 3 and eventState = 0"
    rulesetEventWhere = ""
    description = ""
    matchAll = False
    bindTemplates = False
    _properties = (
        {'id':'rulesetGroups', 'type':'lines', 'mode':'w'},
        {'id':'rulesetUsers', 'type':'lines', 'mode':'w'},
        {'id':'rulesetAlerts', 'type':'lines', 'mode':'w'},
        {'id':'rulesetGroupOrganizers', 'type':'lines', 'mode':'w'},
        {'id':'rulesetSystemOrganizers', 'type':'lines', 'mode':'w'},
        {'id':'rulesetAlertWhere', 'type':'string', 'mode':'w'},
        {'id':'rulesetEventWhere', 'type':'string', 'mode':'w'},
        {'id':'rulesetTemplates', 'type':'lines', 'mode':'w'},
        {'id':'description', 'type':'string', 'mode':'w'},
        {'id':'matchAll', 'type':'boolean', 'mode':'w'},
        {'id':'bindTemplates', 'type':'boolean', 'mode':'w'},
    )

    _relations = ZenPackable._relations + (
        ("ruleorganizer", ToOne(ToManyCont, "ZenPacks.community.zenAppProfiler.ProfileOrganizer", "rulesets")),
        ("rules", ToManyCont(ToOne, "ZenPacks.community.zenAppProfiler.ProfileRule", "ruleset")),
    )

    factory_type_information = (
        {
            'immediate_view' : 'viewProfileRuleset',
            'actions'        :
            (
                { 'id'            : 'profileorganizer'
                , 'name'          : 'Profiles'
                , 'action'        : '../viewProfileOrganizer'
                , 'permissions'   : ('View',)
                },
                { 'id'            : 'profileruleset'
                , 'name'          : 'View Ruleset'
                , 'action'        : 'viewProfileRuleset'
                , 'permissions'   : ('View',)
                },
                { 'id'            : 'edit'
                , 'name'          : 'Edit Ruleset'
                , 'action'        : 'editProfileRuleset'
                , 'permissions'   : ( 'Manage DMD', )
                },
            )
         },
        )

    security = ClassSecurityInfo()

    def ruleCount(self):
        """ return number of rules
        """
        count = len(self.rules())
        return count
    
    def currentCount(self):
        """ return number of current matches
        """
        count = 0
        matches = self.getCurrentDeviceMatches()
        if matches != None:
            count = len(matches)
        return count
    
    def potentialCount(self):
        """ return number of potential matches
        """
        count = 0
        matches = self.getPotentialDeviceMatches()
        if matches != None:
            count = len(matches)
        return count
        
    def getRules(self):
        """ update and return rules objects
        """
        self.updateRuleset()
        return self.rules()
 
    def getRuleTypes(self):
        """ return list of supported rule types
        """
        setData = ProfileData(self.dmd)
        ruletypes = setData.getAllComponentMetaTypes()
        ruletypes.sort()
        ruletypes.append('Template')
        ruletypes.append('Ruleset')
        ruletypes.append('System')
        ruletypes.append('Group')
        ruletypes.append('Device')
        ruletypes.append('Location')
        return ruletypes

    def getCurrentDeviceMatches(self):
        """ return list of current member devices 
            complying with any or all rules  in the set
        """
        setMgr = ProfileSets(self.dmd)
        setData = ProfileData(self.dmd)
        sets = []
        for rule in self.rules(): 
            if rule.enabled == True:
                dset = set(rule.ruleCurrentMatches)
                sets.append(dset)
        devices = setMgr.evalSets(sets,self.matchAll)
        return setData.getDeviceObjects(devices)

    def getPotentialDeviceMatches(self):
        """ return list of potential member devices 
            complying with any or all rules in a set
        """
        setMgr = ProfileSets(self.dmd)
        setData = ProfileData(self.dmd)
        sets = []
        for rule in self.rules(): 
            if rule.enabled == True:
                dset = set(rule.rulePotentialMatches)
                sets.append(dset)
        devices = setMgr.evalSets(sets,self.matchAll)
        return setData.getDeviceObjects(devices)

    def updateMatches(self):
        """ recalculate matches for each rule
        """
        for rule in self.rules():
            rule.setRuleMatches()
    
    def getRulesetGroupSettings(self):
        """ return Group objects for this rule set
        """
        groupSettings = []
        for m in self.rulesetGroups:
            settings = self.dmd.ZenUsers.getGroupSettings(m)
            if settings not in groupSettings:
                groupSettings.append(settings)
        return groupSettings
    
    def getRulesetAlertSettings(self):
        """ return alert objects for this rule set's groups
        """
        alertSettings = []
        for group in self.getRulesetGroupSettings():
            alerts = group.getActionRules()
            for alert in alerts:
                for rulesetAlert in self.rulesetAlerts:
                    if alert.id == rulesetAlert:
                        alertSettings.append(alert)    
        return alertSettings

    def getRemovableDeviceMatches(self):
        """ find devices that no longer match a given ruleset
            
        """
        currentMatches = set()
        for rule in self.rules():
            for d in rule.ruleCurrentMatches:
                if d not in currentMatches:
                    currentMatches.add(d)
        #currentMatches = set(self.getCurrentDeviceMatches())
        self.updateMatches()
        removableMatches = set(self.getCurrentDeviceMatches())
        formerMatches = currentMatches.difference(removableMatches)
        setData = ProfileData(self.dmd)
        return setData.getDeviceObjects(formerMatches)

    def updateRuleset(self):
        """    update rules
        """
        self.updateTemplateRules()
        self.updateOrganizerRules('Group',self.rulesetGroupOrganizers)
        self.updateOrganizerRules('System',self.rulesetSystemOrganizers)
        for rule in self.rules():
            rule.setRuleOrganizers()
            
    def updateRuleComponents(self):
        """ set a list of matching components across all rules
        """
        for rule in self.rules():
            rule.setRuleComponents()
            
    def updateRulesetUserGroups(self):
        """    update users,groups, alerts, etc
        """
        from ProfileEvents import ProfileEvents
        evt = ProfileEvents(self.dmd)
        evt.createRulesetGroup(self)
        evt.addRulesetUsersToGroups(self)
        evt.setRulesetAdminGroups(self)
        evt.createRulesetAlert(self)
        evt.createRulesetEventView(self)
        self.addFactoryEvents()
        
    def updateTemplateRules(self):
        """ update rules based on selected templates
        """
        templateRules = []
        for rule in self.rules():
            if rule.ruleKey == 'Template':
                templateRules.append(rule.ruleValue)
        for modTemplate in self.rulesetTemplates:
            if modTemplate not in templateRules:
                ruleid = 'Template-'+modTemplate
                rule = self.createRule(ruleid)
                rule.ruleKey = 'Template'
                rule.ruleValue = modTemplate
        for rule in self.rules():
            if rule.ruleKey == 'Template':
                if rule.ruleValue not in self.rulesetTemplates:
                    self.deleteRules([rule.id])

    def updateOrganizerRules(self,orgType,orgMembers):
        """ create rules based on selected organizers
        """
        for org in orgMembers:
            create = True
            for rule in self.rules():
                if rule.ruleKey == orgType:
                    if rule.ruleValue == org:
                        create = False
            if create == True:
                ruleid = org.replace('/','-')[1:]
                rule = self.createRule(ruleid)
                rule.ruleKey = orgType
                rule.ruleValue = org
                rule.toRemove = False
                rule.enabled = False
                
        for rule in self.rules():
            if rule.ruleKey == orgType:
                if rule.ruleValue not in orgMembers:
                    self.deleteRules([rule.id])
                    
    def applyRules(self,undo):
        """ (un)apply rules in ruleset
        """
        mod = ProfileModify(self.dmd)
        
        if undo == False: 
            self.updateMatches()
            devices = self.getPotentialDeviceMatches()
        else:
            devices = self.getRemovableDeviceMatches()
        
        for device in devices:
            mod.initDevice(device)
            mod.modifyMemberships(self,undo)
            if self.bindTemplates == True:
                mod.modifyTemplateBindings(self,undo)
        self.updateMatches()
        return devices
  
    def addFactoryEvents(self):
        """ add events tab to ruleset page
        """
        finfo = self.factory_type_information
        actions = list(finfo[0]['actions'])
        actionpath = '/dmd/ZenUsers/'+self.id+'/'+self.id +'-eventview-'+self.id+'/viewEvents'
        actionTab = { 'id'            : 'events'
                , 'name'          : 'Events'
                , 'action'        : actionpath
                , 'permissions'   : ('View',)
                }
        for a in actions:
            flag = False
            if a['name'] == 'Events':
                a['action'] = actionpath
                flag = True
        if flag == False:
            actions.append(actionTab)
        finfo[0]['actions'] = tuple(actions)
        self.factory_type_information = finfo

    def createRule(self, id, enabled=True, \
                   toRemove=False, ruleKey='IpService', \
                   ruleValue='',ruleEventClass=''):
        """ Create a Rule
        """
        from ProfileRule import ProfileRule
        rule = ProfileRule(id)
        self.rules._setObject(rule.id, rule)
        rule = self.rules._getOb(rule.id)
        rule.ruleRulesetName = id
        rule.ruleGroups = self.rulesetGroupOrganizers
        rule.ruleSystems = self.rulesetSystemOrganizers
        rule.enabled = enabled
        rule.toRemove = toRemove
        rule.ruleKey = ruleKey
        rule.ruleValue = ruleValue
        rule.ruleEventClass = ruleEventClass
        return rule
    
    def addRule(self, id, enabled=True, \
                toRemove=False, ruleKey='IpService', \
                ruleValue='', ruleEventClass='',REQUEST=None):
        """ Add a Rule
        """
        self.createRule(id, enabled, toRemove, ruleKey, ruleValue, ruleEventClass)
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(
                'Rule Created',
                'Rule %s was created.' % id
            )
            return self.callZenScreen(REQUEST)
        else:
            return self.rules._getOb(id)
        
    def deleteRules(self, ids=[], REQUEST=None):
        """ Delete selected rules
        """
        for rule in self.rules():
            id = getattr(rule, 'id', None)
            if id in ids:
                self.rules._delObject(id)
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(
                'Rules Deleted',
                'Rules deleted: %s' % (', '.join(ids))
            )
            return self.callZenScreen(REQUEST)
        
    def manage_runMatches(self, REQUEST=None):
        """ build alert definitions based on rules
        """
        self.updateMatches()
        message = 'Matches updated'
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(message,message)
            return self.callZenScreen(REQUEST)
        
    def manage_buildAlerts(self, REQUEST=None):
        """ build alert definitions based on rules
        """
        self.updateRulesetUserGroups()
        message = 'Alerts built for user groups: %s'   % ', '.join(self.rulesetGroups)
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(message,message)
            return self.callZenScreen(REQUEST)

    def manage_runRuleset(self, REQUEST=None):
        """ manage memberships and template bindings
        """
        data = ProfileData(self.dmd)
        rmvs = self.applyRules(True)
        adds = self.applyRules(False)
        message = 'No changes were made'
        if len(rmvs) > 0 or len(adds) > 0:
            message = ''
            if len(rmvs) > 0:
                message += 'Ruleset unapplied to %s' % ', '.join(data.getDeviceNames(rmvs))
            if len(adds) > 0:
                message += ' Ruleset applied to %s' % ', '.join(data.getDeviceNames(adds))
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(message,message)
            return self.callZenScreen(REQUEST)
    
InitializeClass(ProfileRuleset)
