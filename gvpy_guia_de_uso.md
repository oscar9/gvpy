
#gvpy: Guía de uso



----------

**Lanzar geoprocesos desde el Módulo de Scripting**

Github con el código y actualizaciones del proyecto: https://github.com/oscar9/gvpy
Explicación del proyecto: http://oscar9.github.io/gvpy/

Autor: **Óscar Martínez Olmos** 
Email: <masquesig@gmail.com> 
Blog: http://www.masquesig.com 
Twitter: https://twitter.com/masquesig 

----------


[TOC]

Los geoprocesos de gvSIG y SEXTANTE ahora están accesibles con una sola línea de código y pueden formar parte de tus scripts. Podrás ejecutarlos desde la consola de Jython o desde el Scripting Composer, ubicados ambos dentro del módulo de Scripting. Este módulo de programación solo está disponible en la nueva versión de gvSIG 2.x en adelante.

##Librería gvpy
Para acceder a esta opción lo primero que debes hacer es descargar el archivo gvpy.py:
https://raw.githubusercontent.com/oscar9/gvpy/master/src/gvpy.py

Ubicarlo dentro de la carpeta:
 `C:\Users[name]\gvSIG\Plugins\org.gvsig.scripting.app.extension\lib`

Si tenías gvSIG abierto, deberás de cerrarlo y volverlo a abrir.

Ahora, para poder acceder a esta librería en tus scripts lo único que debes de hacer es escribir al inicio de tu código o en la Consola de Jython esto:

```python
import gvpy
```

Esto te permitirá utilizar la librería y acceder a todas sus funciones.

##Algoritmos
Los algoritmos que están disponibles desde la librería de gvpy también los encontrarás en la Caja de Herramientas, puedes acceder a ella en `Herramientas-Geoprocesamiento-Caja de Herramientas`

Tendrás acceso tanto a los algoritmos de geoprocesamiento de gvSIG como de SEXTANTE.

En esta Caja de Herramientas podemos realizar búsquedas de algoritmos, pero también desde gvpy.

Si abrimos la Consola de Jython (Herramientas-Scripting-Jython Console) y escribimos `import gvpy` ya podemos acceder a sus funcionalidades. Estos comandos también podemos utilizarlos desde el Scripting Composer desde un script nuevo.

Por ejemplo, si queremos buscar un algoritmos que genere vectores aleatorios podemos hacer una búsqueda del tipo:
`gvpy.algSearch("aleatorias")`

> La descripción de los algoritmos, tanto en gvSIG-Geoprocesos y SEXTANTE, se encuentra en español, así que para que funcionen las búsquedas tendrán que realizar en este idioma

De los resultados que nos aparecen, podemos ver un algoritmo denominado: `randomvector`

##Parámetros del algoritmo
Si queremos conocer más sobre el podemos escribir el mismo comando que hemos usado antes:
`gvpy.algSearch("randomvector")`

Si la búsqueda coincide exactamente con el nombre de un algoritmo, la información que nos muestra gvpy será la información sobre ese algoritmo, su descripción y sus parámetros.

```python
gvpy.algHelp("randomvector")
* Algorithm help: 
Capa vectorial con geometrias aleatorias
*
Usage: runalg( "randomvector",
                               COUNT[Numerical Value],
                               TYPE[Selection],
                               RESULT[output vector layer],
                               );
```

Lo mismo, podemos hacer la búsqueda en la **caja de herramientas**. Si entramos en el algoritmo podemos ver ayuda sobre lo que hace y abajo a la izquierda aparece el nombre clave del algoritmo (si no aparece, cierra la pantalla y vuelve a darle).

## Línea de código
Ahora que **conocemos los parámetros necesarios** para ejecutar el algoritmo, los escribiremos en forma de línea de código.

Hay que **escribir gvpy** delante para acceder a la función que se encuentra dentro de la librería. El atributo RESULT, siempre que se refieran a los archivos de salida (output vector, etc), no deberemos ponerlos.

Ejemplo: `gvpy.runalg("randomvector", COUNT= , TYPE= )`

Estos parámetros del ejemplo se refieren a:
- **COUNT**: número de geometrías aleatorias que queremos generar
- **TYPE**: tipo de geometrías que queremos generar (polígono/línea/punto)

