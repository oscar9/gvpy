#GSoC Project 2014: 
##Access geoprocessing tools with gvsig 2.x scripting framework 
----------
**Working for gvSIG and OSGeo Foundation**


Developing for gvSIG 2.x:
 
**Do you want to know more about what am i doing?**
Visit my project page: [\[gvpy project\]][1]

**How install gvpy?**

 1. You just need [gvSIG 2.x][2] 
 2. Download `src/gvpy.py`, you don't need more.
 2. Move `gvpy.py` to C:\Users\[name]\gvSIG\Plugins\org.gvsig.scripting.app.extension\lib
 3. Open gvSIG 2.1 Desktop, and go to Scripting Composer or Jython Console
 4. Write before your script: `import gvpy`

----------
###Src folder:

###gvpy_library.py + gvpy_algortihms = **gvpy**
That means, access to shortcuts for coding inside gvsig, and access to geoprocess algorithms

####**I. gvpy_algorithms.py **
Developing access to SEXTANTE and gvSIG-geoprocess. 
This library will allow you to launch one geoprocess with your jython script.

##### Ex: Access to SEXTANTE
```
    r = geoprocess("perturbatepointslayer", LAYER = layer1,MEAN = 5, STDDEV = 5 ) 
```


----------


####**II. gypy_library.py**
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
You can find more info about what is gvpy here: http://oscar9.github.io/gvpy/

And my weekly reports: http://masquesig.com/category/gsoc-2/


  [1]: http://oscar9.github.io/gvpy/
  [2]: http://www.gvsig.org/plone/home/projects/gvsig-desktop/official/gvsig-2.1/descargas