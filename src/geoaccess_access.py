from gvsig import *
from geom import *
from org.gvsig.andami import PluginsLocator
from org.gvsig.fmap.mapcontext import MapContextLocator
import java.awt
import java.awt.event
import java.awt.geom

def addDependencyWithPlugin(pluginCode):
  pluginsManager = PluginsLocator.getManager()
  scriptingPlugin = pluginsManager.getPlugin("org.gvsig.scripting.app.extension")
  scriptingPlugin.addDependencyWithPlugin(pluginsManager.getPlugin(pluginCode))

addDependencyWithPlugin("org.gvsig.geoprocess.app.mainplugin")

from es.unex.sextante.core import Sextante
from es.unex.sextante.gui.core import SextanteGUI
from org.gvsig.geoprocess.lib.sextante.dataObjects import FlyrVectIVectorLayer, FLyrRasterIRasterLayer
from org.gvsig.fmap.mapcontext.layers import FLayer
from es.unex.sextante.core import OutputFactory
from es.unex.sextante.core import AnalysisExtent
from java.awt.geom import RectangularShape, Rectangle2D

class Geoprocess:
  def __init__(self):
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

  def getAlgorithms(self):
    return self.__algorithms

  def execute(self, algorithmId, kwparams):
    algorithm = self.getAlgorithms()[algorithmId]
    
    #Parametros de entrada
    params = algorithm.getParameters()
    for i in range(0,params.getNumberOfParameters()):
      param = params.getParameter(i)
      paramValue = kwparams[param.getParameterName()]
      #Vector a SEXTANTE
      if param.getParameterTypeName() == "Vector Layer":
        paramValue = self.__createSextanteLayer(paramValue())
      #Raster a SEXTANTE
      if param.getParameterTypeName() == "Raster Layer":
        print "Raster parameter"
        return
      param.setParameterValue(paramValue)
      
    #Extension
    if 'EXTENT' in kwparams.keys():
        AExtent = AnalysisExtent()
        frame = kwparams['EXTENT']
        print frame
        if frame == 'VIEW':
            envelope = currentView().getMap().getFullEnvelope()
            xlow = envelope.getLowerCorner().getX()
            ylow = envelope.getLowerCorner().getY()
            xup = envelope.getUpperCorner().getX()
            yup = envelope.getUpperCorner().getY()
        else: #lista
            xlow = frame[0]
            ylow = frame[1]
            xup = frame[2]
            yup = frame[3]
        frame = Rectangle2D.Double(xlow, ylow, xup, yup)
        AExtent.addExtent(frame)
        algorithm.setAnalysisExtent(AExtent)
        print "Set Extent"
    else:
        print "Not Extent"
    try:
        if 'PATH' in kwparams.keys():
            path = kwparams['PATH']
            output0 = algorithm.getOutputObjects().getOutput(0)
            out0 = output0.getOutputChannel()
            out0.setFilename(path)
        else: 
            output0 = algorithm.getOutputObjects().getOutput(0)
            out0 = output0.getOutputChannel()
            out0.setFilename(None)
    except:
        pass
        
    
    #Ejecutar algorithm
    algorithm.execute(None,self.__outputFactory)
    print algorithm.algorithmAsCommandLineSentences

    #Archivo de salida
    try:
        if 'PATH' in kwparams.keys():
            path = kwparams['PATH']
            output0 = algorithm.getOutputObjects().getOutput(0)
            out0 = output0.getOutputChannel()
            out0.setFilename(path)
        else: 
            output0 = algorithm.getOutputObjects().getOutput(0)
            out0 = output0.getOutputChannel()
            out0.setFilename(None)
    except:
        pass
        
    #Objetos de salida
    oos = algorithm.getOutputObjects()
    ret = dict()
    for i in range(0,oos.getOutputObjectsCount()):
      oo = oos.getOutput(i)
      value = oo.getOutputObject()
      if isinstance(value,FlyrVectIVectorLayer):
        store = value.getFeatureStore()
        layer = MapContextLocator.getMapContextManager().createLayer(value.getName(),store)
        ret[value.getName()] = layer
      elif isinstance(value,FLyrRasterIRasterLayer):
        print "********* Raster layer"
      else:
        ret[value.getName()] = value

    return ret

def geoprocess(algorithmId, **kwparams):
  geoprocess = Geoprocess()
  r = geoprocess.execute(algorithmId, kwparams )
  view = currentView()
  outList = []
  
  print "Output layers: "
  for value in r.values():
    print "\t", value, value.getDataStore().getFullName()
    if isinstance(value,FLayer): 
        out = loadShapeFile(str(value.getDataStore().getFullName()))
        outList.append(out)
  return outList

def geoprocessHelp(geoalgorithmId):
    geoprocess = Geoprocess() 
           
    for algorithmId, algorithm in geoprocess.getAlgorithms().items():
      if algorithmId == geoalgorithmId or geoalgorithmId == "All": pass
      else: continue
      print "* Algorithm help: ", algorithm.getName()
      print "*", algorithm.commandLineHelp

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
    
def main(*args):
    #geoprocessSearch(" ")
    #geoprocessHelp("closegapsnn")
    #geoprocessHelp("perturbatepointslayer")
    #r = geoprocess("perturbatepointslayer", LAYER = currentLayer(),MEAN = 10, STDDEV = 10 )
    #r = geoprocess("perturbatepointslayer", EXTENT = "VIEW", LAYER = currentLayer(),MEAN = 10, STDDEV = 10 )
    #r = geoprocess("perturbatepointslayer", EXTENT = [0,0,500,500], LAYER = currentLayer(), MEAN = 10, STDDEV = 10 )
    r = geoprocess("perturbatepointslayer", PATH = "C:/gvsig/perturbatepoints001.shp", LAYER = currentLayer(),MEAN = 5, STDDEV = 5 )
    #Devuelve una lista con las capas resultado que han sido cargadas en la vista
    print ""
    print r
    print r[0].features().getCount()
