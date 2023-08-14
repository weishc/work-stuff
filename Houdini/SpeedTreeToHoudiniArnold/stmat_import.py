import xml.dom.minidom as xmldom
import os


def parsing_stmat(stmatFile):
    stmatFile = os.path.realpath(stmatFile)
    stmatPath = os.path.dirname(stmatFile).replace("\\", "/") + "/"
    doc = xmldom.parse(stmatFile)
    collection = doc.documentElement
    root = doc.getElementsByTagName("Materials")
    filename = root[0].attributes["Mesh"].value.split('.')[0]
    hou.node("/obj").createNode("subnet").setName(filename)
    materials = collection.getElementsByTagName("Material")
    return materials


def create_material(materials):
    for mat in materials:
        matname = mat.attributes["Name"].value
        matnode = hou.node(
            "/obj/"+filename).createNode("wc_arnold_speedtree_mat")
        matnode.setParms({"use_color_map": 0, "use_opacity_map": 0, "use_normal_map": 0,
                          "use_gloss_map": 0, "use_specular_map": 0, "use_ssscolor_map": 0,
                          "use_sssamount_map": 0})
        matnode.setParms({"color_map": "", "opacity": "", "normal_map": "",
                          "gloss_map": "", "specular_map": "", "ssscolor_map": "", "sssamount_map": ""})
        for maptag in mat.getElementsByTagName("Map"):
            if maptag.attributes["Name"].value == ("Color"):
                if maptag.hasAttribute("File"):
                    file = maptag.attributes['File'].value
                    matnode.setParms(
                        {"color_map": stmatPath + file, "use_color_map": 1})
                if maptag.hasAttribute("ColorR"):
                    r = maptag.attributes['ColorR'].value
                    g = maptag.attributes['ColorG'].value
                    b = maptag.attributes['ColorB'].value
                    matnode.setParms({"colorr": r, "colorg": g, "colorb": b, })
            if maptag.attributes["Name"].value == ("Opacity"):
                if maptag.hasAttribute("File"):
                    file = maptag.attributes['File'].value
                    matnode.setParms(
                        {"opacity": stmatPath+file, "use_opacity_map": 1})
            if maptag.attributes["Name"].value == ("Normal"):
                file = maptag.attributes['File'].value
                matnode.setParms(
                    {"normal_map": stmatPath+file, "normal": 1, "use_normal_map": 1})
            if maptag.attributes["Name"].value == ("Gloss"):
                if maptag.hasAttribute("File"):
                    file = maptag.attributes['File'].value
                    matnode.setParms(
                        {"use_gloss_map": 1, "gloss_map": stmatPath+file})
                if maptag.hasAttribute("Value"):
                    value = maptag.attributes['Value'].value
                    matnode.setParms({"gloss": value})
            if maptag.attributes["Name"].value == ("Specular"):
                if maptag.hasAttribute("File"):
                    file = maptag.attributes['File'].value
                    matnode.setParms(
                        {"specular_map": stmatPath+file, "use_specular_map": 1})
                if maptag.hasAttribute("ColorR"):
                    r = maptag.attributes['ColorR'].value
                    g = maptag.attributes['ColorG'].value
                    b = maptag.attributes['ColorB'].value
                    matnode.setParms(
                        {"specularr": r, "specularg": g, "specularb": b, })
            if maptag.attributes["Name"].value == ("SubsurfaceColor"):
                if maptag.hasAttribute("File"):
                    file = maptag.attributes['File'].value
                    matnode.setParms(
                        {"ssscolor_map": stmatPath+file, "use_ssscolor_map": 1})
                if maptag.hasAttribute("ColorR"):
                    r = maptag.attributes['ColorR'].value
                    g = maptag.attributes['ColorG'].value
                    b = maptag.attributes['ColorB'].value
                    matnode.setParms(
                        {"ssscolorr": r, "ssscolorg": g, "ssscolorb": b, })
            if maptag.attributes["Name"].value == ("SubsurfaceAmount"):
                if maptag.hasAttribute("File"):
                    file = maptag.attributes['File'].value
                    matnode.setParms(
                        {"sssamount_map": stmatPath+file, "use_sssamount_map": 1})
                if maptag.hasAttribute("Value"):
                    value = maptag.attributes['Value'].value
                    matnode.setParms({"SSS_scale": 0.001})
        matnode.setName(matname)
    hou.node("/obj/"+filename).layoutChildren()


stmatFile = hou.ui.selectFile(
    title="Select SpeedTree File", file_type=hou.fileType.Any, pattern="*.stmat")
materials = parsing_stmat(stmatFile)
create_material(materials)
