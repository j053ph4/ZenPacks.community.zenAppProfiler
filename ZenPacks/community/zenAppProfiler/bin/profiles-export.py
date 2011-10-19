#!/usr/bin/env python
import Globals
from optparse import OptionParser
import re
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from transaction import commit

class ProfileExport(ZenScriptBase):
    def __init__(self):
        ZenScriptBase.__init__(self, connect=True)
        self.profiles = self.dmd.Profiles
        self.rulesets = self.profiles.getAllRulesets()
        self.rulesetfile = 'profiles-rulesets-export.txt'
        self.rulefile = 'profiles-rules-export.txt'
        self.exportrulesets = []
        self.exportrules = []
        
    def run(self):
        print "running export"
        self.getRulesets()
        self.getRules()
        self.writeData()
        
    def getRulesets(self):
        """ retrieve all rulesets and write them to the file
        """
        print "exporting rulesets"
        output = []
        for r in self.rulesets:
            rsdict = {}
            rsdict['id'] = r.id
            rsdict['rulesetGroups'] = r.rulesetGroups
            rsdict['rulesetUsers'] = r.rulesetUsers  
            rsdict['rulesetTemplates'] = r.rulesetTemplates
            rsdict['rulesetGroupOrganizers'] = r.rulesetGroupOrganizers
            rsdict['rulesetSystemOrganizers'] = r.rulesetSystemOrganizers
            rsdict['rulesetAlertWhere'] = r.rulesetAlertWhere
            rsdict['rulesetEventWhere'] = r.rulesetEventWhere
            rsdict['description'] = r.description
            rsdict['matchAll'] = r.matchAll
            rsdict['bindTemplates'] = r.bindTemplates
            self.exportrulesets.append(rsdict)
        print "found",len(self.exportrulesets),"rulesets"
        
    def getRules(self):
        """ retrieve all rules and write them to the file
        """
        print "exporting rules"
        for rs in self.rulesets:
            rules = rs.rules()
            for r in rules:
                rdict = {}
                rdict['id'] = r.id
                rdict['ruleset'] = rs.id
                rdict['ruleSystems'] = r.ruleSystems
                rdict['ruleGroups'] = r.ruleGroups
                rdict['ruleKey'] = r.ruleKey
                rdict['ruleValue'] = r.ruleValue
                rdict['ruleRulesetName'] = r.ruleRulesetName
                rdict['ruleEventClass'] = r.ruleEventClass
                rdict['toRemove'] = r.toRemove
                rdict['enabled'] = r.enabled
                self.exportrules.append(rdict)
                
        print "found",len(self.exportrules),"rules"
            
    def writeData(self):
        print "writing export to file"
        rsfile = open(self.rulesetfile, 'a')
        rfile = open(self.rulefile, 'a')
        for rs in self.exportrulesets:
            value = str(rs)+'\n'
            rsfile.write(value)
        for r in self.exportrules:
            value = str(r)+'\n'
            rfile.write(value)
        rsfile.close()
        rfile.close()
        print "complete"
        
        
if __name__ == "__main__":
    u = ProfileExport()
    u.run()     
