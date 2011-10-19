import re
import os
import string
import Globals
from Products.ZenModel.ZenPackable import ZenPackable
from ProfileData import ProfileData

class ProfileEvents(ZenPackable):
    """ Class containing routines for handling 
        event filters
    """
    
    def __init__(self,dmd):
        self.dmd = dmd
        self.data = ProfileData(self.dmd)

    def createRulesetGroup(self,ruleset):
        """ create Group named after this ruleset
            if it doesn't exist
        """
        ruleset.rulesetGroups = []
        if ruleset.id not in self.dmd.ZenUsers.getAllGroupSettingsNames():
            ruleset.dmd.ZenUsers.manage_addGroup(ruleset.id)
        if ruleset.id not in ruleset.rulesetGroups:
            ruleset.rulesetGroups.append(ruleset.id)
            
    def addRulesetUsersToGroups(self,ruleset):
        """ add rulesetUsers to rulesetGroups
        """
        for g in ruleset.rulesetGroups:
            group = self.dmd.ZenUsers.getGroupSettings(g)
            for u in ruleset.rulesetUsers:
                if u not in group.getMemberUserIds():
                    user = self.dmd.ZenUsers.getUserSettings(u)
                    group.manage_addUsersToGroup([user.id])
        
    def setRulesetAdminGroups(self,ruleset):
        """ build Add rulesetGroups to Administrative
            Roles on Group/System Organizers
        """
        for rulesetGroup in ruleset.rulesetGroups:
            usergroup = self.dmd.ZenUsers.getGroupSettings(rulesetGroup)
            for group in ruleset.rulesetGroupOrganizers:
                usergroup.manage_addAdministrativeRole(group,type='group')
                usergroup.manage_editAdministrativeRoles(group,role='ZenManager',level=1)
            for system in ruleset.rulesetSystemOrganizers:
                usergroup.manage_addAdministrativeRole(system,type='system')
                usergroup.manage_editAdministrativeRoles(system,role='ZenManager',level=1)
    
    def createRulesetEventView(self,ruleset):
        """ build the event view object for a ruleset
        """
        eventWhere = self.rulesetWhere(ruleset)
        ruleset.rulesetEventWhere = eventWhere
        for g in ruleset.rulesetGroups:
            groupSettings = self.dmd.ZenUsers.getGroupSettings(g)
            eventViewName = g + '-eventview-' + ruleset.id
            ids = []
            for eventView in groupSettings.objectValues(spec='CustomEventView'):
                ids.append(eventView.id)
            if eventViewName not in ids:
                groupSettings.manage_addCustomEventView(eventViewName)
            for eventView in groupSettings.objectValues(spec='CustomEventView'):
                if eventView.id == eventViewName:
                    eventView.where = eventWhere

    def createRulesetAlert(self,ruleset):
        """ build the alert object for a ruleset
        """
        eventWhere = self.rulesetWhere(ruleset)
        for g in ruleset.rulesetGroups:
            alertName = g + '-ruleset-'+ruleset.id
            groupSettings = self.dmd.ZenUsers.getGroupSettings(g)
            ids = []
            for alert in groupSettings.getActionRules():
                ids.append(alert.id)
            if alertName not in ids:
                groupSettings.manage_addActionRule(alertName)
            for alert in groupSettings.getActionRules():
                if alert.id == alertName:
                    alert.enabled = True
                    alert.where = ruleset.rulesetAlertWhere
                    alert.where += ' and ' + eventWhere
                    alert.clearFormat = alert.clearFormat.replace('[zenoss]',ruleset.id)
                    alert.format = alert.format.replace('[zenoss]',ruleset.id)
            if alertName not in ruleset.rulesetAlerts:
                ruleset.rulesetAlerts.append(alertName)
    
    def rulesetWhere(self,ruleset):
        """ create where statement for ruleset
        """
        # create "AND" conditions to narrow events by org membership
        condition = ''
        orgWheres = []
        for group in ruleset.rulesetGroupOrganizers:
            orgWheres.append(self.groupWhere(group))
        for system in ruleset.rulesetSystemOrganizers:
            orgWheres.append(self.systemWhere(system))
        orgCondition = self.compoundWhere(orgWheres,"and")
        # add "OR" conditions to collect events for each rule
        ruleWheres = []
        for rule in ruleset.rules():
            if rule.enabled == True:
                if rule.ruleKey != 'System' and rule.ruleKey != 'Group':
                    rulewhere = self.ruleWhere(rule)
                    ruleWheres.append(rulewhere)
        ruleCondition = self.compoundWhere(ruleWheres,"or")
        # join organizational and rule-based filters
        if len(orgWheres) > 0 :
            condition += orgCondition
            if len(ruleWheres) > 0:
                condition += ' and ' + ruleCondition
        else:
            if len(ruleWheres) > 0:
                condition += ruleCondition
        return condition
    
    def ruleWhere(self,rule):
        """ create where statement for ruleset
        """
        conditions = []
        if rule.ruleKey in self.data.getAllComponentMetaTypes():
            conditions.append(self.componentWhere(rule.ruleValue))
            if rule.ruleEventClass != None: # if there is an event class associated w/the rule
                conditions.append(self.eventClassWhere(rule.ruleEventClass))
        elif rule.ruleKey == 'Template':
            conditions.append(self.templateWhere(rule))    
        elif rule.ruleKey == 'Ruleset':
            ruleset = self.dmd.Profiles.findRuleset(rule.ruleValue)
            if ruleset != None:
                conditions.append(self.rulesetWhere(ruleset))
        elif rule.ruleKey == 'Location':
            conditions.append(self.locationWhere(rule.ruleValue))   
        elif rule.ruleKey == 'Device':
            conditions.append(self.deviceWhere(rule.ruleValue))
        where = self.compoundWhere(conditions,"and")
        return where
    
    def templateWhere(self,rule):
        """ create where statement for template
        """
        properties = self.findTemplateProperties(rule)
        conditions = []
        where = ''
        for property in properties:
            tConds = []
            eventclass,component = property
            if len(eventclass) > 0:
                tConds.append(self.eventClassWhere(eventclass))
            if len(component) > 0:
                tConds.append(self.componentWhere(component))
            if len(tConds) > 0:
                if len(tConds) == 1:
                    conditions.append(tConds[0])
                else:
                    conditions.append(self.compoundWhere(tConds,"and"))
        if len(conditions) > 0:
            if len(conditions) == 1:
                where = conditions[0]
            else:
                where = self.compoundWhere(conditions,"or")
        return where
    
    def compoundWhere(self,wheres,conjunction):
        """ combine where statements
        """
        condition = '('
        entries = len(wheres)
        for i in range(entries):
            condition += wheres[i]
            if i < entries-1:
                condition += " " + conjunction + " "
        condition += ')'
        return condition 
    
    def systemWhere(self,system):
        """ conditional expression for system organizer
        """
        return '(systems like \'%|' + system + '%\')'
    
    def groupWhere(self,group):
        """ conditional expression for system organizer
        """
        return '(deviceGroups like \'%|' + group + '%\')'
    
    def deviceWhere(self,device):
        """ conditional expression for event device
        """
        return 'device like \'%' + device + '%\''
    
    def locationWhere(self,location):
        """ conditional expression for event device
        """
        return 'location like \'%' + location + '%\''
    
    def componentWhere(self,component):
        """ conditional expression for event component
        """
        return 'component like \'%' + component + '%\''
    
    def eventClassWhere(self,eventclass):
        """ conditional expression for event class
        """
        return 'eventClass like \''+eventclass+'%\''
    
    def findTemplateProperties(self,rule):
        """ find filter-related properties for template alert
        """
        properties = []
        for template in self.dmd.Devices.getAllRRDTemplates():
            if template.id.find(rule.ruleValue) >=0:
                for ds in template.getRRDDataSources():
                    eventclass = ds.eventClass
                    component = ds.component
                    properties.append((eventclass,component))
        return properties
