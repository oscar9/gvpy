import gvsig
import geom
import gvsig_raster

from org.gvsig.andami import PluginsLocator
from org.gvsig.fmap.mapcontext import MapContextLocator
import java.awt
import java.awt.event
import java.awt.geom
from java.io import File

def addDependencyWithPlugin(pluginCode):
  pluginsManager = PluginsLocator.getManager()
  scriptingPlugin = pluginsManager.getPlugin("org.gvsig.scripting.app.extension")
  scriptingPlugin.addDependencyWithPlugin(pluginsManager.getPlugin(pluginCode))

addDependencyWithPlugin("org.gvsig.geoprocess.app.mainplugin")

from es.unex.sextante.core import Sextante, OutputFactory, AnalysisExtent
from es.unex.sextante.outputs import FileOutputChannel
from es.unex.sextante.gui.core import SextanteGUI
from es.unex.sextante.dataObjects import IRasterLayer

from org.gvsig.geoprocess.lib.sextante.dataObjects import FlyrVectIVectorLayer, FLyrRasterIRasterLayer, TableDocumentITable
from org.gvsig.fmap.mapcontext.layers import FLayer
from java.awt.geom import RectangularShape, Rectangle2D
from org.gvsig.fmap.mapcontext.layers.vectorial import FLyrVect
from org.gvsig.raster.fmap.layers import DefaultFLyrRaster

#Constant
TYPE_POLYGON = 0
TYPE_LINE = 1
TYPE_POINT = 2

