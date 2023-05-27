import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import math

# Modify for script orignally create by Kirill Kovalevskiy
# https://gist.github.com/Kif11/247f6b05e8d3a6c3ffb193b8c6f4dec7
 
class Plane(object):
    def __init__(self, normalisedVector):
        # OpenMaya.MVector.__init__()
        self.vector = normalisedVector
        self.distance = 0.0

    def relativeToPlane(self, point):
        # Converting the point as a vector from the origin to its position
        pointVec = OpenMaya.MVector(point.x, point.y, point.z)
        val = (self.vector * pointVec) + self.distance

        if (val > 0.0):
            return 1  # In front
        elif (val < 0.0):
            return -1  # Behind

        return 0  # On the plane


class Frustum(object):
    def __init__(self, cameraName):
        # Initialising selected transforms into its associated dagPaths
        selectionList = OpenMaya.MSelectionList()
        objDagPath = OpenMaya.MDagPath()
        selectionList.add(cameraName)
        selectionList.getDagPath(0, objDagPath)
        self.camera = OpenMaya.MFnCamera(objDagPath)

        self.nearClip = self.camera.nearClippingPlane()
        self.farClip = self.camera.farClippingPlane()
        self.aspectRatio = self.camera.aspectRatio()

        left_util = OpenMaya.MScriptUtil()
        left_util.createFromDouble(0.0)
        ptr0 = left_util.asDoublePtr()

        right_util = OpenMaya.MScriptUtil()
        right_util.createFromDouble(0.0)
        ptr1 = right_util.asDoublePtr()

        bot_util = OpenMaya.MScriptUtil()
        bot_util.createFromDouble(0.0)
        ptr2 = bot_util.asDoublePtr()

        top_util = OpenMaya.MScriptUtil()
        top_util.createFromDouble(0.0)
        ptr3 = top_util.asDoublePtr()

        stat = self.camera.getViewingFrustum(
            self.aspectRatio, ptr0, ptr1, ptr2, ptr3, False, True
        )

        planes = []

        left = left_util.getDoubleArrayItem(ptr0, 0)
        right = right_util.getDoubleArrayItem(ptr1, 0)
        bottom = bot_util.getDoubleArrayItem(ptr2, 0)
        top = top_util.getDoubleArrayItem(ptr3, 0)

        # planeA = right plane
        a = OpenMaya.MVector(right, top, -self.nearClip)
        b = OpenMaya.MVector(right, bottom, -self.nearClip)
        c = (a ^ b).normal()  # normal of plane = cross product of vectors a and b
        planeA = Plane(c)
        planes.append(planeA)

        # planeB = left plane
        a = OpenMaya.MVector(left, bottom, -self.nearClip)
        b = OpenMaya.MVector(left, top, -self.nearClip)
        c = (a ^ b).normal()
        planeB = Plane(c)
        planes.append(planeB)

        # planeC = bottom plane
        a = OpenMaya.MVector(right, bottom, -self.nearClip)
        b = OpenMaya.MVector(left, bottom, -self.nearClip)
        c = (a ^ b).normal()
        planeC = Plane(c)
        planes.append(planeC)

        # planeD = top plane
        a = OpenMaya.MVector(left, top, -self.nearClip)
        b = OpenMaya.MVector(right, top, -self.nearClip)
        c = (a ^ b).normal()
        planeD = Plane(c)
        planes.append(planeD)

        # planeE = far plane
        c = OpenMaya.MVector(0, 0, 1)
        planeE = Plane(c)
        planeE.distance = self.farClip
        planes.append(planeE)

        # planeF = near plane
        c = OpenMaya.MVector(0, 0, -1)
        planeF = Plane(c)
        planeF.distance = self.nearClip
        planes.append(planeF)

        self.planes = planes
        self.numPlanes = 6

    def relativeToFrustum(self, pointsArray):
        numInside = 0
        numPoints = len(pointsArray)

        for j in range(0, 6):
            numBehindThisPlane = 0

            for i in range(0, numPoints):
                if (self.planes[j].relativeToPlane(pointsArray[i]) == -1):  # Behind
                    numBehindThisPlane += 1
                if numBehindThisPlane == numPoints:
                    # all points were behind the same plane
                    return False
                elif (numBehindThisPlane == 0):
                    numInside += 1

        if (numInside == self.numPlanes):
            return True  # Inside
        return True  # Intersect


def in_frustum(cameraName, objectName):
    """
    returns: True if withing the frustum of False if not
    """
    selectionList = OpenMaya.MSelectionList()
    camDagPath = OpenMaya.MDagPath()
    selectionList.add(cameraName)
    selectionList.getDagPath(0, camDagPath)

    cameraDagPath = OpenMaya.MFnCamera(camDagPath)

    camInvWorldMtx = camDagPath.inclusiveMatrixInverse()

    fnCam = Frustum(cameraName)
    points = []

    # For node inobjectList
    selectionList = OpenMaya.MSelectionList()
    objDagPath = OpenMaya.MDagPath()
    selectionList.add(objectName)
    selectionList.getDagPath(0, objDagPath)

    fnDag = OpenMaya.MFnDagNode(objDagPath)
    obj = objDagPath.node()

    dWorldMtx = objDagPath.exclusiveMatrix()
    bbox = fnDag.boundingBox()

    minx = bbox.min().x
    miny = bbox.min().y
    minz = bbox.min().z
    maxx = bbox.max().x
    maxy = bbox.max().y
    maxz = bbox.max().z

    # Getting points relative to the cameras transmformation matrix
    points.append(bbox.min() * dWorldMtx * camInvWorldMtx)
    points.append(OpenMaya.MPoint(maxx, miny, minz)
                  * dWorldMtx * camInvWorldMtx)
    points.append(OpenMaya.MPoint(maxx, miny, maxz)
                  * dWorldMtx * camInvWorldMtx)
    points.append(OpenMaya.MPoint(minx, miny, maxz)
                  * dWorldMtx * camInvWorldMtx)
    points.append(OpenMaya.MPoint(minx, maxy, minz)
                  * dWorldMtx * camInvWorldMtx)
    points.append(OpenMaya.MPoint(maxx, maxy, minz)
                  * dWorldMtx * camInvWorldMtx)
    points.append(bbox.max() * dWorldMtx * camInvWorldMtx)
    points.append(OpenMaya.MPoint(minx, maxy, maxz)
                  * dWorldMtx * camInvWorldMtx)

    return fnCam.relativeToFrustum(points)


all_objs_mesh = cmds.ls(tr=True)
startF = cmds.playbackOptions(q=True, ast=True)
endF = cmds.playbackOptions(q=True, aet=True)
keep_objs = []
count = 0
for frame in range(int(startF), int(endF)+1):
    if frame % 10 == 0 or frame == int(startF) or frame == int(endF)+1:
        cmds.currentTime(frame)
        for obj in all_objs_mesh:
            if obj in keep_objs:
                continue
            if in_frustum('camRender', obj):
                keep_objs.append(obj)
for i in all_objs_mesh:
    if i not in keep_objs:
        try:
            cmds.delete(i)
        except:
            count += 1
print count
