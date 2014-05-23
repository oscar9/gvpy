gvpy
====

GSoC Project 2014: access geoprocessing tools with scripting framework for gvsig 2.x
Working for gvSIG and OSGeo

Developing access to SEXTANTE and gvSIG-geoprocess. This library will allow you to launch one geoprocess with your jython script.

Ex: >>> geoprocess(“gvSIG-xyshift”, LAYER=currentLayer(), X=150, Y=150, CHECK=False) 
