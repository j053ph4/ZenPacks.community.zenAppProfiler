from Products.Zuul.interfaces import ITreeNode
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t
#from Products.Zuul.info import IInfo

class ProfileRulesetInfo(ITreeNode):
    """
    Info adapter for ProfileRuleset components.
    """
    rulesetAlerts = schema.List(title=u"Alerts")
    rulesetGroups = schema.List(title=u"Groups")
    rulesetUsers = schema.List(title=u"Contacts")
    rulesetTemplates = schema.List(title=u"Ruleset Templates")
    rulesetGroupOrganizers = schema.List(title=u"Group Organizers")
    rulesetSystemOrganizers = schema.List(title=u"System Organizers")
    description = schema.Text(title=u"Description")
    bindTemplates = schema.Bool(title=u"Bind Templates")
    matchAll = schema.Bool(title=u"Match All")
    

class ProfileRuleInfo(ITreeNode):
    """
    Info adapter for ProfileRule components.
    """
    ruleSystems = schema.List(title=u"System Organizers")
    ruleGroups = schema.List(title=u"Group Organizers")
    ruleKey = schema.Text(title=u"Key")
    ruleValue = schema.Text(title=u"Value")
    ruleRulesetName = schema.Text(title=u"Rule Name")
    ruleEventClass = schema.Text(title=u"Rule EventClass")
    toRemove = schema.Bool(title=u"Remove Nonmatches")
    enabled = schema.Bool(title=u"Enabled")
    ruleCurrentMatches = schema.List(title=u"Current Matches")
    rulePotentialMatches = schema.List(title=u"Potential Matches")
