import maya.cmds as mc
import maya.mel as mel
import ConfigParser


cfg = caseSensIni()
cfg.read(r"D:\Code\autoRenderLayer.ini") #ini location


class caseSensIni(ConfigParser.ConfigParser):
    #set ConfigParser options for case sensitive.
    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=defaults)
    def optionxform(self, optionstr):
        return optionstr


def getSGfromShader(shader=None):
    if shader:
        if mc.objExists(shader):
            sgq = mc.listConnections(shader, d=True, et=True, t='shadingEngine')
            if sgq:
                return sgq[0]
    return None


def assignObjListToShader(objList=None, shader=None):
    shaderSG = getSGfromShader(shader)
    if objList:
        if shaderSG:
            mc.sets(objList, e=True, forceElement=shaderSG)
        else:
            mc.warning('Shader Error: '+shader)


layerList = cfg.get('-rndrLayer_to_add', 'rndrLayer').split(',')
for aov in cfg.options('-AovSetting'):
	mc.rsCreateAov(type=aov)
	rename = cfg.get('-AovSetting', aov)
	if rename:
		mc.setAttr('rsAov_'+aov+'.name', rename,type="string")
mel.eval("redshiftUpdateActiveAovList()")
for layer in layerList:
    sectionObj = layer+'_object'
    sectionMat = layer+'_material'
    sectionOvr = layer+'_override'
    if not (cfg.has_section(sectionObj) and cfg.has_option(sectionObj, 'selectAll')):
    	continue
    #add members
    if cfg.getboolean(sectionObj, 'selectAll'):
        mc.createRenderLayer(name=layer,g=True,mc=True)
        for option in cfg.options(sectionObj):
            if not (cfg.get(sectionObj, option) and option.startswith('excludeObj')):
                continue
            for i in cfg.get(sectionObj, option).split(','):
                mc.editRenderLayerMembers(layer, i, remove=True)
    else:
    	mc.createRenderLayer(name=layer,mc=True)
        for option in cfg.options(sectionObj):
            if not (cfg.get(sectionObj, option) and option.startswith('excludeObj')):
                continue
            for i in cfg.get(sectionObj, option).split(','):
                mc.editRenderLayerMembers(layer, i)
    #assign material
    for shader in cfg.options(sectionMat):
    	obj_list = cfg.get(sectionMat, shader).split(',')
    	assignObjListToShader(obj_list, shader)
    #create override
    for ovrAtr in cfg.options(sectionOvr):
    	value = cfg.getfloat(sectionOvr, ovrAtr)
    	mc.editRenderLayerAdjustment(ovrAtr, layer=layer)
    	mc.setAttr(ovrAtr, value)
