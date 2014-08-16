
#gvpy: User guide



----------

**Access to geoprocessing tools with gvSIG 2.x Scripting Framework**

Github have the code you need and i explain there all the updates: https://github.com/oscar9/gvpy
What is gvpy: http://oscar9.github.io/gvpy/

Autor: **Óscar Martínez Olmos**
Email: <masquesig@gmail.com>
Blog: http://www.masquesig.com
Twitter: https://twitter.com/masquesig

----------


[TOC]

The geoprocessing tools of gvSIG and SEXTANTE are now accessible using just one line of code and can be part of your scripts. You could execute them from the Jython Console or from the Scripting Composer, both of them are inside the Scripting Framework. This scripting module are only available since the new version of gvSIG 2 or greater. 

##gvpy library
The first thing you have to do is download the library, is just one file. Name of this file is: gvpy.py
https://raw.githubusercontent.com/oscar9/gvpy/master/src/gvpy.py

You should move them to:
 `C:\Users[name]\gvSIG\Plugins\org.gvsig.scripting.app.extension\lib`

If you have opened gvSIG, you should **close it and open it again**.

Now, to use this library in your scripts, you just have to write at the beginning of your scripts or in the Jython Console this:

```
import gvpy
```

This will allow you to use the gvpy library and access to all the functions.

##Algorithms
The algorithms that are available with the gvpy library, you can also use them without using scripting and find them in: `Tools - Geoprocessing - Tool box`

You will have access to gvSIG-Geoprocess and SEXTANTE.

Inside the tool box, you can search for algorithms, but with gvpy too.

If we open the Jython Console `Tools-Scripting-Jython Console` and write: `import gvpy` we can access to all the library. This functions that i'm going to explain you can also use them from the Scripting Composer.

For example, if we want to search for a algorithm that create random geometries, we can search something like this: 
`gvpy.algSearch("aleatorias")`

> Sorry, but gvSIG-Geoprocess and SEXTANTE descriptions, for now, are write in Spanish.

From the result that appear, we can find one algorithm call it: `randomvector`

##Parameters of the algorithm
If we want to know more about this algorithm we can write the same function that we used, but now with:
`gvpy.algSearch("randomvector")`

If the name match with the name of one algorithm, gvpy will show you the info about that algorithm, description and parameters:

```
gvpy.algSearch("randomvector")
* Algorithm help: 
Capa vectorial con geometrias aleatorias
*
Usage: runalg( "randomvector",
                               COUNT[Numerical Value],
                               TYPE[Selection],
                               RESULT[output vector layer],
                               );
```

If you search for a algorithm using the Tool Box, you can find the key-name of that algorithm. Double-click to open the algorithm, and you will find one button for help and also, one box in the left-down corner with the key-name. If this box doesn't appear, you can close and open again the algorithm and probably now will appear.

## Line of code
Now **we know all the parameters** needed for execute the `randomvector` algortihm, we will write them like one line of code:

We have to write `gvpy.` to access to the gvpy library that we imported before with `import gvpy`. We will not use the parameter `RESULT`. When the parameter is about the output layers, we will not needed. So, we can write the algorithm now.

Example: `gvpy.runalg("randomvector", COUNT= , TYPE= )`

This parameters means:
- **COUNT**: number of random geometries
- **TYPE**: type of the geometries (polygon/line/point)

Example: `gvpy.runalg("randomvector", COUNT=10, TYPE=0)`

This algorithm is ready to work. You can execute them if your Jython Console or in your scripts.

> Remember that you always need to have one View open, if you don't do that, gvSIG will not know where to work. I recommend (also because gvpy is still in development), open one new Project, one new View and work there.

I recommend the formt that i explain it before, but you can write the algorithm without writing the name of the parameters, just write them in order.
Example: `gvpy.runalg("randomvector", 10, 0)`

Also, you can write them like a string.
Example: `gvpy.runalg("randomvector", "10", "0")`

##Input parameters
###Type of layers and geometries
If we forget with number is which geometry, inside gvpy exist some constants that will help you.

In the previous example, the `TYPE` parameter means with type of geometry we want, and we can write the numbers or using this constants.

**Type polygon**: value=0 or gvpy.TYPE_POLYGON
**Type line** value=1 or gvpy.TYPE_LINE
**Type point**: value=2 or gvpy.TYPE_POINT

This are the same examples:
`gvpy.runalg("randomvector",10, 0)`
`gvpy.runalg("randomvector",10, gvpy.TYPE_POLYGON)`

