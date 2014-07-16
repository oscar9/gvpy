import xml.dom.minidom

def main(*args):
    #eliminar la ultima linea
    pathXML = 'C:/gsoc/test02.model'
    pathFILE = 'C:/gsoc/script0002.py'

    fileFile = open(pathXML, 'r')
    document = fileFile.read()
    root = xml.dom.minidom.parseString(document)
    #root
    inputObject = {}
    inputObjectParams = {}
    dataObject = {}
    algorithms = {}
    tab = "    "
    gvpyFile = open(pathFILE, "w")
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

