# -*- coding: utf-8 -*-
#
# File: gvpy.py
# Version: v0.01
#

__author__ = """Oscar Martinez Olmos <masquesig@gmail.com>"""

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



class Geoprocess:
  def __init__(self):
    #Sextante.initialize()
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
      slayer = FlyrVectIVectorLayer()
      slayer.create(layer)
      return slayer
    
  def __createSextanteRaster(self, layer):
      rlayer = FLyrRasterIRasterLayer()
      rlayer.create(layer)
      return rlayer

  def __createSextanteTable(self, layer):
      table = TableDocumentITable()
      table.create(layer)
      return table
    
  def getAlgorithms(self):
      return self.__algorithms
    
  def __defineParameters(self, algorithm, kwparams):
      """ Input parameters """
      params = algorithm.getParameters()
      for i in range(0,params.getNumberOfParameters()):
          param = params.getParameter(i)
          paramValue = kwparams[param.getParameterName()]
          print "PARAMETRO", param, param.getParameterTypeName()
          #Vector a SEXTANTE
          if param.getParameterTypeName() == "Vector Layer":
            paramValue = self.__createSextanteLayer(paramValue())
          #Raster a SEXTANTE
          elif param.getParameterTypeName() == "Raster Layer":
            paramValue = self.__createSextanteRaster(paramValue)
          #Tabla a SEXTANTE
          elif param.getParameterTypeName() == "Table":
            paramValue = self.__createSextanteTable(paramValue())
          param.setParameterValue(paramValue)
      
  def __defineExtent(self, algorithm, kwparams):
      """ Define Analysis Extent """
      if 'EXTENT' in kwparams.keys():
          print ("|"+str(kwparams.keys()))
          frame = kwparams['EXTENT']
          print ("|"+str(frame))
          print "TIPO DE FRAME", type(frame)
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
              #print xlow, ylow, xup, yup
              frame = Rectangle2D.Double(xlow, ylow, xup, yup)
              print frame
              AExtent.addExtent(frame)
          #elif isinstance(frame, raster):
          elif isinstance(frame, DefaultFLyrRaster):
              print "EXTENT ************ RASTER"
              layer = self.__createSextanteRaster(frame)
              AExtent = AnalysisExtent(layer)
          elif isinstance(frame, list):
              print "EXTENT ************ LIST"
              AExtent = AnalysisExtent()
              xlow, ylow, xup, yup  = frame[0], frame[1], frame[2], frame[3]
              frame = Rectangle2D.Double(xlow, ylow, xup, yup)
              print frame
              AExtent.addExtent(frame)
          elif isinstance(frame, gvsig.Layer):
              print "EXTENT ************ layer"
              layer = self.__createSextanteLayer(frame())
              AExtent = AnalysisExtent(layer)
              """
              envelope = frame.data().getEnvelope()
              xlow = envelope.getLowerCorner().getX()
              ylow = envelope.getLowerCorner().getY()
              xup = envelope.getUpperCorner().getX()
              yup = envelope.getUpperCorner().getY()
              """
          else:
              raise NameError("Not Extent Define")

          #Set: cellsize
          if 'CELLSIZE' in kwparams.keys():
              AExtent.setCellSize(kwparams['CELLSIZE'])
              print "| New Cellsize: ", kwparams['CELLSIZE'], AExtent.getCellSize()
          else:
              print "| Cellsize: ", AExtent.getCellSize()
              
          algorithm.setAnalysisExtent(AExtent)
          print ("| Set Extent")
      else:
          print ("| Not Extent")
          #???
          if algorithm.canDefineOutputExtentFromInput(): algorithm.adjustOutputExtent()

  def __defineOutput(self, algorithm, kwparams):
    if 'PATH' in kwparams.keys():
        try:
            path = kwparams['PATH']
            output0 = algorithm.getOutputObjects().getOutput(0)
            out0 = output0.getOutputChannel()
            out0.setFilename(path)
            print "| PATH -> Good path"
        except:
            print"| PATH -> Bad path"
            
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
        
    algorithm.execute(None, self.__outputFactory)
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

    #Parametros de entrada
    print "** Define parameters"
    self.__defineParameters(algorithm, kwparams)

    #Extension
    print "** Define Extent"
    self.__defineExtent(algorithm, kwparams)
    
    #Archivo de salida
    print "** Define Output"
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
    #algorithm.preprocessForModeller()

    #Ejecutar algorithm
    print "**Execute algorithm"
    self.__executeAlgorithm(algorithm)
    
    #Output objects
    print "** Get output objects"
    ret = self.__getOutputObjects(algorithm)
    return ret

