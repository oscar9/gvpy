
import gvsig
import geom
import gvpy

def main(*args):
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
            #print "Comprobación:", sch, isinstance(value, list)
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

    fileFile = open(pathXML, 'r')
    document = fileFile.read()
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
    
    
    print "gvpy - algoritms"
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

