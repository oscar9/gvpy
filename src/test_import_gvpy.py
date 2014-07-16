
import gvpy
import gvsig
import gvsig_raster

def main(*args):

    #Generate random raster inside the analysis extent
    #can set cellsizeo of the raster result
    #if you want choose where to save the shape, you should add one attribute like this:
    #     ,PATH="C://gvsig//random_shape.shp",
    r = gvpy.runalg("generaterandomnormal", EXTENT = [0,0,0,500,500,0], CELLSIZE=10, MEAN =0.5, STDDEV = 0.5)

    #Change the orientation of the grid
    #we can set the path
    r1 = gvpy.runalg("gridorientation",r,0)

    #Gradient lines (vector) 
    #as input we introduce the result of the last geoprocess r1
    r2 = gvpy.runalg("gradientlines", EXTENT = gvsig.currentView(),INPUT = r1, MIN=1, MAX=10, SKIP=1)

    #cva algorithm
    #we don't need to write parameters name as we introduce them in order
    # and if the algorithm generates 2 or more layers as result, we will pick them as list
    # if is just one, as unique object
    #Also, you can specify both names with: , PATH=["C:/gvsig/1.tif","C:/gvsig/2.tif"]
    r3 = gvpy.runalg("cva", r1, r1, r1, r1, CELLSIZE=100)
    print "List layers result:",r3[0], r3[1]

    #You can check the orden of the params writing this here or in Jython console
    gvpy.algHelp("cva")

    #or search for a algorithm with a certain words inside his description
    gvpy.algSearch("aleatorio")

    #Random vector
    #also we can introduce a layer as Analysis Extent
    #doesnt matter if is: vector, raster, gvsig.currentView(), gvsig.currentLayer() or
    #coordinates of corners [0,0,500,500]
    v = gvpy.runalg("randomvector", 20, 1, EXTENT=r1)

    #We don't need to write "v=" before the algorithm if we don't want take the layer result
    gvpy.runalg("gvSIG-convexhull", v, True)

    #More
    gvpy.algHelp("generaterandomnormal")
    r = gvpy.runalg("generaterandomnormal", 100,100, CELLSIZE=100, EXTENT=[250,250,0,500,500,0])
    r = gvpy.runalg("generaterandomnormal", 10, 10, CELLSIZE=50, EXTENT=[500,500,0, 1000,1000,0])
    r = gvpy.runalg("generaterandombernoulli", 50.0, CELLSIZE=25, EXTENT=[1000,1000,0, 1250,1250,0])
    r = gvpy.runalg("gradientlines", r, 1, 100, 1)
    
    v1 = gvpy.runalg("randomvector",10, gvpy.TYPE_POLYGON, EXTENT=[0,0,0,500,500,0])
    v2 = gvpy.runalg("randomvector", 5, gvpy.TYPE_POLYGON, EXTENT=v1)
    v3 = gvpy.runalg("difference", v1, v2)
    v4 = gvpy.runalg("randomvector", 5, 0, EXTENT=v3)
    v5 = gvpy.runalg("randomvector", 100, 2)
    gvpy.algHelp("tablebasicstats")
    print "End"


