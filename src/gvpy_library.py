
import gvsig
import geom

def main(*args):
    layer = gvsig.currentLayer()
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
            #print "Comprobaci�n:", sch, isinstance(value, list)
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
