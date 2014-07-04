
import gvpy
import gvsig
import gvsig_raster

def main(*args):
    #You just need to change the param PATH for one that exist in your computer
    
    #Generate random raster inside the analysis extent
    #can set cellsizeo of the raster result
    r = gvpy.runalg("generaterandomnormal", EXTENT = [0,0,500,500], CELLSIZE=10, MEAN =0.5, STDDEV = 0.5)

    #Change the orientation of the grid
    #we can set the path
    r1 = gvpy.runalg("gridorientation",r,0, PATH = "C://gvsig//Grid_orientation.tif")

    #Gradient lines (vector) 
    #as input we introduce the result of the last geoprocess r1
    r2 = gvpy.runalg("gradientlines", EXTENT = gvsig.currentView(),INPUT = r1, MIN=1, MAX=10, SKIP=1)

    #cva algorithm
    #we don't need to write parameters name as we introduce them in order
    # and if the algorithm generates 2 or more layers as result, we will pick them as list
    # if is just one, as unique object
    r3 = gvpy.runalg("cva", r1, r1, r1, r1, PATH=["C:/gvsig/1.tif","C:/gvsig/2.tif"])
    print "List layers result:",r3[0], r3[1]

    #You can check the orden of the params writing this here or in Jython console
    gvpy.algHelp("cva")

    #or search for a algorithm with a certain words inside his description
    gvpy.algSearch("aleatorio")

    #Random vector
    #also we can introduce a layer as Analysis Extent
    #doesnt matter if is: vector, raster, gvsig.currentView(), gvsig.currentLayer() or
    #coordinates of corners [0,0,500,500]
    v = gvpy.runalg("randomvector", 20, 1, EXTENT=r1, PATH = "C://gvsig//random_vector.shp")

    #We don't need to write "v=" before the algorithm if we don't want take the layer result
    gvpy.runalg("gvSIG-convexhull", "random_vector", True)
    

