# -*- coding: utf-8 -*-
#
# File: gvpy.py
# Version: v0.4
#

__author__ = """Oscar Martinez Olmos <masquesig@gmail.com>"""

import gvsig
import geom
import gvsig_raster
from org.gvsig.app import ApplicationLocator
from org.gvsig.fmap.dal import DALLocator
import os.path
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

#With True will appear a lot of extra info about all steps through the process
DEV_INFO = False

class Geoprocess:
  def __init__(self):
    Sextante.initialize()
    SextanteGUI.initialize()
    self.__FlyrVectIVectorLayer = None
    self.__outputFactory = SextanteGUI.getOutputFactory()
    self.__algorithms = dict()
    self.__defaultAE = None #default AExtension

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

  def __defineParameters_str2value(self, i, param, kwparams):
      if param.getParameterName() in kwparams:
          paramValue = kwparams[param.getParameterName()]
      else:
          paramValue = kwparams[i]

      #Input params: Tranform STRING to NUMERIC
      cond1 = (str(param) == "Numerical Value")
      cond2 = (str(param) == "Selection")
      isstr = isinstance(paramValue, str)
      cond4 = (str(param) == "Boolean")
      cond5 = (str(param) == "Table Field")
      if "Multi" in (str(param)):
          cond6 = True
      else:
          cond6 = False
      cond7 = (str(param) == "Point")

      if isstr:
          if cond1:
              paramValue = float(paramValue)
          elif cond2:
              paramValue = int(paramValue)
          elif cond4:
              paramValue = eval(paramValue.capitalize())
          elif cond5:
              paramValue = int(paramValue)
          elif cond6:
              #  <type 'java.util.ArrayList'>
              paramValue = list(paramValue)
          elif cond7: #Point
              paramValue = paramValue.split(',')
              x = float(paramValue[0])
              y = float(paramValue[1])
              paramValue = java.awt.geom.Point2D.Double(x, y)
          else: #is str
              pass
      else:
          if cond7: #punto de gvsig. agregar condicion punto
              x = paramValue.getX()
              y = paramValue.getY()
              paramValue = java.awt.geom.Point2D.Double(x, y)
      if DEV_INFO:
          print "Param Name: ", param.getParameterName()
          print "Param: ", param
          print "Resulta: ", paramValue, type(paramValue)
      return paramValue

  def __defineParameters_vector2sextante(self, param, paramValue):
              if isinstance(paramValue, str):
                  layer = gvsig.currentView().getLayer(paramValue)
                  paramValue = self.__createSextanteLayer(layer())
              else:
                  paramValue = self.__createSextanteLayer(paramValue())

              if DEV_INFO: print "extent add+"
              if self.__defaultAE == None:
                  self.__defaultAE = AnalysisExtent(paramValue)
              else:
                  self.__defaultAE.addExtent(AnalysisExtent(paramValue))
              if DEV_INFO: print "PARAM VALUE 1: ", paramValue
              return paramValue

  def __defineParameters_multi2sextante(self, param, paramValue):
              if DEV_INFO: print "PARAM VALUE PRE", paramValue
              paramValue2 = []
              for i in paramValue:
                  if isinstance(i, str):
                      layer = gvsig.currentView().getLayer(i)
                      i = self.__createSextanteLayer(layer())
                      ii = self.__createSextanteLayer(layer())

                  else:
                      if DEV_INFO: print type(i)
                      if isinstance(i, tuple): #si dentro de la lista viene una tupla identificamos que es un raster y su banda
                          from es.unex.sextante.parameters import RasterLayerAndBand
                          rlb = RasterLayerAndBand(self.__createSextanteRaster(i[0]),i[1])  #puesta numero de banda

                          ii = self.__createSextanteRaster(i[0])
                          i = rlb
                          if DEV_INFO: print "*************************** RASTERLAYERBAND", rlb

                      else:
                          if str(type(i)) == "<type 'org.gvsig.raster.fmap.layers.DefaultFLyrRaster'>":
                              ii = self.__createSextanteRaster(i)
                              i = self.__createSextanteRaster(i)
                          else:
                              ii = self.__createSextanteLayer(i())
                              i = self.__createSextanteLayer(i())

                      if DEV_INFO: print "createStextenatnte Layer i :", i
                      paramValue2.append(i)

                  if self.__defaultAE == None:
                          try:
                              self.__defaultAE = AnalysisExtent(AnalysisExtent(ii))
                              self.__defaultAE.setCellSize(0.49) ### test
                              self.__defaultAE.setCellSizeZ(0.49)  ### test
                              #self.__defaultAE.addExtent( )
                              if DEV_INFO: print "----------- ini defaultAE"
                          except:
                              try:
                                  self.__defaultAE = AnalysisExtent(ii())
                              except:
                                  self.__defaultAE = AnalysisExtent(ii)
                  elif self.__defaultAE != None:
                          try:
                              ae = self.__defaultAE
                              #ae.addExtent(AnalysisExtent(ii))
                              if DEV_INFO: print "------------ diferente defaultAE"
                          except:

                              self.__defaultAE.addExtent(AnalysisExtent(ii()))

                  """
                  if self.__defaultAE == None:
                      try:
                          self.__defaultAE = AnalysisExtent(i)
                      except:
                          print "excepttttttttttttttt", i
                          ae = i.getRasterLayer()
                          self.__defaultAE = AnalysisExtent(ae)
                  else:
                      try:

                          self.__defaultAE.addExtent(AnalysisExtent(i))
                      except:
                          print 'exceptttttttttttttt 222222222"', i
                          ae = i.getRasterLayer()
                          print 'ae',ae
                          self.__defaultAE.addExtent(AnalysisExtent(ae))
                          #print self.__defaultAE
                  """

              paramValue = paramValue2
              from java.util import ArrayList
              if DEV_INFO:
                  print "PARAM VALUE 2: ", paramValue
                  print "****************** CONDI6: ", paramValue
                  print "****************** CONDI6: ", ArrayList(paramValue)
              newParamValue = ArrayList()
              for i in paramValue:
                  newParamValue.add(i)
              paramValue = newParamValue
              #print "***************** CONDI6: ", paramValue
              #from es.unex.sextante.parameters import ParameterMultipleInput
              #pmi = ParameterMultipleInput()
              #pmi.setParameterValue(paramValue)
              #paramValue = pmi
              if DEV_INFO: print "#####################################################################"
              return paramValue

  def __defineParameters_raster2sextante(self, param, paramValue):
              if isinstance(paramValue, str):
                  layer = gvsig.currentView().getLayer(paramValue)
                  paramValue = self.__createSextanteRaster(layer)
              else:
                  paramValue = self.__createSextanteRaster(paramValue)

              if DEV_INFO: print "** extent add+"
              if self.__defaultAE == None:
                  self.__defaultAE = AnalysisExtent(paramValue)
              else:
                  self.__defaultAE.addExtent(AnalysisExtent(paramValue))
              return paramValue

  def __defineParameters_table2sextante(self, param, paramValue):
              if isinstance(paramValue, str):
                  layer = gvsig.currentProject().getTable(paramValue)
                  paramValue = self.__createSextanteTable(layer())
              else:
                  paramValue = self.__createSextanteTable(paramValue())
              return paramValue

  def __defineParameters(self, algorithm, kwparams):
      """ Define input parameters """
      params = algorithm.getParameters()
      if DEV_INFO: print self.__defaultAE

      for i in xrange(0,params.getNumberOfParameters()):
          param = params.getParameter(i)
          if DEV_INFO: print "****************************************** PARAMETER *******************************************"
          #print "********************* ", dir(param)
          #print "********************* ", type(param)
          #print "********************* ", param.getParameterName()
          #print "********************* ", param.getParameterDescription()
          #print "********************* ", param.getParameterTypeName()
          #print "********************* ", param.getParameterTooltip()
          #print "********************* ", param.getParameterClass()
          #print "********************* ", param.getClass()
          #print "********************* ", param.parameterName
          #print "********************* ", param.parameterTypeName
          paramValue = self.__defineParameters_str2value( i, param, kwparams)
          #print type(paramValue)

          #Vector to SEXTANTE
          if DEV_INFO: print  "PARAMETER TYPE: ",param.getParameterTypeName()
          if param.getParameterTypeName() == "Vector Layer":
              paramValue = self.__defineParameters_vector2sextante(param, paramValue)

          # Multiple input: Vector and Raster
          elif param.getParameterTypeName() == "Multiple Input": #para vectores y raster
              paramValue = self.__defineParameters_multi2sextante(param, paramValue)
          #Raster to SEXTANTE
          elif param.getParameterTypeName() == "Raster Layer":
              paramValue = self.__defineParameters_raster2sextante(param, paramValue)
          #Table to SEXTANTE
          elif param.getParameterTypeName() == "Table":
              paramValue = self.__defineParameters_table2sextante(param, paramValue)
          #Set parameter value
          #print  "@@@@@@@@@@@@@@@@@@@@@@@@ cluster error: ", paramValue, type(paramValue)
          #print "@@@@@@@@@@@@@@@@@@@@@@@@ ", type(param)

          param.setParameterValue(paramValue)
          #print "@@@@@@@@@@@@@@", dir(param)

          #print "@@@@@@@@@@@@@@", param.isParameterValueCorrect()
          #print "@@@@@@@@@@@@@@ param:", param
          #print "@@@@@@@@@@@@@@ ", param.getParameterValueAsArrayList()


  def __defineExtent(self, algorithm, kwparams):
      """ Define Analysis Extent """
      if self.__defaultAE == None:
          if DEV_INFO: print "-------- cambiar extent"
          change=True
      else:
          if DEV_INFO: print "-------- no cambiar extent"
          change = False
          AExtent = self.__defaultAE
      changeCell = False
      if 'EXTENT' in kwparams.keys() and algorithm.getUserCanDefineAnalysisExtent() :
          changeCell = True
          frame = kwparams['EXTENT']
          if isinstance(frame, str): frame = gvsig.currentView().getLayer(frame)
          #print ("|"+str(frame)+"||"+str(type(frame)))
          if isinstance(frame, str) or isinstance(frame, gvsig.View):
              AExtent = AnalysisExtent()
              if DEV_INFO: print "| EXTENT from VIEW"
              if isinstance(frame, gvsig.View): view = frame
              else: view = gvsig.currentProject().getView(frame)
              envelope = view.getMap().getFullEnvelope()
              xlow = envelope.getLowerCorner().getX()
              ylow = envelope.getLowerCorner().getY()
              xup = envelope.getUpperCorner().getX()
              yup = envelope.getUpperCorner().getY()
              AExtent.setXRange(xlow, xup, False)
              AExtent.setYRange(ylow, yup, False)
              AExtent.setZRange(0, 0, False)
          elif isinstance(frame, DefaultFLyrRaster):
              if DEV_INFO: print "| EXTENT from RASTER"
              layer = self.__createSextanteRaster(frame)
              AExtent = AnalysisExtent(layer)
              changeCell = False
              #AExtent.setZRange(0, 1, True)
              if DEV_INFO: print AExtent
          elif isinstance(frame, list):
              if DEV_INFO: print "| EXTENT from LIST"
              AExtent = AnalysisExtent()
              AExtent.setCellSize(0.49)
              AExtent.setCellSizeZ(0.49)
              xlow, ylow, zlow, xup, yup, zup  = frame[0], frame[1], frame[2], frame[3], frame[4], frame[5]
              AExtent.setXRange(xlow, xup, True)
              AExtent.setYRange(ylow, yup, True)
              AExtent.setZRange(zlow, zup, True)
          elif isinstance(frame, gvsig.Layer):
              if DEV_INFO: print "| EXTENT from Layer"
              layer = self.__createSextanteLayer(frame())
              AExtent = AnalysisExtent(layer)
          else:
              raise Exception("Not Extent Define")
          algorithm.setAnalysisExtent(AExtent)

      elif change == True:
          if DEV_INFO: print ("| Not Extent: No input data")
          AExtent = AnalysisExtent()
          changeCell = True
          if self.__defaultAE != None:
              if DEV_INFO: print "| Extent from Algorithm Layers"
              AExtent = self.__defaultAE
          else:
              try:
                  if DEV_INFO: print "| Extent from View"
                  envelope = gvsig.currentView().getMap().getFullEnvelope()
              except:
                  raise Exception("None open View")

              if DEV_INFO: print "| Setting AExtent: ",
              try: #from view
                  xlow = envelope.getLowerCorner().getX()
                  ylow = envelope.getLowerCorner().getY()
                  zlow = 0
                  xup = envelope.getUpperCorner().getX()
                  yup = envelope.getUpperCorner().getY()
                  zup = 0
                  if DEV_INFO: print "| View: ",
                  if DEV_INFO: print xlow, ylow, xup,yup
              except: # default
                  xlow, ylow, zlow, xup, yup, zup = 0,0,0,100,100,0
                  if DEV_INFO: print "| Default:", xlow, ylow, xup, yup

              frame = Rectangle2D.Double(xlow, ylow, xup, yup)
              AExtent.setXRange(xlow, xup, False)
              AExtent.setYRange(ylow, yup, False)
              AExtent.setZRange(zlow, zup, False)
          algorithm.setAnalysisExtent(AExtent)

      #Set: cellsize

      if 'CELLSIZE' in kwparams.keys():
          AExtent.setCellSize(kwparams['CELLSIZE'])
          if DEV_INFO: print "| New Cellsize: ", kwparams['CELLSIZE'], AExtent.getCellSize()
      elif changeCell == True:
          AExtent.setCellSize(AExtent.getCellSize())
          if DEV_INFO: print "| Cellsize: ", AExtent.getCellSize()

      if 'CELLSIZEZ' in kwparams.keys():
          AExtent.setCellSizeZ(kwparams['CELLSIZEZ'])
          if DEV_INFO: print "| New Cellsize Z: ", kwparams['CELLSIZEZ'], AExtent.getCellSizeZ()
      elif changeCell == True:
          AExtent.setCellSize(AExtent.getCellSizeZ())
          if DEV_INFO: print "| CellsizeZ: ", AExtent.getCellSizeZ()

      if DEV_INFO: print "Å‚Å‚ end extent: ", AExtent
      #AExtent.setZRange(0.0, 0.0, True)
      algorithm.setAnalysisExtent(AExtent)
      if DEV_INFO: print ("| Set Extent")

  def __defineOutput(self, algorithm, kwparams):
    if 'PATH' in kwparams.keys():
        path = kwparams['PATH']
        checkFilesExist(path)
        outputSet = algorithm.getOutputObjects()
        if outputSet.getOutputDataObjectsCount() == 1:
            out1 = outputSet.getOutput(0)
            out1.setOutputChannel(FileOutputChannel("New_name"))
            out1channel = out1.getOutputChannel()
            if isinstance(path, str):
                out1channel.setFilename(path)
            elif isinstance(path, list):
                out1channel.setFilename(path[0])
            else:
                raise Exception("No valid path")
            if DEV_INFO: print "| PATH: Good path"
        elif outputSet.getOutputDataObjectsCount() > 1 and isinstance(path, list):
            for n in xrange(0, outputSet.getOutputDataObjectsCount()):
                out1 = outputSet.getOutput(n)
                out1.setOutputChannel(FileOutputChannel("New_name"))
                out1channel = out1.getOutputChannel()
                out1channel.setFilename(path[n])
                if DEV_INFO: print "| PATH: Good path"
        else:
            raise Exception("Bad path")

    elif algorithm.getOutputObjects().getOutput(0).getOutputChannel():
        output0 = algorithm.getOutputObjects().getOutput(0)
        out0 = output0.getOutputChannel()
        out0.setFilename(None)
        if DEV_INFO: print "| PATH: Without path"

  def __executeAlgorithm(self, algorithm):
    """Execute Algorithm"""
    #Check algorithm
    correctValues = algorithm.hasCorrectParameterValues()
    if DEV_INFO: print "| Parameter values:", correctValues
    if not correctValues: raise Exception("Not correct values")
    try:
        if DEV_INFO: print "| Pre-algorithm:", list(algorithm.algorithmAsCommandLineSentences)
    except:
        if DEV_INFO: print "| Not - algorithm"

    algorithm.execute( None, self.__outputFactory)
    print "| Algorithm:", list(algorithm.algorithmAsCommandLineSentences)

  def __getOutputObjects(self, algorithm):
    """Take outputObjets of the algorithm"""
    oos = algorithm.getOutputObjects()
    ret = dict()
    for i in xrange(0,oos.getOutputObjectsCount()):
      oo = oos.getOutput(i)
      value = oo.getOutputObject()
      if isinstance(value, FlyrVectIVectorLayer):
          if DEV_INFO: print "| Vector"
          store = value.getFeatureStore()
          layer = MapContextLocator.getMapContextManager().createLayer(value.getName(),store)
          store.dispose()
          ret[value.getName()] = layer
          layer.dispose()
      elif isinstance(value, IRasterLayer):
          if DEV_INFO: print "| Raster layer"
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
    if DEV_INFO: print "@@@@@@@@ ret:", ret
    return ret

  def __returnOutputObjects(self, r, kwparams):
      if r == None: return
      outList = []
      print "| Output layers: "
      for value in r.values():
        if isinstance(value, unicode):
            outList.append(value.encode("UTF-8"))
        elif isinstance(value, FLyrVect):
            print "|\t Value:", value.getName().encode("UTF-8")
            path = value.getDataStore().getFullName()
            print "|\t\tPath: ", path
            if "OUTVIEW" in kwparams: # other view
                viewName = (kwparams["OUTVIEW"]).decode("UTF-8")
                if "TOCNAME" in kwparams:
                    value = loadShapeFileNew(str(path), view=viewName, tocName=kwparams["TOCNAME"])
                else:
                    value = loadShapeFileNew(str(path), view=viewName)
            else: #current view
                if "TOCNAME" in kwparams:
                    value = loadShapeFileNew(str(path), tocName=kwparams["TOCNAME"])
                else:
                    value = loadShapeFileNew(str(path))


            outList.append(value)
        elif isinstance(value,FLayer):
            print "|\t Value:", value.getName()
            print "|\t\t", value.getFileName()[0]
            #Not yet: Waiting for new loadRasterLayer that can set OUTVIEW
            if "TOCNAME" in kwparams:
                value = loadRasterLayerNew(value.getFileName()[0], tocName=kwparams["TOCNAME"])
            else:
                value = loadRasterLayerNew(value.getFileName()[0])
                
            outList.append(value)
        else:
            print "|\t Non-type"
            print "\tValue: ", value
      print "\n"

      #Return object or list
      if len(r.values()) > 1: return outList
      elif len(r.values()) == 1: return value
      else: return None


  def execute(self, algorithmId, kwparams):
    print "| Algoritmo: ", algorithmId
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

    #Exec algorithm
    self.__executeAlgorithm(algorithm)

    #Output objects
    ret = self.__getOutputObjects(algorithm)
    r = self.__returnOutputObjects(ret, kwparams)

    return r

