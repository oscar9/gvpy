gvpy
====

GSoC Project 2014: access geoprocessing tools with scripting framework for gvsig 2.x
Working for gvSIG and OSGeo

I. geoprocess_access.py
Developing access to SEXTANTE and gvSIG-geoprocess. This library will allow you to launch one geoprocess with your jython script.

Ex: 

        r = geoprocess("perturbatepointslayer", LAYER = layer1,MEAN = 5, STDDEV = 5 ) 



II. gypy.py
For now, this library will be to develop easy access to the scripting functions. With less code will be more easy, and more powerful.

Ex:

        #New shape
        layer3 = newLayer(layer,"C:/gvsig/polygon_shape", 3) 
        #Add new features 
        addFeature(layer1, "point", "04",[0,10]) 
        addFeature(layer2, "line", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])         #New Line 
        addFeature(layer3, "polygon", "01", [[50,80],[150,50],[100,10],[0,10],[50,80]])          #New polygon  
        #Modify all values in one column 
        modifyFeatures(layer1, "field1", "Points_gsoc") 
        modifyFeatures(layer2, "field1", "Lines_gsoc") 
        #Modify schema 
        addField(layer1,"Name") 
        removeField(layer1,"Name") 

You can find more info about what is gvpy here: http://oscar9.github.io/gvpy/

And my weekly reports: http://masquesig.com/category/gsoc-2/
