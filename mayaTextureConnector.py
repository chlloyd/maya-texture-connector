import maya.cmds as cmds

"""try:
    from arnold import *
    from prman import *
except ImportError:
    cmds.warning("Arnold or Renderman was not found")"""

class mayaTextureConnector(object):
    def __init__(self):
        self.window = 'textureLinker'
        self.title = "Texture Linker"
        self.size = (600, 500)

    def buildUI(self):

        # TODO: Fix UI
        # Check to see if the window is already open
        if cmds.window(self.window, exists = True)==True:
            cmds.deleteUI(self.window, window=True)

        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size, menuBar=True)

        # Cretes a form layout to window
        self.mainForm = cmds.formLayout(numberOfDivisions=100)

        # Creates Renderer Radio Buttons
        cmds.frameLayout(label="Choose a Renderer")
        self.objType = cmds.radioCollection("rendererSelection")
        arnoldSelect = cmds.radioButton(label='Arnold', select=True)
        rendermanSelect = cmds.radioButton(label='Renderman')

        # Adds set texture button button
        self.btnFolderSet = cmds.button(label='Set Texture Folder', height=30, width=150, command=self.setFolderBtn)

        # Adds folder location textfield
        self.txtFieldFolderLocation = cmds.textField(text="D:/Castle Hallway Animation/torch textures") # Set Location")

        # Adds link Texture Button
        self.btnlinkTextures = cmds.button(label='Link Textures', height=30, width=150 , command=self.linkBtn)

        # Remove this when script is finished
        self.btnlinkTextures = cmds.button(label='Create Test Geo', height=30, width=150, command=self.createGeo)

        #Renders the final UI
        cmds.showWindow()


    def createGeo(self, *args): # Only used for testing
        radio = cmds.radioCollection("rendererSelection", query=True, select=True)
        mode = cmds.radioButton(radio, query=True, label=True)
        names = ["cloth", "strap", "torch"]
        for name in names:
            if mode == "Arnold":
                cmds.polySphere(name = name)
                cmds.shadingNode('aiStandardSurface', name=name+"_shader", asShader=True)
                cmds.sets(name=name+"_shaderSG", empty=True, renderable=True, noSurfaceShader=True)
                cmds.connectAttr( name+"_shader.outColor", name+".surfaceShader")
            elif mode == "Renderman":
                cmds.polySphere(name = name)
                cmds.shadingNode('PxrSurface', name=name+"_shader", asShader=True)
                cmds.sets(name=name+"_shaderSG", empty=True, renderable=True, noSurfaceShader=True)
                cmds.connectAttr( name+"_shader.outColor", name+".surfaceShader")
            else:
                pass



    def setFolderBtn(self, *args):
        cmds.fileBrowserDialog(mode=4, fileCommand=self.linkFolder, actionName='Set Folder', operationMode='Reference')

    # Function called when folder is set in set file broser dialogue
    def linkFolder(self, fileName, fileType):
        cmds.textField(self.txtFieldFolderLocation, edit=True, text=fileName)

    def linkBtn(self, *args):

        # Gets Renderer Button Selection
        radio = cmds.radioCollection("rendererSelection", query=True, select=True)
        mode = cmds.radioButton(radio, query=True, label=True)

        # Get Files within selected folder
        basePath = cmds.textField(self.txtFieldFolderLocation, query=True, text=True)
        files = cmds.getFileList(folder=basePath)

        # For each file in folder, get the object name and renderpass
        materialList = []
        renderPassList = []

        # For Loop to fill materialList and renderPassList
        for file in files:
            fileNameSplit = file.split(".")[0].split("_")
            extension = file.split(".")[1]
            material = fileNameSplit[0]
            renderPass = fileNameSplit[-1]
            if material not in materialList:
                materialList.append(material)
            if renderPass not in renderPassList:
                renderPassList.append(renderPass)

        # Checks for the renderer selected
        if mode == "Arnold": # For arnold shaders
            for material in materialList:
                for renderPass in renderPassList:
                    if renderPass == "color": # setting correct settings and linking nodes up for colour
                        fileNode = cmds.shadingNode("file", asTexture=True, name=(material+"_"+renderPass))
                        cmds.setAttr(material+"_"+renderPass+".colorSpace", "sRGB", type = "string")
                        cmds.setAttr(material + "_" + renderPass + ".fileTextureName", basePath+"/"+material+"_shader_"+renderPass+"."+extension, type="string")
                        cmds.connectAttr(material+"_"+renderPass+".outColor", material+"_shader.baseColor", force = True)
                    elif renderPass == "roughness": # setting correct settings and linking nodes up for roughness
                        fileNode = cmds.shadingNode("file", asTexture=True, name=(material + "_" + renderPass))
                        cmds.setAttr(material + "_" + renderPass + ".colorSpace", "Raw", type="string")
                        cmds.setAttr(material + "_" + renderPass + ".fileTextureName", basePath+"/"+material+"_shader_"+renderPass+"."+extension, type="string")
                        cmds.setAttr(material + "_" + renderPass + ".alphaIsLuminance", True)
                        cmds.connectAttr(material + "_" + renderPass + ".outAlpha", material + "_shader.specularRoughness", force=True)
                    elif renderPass == "metalness": # setting correct settings and linking nodes up for metalness
                        fileNode = cmds.shadingNode("file", asTexture=True, name=(material + "_" + renderPass))
                        cmds.setAttr(material + "_" + renderPass + ".colorSpace", "Raw", type="string")
                        cmds.setAttr(material + "_" + renderPass + ".fileTextureName", basePath+"/"+material+"_shader_"+renderPass+"."+extension, type="string")
                        cmds.setAttr(material + "_" + renderPass + ".alphaIsLuminance", True)
                        cmds.connectAttr(material + "_" + renderPass + ".outAlpha", material + "_shader.metalness", force=True)
                    elif renderPass == "normal": # setting correct settings and linking nodes up for normal map
                        fileNode = cmds.shadingNode("file", asTexture=True, name=(material + "_" + renderPass))
                        cmds.setAttr(material + "_" + renderPass + ".colorSpace", "Raw", type="string")
                        cmds.setAttr(material + "_" + renderPass + ".fileTextureName", basePath + "/" + material + "_shader_" + renderPass + "." + extension, type="string")
                        bump2d = cmds.shadingNode("bump2d", asTexture=True, name=material + "_bump2d")
                        cmds.setAttr(material + "_bump2d.bumpInterp", 1)
                        cmds.connectAttr(material + "_" + renderPass + ".outAlpha", material + "_bump2d.bumpValue", force=True)
                        cmds.connectAttr(material + "_bump2d.outNormal", material + "_shader.normalCamera", force=True)
                    elif renderPass == "height": # setting correct settings and linking nodes up for height/displacement map
                        #TODO:
                        displacementNode = cmds.shadingNode("displacementShader", asTexture=True, name=(material + "_displacement_shader"))
                        fileNode = cmds.shadingNode("file", asTexture=True, name=(material + "_" + renderPass))
                        cmds.connectAttr(material + "_" + renderPass + ".outAlpha", material + "_displacement_shader.displacement", force=True)
                        cmds.connectAttr(material + "_displacement_shader.displacement", material + "_shaderSG.displacementShader", force=True)
                    else:
                        pass
        elif mode == "Renderman":
            for material in materialList:
                for renderPass in renderPassList:
                    if renderPass == "color": # setting correct settings and linking nodes up for colour
                        fileNode = cmds.shadingNode("file", asTexture=True, name=(material+"_"+renderPass))
                        cmds.setAttr(material+"_"+renderPass+".colorSpace", "sRGB", type = "string")
                        cmds.setAttr(material + "_" + renderPass + ".fileTextureName", basePath+"/"+material+"_shader_"+renderPass+"."+extension, type="string")
                        cmds.connectAttr(material+"_"+renderPass+".outColor", material+"_shader.diffuseColor", force = True)
                    elif renderPass == "specular": # setting correct settings and linking nodes up for specular
                        fileNode = cmds.shadingNode("file", asTexture=True, name=(material + "_" + renderPass))
                        cmds.setAttr(material + "_" + renderPass + ".colorSpace", "sRGB", type="string")
                        cmds.setAttr(material + "_" + renderPass + ".fileTextureName", basePath+"/"+material+"_shader_"+renderPass+"."+extension, type="string")
                        cmds.connectAttr(material + "_" + renderPass + ".outColor", material + "_shader.specularRoughness", force=True)
                        cmds.connectAttr(material + "_" + renderPass + ".outColor", material + "_shader.specularEdgeColor", force=True)
                    elif renderPass == "roughness": # setting correct settings and linking nodes up for roughness
                        fileNode = cmds.shadingNode("file", asTexture=True, name=(material + "_" + renderPass))
                        cmds.setAttr(material + "_" + renderPass + ".colorSpace", "Raw", type="string")
                        cmds.setAttr(material + "_" + renderPass + ".fileTextureName", basePath+"/"+material+"_shader_"+renderPass+"."+extension, type="string")
                        cmds.setAttr(material + "_" + renderPass + ".alphaIsLuminance", True)
                        cmds.connectAttr(material + "_" + renderPass + ".outAlpha", material + "_shader.diffuseRoughness", force=True)
                    elif renderPass == "normal": # setting correct settings and linking nodes up for normal map
                        fileNode = cmds.shadingNode("file", asTexture=True, name=(material + "_" + renderPass))
                        cmds.setAttr(material + "_" + renderPass + ".colorSpace", "Raw", type="string")
                        cmds.setAttr(material + "_" + renderPass + ".fileTextureName", basePath + "/" + material + "_shader_" + renderPass + "." + extension, type="string")
                        pxrNormalMap = cmds.shadingNode("PxrNormalMap", asTexture=True, name=g+"_PxrNormalMap")
                        cmds.setAttr(material + "_PxrNormalMap.orientation", 0)
                        cmds.connectAttr(material + "_" + renderPass + ".outColor", material + "_PxrNormalMap.inputRGB", force=True)
                        cmds.connectAttr(material + "_PxrNormalMap.resultN", material + "_shader.bumpNormal", force=True)
                    elif renderPass == "height": # setting correct settings and linking nodes up for height/displacement map
                        # displacementNode = cmds.shadingNode("displacementShader", asTexture=True, name=(material + "_displacement_shader"))
                        # fileNode = cmds.shadingNode("file", asTexture=True, name=(material + "_" + renderPass))
                        # cmds.connectAttr(material + "_" + renderPass + ".outAlpha", material + "_displacement_shader.displacement", force=True)
                        # cmds.connectAttr(material + "_displacement_shader.displacement", material + "_shaderSG.displacementShader", force=True)
                        print(1)
                    else:
                        pass

linkTexture = mayaTextureConnector()
linkTexture.buildUI()


"""
References
https://download.autodesk.com/us/maya/2010help/CommandsPython/
http://help.autodesk.com/view/MAYAUL/2018/ENU/?guid=__CommandsPython_index_html
https://support.allegorithmic.com/documentation/integrations/arnold-5-for-maya-157352171.html
https://support.allegorithmic.com/documentation/integrations/renderman-for-maya-162005078.html
https://forums.cgsociety.org/t/is-it-possible-to-change-color-space-in-file-node/1814100      - for change file node settings
"""

# TODO: Add subdirectory search for sourceimage folder
# TODO: Replace fileBrowserDialog with fileDialog or fileDialog2
# TODO: Creates Shader Nodes if they don't exsit
# TODO: Limit Radio Buttons if one renderer isn't avaliable