def unionParameters(params, kwparams):
    for i in range(0,len(params)):
      kwparams[i]=params[i]
    return kwparams

def runalg(algorithmId,*params, **kwparams):
    kwparams = unionParameters(params, kwparams)
    geoprocess = Geoprocess()
    r = geoprocess.execute(algorithmId, kwparams)
    del(geoprocess)
    return r


def loadShapeFileNew(shpFile, CRS='CRS:84', tocName=False, active=False, view=gvsig.currentView()):
    try:
        CRS = gvsig.currentView().getProjectionCode()
    except:
        pass
    layer = loadLayerNew('Shape', shpFile=shpFile, CRS=CRS, tocName=tocName, )
    if isinstance(view,str):
        view = gvsig.currentProject().getView(view)
    else:
        view= gvsig.currentView()
    view.addLayer(layer)
    layer.setActive(active)
    return gvsig.Layer(layer)
    
def loadLayerNew(layerType, tocName=False, **parameters): #
        try:
            application = ApplicationLocator.getManager()
            datamanager =  application.getDataManager()
            mapcontextmanager = application.getMapContextManager()
            store_parameters = datamanager.createStoreParameters(layerType)
            gvsig.copyToDynObject(parameters, store_parameters)
            store = datamanager.openStore(layerType, store_parameters)       
            if tocName!=False:
                nameStore = tocName
            else:
                nameStore = store.getName()
            layer = mapcontextmanager.createLayer(nameStore, store)
        except Throwable, ex:
            raise RuntimeException("Can't load layer, "+ str(ex))  

        return layer