###Type layer parameters
If the algorithm need one **layer type parameter**, doesn't matter if is a table, vector or raster, we should load this layer in gvSIG, and use them like parameter.

There are different ways to do this in the **gvsig library**:
`currentLayer(), currentView().getLayer(name), loadShapeFile(path)`

Inside the **gvsig_raster library** for open raster layers:
`loadRasterLayer()`

Inside **gvpy library**, you could find some new ways to access to this layers like:
`currentRaster()` first active raster in the View
`currentActive()` first active layer in the View, doesn't matter the type.
`gvpy.getProjectLayer("View", "Layer name")` search for a layer in a View

Also, as i will explain better in the next chapter, you can get the new layers created in your algorithms, and use them as parameters of the next one.

##Output files
The output files (RESULT) are the layer or layers created in the algorithm, or others outputs like text. If you don't specify where do you want save this layers, will be created in a temp folder:
`C:\Users\Oscar\AppData\Local\Temp\tmp-andami`

We will set the path and the name using the attribute `PATH` that we will explain how to use it better in the next chapter.

The important part is, we can **get this new layers**, and use them again as parameters on the next algorithms or change them in gvSIG. The code will be like:
`layerResult = gvpy.runalg("randomvector",10,0)`

So we will have the new layer created with the algorithm inside the variable: `layerResult`. If we write `print layerResult`, we will see that contains a layer type object.

If the algorithm create two or more results, doesn't matter the type, we will get as return parameter one list with all inside them. You could access using: 
`print layerResult[0], layerResult[1], layerResult[2]`

##Other attributes
You could set other **optional attributes** in all algorithms, different than the parameters that we see before. With this parameters, you could change variables like the Output path, Analysis Extension, Output View..

###EXTENT
Define the Analysis Extension that will use the algorithm. For example, in out example that we saw, with this attribute, will create all the geometries inside this extension.

You will write: `EXTENT =` inside the algorithm

We can set this parameter using different ways:
- **Name of the View** (string): Search for a View with this name in out Project and set his envelope as parameter. It's the same that use: `currentProject().getView(name)`. Example `EXTENT="View1"`
- **View** (gvsig.View): Using directly the object View, and will that the envelope of the layers that are inside. Example: `EXTENT=currentView()`
- **Raster** (defaultRaster): Raster file in our View. Example: `EXTENT=currentRaster()`
- **Layer** (gvsig.Layer): Envelope of the layer. Example: `EXTENT=layerResult`, like in our past example, this algorithm will use the envelope of the result. 
- **List** (list): Coordinates of the extension. Lower-left corner and up-right corner, including the coordinate Z. Example: `EXTENT=[100,100,0,500,500,0]`
- **Default**: If you don't set any Analysis Extension, the algorithm will use `currentView()` as extension, View of the current Project. In case that we don't set any and the algorithm couldn't find any layer in the View, will use this coordinates as default: `EXTENT=[0,0,0,100,100,0]`

###CELLSIZE and CELLSIZEZ
Use it when the algorithm create raster files and there are set to the analysis extension. They will set the size of the pixel (x,y) and (z)

> Sometimes appear one error in the algorithm and is because the size of the raster with that cell size is so big. You can fix setting a bigger value for the pixel, this will make the raster file smaller.

Example:
`CELLSIZE=10, CELLSIZEZ=1`

###PATH
With this attribute we set the name and the path of the new result layers.

Depends of the how many layers create the algorithm, we can see this using `gvpy.algSearch("key-name-algorithm")` and see how many new layers create (output).
- If the algorithm return one layer, we set the value using a string: `PATH="C://1.shp"` or a list with just one parameter: `PATH=["C://1.shp"]`
- If the algorithm return two or more, we set them with a list: `PATH=["C://1.shp", "C://2.shp"]`

###OUTVIEW
This allow to select the View where we want load the layers generated in the algorithm.

We can set it writing the name of the View:
`OUTVIEW="View1"`

or a View object:
`OUTVIEW=currentView()`

##model2script: SEXTANTE model to Script
Transform your actual `sextante.model` files, created for Model Builder, into scripts. Just use `gvpy.model2script` with the path of the file, and the path of the new file. You should move the script to your Scripting folder in:
`C:\Users\[user]\gvSIG\plugins\org.gvsig.scripting.app.extension\scripts`
or just copy&paste inside a new script.

> This function is still being developed and could contain bugs.

Example: `gvpy.model2script("C://gsoc//test02.model", "C://gsoc//newScript.py")`