Ejemplo: `gvpy.runalg("randomvector", COUNT=10, TYPE=0)`

Este algoritmo **ya lo podríamos ejecutar** en nuestra consola de Jython o en nuestros scripts.

> Recuerda que siempre tienes que tener alguna **VISTA abierta**, sino el programa no sabrá sobre qué espacio trabajar. Por lo general, antes de ejecutar tus scripts (sobre todo ahora que aún se encuentra en versión de desarrollo), abre un proyecto nuevo, abre una vista nueva, y entonces, accede al módulo de Scripting de la manera que desees.

Recomiendo escribirlo con el formato anterior pero también, siempre que guardemos el orden que nos dan los parámetros, podemos escribirlos sin especificar que atributo es.
Ejemplo: `gvpy.runalg("randomvector", 10, 0)`

Y para ser compatible con unas funcionalidades extra, también es posible si todos los parámetros los pasamos como texto con las comillas puestas:
Ejemplo: `gvpy.runalg("randomvector", "10", "0")`

##Parámetros de entrada
###Tipos de capas / geometrías
Por si nos olvidamos qué número corresponde a qué tipo de geometría o de capa, existen unas constantes dentro de gvpy para ayudarnos a recordarlas. 

En el ejemplo anterior, el parámetro `TYPE` que hace referencia a este tipo de polígonos, podemos escribirlo de diferentes maneras ayudándonos de estas constantes.

Tipo polígono: corresponde al valor 0, o también como gvpy.TYPE_POLYGON
Tipo línea: corresponde al valor 1, o también como gvpy.TYPE_LINE
Tipo punto: corresponde al valor 2, o también como gvpy.TYPE_POINT

Estos dos ejemplos son iguales:
`gvpy.runalg("randomvector",10, 0)`
`gvpy.runalg("randomvector",10, gvpy.TYPE_POLYGON)`

###Parametros de tipo Capa
Si el **algoritmo nos pide un parámetro de tipo capa** (ya sea tabla, vectorial o raster), tendremos que cargar esta capa en una variable y pasarla como parámetro. Existen diversas formas para hacer esto:

En la **librería de gvsig** existen diversas formas, tales como:
`currentLayer(), currentView().getLayer(name), loadShapeFile() `

En la **librería de gvsig_raster** para capas raster:
`loadRasterLayer()`

En la **librería de gvpy** he creado unas extras a las que podrás acceder como son:
`gvpy.currentRaster()` carga el raster activo en la Vista
`gvpy.currentActive()` carga la primera capa activa en la Vista, sea del tipo que sea
`gvpy.getProjectLayer("View", "Layer name")` busca el nombre de una capa en la Vista

Además, como explico en el siguiente apartado, **se pueden capturar las capas resultado de la ejecución de un algoritmo**, para poder ser usadas en otro pasadas como parámetro.

### Parámetros Multi input (beta)
Si son de tipo Vector se incluirán mediante una lista Ej. [vectorLayer1, vectorLayer2, ..... ]

### Parámetros Raster + Banda
Si son de tipo raster + banda se incluyen con una tupla Ej. (raster, 1)

Ej. Usando multi input de rasters
runalg("vectorizetrees", [(sRaster(0),1), (sRaster(1),1)], "capa1", "1.0", "1.0", "#")

### Parámetro Point
Se puede pasar como texto: "100.0, 150.0"
o como geometría de gvSIG: geom.createPoint(100.0, 150.0)

### Parámetros Fixed table
Se tienen que añadir como texto (string), con una sucesión de números a modo de lista.
Ej. LUT="1,1,1,0,0,0"



##Archivos de salida
Los archivos de salida (RESULT) son la capa o capas que generarán como resultado el ejecutar nuestro algoritmo, también salidas de tipo texto. Si no se especifica se guardarán en una carpeta temporal:
`C:\Users\Oscar\AppData\Local\Temp\tmp-andami`

Nosotros estableceremos la ruta que queremos con el comando PATH para indicar ruta y nombre. 

Además, **podemos capturar estas capas** para poder seguir utilizándolas en nuestro script recogiendo la salida del algoritmo:
`capa = gvpy.runalg("randomvector",10,0)`

