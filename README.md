#GSoC Project 2014: 
##Access to geoprocessing tools with gvSIG 2.x Scripting Framework 
**Working for gvSIG and OSGeo Foundation**

----------
###gvpy: USER GUIDE in English
https://github.com/oscar9/gvpy/blob/master/gvpy_user_guide.md

All the options needed for launch geoprocess from the Scripting Framework

###gvpy: GUÍA DE USO en Español
https://github.com/oscar9/gvpy/blob/master/gvpy_guia_de_uso.md

Todas las opciones disponibles para lanzar geoprocesos desde el Módulo de Scripting

> See one good example using gvpy! Go to the the folder `/example/` inside this repository

----------

##Install
###Developing for gvSIG 2.x
 
**Do you want to know more about what am i doing?**
Visit my project page: [\[gvpy project\]][1]
Or read all my weekly reports in my blog: [\[weekly reports\]][2]

**How install gvpy?**

 1. You just need [gvSIG 2.x][3] 
 2. Download `src/gvpy.py`, you don't need more.
 3. Move `gvpy.py` to C:\Users\[name]\gvSIG\Plugins\org.gvsig.scripting.app.extension\lib
 4. Open gvSIG 2.1 Desktop, and go to Scripting Composer or Jython Console
 5. Write before your script: `import gvpy`

##Test
Now try to use it:

 1. You can download: `src/test_import_gvpy.py`
 2. Create a new View in a new Project
 3. Open gvSIG 2 - Tools - Scripting Composer 
 4. Copy text inside `test_import_gvpy.py` & Paste inside a new script, execute!
 5. Commets in every line of code inside test_import_gvpy.py, this will help you to understand how it works

![Result of test_import_gvpy.py][5]

----------
###Src folder:

###`gvpy_library`  +  `gvpy_algortihms` = **gvpy**
That means, access to shortcuts for coding inside gvsig, and access to geoprocess algorithms


### I. gvpy_algorithms.py
Developing access to SEXTANTE and gvSIG-geoprocess. 
This library will allow you to launch one geoprocess with your jython script.

##### Ex: Access to SEXTANTE
```python
    r = gvpy.runalg("perturbatepointslayer", LAYER = currentLayer(),MEAN = 5, STDDEV = 5 ) 
    r = gvpy.runalg("generaterandomnormal", EXTENT = [0,0,0,500,500,0], CELLSIZE=10, MEAN =0.5, STDDEV = 0.5)
    v = gvpy.runalg("randomvector", 20, 1, EXTENT=gvsig.currentView(), PATH = "C://gvsig//random_vector.shp")
```


----------


### II. gypy_library.py
(I will develop this part in the next weeks)
For now, this library will be to develop easy access to the scripting functions. With less code will be more easy, and more powerful.

#####Ex: Shortcuts for gvSIG Scripting
```
    #New shape
    layer3 = newLayer(layer,"C:/gvsig/polygon_shape", 3) 
    #Add new features 
    addFeature(layer1, "point", "04",[0,10]) 
    addFeature(layer2, "line", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])
    #New Line 
    addFeature(layer3, "polygon", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])
    #New polygon  
    #Modify all values in one column 
    modifyFeatures(layer1, "field1", "Points_gsoc") 
    modifyFeatures(layer2, "field1", "Lines_gsoc") 
    #Modify schema 
    addField(layer1,"Name") 
    removeField(layer1,"Name") 
```

### III. xml_model2script.py

> UPDATE: Now is inside gvpy! Just execute `gvpy.model2script(pathModel, pathNewScript)`

Script for gvSIG 2 that allows export from SEXTANTE.model to Python Script with one click.

![Export SEXTANTE.model to Script][4]






#Info
You can find more info about what is gvpy here: http://oscar9.github.io/gvpy/

And my weekly reports: http://masquesig.com/category/gsoc-2/


  [1]: http://oscar9.github.io/gvpy/
  [2]: http://masquesig.com/category/gsoc-2/
  [3]: http://www.gvsig.org/plone/home/projects/gvsig-desktop/official/gvsig-2.1/descargas
  [4]: https://raw.githubusercontent.com/oscar9/gvpy/master/data/images/modelosextante-scripting.png
  [5]: https://raw.githubusercontent.com/oscar9/gvpy/master/data/images/test_import_gvpy.png