def loadRasterLayerNew(rasterfile, mode = "r", tocName=False ):
    ## Load a Raster file in a Layer
    gvsig_raster.sourceFileName[0]=rasterfile
    if not isinstance (rasterfile,File):
        rasterfile = File(rasterfile)
    
    name, ext = gvsig_raster.splitext(rasterfile.getName())
        
    if tocName!=False:
        name = tocName
    else:
        name = name


    view = gvsig.currentView()
    
    # Get the manager to use
    dalManager = DALLocator.getDataManager()
    mapContextManager = MapContextLocator.getMapContextManager()

    if ext.lower() == ".ecw" or ext.lower() == ".jp2" :
        # FIXME
        pass
    elif ext.lower() == ".mrsid":
        # FIXME
        pass
    else:
        # Create the parameters to open the raster store based in GDAL
        params = dalManager.createStoreParameters("Gdal Store")
        params.setFile(rasterfile)

    # Create the raster store
    dataStore = dalManager.createStore(params)

    # Create a raster layer based in this raster store
    layer = mapContextManager.createLayer(name, dataStore);

    view.addLayer(layer)
    return layer
    
def algHelp(geoalgorithmId):
    geoprocess = Geoprocess()
    for algorithmId, algorithm in geoprocess.getAlgorithms().items():
        if algorithmId.encode('UTF-8') == geoalgorithmId.encode('UTF-8') or geoalgorithmId == "All": 
            pass
        else: 
            continue
        print "* Algorithm help: ", algorithm.getName().encode('UTF-8')
        print "*", algorithm.commandLineHelp.encode('UTF-8')
    del(geoprocess)