def geoprocess(algorithmId, **kwparams):
  geoprocess = Geoprocess()
  r = geoprocess.execute(algorithmId, kwparams )
  #view = gvsig.currentView()
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
        crs = gvsig.currentView().getProjectionCode()
        out = loadShapeFileFalse(str(path),crs)
        outList.append(out)
    #elif isinstance(value, IRasterLayer):
    elif isinstance(value,FLayer):
        print "|\t Value:", value.getName()
        print "|\t\t", value.getFileName()[0]
        raster = gvsig_raster.loadRasterLayer(value.getFileName()[0])
        outList.append(raster)
    else:
        print "Non-type"
        print "\tValue: ", value
  print "\n"
  return outList
  
def loadShapeFileFalse(shpFile, CRS='CRS:84'):
    try:
        CRS = gvsig.currentProject().getProjectionCode()
    except:
        pass
    layer = gvsig.loadLayer('Shape', shpFile=shpFile, CRS=CRS)
    gvsig.currentView().addLayer(layer)
    return gvsig.Layer(layer)
    
def geoprocessHelp(geoalgorithmId):
    geoprocess = Geoprocess() 
    for algorithmId, algorithm in geoprocess.getAlgorithms().items():
      if algorithmId.encode('UTF-8') == geoalgorithmId.encode('UTF-8') or geoalgorithmId == "All": pass
      else: continue
      print "* Algorithm help: ", algorithm.getName().encode('UTF-8')
      print "*", algorithm.commandLineHelp.encode('UTF-8')
    del(geoprocess)
   
def geoprocessSearch(strSearch):
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
    """
    #BUG
    for i in gvsig.currentView().getLayers(): 
        print i
    """
    layers = gvsig.currentView().getLayers()
    lyrlist = [ layers[i] for i in range(0,3)]
    for i in lyrlist: 
      if i.isActive and isinstance(i, DefaultFLyrRaster): return i
    #print lyrlist
    #if isinstance(i(), DefaultFLyrRaster):
    #        if i.isActive: return i
    #if i.isActive(): print i
    return None
    
