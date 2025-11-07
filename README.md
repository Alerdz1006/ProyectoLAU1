# Proyecto 6 - Algoritmo de Ford-Fulkerson (Optimización de Flujo)

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![Algorithm](https://img.shields.io/badge/Algorithm-Max_Flow_Min_Cut-orange)

Aplicación de escritorio implementada en **Python** que modela y simula problemas de **flujo máximo** en una red. Utiliza los algoritmos de **Ford-Fulkerson (DFS)** y **Edmonds-Karp (BFS)** para optimizar el transporte.

El sistema representa una "red de tuberías", donde las **juntas** son los nodos y las **tuberías** son las aristas con una **capacidad** límite.

---

## Características principales

* **Algoritmos de Flujo Máximo:** Implementación de **Ford-Fulkerson** (vía DFS) y **Edmonds-Karp** (vía BFS) para encontrar el flujo máximo entre la fuente (**S**) y el sumidero (**T**).
* **Interfaz Gráfica (GUI):** Desarrollada con **Tkinter** y mejorada con `ttkthemes`. Permite la interacción completa para definir la red y ejecutar los algoritmos.
* **Visualización Dinámica:** La red se dibuja en un **lienzo (Canvas)** con un diseño circular. Se muestra el flujo actual sobre la capacidad de cada tubería (ej. "7/10 L/s"). La **Fuente** (verde) y el **Sumidero** (rojo) se resaltan.
* **Monitorización y Resultados:** Pestaña dedicada para ver el desglose del flujo máximo total y el detalle de los flujos de cada tubería en tiempo real.
* **Gestión de Datos:** Pestaña de **"Lista"** que muestra un resumen tabular de todas las juntas y tuberías definidas en el grafo.

---

## Estructura del Código

El código (`Proyecto6.py`) está organizado en clases para la separación de la lógica del grafo y la interfaz gráfica.

* `MaximoFLujo`: Clase principal que modela el grafo (nodos, aristas, capacidad y flujo).
    * Métodos `_dfs_aumento` y `_bfs_aumento`: Implementan la búsqueda de caminos de aumento para Ford-Fulkerson y Edmonds-Karp, respectivamente.
* `AcomodaTexto`: Clase auxiliar que redirige la salida estándar (`sys.stdout`) a la consola de resultados de la GUI.
* `AppGrafo`: Clase principal de la aplicación gráfica, que maneja la UI, el dibujo y la interacción con `MaximoFLujo`.

---

## Requisitos y Ejecución

### Requisitos

* **Python 3.x**
* Librería `tkinter` (Incluida con la mayoría de las distribuciones de Python).
* Librería **`ttkthemes`** (Para el tema oscuro de la interfaz).

### Instalación de dependencias

Instala la librería de temas ejecutando:

```bash
pip install ttkthemes
### Cómo ejecutar
Guarda el código en un archivo llamado Proyecto6.py.

Abre una terminal en la carpeta donde guardaste el archivo.

Ejecuta la aplicación:

Bash

python Proyecto6.py
🖱️ Uso del Sistema
Editar Red: Utiliza la pestaña "Editar Red" para:

Agregar o eliminar Juntas (nodos).

Establecer la Capacidad de las Tuberías (aristas). Una capacidad de 0 elimina la tubería.

Definir S y T: Ingresa los IDs de la Planta (S) y el Destino (T) en el panel superior.

Ejecutar Algoritmo: Haz clic en "Ejecutar Ford-Fulkerson (DFS)" o "Ejecutar Edmonds-Karp (BFS)" para ver el resultado.

Resultados: Consulta el flujo máximo total en el Canvas y el detalle de los flujos por arista en la pestaña "Resultados".