def algSearch(strSearch):
    print "\nInicio de busqueda.."
    geoprocess = Geoprocess()
    search = strSearch.lower().encode('ASCII','ignore')
    for algorithmId, algorithm in geoprocess.getAlgorithms().items():
        name = (algorithm.getName()).lower().encode('ASCII','ignore')
        group = (algorithm.getGroup()).lower().encode('ASCII','ignore')
        con1 = str(name).find(search) >= 0
        con2 = str(group).find(search) >= 0
        con3 = algorithmId.encode('ASCII').find(search) >= 0
        if con1 or con2 or con3:
            if con1 or con2:
                print "ID: ", algorithmId, " || GROUP: ", algorithm.getGroup().encode('UTF-8'), " || NAME: ", algorithm.getName().encode('UTF-8')
            else:
                print "*", algorithm.commandLineHelp.encode('UTF-8')
    print "..Busqueda finalizada\n"
    del(geoprocess)

def currentRaster():
    """Return first raster active layer on the View"""
    layers = gvsig.currentView().getLayers()
    lyrlist = [ layers[i] for i in range(0,layers.__len__())]
    for i in lyrlist:
      if i.isActive() and isinstance(i, DefaultFLyrRaster):  return i
    return None

def firstRaster():
    """Return first raster active layer on the View"""
    layers = gvsig.currentView().getLayers()
    lyrlist = [ layers[i] for i in range(0,layers.__len__())]
    for i in lyrlist:
      if isinstance(i, DefaultFLyrRaster):  return i
    return None