def main(*args):
    #geoprocessSearch(" ")
    #geoprocessHelp("closegapsnn")
    #geoprocessHelp("perturbatepointslayer")
    #r = geoprocess("perturbatepointslayer", LAYER = gvsig.currentLayer(),MEAN = 10, STDDEV = 10 )
    #r = geoprocess("perturbatepointslayer", EXTENT = "VIEW", LAYER = currentLayer(),MEAN = 10, STDDEV = 10 )
    #r = geoprocess("perturbatepointslayer", EXTENT = [0,0,500,500], LAYER = currentLayer(), MEAN = 10, STDDEV = 10 )
    #r = geoprocess("perturbatepointslayer", PATH = "C://gvsig//perturbatepoints028.shp", LAYER = gvsig.currentLayer(),MEAN = 5, STDDEV = 5 )
    #layer = gvsig.currentView().getLayer("data_test_lines.shp")
    #r = geoprocess("linestoequispacedpoints", LINES=layer,DISTANCE=2)
   
    #for i in range(10):
    #r = geoprocess("perturbatepointslayer", LAYER = r[0],PATH = "C://gvsig//perturbatepoints028_" + str(i) + ".shp",MEAN =0.5, STDDEV = 0.5 )
    #r = geoprocess("fixeddistancebuffer", LAYER = r[0], DISTANCE=1, TYPES="", RINGS=3, NOTROUNDED=False)
    #r = geoprocess("randomvector", COUNT=20, TYPE=1, EXTENT=gvsig.currentView())
    #RASTER
    #r1 = geoprocess("generaterandomnormal", EXTENT = [0,0,500,500], PATH = "C://gvsig//perturbatepoints030.tif", MEAN =0.5, STDDEV = 0.5)
    #layer = gvsig.currentView().getLayer("perturbatepoints030")
    #raster = currentRaster()
    #layer = gvsig_raster.loadRasterLayer('c:/gvsig/test_low.tif')
    #r1 = geoprocess("gradientlines",INPUT = layer, MIN=1, MAX=10, SKIP=1)
    #r = geoprocess("gridorientation",INPUT=layer,METHOD=0)
    #r = geoprocess("gridorientation",INPUT=layer,METHOD=0, PATH = "C://gvsig//perturbatepoints010.tif")
    #r = geoprocess("gridorientation", INPUT=raster, METHOD=0, PATH = "C://gvsig//perturbatepoints011.tif")
    #r = geoprocess("gradientlines", INPUT = layer, MIN=1, MAX=10, SKIP=1, PATH = "C://gvsig//perturbatepoints012.tif")
    #r = geoprocess("generaterandomnormal", EXTENT = [0,0,500,500], PATH = "C://gvsig//perturbatepoints013.tif", MEAN =0.5, STDDEV = 0.5)
    #geoprocessHelp("randomvector")
    #r = geoprocess("randomvector", COUNT=20, TYPE=2, EXTENT=gvsig.currentLayer())
    #r = geoprocess("randomvector", COUNT=20, TYPE=1, EXTENT=gvsig.currentView())
    #r = geoprocess("randomvector", COUNT=20, TYPE=1, EXTENT="VIEW")
    # = geoprocess("randomvector", COUNT=20, TYPE=1, EXTENT=currentRaster())
    #r = geoprocess("gvSIG-convexhull", LAYER=gvsig.currentLayer(), CHECK=True, PATH = "C://gvsig//gvsigconvexhull_001.shp")
    #r = geoprocess("generaterandomnormal", PATH = "C://gvsig//per.tif", EXTENT=gvsig.currentLayer(), CELLSIZE = 100, PATH = "C://gvsig//perturbatepoints014.tif", MEAN =5, STDDEV = 5)
    
    #geoprocessHelp("tablebasicstats")
    #r =geoprocess("tablebasicstats",TABLE=gvsig.currentTable(), FIELD=0)
    print "gvpy on."
    
    
    
    #GVPY_LIBRARY
    #GVPY_LIBRARY
    #GVPY_LIBRARY
    
    #layer = gvsig.currentLayer()
    #showFields(gvsig.currentLayer())
    #removeField(layer, "campo3")
    #removeField(layer, "campo5")
    #addField(layer,"campo1")
    #addField(layer,"campo2")
    #renameField(layer, "campo5", "campo50")

    #print list2geompoly([[1,2],[3,10],[5,30]])
    #addFeature(layer, "test01", "test2", [15,200])
    #addFeature(layer, "test11", "test3", geom.createPoint(300, 301))
    #addFeature(layer, campo1 = "kwparam", campo2 = "kwparam2", GEOMETRY = geom.createPoint(300,300))
    #addFeature(layer, "linea", "01", [[1,2],[3,10],[5,30]])
    #addFeature(layer, "pol", "02", [[50,80],[150,50],[100,10],[0,10],[50,80]])

    
    #layer = newLayer()
    #addFeature(layer, "pol", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])
    #addFeature(layer, "pol", "02", [[0,0],[10,5],[10,10],[0,10],[5,5]])
    #addFeature(layer, "pol", "03", [[-50, -34],[0,0], [-14,30]])
    #addField(layer,"campo3")
    #modifyFeatures(layer, "campo3", "nuevo poligono")
    
    
    #Create shapes
    #layer1 = newLayer(layer,"C:/gvsig/point_shape.shp", 1)
    #layer2 = newLayer(layer,"C:/gvsig/line_shape.shp", 2)
    #layer3 = newLayer(layer,"C:/gvsig/polygon_shape", 3)
    
    #Add features
    #addFeature(layer1, "point", "01", [50,80])
    #addFeature(layer1, "point", "02",[150,50])
    #addFeature(layer1, "point", "03",[100,10])
    #addFeature(layer1, "point", "04",[0,10])

    #addFeature(layer3, "polygon", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])

    #addFeature(layer2, "line", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])
    
    #Modify all values in one column
    #modifyFeatures(layer1, "campo1", "Points_gsoc")
    #modifyFeatures(layer2, "campo1", "Lines_gsoc")

    #Modify schema
    #addField(layer1,"Name")
    #removeField(layer1,"Surname")
    
    ##Execute SEXTANTE
    #r = geoprocess("perturbatepointslayer", LAYER = currentLayer(),MEAN = 5, STDDEV = 5 )
    pass

    
