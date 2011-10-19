import Globals
from zope.interface import implements
from Products.ZenModel.ZenModelRM import ZenModelRM
from Products.ZenModel.ZenPackable import ZenPackable
from Products.ZenModel.interfaces import IIndexed
from Products.ZenRelations.RelSchema import *
from AccessControl import Permissions
from Products.ZenModel.ZenossSecurity import *
from ProfileRuleset import ProfileRuleset
from ProfileData import ProfileData
from ProfileSets import ProfileSets
import re


class ProfileRule(ZenModelRM, ZenPackable):
    """ Class ProfileRule defines the rule and
        its properties
    """
    implements(IIndexed)
    default_catalog = 'profileSearch'

    ruleSystems = []
    ruleGroups = []
    ruleKey = ""
    ruleValue = ""
    ruleRulesetName = ""
    ruleEventClass = ""
    toRemove = False
    enabled = False
    ruleCurrentMatches = []
    rulePotentialMatches = []
    ruleComponents = []

    _properties = (
        {'id':'ruleSystems', 'type':'lines', 'mode':'w'},
        {'id':'ruleGroups', 'type':'lines', 'mode':'w'},
        {'id':'ruleKey', 'type':'string', 'mode':'w',},
        {'id':'ruleValue', 'type':'string', 'mode':'w'},
        {'id':'ruleRulesetName', 'type':'string', 'mode':'w'},
        {'id':'ruleEventClass', 'type':'string', 'mode':'w'},
        {'id':'toRemove', 'type':'boolean', 'mode':'w'},
        {'id':'enabled', 'type':'boolean', 'mode':'w'},
        {'id':'ruleCurrentMatches', 'type':'lines', 'mode':'w'},
        {'id':'rulePotentialMatches', 'type':'lines', 'mode':'w'},
        {'id':'ruleComponents', 'type':'lines', 'mode':'w'},

    )

    _relations = ZenPackable._relations[:] + (
        ("ruleset", ToOne(ToManyCont, "ZenPacks.community.zenAppProfiler.ProfileRuleset", "rules")),
    )

    factory_type_information = (
        {
            'immediate_view' : 'editProfileRule',
            'actions'        :
            (
                { 'id'            : 'profilerule'
                , 'name'          : 'View Rule'
                , 'action'        : 'viewProfileRule'
                , 'permissions'   : ( 'Manage DMD', )
                },
                { 'id'            : 'edit'
                , 'name'          : 'Edit Rule'
                , 'action'        : 'editProfileRule'
                , 'permissions'   : ( 'Manage DMD', )
                },
            )
         },
        )
    
    def __init__(self, id, title="", **kwargs):
        super(ZenModelRM, self).__init__(id, title)
        atts = self.propertyIds()
        for key, val in kwargs.items():
            if key in atts: setattr(self, key, val)

    def getRulePotentialMatches(self):
        """ find potential matches for this rule:
        """
        data = ProfileData(self.dmd)
        return data.getDeviceObjects(self.rulePotentialMatches)
    
    def getRuleCurrentMatches(self):
        """ find current rule matches that are 
            already members of groups
        """
        data = ProfileData(self.dmd)
        return data.getDeviceObjects(self.ruleCurrentMatches)

    def setRuleMatches(self):
        """ find potential matches for this rule:
            potential matches match the rule, but are not members of all 
            rule organizers
        """
        self.rulePotentialMatches = []
        self.ruleCurrentMatches = []
        setmgr = ProfileSets(self.dmd)
        data = ProfileData(self.dmd)
        devices = setmgr.evalRule(self)
        if devices:
            data.setRuleMembers(self,devices)
        else:
            self.rulePotentialMatches = []
            self.ruleCurrentMatches = [] 
        #setmgr.evalRuleComponents(self)
        
    def setRuleComponents(self):
        """ collect components that match rule
        """
        setmgr = ProfileSets(self.dmd)
        devices = self.ruleset.getCurrentDeviceMatches() + self.ruleset.getPotentialDeviceMatches()
        setmgr.evalRuleComponents(self,devices)

    def setRuleOrganizers(self):
        """ propagate ruleset organizers to rules
        """
        self.ruleGroups = self.ruleset.rulesetGroupOrganizers
        self.ruleSystems = self.ruleset.rulesetSystemOrganizers
    


