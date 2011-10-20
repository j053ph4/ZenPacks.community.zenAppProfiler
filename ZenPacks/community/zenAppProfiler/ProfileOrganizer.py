import types
from Globals import *
from AccessControl import ClassSecurityInfo
from AccessControl import Permissions
from Products.ZenModel.ZenossSecurity import *
from Products.ZenModel.Organizer import Organizer
from Products.ZenRelations.RelSchema import *
from Products.ZenUtils.Search import makeCaseInsensitiveKeywordIndex
from Products.ZenWidgets import messaging
from Products.ZenModel.ZenPackable import ZenPackable
from ProfileData import ProfileData

def manage_addProfileOrganizer(context, id='Profiles', REQUEST = None):
    """make a device class"""
    porg = ProfileOrganizer(id)
    context._setObject(id, porg)
    porg = context._getOb(id)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(context.absolute_url() + '/manage_main')
        
addProfileOrganizer = DTMLFile('dtml/addProfileOrganizer',globals())


class ProfileOrganizer(Organizer, ZenPackable):
    """
    ProfileOrganizer is the base class for rulesets and rules
    """
    meta_type = "ProfileOrganizer"
    dmdRootName = "Profiles"
    default_catalog = 'profileSearch'
    
    security = ClassSecurityInfo()

    _relations = Organizer._relations + ZenPackable._relations + (
        ("rulesets", ToManyCont(ToOne,"ZenPacks.community.zenAppProfiler.ProfileRuleset","ruleorganizer")),
        )

    factory_type_information = (
        {
            'immediate_view' : 'viewProfileOrganizer',
            'actions'        :
            (
                { 'id'            : 'profileorganizer'
                , 'name'          : 'Profiles'
                , 'action'        : 'viewProfileOrganizer'
                , 'permissions'   : ( 'Manage DMD', )
                },
            )
         },
        )

    def __init__(self, id=None):
        if not id: id = self.dmdRootName
        super(ProfileOrganizer, self).__init__(id)
        if self.id == self.dmdRootName:
            self.createCatalog()

    def countClasses(self):
        """ Count all rulesets with in a ProfileOrganizer.
        """
        count = self.rulesets.countObjects()
        for group in self.children():
            count += group.countClasses()
        return count
    
    def getAllTemplates(self):
        """ return list of all unique templates 
        """
        templates = ['']
        for t in self.dmd.Devices.getAllRRDTemplates():
            if t.id not in templates:  templates.append(t.id)
        templates.sort()
        return templates
    
    def getAllUserNames(self):
        """ return list of all user names 
        """
        users = ['']
        for u in self.dmd.ZenUsers.getAllUserSettingsNames():
            if u not in users:  users.append(u)
        return users
    
    def getAllGroupNames(self):
        """ return list of all user group
        """
        groups = []
        for g in self.dmd.ZenUsers.getAllGroupSettingsNames():
            if g not in groups:  groups.append(g)
        return groups
    
    def getAllRulesets(self):
        """ find all rulesets recursively
        """
        data = ProfileData(self.dmd)
        rulesets =  data.getAllRulesets()
        return rulesets
    
    def findRuleset(self,rulesetName):
        """ find a ruleset by name
        """
        rulesets = self.getAllRulesets()
        for ruleset in rulesets:
            if ruleset.id == rulesetName:
                return ruleset
        return None
    
    def setRulesetComponents(self):
        """ set a list of matching components across all rulesets
        """
        for ruleset in self.getAllRulesets():
            ruleset.updated = False
            for rule in ruleset.rules():
                rule.updated = False
        
        for ruleset in self.getAllRulesets():
            #print "examining ruleset",ruleset.id
            if ruleset.updated == False:
                for rule in ruleset.rules():
                    if rule.updated == False:
                        if rule.ruleKey == "Ruleset":
                            rs = self.findRuleset(rule.ruleValue)
                            if rs.updated == False:
                                print "updating ruleset rule",rule.id
                                rule.setRuleComponents()
                                rule.updated = True
                                rs.updated = True
                            else:
                                print "already current",rule.id
                        else:
                            print "updating rule",rule.id
                            rule.setRuleComponents()
                            rule.updated == True
                    else:
                        print "already current",rule.id
            ruleset.updated = True

    def runAllRuleMatches(self):
        """ run recursive rules after normal rules for matches
        """
        rulesets = self.getAllRulesets()
        
        rules = []
        rsrules = []
        for rs in rulesets:
            for r in rs.rules():
                if r.ruleKey == 'Ruleset':
                    rsrules.append(r)
                else:
                    rules.append(r)
        for r in rules:
            r.setRuleMatches()
        for r in rsrules:
            r.setRuleMatches()
        
    def createProfileRuleset(self, id, description="",  \
                                matchAll=False, bindTemplates=False, \
                                rulesetUsers=[], rulesetGroups=[], rulesetTemplates=[], \
                                rulesetGroupOrganizers=[], rulesetSystemOrganizers=[]):
        """ Create a rule set
        """
        from ProfileRuleset import ProfileRuleset
        ruleset = ProfileRuleset(id)
        self.rulesets._setObject(id, ruleset)
        ruleset = self.rulesets._getOb(ruleset.id)
        ruleset.description = description
        ruleset.matchAll = matchAll
        ruleset.bindTemplates = bindTemplates
        ruleset.rulesetUsers = rulesetUsers
        ruleset.rulesetGroups = rulesetGroups
        ruleset.rulesetTemplates = rulesetTemplates
        ruleset.rulesetGroupOrganizers = rulesetGroupOrganizers
        ruleset.rulesetSystemOrganizers = rulesetSystemOrganizers
        ruleset.updateRuleset()
        ruleset.updateRulesetUserGroups()
        return ruleset
    
    def runAllRulesetsOptimized(self):
        """ routine to run all rulesets in an optimal way
        """
        # first get all rulesets and add a property stating whether each has been run yet
        # loop through all rulesets
        # if rs contains pointer to another, move it to end of the list and run the next
        
        
    def manage_runAllMatches(self, REQUEST=None):
        """ build alert definitions based on rules
        """
        self.runAllRuleMatches()
        message = 'All matches updated'
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(message,message)
            return self.callZenScreen(REQUEST)

    def manage_runAllRulesets(self, REQUEST=None):
        """ build current/potential matches
            for devices matching all ruleset rules
        """
        data = ProfileData(self.dmd)
        rmvs = []
        adds = []
        print "building adds and removes sets"
        for ruleset in self.getAllRulesets():
            print "ruleset",ruleset.id
            rmvs.append(set(ruleset.applyRules(True)))
            adds.append(set(ruleset.applyRules(False)))
        print "rebuilding components for all rulesets"
        self.setRulesetComponents()
        from ProfileSets import ProfileSets
        setMgr = ProfileSets(self.dmd)
        rmdevs = setMgr.evalSets(rmvs,False)
        addevs = setMgr.evalSets(adds,False)
        message = 'No changes were made'
        if len(rmdevs) > 0 or len(addevs) > 0:
            message = ''
            if len(rmdevs) > 0:
                message += 'Rulesets unapplied to %s' % ', '.join(data.getDeviceNames(rmdevs))
            if len(addevs) > 0:
                message += ' Rulesets applied to %s' % ', '.join(data.getDeviceNames(addevs))
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(message,message)
            return self.callZenScreen(REQUEST)
        
    def manage_buildAllAlerts(self, REQUEST=None):
        """ manage groups, users, and alerts for all rulesets
        """
        sets = []
        for ruleset in self.getAllRulesets():
            sets.append(ruleset.id)
            ruleset.updateRulesetUserGroups()
        message = 'User Groups, Members, and Alerts modified for rulesets: %s' % ', '.join(sets)
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(message,message)
            return self.callZenScreen(REQUEST)

    def manage_addProfileRuleset(self, id, description="",  \
                                matchAll=False, bindTemplates=False, \
                                rulesetUsers=[], rulesetGroups=[], rulesetTemplates=[], \
                                rulesetGroupOrganizers=[], rulesetSystemOrganizers=[], \
                                REQUEST=None):
        """ Create a new service class in this Organizer.
        """
        self.createProfileRuleset(id,description,matchAll,bindTemplates,rulesetUsers,rulesetGroups,rulesetTemplates,rulesetGroupOrganizers,rulesetSystemOrganizers)
        message = 'Ruleset %s was created.' % id
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(message,message)
            return self.callZenScreen(REQUEST)
        else:
            return self.rulesets._getOb(id)
        
    def removeProfileRulesets(self, ids=None, REQUEST=None):
        """ Remove Profile Rulesets from an EventClass.
        """
        if not ids: return self()
        if type(ids) == types.StringType: ids = (ids,)
        for id in ids:
            self.rulesets._delObject(id)
        message = 'Rulesets deleted: %s' % ', '.join(ids)
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(message,message)
            return self()
        
    def moveProfileRulesets(self, moveTarget, ids=None, REQUEST=None):
        """Move ProfileRulesets from this EventClass to moveTarget.
        """
        if not moveTarget or not ids: return self()
        if type(ids) == types.StringType: ids = (ids,)
        target = self.getChildMoveTarget(moveTarget)
        for id in ids:
            rec = self.rulesets._getOb(id)
            rec._operation = 1 # moving object state
            self.rulesets._delObject(id)
            target.rulesets._setObject(id, rec)
        message = 'Rulesets moved to %s:' % moveTarget
        if REQUEST:
            messaging.IMessageSender(self).sendToBrowser(message,message)
            REQUEST['RESPONSE'].redirect(target.getPrimaryUrlPath())

    def reIndex(self):
        """Go through all devices in this tree and reindex them."""
        zcat = self._getOb(self.default_catalog)
        zcat.manage_catalogClear()
        for org in [self,] + self.getSubOrganizers():
            for ruleset in org.rulesets():
                for thing in ruleset.rules():
                    thing.index_object()

    def createCatalog(self):
        """Create a catalog for rules searching"""
        from Products.ZCatalog.ZCatalog import manage_addZCatalog
        # XXX update to use ManagableIndexcreateRulesetGroup 
        manage_addZCatalog(self, self.default_catalog, self.default_catalog)
        zcat = self._getOb(self.default_catalog)
        cat = zcat._catalog
        cat.addIndex('ruleSystems', makeCaseInsensitiveKeywordIndex('ruleSystems'))
        cat.addIndex('ruleGroups', makeCaseInsensitiveKeywordIndex('ruleGroups'))
        cat.addIndex('ruleKey', makeCaseInsensitiveKeywordIndex('ruleKey'))
        cat.addIndex('ruleValue', makeCaseInsensitiveKeywordIndex('ruleValue'))
        zcat.addColumn('toRemove')
        zcat.addColumn('enabled')
        zcat.addColumn('ruleCurrentMatches')
        zcat.addColumn('rulePotentialMatches')
        zcat.addColumn('ruleRulesetName')
        zcat.addColumn('ruleEventClass')

InitializeClass(ProfileOrganizer)