class Geoprocess:
  def __init__(self):
    Sextante.initialize()
    SextanteGUI.initialize()
    self.__FlyrVectIVectorLayer = None
    self.__outputFactory = SextanteGUI.getOutputFactory()
    self.__algorithms = dict()

    keySetIterator = Sextante.getAlgorithms().keySet().iterator()
    while(keySetIterator.hasNext()):
      key = keySetIterator.next()
      algorithms = Sextante.getAlgorithms().get(str(key))
      for name in algorithms.keySet():
        self.__algorithms[str(name)] = algorithms.get(name)

  def __createSextanteLayer(self, layer):
      """ gvsig layer -> SEXTANTE """
      slayer = FlyrVectIVectorLayer()
      slayer.create(layer)
      return slayer
    
  def __createSextanteRaster(self, layer):
      """ gvsig raster -> SEXTANTE """
      rlayer = FLyrRasterIRasterLayer()
      rlayer.create(layer)
      return rlayer

  def __createSextanteTable(self, layer):
      """ gvsig table -> SEXTANTE """
      table = TableDocumentITable()
      table.create(layer)
      return table
    
  def getAlgorithms(self):
      return self.__algorithms
    
  def __defineParameters(self, algorithm, kwparams):
      """ Define input parameters """
      params = algorithm.getParameters()
      for i in range(0,params.getNumberOfParameters()):
          param = params.getParameter(i)
          if param.getParameterName() in kwparams:
              paramValue = kwparams[param.getParameterName()]
          else:
              paramValue = kwparams[i]
              
          #Vector to SEXTANTE
          if param.getParameterTypeName() == "Vector Layer":
              if isinstance(paramValue, str):
                  layer = gvsig.currentView().getLayer(paramValue)
                  paramValue = self.__createSextanteLayer(layer())
              else:
                  paramValue = self.__createSextanteLayer(paramValue())
          #Raster to SEXTANTE
          elif param.getParameterTypeName() == "Raster Layer":
              if isinstance(paramValue, str):
                  layer = gvsig.currentView().getLayer(paramValue)
                  paramValue = self.__createSextanteRaster(layer)
              else:
                  paramValue = self.__createSextanteRaster(paramValue)
          #Table to SEXTANTE
          elif param.getParameterTypeName() == "Table":
              if isinstance(paramValue, str):
                  layer = gvsig.currentProject().getTable(paramValue)
                  paramValue = self.__createSextanteTable(layer())
              else:
                  paramValue = self.__createSextanteTable(paramValue())

          #Set parameter value
          param.setParameterValue(paramValue)
      
  def __defineExtent(self, algorithm, kwparams):
      """ Define Analysis Extent """
      if 'EXTENT' in kwparams.keys() and algorithm.getUserCanDefineAnalysisExtent() :
          frame = kwparams['EXTENT']
          if isinstance(frame, str): frame = gvsig.currentView().getLayer(frame)
          print ("|"+str(frame)+"||"+str(type(frame)))
          if isinstance(frame, str) and frame == 'VIEW' or isinstance(frame, gvsig.View):
              AExtent = AnalysisExtent()
              print "EXTENT ************ VIEW"
              if isinstance(frame, gvsig.View): view = frame
              else: view = gvsig.currentView()
              envelope = view.getMap().getFullEnvelope()
              xlow = envelope.getLowerCorner().getX()
              ylow = envelope.getLowerCorner().getY()
              xup = envelope.getUpperCorner().getX()
              yup = envelope.getUpperCorner().getY()
              frame = Rectangle2D.Double(xlow, ylow, xup, yup)
              #AExtent.addExtent(frame)
              AExtent.setXRange(xlow, xup, False)
              AExtent.setYRange(ylow, yup, False)
              AExtent.setZRange(0, 0, False)
              print "EXTENSIONNNNNNNNNNNNNNNNNNNNNN", AExtent
              
          elif isinstance(frame, DefaultFLyrRaster):
              print "EXTENT ************ RASTER"
              layer = self.__createSextanteRaster(frame)
              AExtent = AnalysisExtent(layer)
              
          elif isinstance(frame, list):
              print "EXTENT ************ LIST"
              AExtent = AnalysisExtent()
              xlow, ylow, zlow, xup, yup, zup  = frame[0], frame[1], frame[2], frame[3], frame[4], frame[5]
              frame = Rectangle2D.Double(xlow, ylow, xup, yup)
              print frame
              #AExtent.addExtent(frame)
              AExtent.setXRange(xlow, xup, False)
              AExtent.setYRange(ylow, yup, False)
              AExtent.setZRange(zlow, zup, False)
              
          elif isinstance(frame, gvsig.Layer):
              print "EXTENT ************ layer"
              layer = self.__createSextanteLayer(frame())
              AExtent = AnalysisExtent(layer)
              
          else:
              raise NameError("Not Extent Define")

      else:
          print ("| Not Extent: No input data")
          #check
          AExtent = AnalysisExtent()
          #algorithm.setAnalysisExtent(AExtent)
          if algorithm.canDefineOutputExtentFromInput(): algorithm.adjustOutputExtent()
          print algorithm.getAnalysisExtent() 
          print algorithm.isAutoExtent() 
          print "set auto view"
          AExtent = AnalysisExtent()
          print "EXTENT ************ VIEW"
          view = gvsig.currentView()
          envelope = view.getMap().getFullEnvelope()
          print "Setting AExtent...",
          try:
              print "View"
              xlow = envelope.getLowerCorner().getX()
              ylow = envelope.getLowerCorner().getY()
              xup = envelope.getUpperCorner().getX()
              yup = envelope.getUpperCorner().getY()
              print xlow, ylow, xup,yup
          except:
              print "Default"
              xlow, ylow, xup, yup = 0,0,100,100
          frame = Rectangle2D.Double(xlow, ylow, xup, yup)
          AExtent.setXRange(xlow, xup, False)
          AExtent.setYRange(ylow, yup, False)
          AExtent.setZRange(0, 0, False)
          algorithm.setAnalysisExtent(AExtent)
          
      #Set: cellsize
      if 'CELLSIZE' in kwparams.keys():
          AExtent.setCellSize(kwparams['CELLSIZE'])
          print "| New Cellsize: ", kwparams['CELLSIZE'], AExtent.getCellSize()
      else:
          print "| Cellsize: ", AExtent.getCellSize()
      if 'CELLSIZEZ' in kwparams.keys():
          AExtent.setCellSizeZ(kwparams['CELLSIZEZ'])
          print "| New Cellsize Z: ", kwparams['CELLSIZEZ'], AExtent.getCellSizeZ()
      else:
          print "| Cellsize: ", AExtent.getCellSizeZ()
      algorithm.setAnalysisExtent(AExtent)
      print ("| Set Extent")
      
  def __defineOutput(self, algorithm, kwparams):
    if 'PATH' in kwparams.keys():
        path = kwparams['PATH']
        outputSet = algorithm.getOutputObjects()
        if outputSet.getOutputDataObjectsCount() == 1:
            out1 = outputSet.getOutput(0)
            out1.setOutputChannel(FileOutputChannel("New_name"))
            out1channel = out1.getOutputChannel()
            out1channel.setFilename(path)
            print "| PATH -> Good path"
        elif outputSet.getOutputDataObjectsCount() > 1 and isinstance(path, list):
            for n in range(0, outputSet.getOutputDataObjectsCount()):
                out1 = outputSet.getOutput(n)
                out1.setOutputChannel(FileOutputChannel("New_name"))
                out1channel = out1.getOutputChannel()
                out1channel.setFilename(path[n])
                print "| PATH -> Good path"
        else:
            print "| PATH -> Bad path"
    elif algorithm.getOutputObjects().getOutput(0).getOutputChannel(): 
        output0 = algorithm.getOutputObjects().getOutput(0)
        out0 = output0.getOutputChannel()
        out0.setFilename(None)
        print "| Without path"
        
  def __executeAlgorithm(self, algorithm):
    try:
        print "| Algoritmo:", list(algorithm.algorithmAsCommandLineSentences)
    except:
        print "| Not - algorithm"
        
    algorithm.execute( None, self.__outputFactory)
    print "| Algoritmo:", list(algorithm.algorithmAsCommandLineSentences)
    
  def __getOutputObjects(self, algorithm):
    #Recoge los objetos de salida del algoritmo
    oos = algorithm.getOutputObjects()
    ret = dict()
    for i in range(0,oos.getOutputObjectsCount()):
      oo = oos.getOutput(i)
      value = oo.getOutputObject()
      if isinstance(value, FlyrVectIVectorLayer):
        print "| Vector"
        store = value.getFeatureStore()
        layer = MapContextLocator.getMapContextManager().createLayer(value.getName(),store)
        ret[value.getName()] = layer
      elif isinstance(value, IRasterLayer):
        print "| Raster layer"
        dalManager = gvsig.DALLocator.getDataManager()
        mapContextManager = gvsig.MapContextLocator.getMapContextManager()
        params = dalManager.createStoreParameters("Gdal Store")
        params.setFile(File(value.getFilename()))
        dataStore = dalManager.createStore(params)
        layer = mapContextManager.createLayer(value.getName(), dataStore)
        ret[value.getName()] = layer
      else:
        try:
            ret[value.getName()] = value
        except:
            if not value == None: 
                x = 0
                while True:
                    field = "value_" + str(x)
                    if any(field in s for s in ret.keys()):
                        x += 1
                    ret[str(x)] = value
                    break
    return ret
    
  def execute(self, algorithmId, kwparams):
    
    algorithm = self.getAlgorithms()[algorithmId]
    #print algorithm.getAlgorithmAsCommandLineSentences()

    #Input params
    self.__defineParameters(algorithm, kwparams)

    #Analisys Extension
    self.__defineExtent(algorithm, kwparams)
    
    #Output files
    self.__defineOutput(algorithm, kwparams)
    

    #***Cambiar nombre NO el de las capas
    """
    print "** Define name"
    if 'PATH' in kwparams.keys():
        print "| Nombre: Capa_resultados"
        out0 = java.util.HashMap()
        out0["RESULT"] = "Capa_resultados"
    """
    
    #Check algorithm
    correctValues = algorithm.hasCorrectParameterValues()
    print "| Parameter values:", correctValues
    if not correctValues: raise NameError("Not correct values")

    #Exec algorithm
    self.__executeAlgorithm(algorithm)
    
    #Output objects
    ret = self.__getOutputObjects(algorithm)
    return ret