def sRaster(n):
    """Return first raster active layer on the View"""
    layers = gvsig.currentView().getLayers()
    lyrlist = [ layers[i] for i in range(0,layers.__len__())]
    count = 0
    for i in lyrlist:
      if isinstance(i, DefaultFLyrRaster):
          if count == n:
              return i
          else:
             count+=1
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
        if isinstance(view, str): view = gvsig.currentProject().getView(view)
        if isinstance(layer, str):
            return view.getLayer(layer)
        else:
            return layer
    except: #Bug: Raster problem with getLayer
        for i in gvsig.currentProject().getView(view).getLayers():
            if i.name == layer: return i

def getProjectTable(table):
    """Get table"""
    return gvsig.currentProject().getTable(table)

def checkFilesExist(files):
    """Path or Paths of files"""
    #raise a exception

    if isinstance(files, str):
        if os.path.isfile(files): raise Exception("File already exist" + files)
    elif isinstance(files, list):
        for fname in files:
            if os.path.isfile(fname): raise Exception("File already exist" + fname)

def main(*args):
    #checkFilesExist(["C:/gvsig/ran10.shp"])

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

    #algHelp("generaterandomnormal")
    """
    r = runalg("generaterandomnormal", 100,100, CELLSIZE=100, EXTENT=[250,250,0,500,500,0])
    r = runalg("generaterandomnormal", 10, 10, CELLSIZE=50, EXTENT=[500,500,0, 1000,1000,0])
    r = runalg("generaterandombernoulli", 50.0, CELLSIZE=25, EXTENT=[1000,1000,0, 1250,1250,0])
    r = runalg("gradientlines", r, 1, 100, 1)

    v1 = runalg("randomvector",10, TYPE_POLYGON, EXTENT=[0,0,0,500,500,0])
    v2 = runalg("randomvector", 5, TYPE_POLYGON, EXTENT=v1)
    v3 = runalg("difference", v1, v2, PATH="C:/gvsig/Diferencia.shp")
    v4 = runalg("randomvector", 5, 0, PATH="C:/gvsig/randomvector.shp", EXTENT=v3)
    v5 = runalg("randomvector", 100, 2, PATH="C:/gvsig/randompoints.shp", EXTENT="randomvector", OUTVIEW="Nueva")
    v6 = runalg("gvSIG-xyshift", "randompoints", "false", "-250.0", "-250.0", PATH=["C:/gvsig/ran1010.shp","C:/gvsig/ran2020.shp","C:/gvsig/ran3030.shp"])
    algHelp("tablebasicstats")
    v7 = runalg("gvSIG-buffer", "randompoints", False, 50.0, 0, False, True, 0, 0, PATH="C:/gvsig/buffer_gvsig0138.shp")
    v5 = runalg("randomvector", 100, 2, EXTENT=[0,0,0,500,500,0])

    #Test for model sextante
    v5 = runalg("randomvector", 10, 2, EXTENT=[0,0,0,500,500,0], OUTVIEW="Nueva")
    v5 = runalg("randomvector", "5", 2, EXTENT=[0,0,0,500,500,0], OUTVIEW="Nueva")

    r = runalg("generaterandomnormal", 100,100, CELLSIZE=1)

    vista= (gvsig.currentView().name).encode('UTF-8')
    """


    """
    vista= "Sin tÃ­tulo"
    #vista = vista.encode("UTF-8")

    print gvsig.currentProject().getView(vista)


    endid = "_104.shp"
    v = runalg("randomvector", 20, 0)
    v2 = runalg("randomvector", 20, 0,PATH=["C://gvsig//i"+endid])
    #fitpoints = runalg("fitnpointsinpolygon",v, "2", "74", 1, 0)
    intersection = runalg("gvSIG-intersection", v, getProjectLayer(gvsig.currentView(),"i_102"), True, True,PATH=["C://gvsig//inter_pol"+endid,"C://gvsig//inter_line"+endid,"C://gvsig//inter_point"+endid])
    """
    #algSearch("nodelines")
    #ID:  extractendpointsoflines  || GROUP:  Topolog????a  || NAME:  Obtener extremos de l??neas

    #v7 = runalg("gvSIG-buffer", v, "False", 50.0, 0, "false", "true", 0, 0)
    #print "**Addfield: ", gvpy.addField(v, "ID5")
    #import gvpy
    #gvpy.addField(v, "ID89")
    #runalg("vectoraddfield", v, "Campo1", 0, 1, 0, 1, PATH="C:\\Users\\Oscar\\Desktop\\testi.shp")
    #layer = runalg("randomvector", 20, TYPE_LINE, EXTENT=[0,0,0,500,500,0], OUTVIEW="Po1")

    #2015-1-2


    #runalg("graticulebuilder", "10.0", "10.0", 1, PATH="/home/oscm/temp/reticula10.shp")
    #layer1 = gvsig.currentView().getLayer("1")
    #layer2 = gvsig.currentView().getLayer("2")
    #print layer1, layer2
    #
    #algHelp("cluster")
    #runalg("merge", layer1, [layer2])

    #layer1 = sRaster(0)
    #layer2 = sRaster(1)
    #print "Layer1: ", layer1.name, layer1, layer1.getCellSize()
    #print "Layer2: ", layer2.name, layer2, layer2.getCellSize()


    #runalg("cluster" , INPUT=[(layer1, 0),(layer2,0)] , NUMCLASS=3)#, CELLSIZE=layer1.getCellSize(), CELLSIZEZ=1)#,EXTENT=layer1)
    #runalg("mergegrids", [layer1, layer2], "0")
    v1 = runalg("randomvector",10, TYPE_POLYGON, EXTENT=[0,0,0,500,500,0], TOCNAME="Random vector")
    r = runalg("generaterandomnormal", EXTENT = [0,0,0,500,500,0], MEAN =0.5, STDDEV = 0.5, TOCNAME="Raster Generate Random normal")
    print "end"

