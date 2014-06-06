# -*- coding: utf-8 -*-
#
# File: gvpy.py
#

__author__ = """Óscar Martínez Olmos <masquesig@gmail.com>"""

import gvsig
import geom
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
        
        
    
    #Ejecutar algorithm
    algorithm.execute(None,self.__outputFactory)
    print algorithm.algorithmAsCommandLineSentences

    #Archivo de salida
    if 'PATH' in kwparams.keys():
        path = kwparams['PATH']
        output0 = algorithm.getOutputObjects().getOutput(0)
        out0 = output0.getOutputChannel()
        out0.setFilename(path)
    else: 
        output0 = algorithm.getOutputObjects().getOutput(0)
        out0 = output0.getOutputChannel()
        out0.setFilename(None)
        
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
  view = gvsig.currentView()
  outList = []
  
  print "Output layers: "
  for value in r.values():
    print "\t", value, value.getDataStore().getFullName()
    if isinstance(value,FLayer): 
        out = gvsig.loadShapeFile(str(value.getDataStore().getFullName()))
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
            #print "Comprobación:", sch, isinstance(value, list)
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