def runalg(algorithmId,*params, **kwparams):
  geoprocess = Geoprocess()
  for i in range(0,len(params)):
      kwparams[i]=params[i]
  r = geoprocess.execute(algorithmId, kwparams )
  if r == None: return
  outList = []
  print "| Output layers: "
  for value in r.values():
    if isinstance(value, unicode):
        outList.append(value.encode("UTF-8"))
    elif isinstance(value, FLyrVect):
        print "|\t Value:", value.getName()
        path = value.getDataStore().getFullName()
        print "|\t\tPath: ", path
        if "OUTVIEW" in kwparams:
            value = loadShapeFileNew(str(path), view=kwparams["OUTVIEW"])
        else: 
            value = loadShapeFileNew(str(path))
        
        outList.append(value)
    #elif isinstance(value, IRasterLayer):
    elif isinstance(value,FLayer):
        print "|\t Value:", value.getName()
        print "|\t\t", value.getFileName()[0]
        #Not yet: Waiting for new loadRasterLayer that can set OUTVIEW
        value = gvsig_raster.loadRasterLayer(value.getFileName()[0])
        outList.append(value)
    else:
        print "Non-type"
        print "\tValue: ", value
  print "\n"
  
  #Return object or list
  if len(r.values()) > 1:
      return outList
  elif len(r.values()) == 1:
      return value
  else:
      return None
  