def mainLibrary():
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

    """
    layer = newLayer()
    addFeature(layer, "pol", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])
    addFeature(layer, "pol", "02", [[0,0],[10,5],[10,10],[0,10],[5,5]])
    addFeature(layer, "pol", "03", [[-50, -34],[0,0], [-14,30]])
    addField(layer,"campo3")
    modifyFeatures(layer, "campo3", "nuevo poligono")
    """
    """
    #Create shapes
    layer1 = newLayer(layer,"C:/gvsig/point_shape.shp", 1)
    layer2 = newLayer(layer,"C:/gvsig/line_shape.shp", 2)
    layer3 = newLayer(layer,"C:/gvsig/polygon_shape", 3)

    #Add features
    addFeature(layer1, "point", "01", [50,80])
    addFeature(layer1, "point", "02",[150,50])
    addFeature(layer1, "point", "03",[100,10])
    addFeature(layer1, "point", "04",[0,10])

    addFeature(layer3, "polygon", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])

    addFeature(layer2, "line", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])

    #Modify all values in one column
    modifyFeatures(layer1, "campo1", "Points_gsoc")
    modifyFeatures(layer2, "campo1", "Lines_gsoc")

    #Modify schema
    addField(layer1,"Name")
    removeField(layer1,"Surname")

    ##Execute SEXTANTE
    #r = geoprocess("perturbatepointslayer", LAYER = currentLayer(),MEAN = 5, STDDEV = 5 )
    """
    #layer = gvsig.currentView().getLayer("line_04.shp")
    #newLayer(layer, "C:/gvsig/gvpy_test006.shp")
    #layer2 = copyLayer(layer, "C:/gvsig/gvpy_copylayer_012.shp")
    #v = copyLayer(layer, "C:/gvpy_copylayer_new_06.shp")
    #layer = gvsig.currentView().getLayer("gvpy_copylayer_new_06")
    #addFeature(v, "Camino", [[50,00],[50,50],[10,10],[0,1],[50,18]])

    #Basics field
    """
    addField(v, "Direccion")
    modifyFeatures(v, "Direccion", "Av")
    removeField(v, "Direccion")
    """

    """
    #EJEMPLO 1
    #New shapes
    layer = gvpy.runalg("randomvector", 20, gvpy.TYPE_LINE, EXTENT=[0,0,0,500,500,0], OUTVIEW="Po1")
    #layer = gvsig.currentLayer()
    #Advanced field
    removeField(layer, "ID")
    removeField(layer, "Distance")
    addField(layer, "ID") #Add fields
    addField(layer, "Distance", "STRING")
    addField(layer, "Long", "LONG")
    removeField(layer, "Long") #Remove field
    modifyFeatures(layer, "ID", "90") #Modify all features
    modifyField(layer, "ID", "LONG") #Modify type of field
    modifyField(layer, "Distance", "FLOAT")
    addFeature(layer, 1, 0, [[50,0],[1000,0]]) #Add new feature with geometry line
    for feature in layer.features():
        perimeter = feature.geometry().perimeter()
        modifyFeature(layer, feature, "Distance", perimeter) #Modify each feature

    pass
    #FIN EJEMPLO 1
    """

    #modifyFeatures(gvsig.currentLayer(), "ID", 100, "Distance == 90")
    layer = gvsig.currentLayer()
    for feature in gvsig.currentLayer().features():
        value = feature.Distance
        #modifyFeature(layer, feature, "ID", distance)
        feature.edit()
        feature.set("ID", value)
        layer.update(feature)
    #model2script("C://gsoc//test02.model", "C://gsoc//nuevoScript.py")
    print "END TEST"

