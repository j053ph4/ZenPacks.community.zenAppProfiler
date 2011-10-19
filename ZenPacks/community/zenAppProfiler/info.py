from zope.interface import implements
from Products.Zuul.infos import InfoBase, ConfigProperty, ProxyProperty
from ZenPacks.community.zenAppProfiler.interfaces import ProfileRulesetInfo, ProfileRuleInfo
from Products.Zuul.decorators import info

class ProfileRulesetInfo(InfoBase):
    implements(ProfileRulesetInfo)
    rulesetAlerts = ProxyProperty("rulesetAlerts")
    rulesetGroups = ProxyProperty("rulesetGroups")
    rulesetUsers = ProxyProperty("rulesetUsers")
    rulesetTemplates = ProxyProperty("rulesetTemplates")
    rulesetGroupOrganizers = ProxyProperty("rulesetGroupOrganizers")
    rulesetSystemOrganizers = ProxyProperty("rulesetSystemOrganizers")
    bindTemplates = ProxyProperty("bindTemplates")
    description = ProxyProperty("description")
    matchAll = ProxyProperty("matchAll")

    
class ProfileRuleInfo(InfoBase):
    implements(ProfileRuleInfo)
    ruleSystems = ProxyProperty("ruleSystems")
    ruleGroups = ProxyProperty("ruleGroups")
    ruleKey = ProxyProperty("ruleKey")
    ruleValue = ProxyProperty("ruleValue")
    ruleEventClass = ProxyProperty("ruleEventClass")
    ruleRulesetName = ProxyProperty("ruleRulesetName")
    toRemove = ProxyProperty("toRemove")
    enabled = ProxyProperty("enabled")
    ruleCurrentMatches = ProxyProperty("ruleCurrentMatches")
    rulePotentialMatches = ProxyProperty("rulePotentialMatches")