De esta forma la variable `capa` contendrá las capas de gvSIG que son el resultado de lanzar el algoritmo. Si realizamos un `print capa` podremos ver como contiene una capa resultado.

Si el algoritmo generase dos o más capas como resultado, nos devolvería una lista con todas ellas, y podríamos acceder a ellas de la forma: 
`print capa[0], capa[1], capa[2]`

##Atributos extra
A parte de los parámetros del algoritmo, podremos designar otros **atributos opcionales** que permitirán modificar otras variables tales como la ruta de salida, región de análisis, etc.

###EXTENT
Define la región de análisis del algoritmo a utilizar. Por ejemplo en nuestros algoritmo anterior hará que las geometrías aleatorias estén todas contenidas en esta región.

Se escribirá: `EXTENT =` dentro del algoritmo

Podemos declararla de diversas formas:
- **Nombre de la Vista** (string): Buscará la Vista con ese nombre en nuestro proyecto. El comando en el que está basado es en: `currentProject().getView(name)`. Ejemplo `EXTENT="Vista1"`
- **Vista** (gvsig.View): Le pasamos directamente la Vista y cogerá la región en la que las capas de esta se expanden. Ejemplo: `EXTENT=currentView()`
- **Raster** (defaultRaster): Archivo raster que esté en nuestra vista. Ejemplo: `EXTENT=currentRaster()`
- **Layer** (gvsig.Layer): Extensión de la capa vectorial. Ejemplo: `EXTENT=capa`, basado en nuestro ejemplo anterior cogería la extensión de la capa generada por nuestro algoritmo.
- **Lista** (list): Pasando las coordenadas de la región. Las esquinas inferior izquierda y superior derecha, incluyendo la coordenada Z. Ejemplo: `EXTENT=[100,100,0,500,500,0]`
- **Por defualt**: Si no se le indica, intentará coger el currentView(), Vista del proyecto actual. En caso de que este no contenga ninguna capa, cogerá las coordenadas predeterminadas de: `EXTENT=[0,0,0,100,100,0]`

###CELLSIZE y CELLSIZEZ
Estos dos comandos se aplican también a la región de análisis, y son utilizados solamente para aquellos algoritmos que generen una capa de tipo Raster. Corresponderán al tamaño de las celdas en (x,y) y en (z).

> Muchas veces en este tipo de algoritmo **salta un error porque la región de análisis es excesivamente grande**. Esto lo podemos **solucionar aumentando el tamaño de las celdas**

Ejemplo:
`CELLSIZE=10, CELLSIZEZ=1`

###PATH
Con este atributo podemos designar el nombre y la ruta de las capas resultado.

Según las capas resultado que genere el algoritmo, esto lo podemos ver cuando utilizamos el comando gvpy.algHelp("") viendo cuantas capas de salida (output) tiene, nos lo devolverá de dos formas diferentes:
- Si solo devuelve una capa, podemos introducir la ruta como: `PATH="C://capa_01.shp"`
- Si devuelves dos o más, las podemos introducir en forma de lista: `PATH=["C://1.shp", "C://2.shp"]`

###OUTVIEW
Nos permite seleccionar en que Vista queremos que se carguen los archivos de salida de nuestros algoritmos ejecutados.

Podemos introducirla tanto como por su nombre: 
`OUTVIEW="Vista1"`

o por el objeto de tipo Vista:
`OUTVIEW=currentView()`

### TOCNAME
Este atributo nos permite modificar el nombre con el que aparecen las capas en el TOC. Es independiente del nombre que tenga la capa.

Ejemplo:
`TOCNAME="Resultado Vector 01"`


##model2script: SEXTANTE model to Script
Convierte tus ficheros `sextante.model`, creados por el Model Builder, en scripts. Tan solo utiliza la función `gvpy.model2script` con la ruta del fichero model, y la ruta del nuevo fichero que vas a crear. Luego deberás de mover tu script a la carpeta de Scripting que está en:
`C:\Users\[user]\gvSIG\plugins\org.gvsig.scripting.app.extension\scripts`
o copiar y pegar en un nuevo script.

> Esta función esta en desarrollo y aún puede contener errores

Ejemplo: `gvpy.model2script("C://gsoc//test02.model", "C://gsoc//nuevoScript.py")`