def copyLayerFeatures2Layer(layer1, layer2):
    for i in layer1.features():
        layer2.append(i.getValues())
    layer2.commit()

def copyLayer(layer, path):
    output = newLayer(layer, path)
    copyLayerFeatures2Layer(layer, output)
    #addLayerView(output)
    return output

def newLayer(layer, path, geometryType=None):
    CRS = layer.getProjectionCode()
    schema = gvsig.createSchema(layer.getSchema())
    if geometryType==None: geometryType = layer.getTypeVectorLayer().getType()
    output = gvsig.createShape( schema, path, CRS=CRS, geometryType=geometryType )
    gvsig.currentView().addLayer(output)
    return output

def addLayerView(layer):
    gvsig.currentView().addLayer(layer)

def addFeature(layer, *params, **kwparams):
    #IN: layer, feature params + geometry
    typeLayer = layer.getTypeVectorLayer().name
    #if kwparams != {}:
    #    layer.append(kwparams)
    #    layer.commit()
    #    return

    if "COMMIT" in kwparams:
        pass
    else:
        COMMIT=1
    if params != ():
        schValues = layer.getSchema().getAttrNames()
        values = {}
        itera = iter((list(params)))
        value = itera.next()
        for sch in schValues:
            #Si el campo a modificar es una geometria
            #print "ComprobaciÃ³n:", sch, isinstance(value, list)
            #re comprobacion si es campo geometry
            #bug: Comprobar si es lista o objeto geom  en primer if
            #... sch == "Geometry" and ES UNA LISTA
            #... sino copia el valor directamente: caso de pasar geometrias
            if sch == "GEOMETRY":
                print typeLayer
                if typeLayer == "Point2D":
                    if isinstance(value, list):
                        values[sch] = geom.createPoint(value[0],value[1])
                elif typeLayer == "MultiCurve2D":
                    if isinstance(value, list):
                        values[sch] = list2geomcurve(value)
                elif typeLayer == "MultiSurface2D":
                    if isinstance(value, list):
                        values[sch] = list2geompoly(value)
                else: #Si son geometrias
                    values[sch] = value
            else:
                values[sch] = value
            try:
                value = itera.next()
            except:
                break
        layer.append(values)
        if COMMIT==1: layer.commit()
    print "Add feature ", params, " to ", layer

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

def modifyFeatures(layer, field, value, COMMIT=1,FILTER=None):
    #IN: layer, field, new value
    if FILTER == None:
        features = layer.features()
    else:
        features = layer.features(FILTER)

    for feature in features:
        feature.edit()
        feature.set(field, value)
        layer.update(feature)
    if COMMIT==1: layer.commit()
    print "Modify feature ", layer.name, field, value