def newLayer(layer, path, geometryType):
    #path = "C:/gvsig/test03.shp"
    CRS= gvsig.currentProject().getProjectionCode()
    schema = gvsig.createSchema(layer.getSchema())
    output = gvsig.createShape( schema, path, CRS=CRS, geometryType = geometryType )
    gvsig.currentView().addLayer(output)
    return output
    
def addFeature(layer, *params, **kwparams):
    #IN: layer, feature params + geometry
    typeLayer = layer.getTypeVectorLayer().name
    if kwparams != {}:
        layer.append(kwparams)
        layer.commit()
        return
    if params != ():
        schValues = layer.getSchema().getAttrNames()
        values = {}
        itera = iter((list(params)))
        value = itera.next()
        for sch in schValues: 
            #Si el campo a modificar es una geometria
            #print "Comprobacion:", sch, isinstance(value, list)
            #re comprobacion si es campo geometry
            #bug: Comprobar si es lista o objeto geom  en primer if
            #... sch == "Geometry" and ES UNA LISTA
            #... sino copia el valor directamente: caso de pasar geometrias
            if sch == "GEOMETRY":
                if typeLayer == "Point2D":
                    if isinstance(value, list):
                        values[sch] = geom.createPoint(value[0],value[1])
                elif typeLayer == "MultiCurve2D":
                    if isinstance(value, list):
                        values[sch] = list2geomcurve(value)
                elif typeLayer == "MultiSurface2D":
                    if isinstance(value, list):
                        values[sch] = list2geompoly(value)
            else:
                values[sch] = value
            try:
                value = itera.next()
            except: break
        layer.append(values)
        layer.commit()
        
def list2geompoly(listPoints):
    #IN: list[[x,y],...]
    #OUT: geometry polygon
    geometry = geom.createGeometry(3)
    for point in listPoints:
        geometry.addVertex(geom.createPoint(point[0],point[1]))
    if listPoints[0] != listPoints[len(listPoints)-1]: 
        geometry.addVertex(geom.createPoint(listPoints[0][0], listPoints[0][1]))
    return geometry
    
def list2geomcurve(listPoints):
    #IN: list [[x,y],...]
    #OUT: geometry line
    geometry = geom.createGeometry(2)
    for point in listPoints:
        geometry.addVertex(geom.createPoint(point[0],point[1]))
    return geometry
    
def modifyFeatures(layer, field, value):
    #IN: layer, field, new value
    features = layer.features()
    for feature in features:
        feature.edit()
        feature.set(field, value)
        layer.update(feature)
    layer.commit()
        
def showFields(layer):
    #IN: layer
    #OUT: str(atributos)
    print layer.getSchema().getAttrNames()
    
def addField(layer,field, sType = "STRING",iSize=20):
    #IN: layer, field, *sType, *iSize)
    #OUT: layer
    #addField(layer, "nombre")
    schema = layer.getSchema()
    schema.modify()
    if isinstance(field,str): schema.append(field,sType,iSize)
    layer.edit()
    layer.updateSchema(schema)
    layer.commit()
    return layer

def removeField(layer, field):
    #IN: layer, field
    #OUT: layer
    #removeField(layer, "apellido")
    print "Campo %s eliminado" % (str(field))
    schema = layer.getSchema()
    schema.modify()
    if isinstance(field,str): schema.remove(field)
    else: return 
    layer.edit()
    layer.updateSchema(schema)
    layer.commit()
    return layer