def loadShapeFileNew(shpFile, CRS='CRS:84', active= False, view=gvsig.currentView()):
    try:
        CRS = gvsig.currentProject().getProjectionCode()
    except:
        pass
    layer = gvsig.loadLayer('Shape', shpFile=shpFile, CRS=CRS)
    if isinstance(view,str): view = gvsig.currentProject().getView(view)
    view.addLayer(layer)
    layer.setActive(active)
    return gvsig.Layer(layer)
    
def algHelp(geoalgorithmId):
    geoprocess = Geoprocess() 
    for algorithmId, algorithm in geoprocess.getAlgorithms().items():
      if algorithmId.encode('UTF-8') == geoalgorithmId.encode('UTF-8') or geoalgorithmId == "All": pass
      else: continue
      print "* Algorithm help: ", algorithm.getName().encode('UTF-8')
      print "*", algorithm.commandLineHelp.encode('UTF-8')
    del(geoprocess)
   
def algSearch(strSearch):
    print "Inicio de busqueda.."
    geoprocess = Geoprocess()
    search = strSearch.encode('UTF-8')
    for algorithmId, algorithm in geoprocess.getAlgorithms().items():
        name = (algorithm.getName()).encode('UTF-8')
        group = (algorithm.getGroup()).encode('UTF-8')
        if (name.find(search) > 0) or (group.find(search)>0):
             print "ID: ", algorithmId, " || GROUP: ", algorithm.getGroup().encode('UTF-8'), " || NAME: ", algorithm.getName().encode('UTF-8')
    print "..Busqueda finalizada"
    del(geoprocess)
    
def currentRaster():
    """Return first raster active layer on the View"""
    layers = gvsig.currentView().getLayers()
    lyrlist = [ layers[i] for i in range(0,layers.__len__())]
    for i in lyrlist:
      if i.isActive() and isinstance(i, DefaultFLyrRaster):  return i
    return None
    
def currentActive():
    """Return first active layer on the View"""
    layers = gvsig.currentView().getLayers()
    lyrlist = [ layers[i] for i in range(0, layers.__len__())]
    for i in lyrlist:
        if i.isActive(): return i
    return None
    
