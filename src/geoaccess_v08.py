
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

    #Region de analisis
    envelope = currentView().getMap().getFullEnvelope()
    geomEnvelope = envelope.getGeometry()
    frame = geomEnvelope.getBounds2D()
    aExtent = AnalysisExtent()
    aExtent.addExtent(frame)
    algorithm.setAnalysisExtent(aExtent)

    #Ejecutar algorithm
    algorithm.execute(None,self.__outputFactory)

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
  r = geoprocess("perturbatepointslayer", LAYER = currentLayer(),MEAN = 10, STDDEV = 10 )
  
  #Devuelve una lista con las capas resultado que han sido cargadas en la vista
  print r
  print r[0].features().getCount()
