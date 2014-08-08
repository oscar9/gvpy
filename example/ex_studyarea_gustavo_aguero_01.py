import gvpy
import gvsig
import commonsdialog
def main(*args):
    """Study area"""
    
    #End-Name of the new layers
    #Increment +1 if you execute again this script
    #This will avoid to overwrite the layers
    #Path is set over the script in C://gvsig//, but you can change it
    endid = "_01.shp"

    #Get load layers
    
    areaprot = gvpy.getProjectLayer("Vista1", "areaprot32617.shp")
    distritos = gvpy.getProjectLayer("Vista1", "distritos32617.shp")
    print areaprot, distritos
    
    #Selection
    areaprot.getSelection().deselectAll()
    distritos.getSelection().deselectAll()
    for feature in areaprot.features():
        if feature.Nombre_ == "ARENAL-MONTERVERDE":
            areaprot.getSelection().select(feature)

    for feature in distritos.features():
        if feature.NDISTRITO == "UNION":
            distritos.getSelection().select(feature)

    #Intersection
    intersection = gvpy.runalg("gvSIG-intersection", areaprot, distritos, True, True, PATH=["C://gvsig//inter_pol"+endid,"C://gvsig//inter_line"+endid,"C://gvsig//inter_point"+endid])
    
    #Buffer area of interest
    bufferArea = gvpy.runalg("gvSIG-buffer", intersection[1], False, "100.0", 0, False, True, "0", "0", PATH="C://gvsig//buffer"+endid)
    
    #Reticula
    grid = gvpy.runalg("graticulebuilder", 100, 100, gvpy.TYPE_POLYGON, EXTENT=bufferArea, PATH="C://gvsig//grid"+endid)
    
    #Selection reticula
    grid.getSelection().deselectAll()
    #New layer with the same structure
    gridSelect = gvpy.newLayer(grid, "C://gvsig//grid_select"+endid)
    #If reticula intersect with areaInterest, add to a newLayer reticulaSelect
    for area in intersection[1].features():
        for ret in grid.features():
            if ret.geometry().intersects(area.geometry()): 
                gridSelect.append(ret.getValues())
    gridSelect.commit()
    

    #Random points inside shape "1" area of interest
    fitpoints = gvpy.runalg("fitnpointsinpolygon",intersection[1], 2, "74", 1, 0, PATH="C://gvsig//fitpoints"+endid)
    
    #New layer with points inside grid
    gridFinal = gvpy.newLayer(gridSelect, "C://gvsig//grid_final"+endid)
    for point in fitpoints.features():
        for ret in gridSelect.features():
            if ret.geometry().intersects(point.geometry()):
                gridFinal.append(ret.getValues())
    gridFinal.commit()
   
    #Centroids
    centroids = gvpy.runalg("centroids", gridFinal, PATH="C://gvsig//centroids"+endid)
    gvpy.removeField(centroids, "X")
    gvpy.removeField(centroids, "Y")

    #Pointcoordinates: add coordinates to the table
    centroidsXY = gvpy.runalg("pointcoordinates", centroids, PATH="C://gvsig//centroidsXY"+endid)
    gvpy.modifyField(centroidsXY, "X", iType="FLOAT",  newField="X_1")
    gvpy.modifyField(centroidsXY, "Y", iType="FLOAT", newField="Y_1")
    
    #Spatial join
    union = gvpy.runalg("gvSIG-spatialjoin", gridFinal, centroidsXY, False, False, True,"", PATH="C://gvsig//spatialjoin"+endid)
    print "End"