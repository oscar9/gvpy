
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

#
# Clase usada para acceder a los algoritmos.
# Basicamente me sirbe para aglutinar las variables que
# preciso y asi no las tengo sueltas por ahi.
class Geoprocess:      
  def __init__(self):
    # Inicializo algunas atributos de la clase
    self.__FlyrVectIVectorLayer = None
    self.__outputFactory = SextanteGUI.getOutputFactory()
    #self.__outputFactory = OutputFactory
    self.__algorithms = dict()
    
    keySetIterator = Sextante.getAlgorithms().keySet().iterator()
    while(keySetIterator.hasNext()):
      key = keySetIterator.next()
      algorithms = Sextante.getAlgorithms().get(str(key))
      for name in algorithms.keySet():
        self.__algorithms[str(name)] = algorithms.get(name)
    #print self.__algorithms

  def __createSextanteLayer(self, layer):
    slayer = FlyrVectIVectorLayer()
    slayer.create(layer)
    return slayer
  
  def getAlgorithms(self):
    return self.__algorithms

  def execute(self, algorithmId, **kwparams):
    # Pillo el geoproceso
    algorithm = self.getAlgorithms()[algorithmId]
    # Rellenamos los parametros del geoproceso a partir
    # de los parametros indicados en kwparams.
    params = algorithm.getParameters()
    print "Parametros del geoproceso:", params
    for i in range(0,params.getNumberOfParameters()):
      param = params.getParameter(i)
      paramValue = kwparams[param.getParameterName()]
      if param.getParameterTypeName() == "Vector Layer":
        paramValue = self.__createSextanteLayer(paramValue())
      #Esto es si el parametro de entrada es un raaster, adaptarlo a sextante
      if param.getParameterTypeName() == "RasterLayer":
        print "tak"
        #paramValue = self.__createSextanteRaster(paramValue())
      param.setParameterValue(paramValue)
    #print algorithm.commandLineHelp
    #print algorithm.algorithmAsCommandLineSentences
    # Ejecutamos el geoproceso
    """
    output0 = algorithm.getOutputObjects().getOutput(0)
    output1 = algorithm.getOutputObjects().getOutput(1)
    output2 = algorithm.getOutputObjects().getOutput(2)
    print output0.getTypeDescription(), output0.getName()
    print output1.getTypeDescription(), output1.getName()
    print output2.getTypeDescription(), output2.getName()
    print "*******"
    print "Tipo", type(output0.getOutputChannel())
    print "OutputChannel:", output0.getOutputChannel()
    print "Filename:", output0.getOutputChannel().getFilename()
    out0 = output0.getOutputChannel()
    out1 = output1.getOutputChannel()
    out2 = output2.getOutputChannel()
    print "outs:",out0, out1, out2
    out0.setFilename("C:/Users/Oscar/AppData/Local/Temp/tmp-andami/p01mm.shp")
    out1.setFilename("C:/Users/Oscar/AppData/Local/Temp/tmp-andami/l01mm.shp")
    out2.setFilename("C:/Users/Oscar/AppData/Local/Temp/tmp-andami/c01mm.shp")
    """
    #Extension
    #es.unex.sextante.dataObjects.ILayer
    
    envelope = currentView().getMap().getFullEnvelope()
    geomEnvelope = envelope.getGeometry()
    frame = geomEnvelope.getBounds2D()
    aExtent = AnalysisExtent()
    aExtent.addExtent(frame)
    algorithm.setAnalysisExtent(aExtent)
    
    algorithm.execute(None,self.__outputFactory)

    # recogemos los valores de retorno y rellenamos un
    # un diccioanrio de python para devolverlos.
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

#
# Funcion para probar a ejecutar el geoproceso de ShiftXY
# No se por que falla la segunda vez si no borro los ficheros que se han
# generado en el temporal/tmp-andami
def testRunShiftXY(geoprocess):
  #r = geoprocess.execute("gvSIG-xyshift", LAYER=currentLayer(), X=100, Y=100, CHECK=False)
  #r = geoprocess.execute("pointstoline",LAYER=currentLayer())
  r = geoprocess.execute("perturbatepointslayer", LAYER = currentLayer(),MEAN = 10, STDDEV = 10 )
  #r = geoprocess.execute("generaterandomnormal", MEAN = 30, STDDEV = 30 )
  #r = geoprocess.execute("generaterandombernoulli",PROB=50)
  view = currentView()
  for value in r.values():
    print value, value.getDataStore().getFullName()
    if isinstance(value,FLayer): loadShapeFile(str(value.getDataStore().getFullName()))
  # Parece que la layer no se ha construido correctamente y al añadirla a la vista
  # peta. Si añadimos los ficheros desde el IU parece que funciona.
  #  if isinstance(value,FLayer):
  #    view.addLayer(value)
  

#
# Funcion de test que saca por consola los algoritmos que
# hay y la definicion de los parametros que llevan.
def printAlgorithms(geoprocess):
  # Me recorro los algoritmos
  for algorithmId, algorithm in geoprocess.getAlgorithms().items():
    # Vuelco los datos generales del algoritmo: id, grupo, nombre, descripcion
    #[1] runalg("randomvector", "100", "0", "C:\\Users\\Oscar\\Desktop\\jkl")
    if algorithmId == "perturbatepointslayer": pass
    else: continue
    print algorithm.commandLineHelp
    """
    print "Algorithm ID: ",algorithmId
    print algorithm.getGroup()    
    print algorithm.getName()
    if algorithm.getDescription()==None:
      print "(sin descripcion)"
    else:
      print algorithm.getDescription()
    print "Parametros:"
    params = algorithm.getParameters()
    for i in range(0,params.getNumberOfParameters()):
      param = params.getParameter(i)
      print "  ", param.getParameterName(), " de tipo ", repr(param.getParameterTypeName())
      print "    ", param.getParameterDescription()
    print "Salidas:"
    oos = algorithm.getOutputObjects()
    for i in range(0,oos.getOutputObjectsCount()):
      oo = oos.getOutput(i)
      print "  ", oo.getName(), " de tipo ", repr(oo.getTypeDescription())
      print "    ", oo.getDescription()
    """

def main(*args):
  geoprocess = Geoprocess()
  printAlgorithms(geoprocess)
  testRunShiftXY(geoprocess)
