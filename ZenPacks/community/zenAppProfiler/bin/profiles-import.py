#!/usr/bin/env python
import Globals
from optparse import OptionParser
import re
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from transaction import commit

class ProfileImport(ZenScriptBase):
    def __init__(self):
        ZenScriptBase.__init__(self, connect=True)
        self.profiles = self.dmd.Profiles
        self.rulesets = self.profiles.getAllRulesets()
        self.rulesetfile = 'profiles-rulesets-export.txt'
        self.rulefile = 'profiles-rules-export.txt'
        
    def run(self):
        self.readData()
        
    def readData(self):
        rsfile = open(self.rulesetfile, 'r')
        rfile = open(self.rulefile, 'r')

        for line in rsfile.readlines():
            rs = eval(line)
            print "RS",rs['id']
            self.profiles.createProfileRuleset(rs['id'], description=rs['description'],  \
                                matchAll=rs['matchAll'], bindTemplates=rs['bindTemplates'], \
                                rulesetUsers=rs['rulesetUsers'], rulesetGroups=rs['rulesetGroups'], \
                                rulesetTemplates=rs['rulesetTemplates'], \
                                rulesetGroupOrganizers=rs['rulesetGroupOrganizers'], \
                                rulesetSystemOrganizers=rs['rulesetSystemOrganizers'])
            
        for line in rfile.readlines():
            r = eval(line)
            ruleset = self.profiles.findRuleset(r['ruleset'])
            ruleset.createRule(r['id'], enabled=r['enabled'], \
                   toRemove=r['toRemove'], ruleKey=r['ruleKey'], \
                   ruleValue=r['ruleValue'],ruleEventClass=r['ruleEventClass'])

if __name__ == "__main__":
    u = ProfileImport()
    u.run()     