def getProjectLayer(view,layer):
    """Get vector layer or raster"""
    try:
        return gvsig.currentProject().getView(view).getLayer(layer)
    except:
        for i in gvsig.currentProject().getView(view).getLayers():
            if i.name == layer: return i
            
def getProjectTable(table):
    """Get table"""
    return gvsig.currentProject().getTable(table)
    
def main(*args):
    #geoprocessSearch(" ")
    #geoprocessHelp("closegapsnn")
    #geoprocessHelp("perturbatepointslayer")
    #r = runalg("perturbatepointslayer", LAYER = gvsig.currentLayer(),MEAN = 10, STDDEV = 10 )
    #r = runalg("perturbatepointslayer", EXTENT = "VIEW", LAYER = currentLayer(),MEAN = 10, STDDEV = 10 )
    #r = runalg("perturbatepointslayer", EXTENT = [0,0,500,500], LAYER = currentLayer(), MEAN = 10, STDDEV = 10 )
    #r = runalg("perturbatepointslayer", PATH = "C://gvsig//perturbatepoints028.shp", LAYER = gvsig.currentLayer(),MEAN = 5, STDDEV = 5 )
    #layer = gvsig.currentView().getLayer("data_test_lines.shp")
    #r = runalg("linestoequispacedpoints", LINES=layer,DISTANCE=2)
   
    #for i in range(10):
    #r = runalg("perturbatepointslayer", LAYER = r[0],PATH = "C://gvsig//perturbatepoints028_" + str(i) + ".shp",MEAN =0.5, STDDEV = 0.5 )
    #r = runalg("fixeddistancebuffer", LAYER = r[0], DISTANCE=1, TYPES="", RINGS=3, NOTROUNDED=False)
    #r = runalg("randomvector", COUNT=20, TYPE=1, EXTENT=gvsig.currentView())
    #RASTER
    #r1 = runalg("generaterandomnormal", EXTENT = [0,0,500,500], PATH = "C://gvsig//perturbatepoints030.tif", MEAN =0.5, STDDEV = 0.5)
    #layer = gvsig.currentView().getLayer("perturbatepoints030")
    
    #raster = currentRaster()
    #print raster
    
    #layer = gvsig_raster.loadRasterLayer('c:/gvsig/test_low.tif')
    #r1 = runalg("gradientlines",INPUT = layer, MIN=1, MAX=10, SKIP=1)
    #r = runalg("gridorientation",INPUT=layer,METHOD=0)
    #r = runalg("gridorientation",INPUT=layer,METHOD=0, PATH = "C://gvsig//perturbatepoints010.tif")
    #r = runalg("gridorientation", INPUT=raster, METHOD=0, PATH = "C://gvsig//perturbatepoints011.tif")
    #r = runalg("gradientlines", INPUT = layer, MIN=1, MAX=10, SKIP=1, PATH = "C://gvsig//perturbatepoints012.tif")
    #r = runalg("generaterandomnormal", EXTENT = [0,0,500,500], PATH = "C://gvsig//perturbatepoints013.tif", MEAN =0.5, STDDEV = 0.5)
    #geoprocessHelp("randomvector")
    #r = runalg("randomvector", COUNT=20, TYPE=2, EXTENT=gvsig.currentLayer())
    #r = runalg("randomvector", 200, TYPE_POINT, EXTENT=gvsig.currentLayer(), PATH="C://gvsig//test_puntos_sm01.shp")
    #r = runalg("randomvector", COUNT=20, TYPE=1, EXTENT=gvsig.currentView())
    #r = runalg("randomvector", COUNT=20, TYPE=1, EXTENT="VIEW")
    #r = runalg("randomvector", COUNT=20, TYPE=1, EXTENT=currentRaster())
    #r = runalg("gvSIG-convexhull", LAYER="Puntos_de_interes_01.shp", CHECK=True, PATH = "C://gvsig//gvsigconvexhull_001.shp")
    #r = runalg("generaterandomnormal", PATH = "C://gvsig//per.tif", EXTENT=gvsig.currentLayer(), CELLSIZE = 100, PATH = "C://gvsig//perturbatepoints014.tif", MEAN =5, STDDEV = 5)
    #geoprocessHelp("tablebasicstats")
    #r =runalg("tablebasicstats",TABLE=gvsig.currentTable(), FIELD=0)

    #Without parameters label

    #layers = gvsig.currentView().getLayers()
    ##r = runalg("gridorientation", layer, 0, PATH = "C://gvsig//perturbatepoints012.tif")
    
    #r = runalg("gridorientation", layer, 0)
    #r = runalg("gradientlines", layers[0], 1, 10, 1, PATH = "C://gvsig//perturbatepoints012.shp")
    #r = runalg("cva", "test_low", "test_low", "test_low", "test_low")
    #r = runalg("cva", currentRaster(), currentRaster(), currentRaster(), currentRaster(),PATH=["C:/gvsig/1.tif","C:/gvsig/2.tif"])
    
    #layerRaster = gvsig_raster.loadRasterLayer('c:/gvsig/test_low.tif')
    #r = runalg("gridorientation",layerRaster,0, PATH = "C://gvsig//Grid_orientation.tif",EXTENT=layerRaster, CELLSIZE=1, CELLSIZEZ=10)
    #r2 = runalg("cva", r, r, r, r, PATH=["C:/gvsig/1.tif","C:/gvsig/2.tif"])
    #print r2[0], r2[1]
    #print layerRaster
    #print getProjectLayer("Vista1", "test_low")
    
    
    #layer = getProjectLayer("Vista1", "as.shp")
    #extent = getProjectLayer("Vista1", "analisis_extent")
    #runalg("difference", "as.shp", "vista2_testeo.shp", PATH="C:/gvsig/recorte_extent.shp", EXTENT=[100, 100, 0, 540, 500, 0])
    #runalg("difference", "vista2_testeo.shp", layer, PATH="C:/gvsig/recorte_extent_2.shp", EXTENT=layer, OUTVIEW="Nueva")
    #r = runalg("tablebasicstats", "species", 0)
    #print r.encode("UTF-8")
    print gvsig.currentLayer()
    algHelp("generaterandomnormal")
    r = runalg("generaterandomnormal", 100,100, CELLSIZE=100, EXTENT=[250,250,0,500,500,0])
    r = runalg("generaterandomnormal", 10, 10, CELLSIZE=50, EXTENT=[500,500,0, 1000,1000,0])
    r = runalg("generaterandombernoulli", 50.0, CELLSIZE=25, EXTENT=[1000,1000,0, 1250,1250,0])
    r = runalg("gradientlines", r, 1, 100, 1)
    
    v1 = runalg("randomvector",10, TYPE_POLYGON, EXTENT=[0,0,0,500,500,0])
    v2 = runalg("randomvector", 5, TYPE_POLYGON, EXTENT=v1)
    v3 = runalg("difference", v1, v2, PATH="C:/gvsig/Diferencia.shp")
    v4 = runalg("randomvector", 5, 0, PATH="C:/gvsig/randomvector.shp", EXTENT=v3)
    v5 = runalg("randomvector", 100, 2, PATH="C:/gvsig/randompoints.shp", EXTENT="randomvector")
    #not working v6 = runalg("gvSIG-xyshift", "randompoints", "false", "-250.0", "-250.0", PATH=["C:/gvsig/ran10.shp","C:/gvsig/ran20.shp","C:/gvsig/ran30.shp"])
    algHelp("tablebasicstats")
    v7 = runalg("gvSIG-buffer", "randompoints", False, 50.0, 0, False, True, 0, 0, PATH="C:/gvsig/buffer_gvsig010.shp")
    print "End"