def showFields(layer):
    #IN: layer
    #OUT: str(atributos)
    print layer.getSchema().getAttrNames()

def addField(layer,field, sType = "STRING",iSize=20):
    #IN: layer, field, *sType, *iSize)
    #OUT: layer
    #addField(layer, "nombre")
    schema = gvsig.createSchema(layer.getSchema())
    schema.modify()
    if isinstance(field,str): schema.append(field,sType,iSize)
    layer.edit()
    layer.updateSchema(schema)
    layer.commit()
    print "Add field ", field, " to ", layer.name
    return layer

def modifyField(layer, field, iType="STRING", iSize=20):
    temp = []
    for i in layer.features():
        temp.append(i.get(field))
    removeField(layer, field)
    addField(layer, field, iType, iSize)
    n = 0
    for i in layer.features():
        modifyFeature(layer, i, field, temp[n],COMMIT=0)
        n += 1
    layer.commit()
    print "Modify field type to: ", field, " in ", layer.name

def modifyFeature(layer, feature, field, value, COMMIT=1):
    feature.edit()
    feature.set(field, value)
    layer.update(feature)
    print "Modify Feature field: ", field , " to ", value
    if COMMIT==1: layer.commit()

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


def model2script(pathXML, pathFile):
    #eliminar la ultima linea
    #pathXML = commonsdialog.openFileDialog("Selecciona archivo", 'C:/gsoc/')
    #pathXML = str(pathXML[0])
    #pathXML = 'C:/gsoc/test02.model'
    #pathFILE = 'C:/gsoc/script0002.py'
    import os.path
    if os.path.isfile(pathXML)==True:
        pass
    else:
        print "No valid model file path"
        return
    fileFile = open(pathXML, 'r')
    document = fileFile.read()
    import xml.dom.minidom
    root = xml.dom.minidom.parseString(document)
    #root
    inputObject = {}
    inputObjectParams = {}
    dataObject = {}
    algorithms = {}
    tab = "    "
    gvpyFile = open(pathFile, "w")
    #Cargamos los parametros
    print "\nData object"
    for child in root.getElementsByTagName("data_object"):
        #data_object - Parametros
        if "INNER" in child.getAttribute("key"):
            inputObjectParams[child.getAttribute("key")] = child.getAttribute("value")
        #data_object - result of algorithms
        else:
            inputObject[child.getAttribute("key")]=[child.getAttribute("value"), child.getAttribute("description").encode("UTF-8")]

    print "\n Attribute"
    for child in root.getElementsByTagName("input"):
        for i in child.getElementsByTagName("attribute"):
                if i.getAttribute("name")=="default": dataObject[child.getAttribute("name")] = i.getAttribute("value")

    print "\n Algorithm"
    order = 1
    for child in reversed(root.getElementsByTagName("algorithm")):
        print "Algoritmo: ", child
        keyAlgorithm = child.getAttribute("key")
        algorithmParams = {}
        algorithmParams["alg_cmd_line_name"]=child.getAttribute("alg_cmd_line_name")
        for i in child.getElementsByTagName("assignment"):
            algorithmParams[i.getAttribute("key")] = i.getAttribute("assigned_to")
        algorithmParams["result_of_algorithm"] = keyAlgorithm
        algorithms[order] = algorithmParams
        order +=1

    print "\n\n******* RESULTADO *******"
    print "inputObject: ", inputObject
    print "inputObjectParams: ", inputObjectParams
    print "algorithms: ", algorithms
    print "data object: ", dataObject

    #Writing script .py
    print "\nTransform to gvpy"
    for i in root.getElementsByTagName("model"):
        modelName = i.getAttribute("name")
    gvpyFile.write("# Modelo de SEXTANTE: " + modelName)
    gvpyFile.write(
"""
import gvpy
import gvsig
import geom
import gvsig_raster

def main(*args):
""")

    print "gvpy - data_object"
    listInputObject = []
    for n in reversed(inputObject.keys()):
        listInputObject.append([n,inputObject[n][1]])

    print "gvpy - inputObjectParams"
    for n in (inputObjectParams.keys()):
        gvpyFile.write( tab + n + ' = "' + inputObjectParams[n] + '"\n' )

    print "gvpy - vars"
    for n in (dataObject.keys()):
        gvpyFile.write( tab + n +' = "' + dataObject[n] + '"\n\n' )


    print "gvpy - algorithms"
    #inputObject list of result algorithms names
    for n in reversed(sorted(algorithms.keys())): #reversed(algorithms.keys()):
        gvpy= ""
        alg = algorithms[n]
        #prefijo: buscar en los data_object el nombre que debe de llevar la capa resultado
        for i in listInputObject:
            if alg["result_of_algorithm"] in i[0]:
                prefix = i[0]
                description = i[1]
        #Escribimos el codigo del algoritmo
        gvpyFile.write( tab + '# '+ description + '\n')
        gvpy += prefix + '= gvpy.runalg("'+alg["alg_cmd_line_name"]+'"'
        for i in alg:
            if i == "alg_cmd_line_name" or i == "result_of_algorithm": continue
            gvpy += ', '+i+'='+ alg[i] + ''
        gvpy += ')'
        gvpyFile.write( tab + gvpy + "\n\n" )

    gvpyFile.close()
