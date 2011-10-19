import re
import os
import string
import Globals
from Products.ZenModel.ZenPackable import ZenPackable
from ProfileData import ProfileData

class ProfileSets(ZenPackable):
    '''  Class containing logic for evaluating rule outcomes.
    '''
    
    def __init__(self,dmd):
        self.dmd = dmd
        self.data = ProfileData(self.dmd)

    def evalSets(self,sets,matchAll):
        """  compute union or intersection of a set of sets
            matchAll of True == intersection, union otherwise
        """
        resultSet = None
        for i in range(len(sets)):
            setI = sets[i]
            if resultSet == None:
                resultSet = setI
            for j in range(i):
                setJ = sets[j]
                if matchAll == True:
                    matchSet = setI.intersection(setJ)
                    resultSet = resultSet.intersection(matchSet)
                else:
                    matchSet = setI.union(setJ)
                    resultSet = resultSet.union(matchSet)
        return resultSet
    
    def evalRulesets(self,rulesets,matchAll):
        """  evaluate multiple rulesets
        """
        sets = []
        for ruleset in rulesets:
            rset = self.evalRuleset(ruleset)
            sets.append(rset)
        return self.evalSets(sets,matchAll)
    
    def evalRuleset(self,ruleset,easy=False):
        """  evaluate all rules in a ruleset, return set of matching devices
        """
        sets = [] # array containing sets of rule-matched devices
        if ruleset != None:
            rules = ruleset.rules()
            for rule in rules:
                results = []
                if rule.enabled == True:
                    if easy == True:
                        results = self.evalRuleSimple(rule)
                    else:
                        results = self.evalRule(rule)
                    #if len(results) > 0:
                    sets.append(results)
        if len(sets) > 0:
            return self.evalSets(sets,ruleset.matchAll)
        else:
            "returning sets"
            return sets
    
    def evalRuleSimple(self,rule):
        """ faster testing assuming that matches are already built
        """
        ruleMatches = []
        
#        if rule.ruleKey == 'Ruleset':
#        /    ruleSet = self.dmd.Profiles.findRuleset(rule.ruleValue)
#            ruleMatches += 
#            return self.evalRuleset(ruleSet,easy=True)
#        else:
        ruleMatches += rule.getRulePotentialMatches() 
        ruleMatches += rule.getRuleCurrentMatches()
        return set(ruleMatches)

    def evalRule(self,rule):
        """ evaluate a rule, return set of matching devices
        """
        if rule.ruleKey == 'Ruleset':
            ruleSet = self.dmd.Profiles.findRuleset(rule.ruleValue)
            return self.evalRuleset(ruleSet,easy=True)
        ruleMatches = set()
        for device in self.dmd.Devices.getSubDevices():
            if self.data.evalRuleOnDevice(rule,device) == True:
                ruleMatches.add(device)
        return ruleMatches

    def evalRuleComponents(self,rule,devices,getAll=True):
        """ evaluate a rule, return set of matching devices
        """
        components = []
        if rule.ruleKey != 'System' and rule.ruleKey != 'Group' and rule.ruleKey != 'Ruleset':
            for device in devices:
                components += self.data.evalRuleWithObjects(rule,device)
        if rule.ruleKey == 'Ruleset':
            rs = self.dmd.Profiles.findRuleset(rule.ruleValue)
            if getAll == True:
                components += self.getRulesetComponents(rs,devices)
            else:
                components += self.getRulesetFilteredComponents(rs,devices)
        #print "found",len(components),"components on rule",rule.ruleKey,rule.ruleValue,"for",len(devices),"devices"
        rule.ruleComponents = components
        return components
    
    def getRulesetComponents(self,ruleset,devices):
        print "components on ruleset",ruleset.id,"for",len(devices),"devices"
        components = []
        for rule in ruleset.rules():
            if rule.ruleKey != 'System' and rule.ruleKey != 'Group':
                comps = self.evalRuleComponents(rule,devices)
                components += comps
        #print "found",len(components),"components"
        return components
    
    def getRulesetFilteredComponents(self,ruleset,devices):
        #print "components on ruleset",ruleset.id,"for",len(devices),"devices"
        componentsets = []
        for rule in ruleset.rules():
            if rule.ruleKey != 'System' and rule.ruleKey != 'Group':
                comps = self.evalRuleComponents(rule,devices,False)
                componentsets.append(set(comps))
        rulesetcomponents = self.evalSets(componentsets,ruleset.matchAll)
        #print "set of rs components",len(rulesetcomponents)
        if rulesetcomponents != None:
            return rulesetcomponents
        else:
            return []
