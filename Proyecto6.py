# =====================================================================
#  BLOQUE: IMPORTACIONES
# =====================================================================
# Se importan todas las librerías necesarias.
# - tkinter (ttk, Menu, messagebox, ScrolledText): Para la interfaz gráfica.
# - sys: Para redirigir la salida de 'print'.
# - collections (deque, defaultdict): Para colas (BFS) y diccionarios con
#   valores por defecto (grafo).
# - typing: Mejor legibilidad.
# - math: Para los cálculos trigonométricos del dibujo.
# =====================================================================

import tkinter as tk
from tkinter import ttk, Menu, messagebox
from tkinter.scrolledtext import ScrolledText
import sys
from collections import deque, defaultdict
from typing import Dict, Set, Tuple, Optional
import math
from ttkthemes import ThemedTk

# =====================================================================
#  BLOQUE: CLASE MaximoFLujo
# =====================================================================
# Esta es la clase principal que modela el grafo. Contiene toda la
# lógica para almacenar los nodos, aristas, capacidades, y para
# ejecutar los algoritmos de flujo máximo.
# =====================================================================

class MaximoFLujo:

    # =====================================================================
    #  MÉTODO: __init__ (Constructor)
    # =====================================================================
    # Inicializa un grafo vacío.
    # - self.capacidad: Un diccionario de diccionarios (u -> v -> cap)
    #   para almacenar la capacidad de cada arista.
    # - self.flujo: Similar a 'capacidad', pero almacena el flujo actual.
    # - self.ady: Listas de adyacencia para búsquedas (BFS/DFS).
    # - self._nodos: Un conjunto (set) para llevar registro de todos
    #   los nodos que existen en el grafo.
    # =====================================================================

    def __init__(self):
        self.capacidad: Dict[int, Dict[int, int]] = defaultdict(dict)
        self.flujo: Dict[int, Dict[int, int]] = defaultdict(dict)
        self.ady: Dict[int, Set[int]] = defaultdict(set)
        self._nodos: Set[int] = set()

    # =====================================================================
    #  MÉTODOS: agregar_nodo / eliminar_nodo
    # =====================================================================
    # Estos métodos manejan la lógica para añadir o quitar nodos del
    # grafo. 'eliminar_nodo' es complejo, ya que debe recorrer todas
    # las estructuras de datos (capacidad, flujo, ady) para borrar
    # cualquier referencia al nodo eliminado (aristas entrantes y salientes).
    # =====================================================================

    def agregar_nodo(self, u: int) -> None:
        self._nodos.add(u)

    def eliminar_nodo(self, u: int) -> None:
        self._nodos.discard(u)
        
        if u in self.capacidad:
            del self.capacidad[u]
        if u in self.flujo:
            del self.flujo[u]
        
        for v in list(self.capacidad.keys()):
            self.capacidad[v].pop(u, None)

        for v in list(self.flujo.keys()):
            self.flujo[v].pop(u, None)

        if u in self.ady:
            del self.ady[u]
        for v in list(self.ady.keys()):
            self.ady[v].discard(u)
            if not self.ady[v]:
                del self.ady[v]

    # =====================================================================
    #  MÉTODOS: establecer_capacidad / eliminar_arista
    # =====================================================================
    # Controlan la creación y borrado de aristas (conexiones).
    # 'establecer_capacidad' es el método principal para definir
    # el "peso" (capacidad) de una arista. También se encarga de crear
    # los nodos (u, v) si no existen y de inicializar las estructuras
    # de flujo y adyacencia.
    # Si la capacidad se establece en 0, se trata como una eliminación.
    # =====================================================================

    def agregar_arista(self, u: int, v: int, cap: int) -> None:
        assert cap >= 0, "La capacidad debe ser no negativa."
        self.establecer_capacidad(u, v, self.capacidad[u].get(v, 0) + cap)

    def establecer_capacidad(self, u: int, v: int, cap: int) -> None:
        assert cap >= 0, "La capacidad debe ser no negativa."
        
        if cap == 0:
            self.eliminar_arista(u, v)
            return

        self.capacidad[u][v] = cap
        
        if v not in self.flujo[u]:
            self.flujo[u][v] = 0
        if u not in self.flujo[v]:
            self.flujo[v][u] = 0
            
        self.ady[u].add(v)
        self.ady[v].add(u) 
        
        self._nodos.update({u, v})

    def eliminar_arista(self, u: int, v: int) -> None:
        self.capacidad[u].pop(v, None)

    # =====================================================================
    #  MÉTODOS: UTILIDADES DEL GRAFO (nodos, aristas, reiniciar_flujos)
    # =====================================================================
    # Funciones auxiliares:
    # - nodos(): Devuelve una lista ordenada de todos los IDs de nodos.
    # - aristas(): Devuelve una lista de tuplas (u, v, cap) por cada
    #   arista con capacidad > 0.
    # - reiniciar_flujos(): Pone todo el flujo actual en 0. Esencial
    #   antes de (re)ejecutar un algoritmo.
    # =====================================================================

    def nodos(self):
        return sorted(self._nodos)

    def aristas(self):
        res = []
        for u in self.capacidad:
            for v, cap in self.capacidad[u].items():
                if cap > 0:
                    res.append((u, v, cap))
        return sorted(res)

    def reiniciar_flujos(self):
        for u in list(self.flujo.keys()):
            for v in list(self.flujo[u].keys()):
                self.flujo[u][v] = 0

    # =====================================================================
    #  MÉTODOS: CÁLCULO DE CAPACIDAD RESIDUAL
    # =====================================================================
    # Estos métodos privados (_residual_adelante, _residual_atras)
    # calculan la capacidad restante en el "grafo residual".
    # - _residual_adelante: Capacidad "hacia adelante" (capacidad - flujo).
    # - _residual_atras: Capacidad "hacia atrás" (el flujo actual,
    #   que se puede "devolver").
    # Son la base de Ford-Fulkerson y Edmonds-Karp.
    # =====================================================================

    def _residual_adelante(self, u: int, v: int) -> int:
        return self.capacidad[u].get(v, 0) - self.flujo[u].get(v, 0)

    def _residual_atras(self, u: int, v: int) -> int:
        return self.flujo[v].get(u, 0)

    # =====================================================================
    #  BLOQUE: ALGORITMO FORD-FULKERSON (DFS)
    # =====================================================================
    # Implementación del método de Ford-Fulkerson.
    # - _dfs_aumento: Es una Búsqueda en Profundidad (DFS) que busca
    #   un "camino de aumento" (un camino de S a T con capacidad
    #   residual > 0) en el grafo residual.
    # - ford_fulkerson_dfs: Es el método público. Llama a _dfs_aumento
    #   en un bucle. Mientras encuentre un camino, calcula el "cuello
    #   de botella" (flujo mínimo) de ese camino y lo suma al flujo
    #   total, actualizando el grafo residual. Se detiene cuando
    #   el DFS ya no puede encontrar un camino de S a T.
    # =====================================================================

    def _dfs_aumento(self, actual: int, sumidero: int, visitado: Set[int], padre: Dict[int, Tuple[int, int]]) -> bool:
        if actual == sumidero:
            return True
        visitado.add(actual)
        for vecino in self.ady[actual]:
            if vecino not in visitado and self._residual_adelante(actual, vecino) > 0:
                padre[vecino] = (actual, +1)
                if self._dfs_aumento(vecino, sumidero, visitado, padre):
                    return True
            if vecino not in visitado and self._residual_atras(actual, vecino) > 0:
                padre[vecino] = (actual, -1)
                if self._dfs_aumento(vecino, sumidero, visitado, padre):
                    return True
        return False

    def ford_fulkerson_dfs(self, fuente: int, sumidero: int):
        if not (fuente in self._nodos and sumidero in self._nodos):
            raise ValueError("La Fuente o el Sumidero no existen en el grafo.")
        self.reiniciar_flujos()
        flujo_maximo = 0
        while True:
            visitado: Set[int] = set()
            padre: Dict[int, Tuple[int, int]] = {}
            if not self._dfs_aumento(fuente, sumidero, visitado, padre):
                break
            botella = float("inf")
            v = sumidero
            while v != fuente:
                u, dir_ = padre[v]
                if dir_ == +1:
                    botella = min(botella, self._residual_adelante(u, v))
                else:
                    botella = min(botella, self._residual_atras(u, v))
                v = u
            v = sumidero
            while v != fuente:
                u, dir_ = padre[v]
                if dir_ == +1:
                    self.flujo[u][v] = self.flujo[u].get(v, 0) + botella
                else:
                    self.flujo[v][u] = self.flujo[v].get(u, 0) - botella
                v = u
            flujo_maximo += botella
        flujo_aristas = {}
        for u in self.capacidad:
            for v, cap in self.capacidad[u].items():
                f = max(0, min(cap, self.flujo[u].get(v, 0)))
                flujo_aristas[(u, v)] = f
        return flujo_maximo, flujo_aristas

    # =====================================================================
    #  BLOQUE: ALGORITMO EDMONDS-KARP (BFS)
    # =====================================================================
    # Implementación del método de Edmonds-Karp (mejora de Ford-Fulkerson).
    # La lógica es idéntica a Ford-Fulkerson, con una diferencia clave:
    # - _bfs_aumento: En lugar de DFS, usa una Búsqueda en Anchura (BFS)
    #   para encontrar el camino de aumento.
    # Esto garantiza que siempre encuentra el camino *más corto*
    # (en número de aristas), lo que mejora la eficiencia.
    # - edmonds_karp_bfs: El método público que orquesta el bucle,
    #   idéntico a ford_fulkerson_dfs pero llamando a _bfs_aumento.
    # =====================================================================

    def _bfs_aumento(self, fuente: int, sumidero: int):
        padre: Dict[int, Optional[Tuple[int, int]]] = {n: None for n in self._nodos}
        q = deque([fuente])
        padre[fuente] = (fuente, 0) 
        while q:
            u = q.popleft()
            if u == sumidero:
                return True, padre
            for v in self.ady[u]:
                if padre.get(v) is None and self._residual_adelante(u, v) > 0:
                    padre[v] = (u, +1)
                    if v == sumidero:
                        return True, padre
                    q.append(v)
                if padre.get(v) is None and self._residual_atras(u, v) > 0:
                    padre[v] = (u, -1)
                    if v == sumidero:
                        return True, padre
                    q.append(v)
        return False, None

    def edmonds_karp_bfs(self, fuente: int, sumidero: int):
        if not (fuente in self._nodos and sumidero in self._nodos):
            raise ValueError("La Fuente o el Sumidero no existen en el grafo.")
        self.reiniciar_flujos()
        flujo_maximo = 0
        while True:
            encontro, padre = self._bfs_aumento(fuente, sumidero)
            if not encontro:
                break
            botella = float("inf")
            v = sumidero
            while v != fuente:
                u, dir_ = padre[v]
                if dir_ == +1:
                    botella = min(botella, self._residual_adelante(u, v))
                else:
                    botella = min(botella, self._residual_atras(u, v))
                v = u
            v = sumidero
            while v != fuente:
                u, dir_ = padre[v]
                if dir_ == +1:
                    self.flujo[u][v] = self.flujo[u].get(v, 0) + botella
                else:
                    self.flujo[v][u] = self.flujo[v].get(u, 0) - botella
                v = u
            flujo_maximo += botella
        flujo_aristas = {}
        for u in self.capacidad:
            for v, cap in self.capacidad[u].items():
                f = max(0, min(cap, self.flujo[u].get(v, 0)))
                flujo_aristas[(u, v)] = f
        return flujo_maximo, flujo_aristas

    # =====================================================================
    #  MÉTODOS: IMPRESIÓN DE RESULTADOS (imprimir_desglose, mostrar_grafo)
    # =====================================================================
    # Funciones para mostrar el estado del grafo en la consola (o en la
    # pestaña de "Salida" de la GUI).
    # - imprimir_desglose: Muestra el resultado final (ej. "Flujo: 7/10").
    # - mostrar_grafo: Muestra la estructura actual (Nodos y Aristas).
    # =====================================================================

    def imprimir_desglose(self, flujo_aristas: Dict[Tuple[int, int], int]):
        print("\n--- Desglose del Flujo (flujo/capacidad) ---")
        if not flujo_aristas:
            print(" (No hay flujo)")
        for (u, v) in sorted(flujo_aristas.keys()):
            cap = self.capacidad[u].get(v, 0)
            f = flujo_aristas[(u, v)]
            if cap > 0:
                print(f"Tubería {u} -> {v}:   {f}/{cap}L/s")
        print("------------------------------------------------\n")


def mostrar_grafo(g: MaximoFLujo):
    print("\n--- Estado Actual de la Red ---")
    nodos = g.nodos()
    aristas = g.aristas()
    
    if not nodos:
        print("La red se encuentra vacia.")
        return
        
    print("Juntas (Nodos):", nodos)
    print("Tuberías (u -> v : capacidad L/s):")
    if not aristas:
        print(" (Sin tuberías)")
    for u, v, cap in aristas:
        print(f"  {u} -> {v} : {cap} L/s")
    print("---------------------------------\n")

# =====================================================================
#  FIN: LÓGICA DWL CODIGO
# =====================================================================


# =====================================================================
#  INICIO: INTERFAZ GRÁFICA (Tkinter)
# =====================================================================


# =====================================================================
#  BLOQUE: CLASE AcomodaTexto
# =====================================================================
# Esta clase es un truco para "secuestrar" la función 'print' de Python.
# Todo lo que normalmente se imprimiría en la consola (usando 'print()'),
# se redirige al método 'write' de esta clase.
# Este método, a su vez, inserta el texto en el widget 'ScrolledText'
# (la pestaña de "Salida" de la GUI), logrando que la consola
# de texto esté integrada en la ventana.
# =====================================================================

class AcomodaTexto:
    def __init__(self, widget: ScrolledText):
        self.widget = widget

    def write(self, s: str):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, s)
        self.widget.see(tk.END) # Auto-scroll
        self.widget.config(state=tk.DISABLED)

    def flush(self):
        pass

# =====================================================================
#  BLOQUE: CLASE AppGrafo (Interfaz Gráfica Principal)
# =====================================================================
# Esta es la clase que define toda la aplicación de Tkinter.
# Hereda de 'tk.Tk' (la ventana principal).
# =====================================================================

class AppGrafo(ThemedTk):
    
    # =====================================================================
    #  MÉTODO: __init__ (Constructor de la App)
    # =====================================================================
    # Configura la ventana principal.
    # 1. Llama al constructor de 'tk.Tk'.
    # 2. Establece el título y el tamaño de la ventana.
    # 3. Crea la instancia del 'MaximoFLujo' (el motor lógico).
    # 4. Inicializa el diccionario 'node_positions' (estará vacío).
    # 5. Llama a '_crear_widgets()' y '_crear_menu()' para construir la UI.
    # 6. Redirige 'sys.stdout' a una instancia de 'AcomodaTexto'.
    # 7. Imprime el mensaje de bienvenida y actualiza la vista.
    # =====================================================================

    def __init__(self):
        super().__init__(theme="black")
        self.title("Optimizador de red de tuberías")
        self.geometry("900x700")
        
        self.g = MaximoFLujo()
        
        self.node_radius = 20
        self.node_positions: Dict[int, Tuple[float, float]] = {}

        self._crear_widgets()

        sys.stdout = AcomodaTexto(self.output_text)

        print("¡Bienvenido! La red se encuentra vacía.")
        print("Usa el panel 'Editar Red' para empezar a construir tu tubería.")
        self._update_all_views()

    # =====================================================================
    #  MÉTODO: _crear_widgets
    # =====================================================================
    # Este método construye la interfaz gráfica. Se divide en:
    # 1. 'top_frame': El panel superior con las entradas de Fuente/Sumidero
    #    y los botones para ejecutar los algoritmos.
    # 2. 'main_pane': Un panel dividido (PanedWindow) que separa la
    #    pantalla en dos: Izquierda (Canvas) y Derecha (Notebook).
    # 3. 'canvas_frame': El panel izquierdo. Es el lienzo (Canvas) blanco
    #    donde se dibujará el grafo. Se le asigna un 'bind' para que
    #    detecte cuándo cambia de tamaño.
    # 4. 'notebook': El panel derecho. Es un sistema de pestañas.
    #    - Pestaña 1: "Editar Grafo" (llama a '_crear_tab_editar').
    #    - Pestaña 2: "Resultados" (crea el 'ScrolledText').
    #    - Pestaña 3: "Lista" (llama a '_crear_tab_lista').
    # =====================================================================

    def _crear_widgets(self):
        
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(side=tk.TOP, fill='x')

        ttk.Label(top_frame, text="Planta (S):").pack(side=tk.LEFT, padx=(0, 5))
        self.fuente_var = tk.StringVar(value="0")
        self.fuente_entry = ttk.Entry(top_frame, textvariable=self.fuente_var, width=5)
        self.fuente_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(top_frame, text="Destino (T):").pack(side=tk.LEFT, padx=(10, 5))
        self.sumidero_var = tk.StringVar(value="1")
        self.sumidero_entry = ttk.Entry(top_frame, textvariable=self.sumidero_var, width=5)
        self.sumidero_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(top_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill='y', padx=15, pady=5)

        self.btn_dfs = ttk.Button(top_frame, text="Ejecutar Ford-Fulkerson (DFS)", command=self.ford_fulkerson)
        self.btn_dfs.pack(side=tk.LEFT, padx=5)
        
        self.btn_bfs = ttk.Button(top_frame, text="Ejecutar Edmonds-Karp (BFS)", command=self.accion_edmonds_karp)
        self.btn_bfs.pack(side=tk.LEFT, padx=5)


        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        canvas_frame = ttk.Frame(main_pane, height=500)
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1, highlightbackground="gray")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        main_pane.add(canvas_frame, weight=4) 

        notebook_frame = ttk.Frame(main_pane, height=500)
        notebook = ttk.Notebook(notebook_frame)
        notebook.pack(fill="both", expand=True)
        main_pane.add(notebook_frame, weight=1)

        edit_tab = ttk.Frame(notebook, padding="10")
        notebook.add(edit_tab, text="Editar Red")
        self._crear_tab_editar(edit_tab)

        output_tab = ttk.Frame(notebook)
        notebook.add(output_tab, text="Resultados")
        self.output_text = ScrolledText(output_tab, wrap=tk.WORD, height=20, width=40)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED) 

        list_tab = ttk.Frame(notebook, padding="10")
        notebook.add(list_tab, text="Lista (Juntas/Tuberías)")
        self._crear_tab_lista(list_tab)

    # =====================================================================
    #  MÉTODO: _crear_tab_editar
    # =====================================================================
    # Construye el contenido de la Pestaña 1 ("Editar Grafo").
    # - Sección Nodos: Entradas y botones para 'Agregar'/'Eliminar' Nodo.
    # - Sección Aristas: Entradas (Desde, Hasta, Capacidad) y botones
    #   para 'Agregar'/'Eliminar' Arista.
    # =====================================================================

    def _crear_tab_editar(self, tab: ttk.Frame):        
        nodo_frame = ttk.LabelFrame(tab, text="1. Juntas / Estaciones", padding="10")
        nodo_frame.pack(fill='x', expand=True, pady=(0, 10))
        
        nodo_frame.columnconfigure(1, weight=1)

        ttk.Label(nodo_frame, text="ID de la Junta:").grid(row=0, column=0, sticky='w', padx=(0, 5), pady=2)
        self.nodo_id_var = tk.StringVar()
        self.nodo_id_entry = ttk.Entry(nodo_frame, textvariable=self.nodo_id_var)
        self.nodo_id_entry.grid(row=0, column=1, sticky='we', padx=5, pady=2)

        nodo_buttons_frame = ttk.Frame(nodo_frame)
        nodo_buttons_frame.grid(row=1, column=0, columnspan=2, sticky='we', pady=(10, 0))
        nodo_buttons_frame.columnconfigure(0, weight=1)
        nodo_buttons_frame.columnconfigure(1, weight=1)

        self.btn_add_nodo = ttk.Button(nodo_buttons_frame, text="Agregar", command=self.accion_agregar_nodo)
        self.btn_add_nodo.grid(row=0, column=0, sticky='we', padx=(0, 5))
        
        self.btn_del_nodo = ttk.Button(nodo_buttons_frame, text="Eliminar", command=self.accion_eliminar_nodo)
        self.btn_del_nodo.grid(row=0, column=1, sticky='we', padx=(5, 0))


        arista_frame = ttk.LabelFrame(tab, text="2 y 3. Tuberías (Conexiones y Capacidad)", padding="10")
        arista_frame.pack(fill='x', expand=True)
        
        grid_frame = ttk.Frame(arista_frame)
        grid_frame.pack(fill='x')
        grid_frame.columnconfigure(1, weight=1)

        ttk.Label(grid_frame, text="Desde (U):").grid(row=0, column=0, sticky='e', pady=2, padx=5)
        self.arista_u_var = tk.StringVar()
        self.arista_u_entry = ttk.Entry(grid_frame, textvariable=self.arista_u_var)
        self.arista_u_entry.grid(row=0, column=1, pady=2, padx=5, sticky='we')

        ttk.Label(grid_frame, text="Hasta (V):").grid(row=1, column=0, sticky='e', pady=2, padx=5)
        self.arista_v_var = tk.StringVar()
        self.arista_v_entry = ttk.Entry(grid_frame, textvariable=self.arista_v_var)
        self.arista_v_entry.grid(row=1, column=1, pady=2, padx=5, sticky='we')

        ttk.Label(grid_frame, text="Capacidad (L/s):").grid(row=2, column=0, sticky='e', pady=2, padx=5)
        self.arista_cap_var = tk.StringVar()
        self.arista_cap_entry = ttk.Entry(grid_frame, textvariable=self.arista_cap_var)
        self.arista_cap_entry.grid(row=2, column=1, pady=2, padx=5, sticky='we')

        btn_frame = ttk.Frame(arista_frame)
        btn_frame.pack(pady=10, fill='x')
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        self.btn_add_arista = ttk.Button(btn_frame, text="Agregar / Actualizar", command=self.accion_agregar_arista)
        self.btn_add_arista.grid(row=0, column=0, sticky='we', padx=(0, 5))
        
        self.btn_del_arista = ttk.Button(btn_frame, text="Eliminar (Cap=0)", command=self.accion_eliminar_arista)
        self.btn_del_arista.grid(row=0, column=1, sticky='we', padx=(5, 0))
    
    # =====================================================================
    #  MÉTODO: _crear_tab_lista
    # =====================================================================
    # Construye el contenido de la Pestaña 3 ("Lista").
    # Utiliza dos widgets 'Treeview' (que funcionan como tablas) para
    # mostrar un resumen de todos los nodos y aristas que existen
    # actualmente en el grafo. Incluye un botón de "Refrescar".
    # =====================================================================

    def _crear_tab_lista(self, tab: ttk.Frame):
        
        ttk.Label(tab, text="Juntas Actuales:").pack(anchor='w')
        cols_nodos = ('nodo_id',)
        self.tree_nodos = ttk.Treeview(tab, columns=cols_nodos, show='headings', height=5)
        self.tree_nodos.heading('nodo_id', text='Número de Junta')
        self.tree_nodos.pack(fill='x', expand=True, pady=5)
        
        ttk.Label(tab, text="Tuberías Actuales:").pack(anchor='w')
        cols_aristas = ('u', 'v', 'cap')
        self.tree_aristas = ttk.Treeview(tab, columns=cols_aristas, show='headings', height=10)
        self.tree_aristas.heading('u', text='Desde (U)')
        self.tree_aristas.heading('v', text='Hasta (V)')
        self.tree_aristas.heading('cap', text='Capacidad (L/s)')
        self.tree_aristas.column('u', width=80)
        self.tree_aristas.column('v', width=80)
        self.tree_aristas.column('cap', width=80)
        self.tree_aristas.pack(fill='x', expand=True, pady=5)
        
        self.btn_refresh_listas = ttk.Button(tab, text="Refrescar Listas", command=self._act_listas)
        self.btn_refresh_listas.pack(pady=5)

    # =====================================================================
    #  MÉTODO: _crear_menu
    # =====================================================================
    # Crea la barra de menú superior de la aplicación (Archivo, Grafo,
    # Algoritmos) y asigna los comandos correspondientes a cada opción.
    # =====================================================================

    def _crear_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)

        archivo_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Limpiar Salida", command=self._limpiar_output)
        archivo_menu.add_command(label="Salir", command=self.destroy)

        grafo_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Red", menu=grafo_menu)
        grafo_menu.add_command(label="Mostrar Red (en Salida)", command=self.mostrar_text_grafo)
        
        algo_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Algoritmos", menu=algo_menu)
        algo_menu.add_command(
            label="Ejecutar Ford–Fulkerson (DFS)", 
            command=self.ford_fulkerson
        )
        algo_menu.add_command(
            label="Ejecutar Edmonds–Karp (BFS)", 
            command=self.accion_edmonds_karp
        )

    # =====================================================================
    #  BLOQUE: LÓGICA DE DIBUJO DWL GRAFO
    # =====================================================================
    # Métodos responsables de la visualización dinámica del grafo.
    # - _on_canvas_resize: Se activa automáticamente si la ventana cambia
    #   de tamaño. Llama a '_update_all_views' para redibujar.
    # - _update_node_positions: Calcula las coordenadas (x, y) para cada 
    #   nodo. Obtiene el tamaño actual del canvas y distribuye
    #   los nodos en un círculo perfecto usando trigonometría (seno/coseno).
    #   Guarda estas posiciones en 'self.node_positions'.
    # =====================================================================

    def _on_canvas_resize(self, event):
        self._update_all_views(reset_flujo=False)

    def _update_node_positions(self):
        self.node_positions.clear()
        nodos = self.g.nodos()
        num_nodos = len(nodos)
        
        if num_nodos == 0:
            return

        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        
        center_x = max(50, W / 2)
        center_y = max(50, H / 2)
        padding = self.node_radius + 30
        radius = max(20, min(center_x, center_y) - padding)

        if num_nodos == 1:
            self.node_positions[nodos[0]] = (center_x, center_y)
            return

        for i, nodo_id in enumerate(nodos):
            angle = (i / num_nodos) * 2 * math.pi - (math.pi / 2)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions[nodo_id] = (x, y)

    # =====================================================================
    #  BLOQUE: ACTUALIZACIÓN DE VISTAS
    # =====================================================================
    # Controlan la sincronización de la GUI (interfaz grfica) con los datos del grafo.
    # - _act_listas: Borra y rellena las tablas
    #   (Treeview) de la Pestaña 3 con los datos frescos de 'g.nodos()'
    #   y 'g.aristas()'.
    # - _update_all_views: Es el método de refresco. Se
    #   llama casi después de cualquier acción. Maneja la actualización
    #   de todo:
    #   1. Reinicia los flujos.
    #   2. Recalcula la posición de los nodos ('_update_node_positions').
    #   3. Redibuja el canvas ('_dib_grafo').
    #   4. Refresca las listas ('_act_listas').
    # =====================================================================

    def _act_listas(self):
        for i in self.tree_nodos.get_children():
            self.tree_nodos.delete(i)
        for i in self.tree_aristas.get_children():
            self.tree_aristas.delete(i)
        
        for nodo in self.g.nodos():
            self.tree_nodos.insert('', 'end', values=(nodo,))
            
        for u, v, cap in self.g.aristas():
            self.tree_aristas.insert('', 'end', values=(u, v, cap))

    def _update_all_views(self, flujo_aristas=None, reset_flujo=True):
        if reset_flujo:
            self.g.reiniciar_flujos()
        self._update_node_positions()
        self._dib_grafo(flujo_aristas)
        self._act_listas()

    # =====================================================================
    #  MÉTODO: _dib_grafo
    # =====================================================================
    # Es el método que traduce los datos del grafo en líneas y círculos
    # dentro del Canvas.
    # 1. Borra todo lo que haya en el canvas ('delete("all")').
    # 2. Itera sobre 'g.aristas()'. Usa las posiciones de
    #    'self.node_positions' para dibujar líneas (create_line) y texto
    #    (create_text) para las capacidades o flujos (ej. "7/10").
    # 3. Itera sobre 'self.node_positions'. Dibuja los círculos (create_oval)
    #    y los números de los nodos (create_text).
    # 4. Pinta de color diferente la Fuente (verde) y el Sumidero (rojo).
    # =====================================================================

    def _dib_grafo(self, flujo_aristas: Optional[Dict[Tuple[int, int], int]] = None):
        self.canvas.delete("all")
        R = self.node_radius
        
        fuente, sumidero = self._get_fuente_sumidero(validar_existencia=False)

        for u, v, cap in self.g.aristas():
            if u not in self.node_positions or v not in self.node_positions:
                continue
                
            x1, y1 = self.node_positions[u]
            x2, y2 = self.node_positions[v]
            

            if flujo_aristas is not None:
                f = flujo_aristas.get((u, v), 0)
                label = f"{f} / {cap} L/s"
                if f > 0:
                    color = "steelblue" 
                    ancho = 8
                else:
                    color = "#AAAAAA"
                    ancho = 5
            else:
                label = f"Cap: {cap} L/s"
                color = "#555555"
                ancho = 5

            self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill=color, width=ancho, tags="arista")
            
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            offset_x, offset_y = (y2-y1)*0.1, (x1-x2)*0.1 
            text_x = mid_x + offset_x
            text_y = mid_y + offset_y
            
            self.canvas.create_oval(
                text_x - 30, text_y - 12, text_x + 30, text_y + 12, 
                fill="white", outline=""
            )
            
            self.canvas.create_text(
                mid_x + offset_x, 
                mid_y + offset_y, 
                text=label, 
                fill="black", 
                font=("Arial", 9),
                tags="arista_label"
            )

        for nodo, (x, y) in self.node_positions.items():
            fill_color = "white"
            if nodo == fuente:
                fill_color = "lightgreen"
            elif nodo == sumidero:
                fill_color = "salmon"
            
            self.canvas.create_oval(
                x - R, y - R, x + R, y + R, 
                fill="#BBBBBB", outline="#888888", width=3
            )
            # 2. Dibuja el centro de color
            self.canvas.create_oval(
                x - R + 6, y - R + 6, x + R - 6, y + R - 6, 
                fill=fill_color, outline="#555555"
            )
            
            # 3. Dibuja el texto de la junta encima de todo
            self.canvas.create_text(x, y, text=str(nodo), font=("Arial", 12, "bold"), tags="nodo_label")

    # =====================================================================
    #  MÉTODOS: UTILIDADES DE LA GUI
    # =====================================================================
    # Métodos auxiliares internos de la aplicación.
    # - _limpiar_output: Borra todo el texto de la Pestaña ("Salida").
    # - _get_fuente_sumidero: Obtiene el texto de las cajas de Fuente (S)
    #   y Sumidero (T), las convierte a número (int) y valida que
    #   esos nodos realmente existan en el grafo. Muestra un 'messagebox'
    #   de error si algo falla.
    # =====================================================================

    def _limpiar_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _get_fuente_sumidero(self, validar_existencia=True) -> Tuple[Optional[int], Optional[int]]:
        try:
            fuente = int(self.fuente_var.get())
            sumidero = int(self.sumidero_var.get())
            
            if validar_existencia:
                if fuente not in self.g.nodos():
                    messagebox.showerror("Error", f"La Junta (Planta) '{fuente}' no existe.")
                    return None, None
                if sumidero not in self.g.nodos():
                    messagebox.showerror("Error", f"La Junta (Destino) '{sumidero}' no existe.")
                    return None, None
            
            return fuente, sumidero
        except ValueError:
            messagebox.showerror("Error de Entrada", "La Planta (S) y el Destino (T) deben ser números enteros.")
            return None, None

    # =====================================================================
    #  BLOQUE: ACCIONES (EVENT HANDLERS)
    # =====================================================================
    # Estos métodos son los "comandos" que se ejecutan cuando el
    # usuario presiona un botón o una opción del menú.
    #
    # - mostrar_text_grafo: (Menú) Llama a 'mostrar_grafo'.
    #
    # - ford_fulkerson / accion_edmonds_karp:
    #   1. Obtienen y validan Fuente/Sumidero.
    #   2. Limpian la salida de texto.
    #   3. Ejecutan el algoritmo correspondiente de la clase 'g'.
    #   4. Imprimen los resultados.
    #   5. Llaman a '_update_all_views' pasándole los resultados del
    #      flujo para que el canvas se actualice (ej. "7/10").
    #
    # - accion_agregar_nodo / accion_eliminar_nodo: 
    #   Obtienen el ID del nodo, llaman al método 'g.agregar_nodo' o
    #   'g.eliminar_nodo', e invocan a '_update_all_views'.
    #
    # - accion_agregar_arista / accion_eliminar_arista: 
    #   Obtienen U, V y (opcionalmente) Capacidad. Llaman a
    #   'g.establecer_capacidad' (con Cap > 0 para agregar, o Cap = 0
    #   para eliminar) e invocan a '_update_all_views'.
    # =====================================================================

    def mostrar_text_grafo(self):
        mostrar_grafo(self.g)

    def ford_fulkerson(self):
        fuente, sumidero = self._get_fuente_sumidero()
        if fuente is None: return

        self._limpiar_output()
        print(f"=== Calciulando flujo de tuberias desde la planta {fuente} hacia el destino {sumidero} usando Ford–Fulkerson (DFS) ===")
        try:
            flujo_max, flujo_aristas = self.g.ford_fulkerson_dfs(fuente, sumidero)
            print(f"\n Flujo máximo total (Ford–Fulkerson): {flujo_max}")
            self.g.imprimir_desglose(flujo_aristas)
            self._update_all_views(flujo_aristas=flujo_aristas, reset_flujo=False)
        except Exception as e:
            messagebox.showerror("Error en Algoritmo", f"Ocurrió un error: {e}")
            print(f"\nERROR: {e}")

    def accion_edmonds_karp(self):
        fuente, sumidero = self._get_fuente_sumidero()
        if fuente is None: return

        self._limpiar_output()
        print(f"=== Calciulando flujo de tuberias desde la planta {fuente} hacia el destino {sumidero} usando Edmonds–Karp (BFS) ===")
        try:
            flujo_max, flujo_aristas = self.g.edmonds_karp_bfs(fuente, sumidero)
            print(f"\n Flujo máximo total (Edmonds–Karp): {flujo_max}")
            self.g.imprimir_desglose(flujo_aristas)
            self._update_all_views(flujo_aristas=flujo_aristas, reset_flujo=False)
        except Exception as e:
            messagebox.showerror("Error en Algoritmo", f"Ocurrió un error: {e}")
            print(f"\nERROR: {e}")

    def accion_agregar_nodo(self):
        try:
            nodo_id = int(self.nodo_id_var.get())
            self.g.agregar_nodo(nodo_id)
            self._update_all_views()
            print(f"Junta {nodo_id} agregada.")
            self.nodo_id_var.set("") 
        except ValueError:
            messagebox.showerror("Error", "El ID de la junta debe ser un número entero.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar la junta: {e}")

    def accion_eliminar_nodo(self):
        try:
            nodo_id = int(self.nodo_id_var.get())
            if nodo_id not in self.g.nodos():
                messagebox.showwarning("Aviso", f"La junta {nodo_id} no existe.")
                return
                
            if messagebox.askyesno("Confirmar", f"¿Seguro que quieres eliminar la junta {nodo_id} y TODAS sus conexiones?"):
                self.g.eliminar_nodo(nodo_id)
                self._update_all_views()
                print(f"La junta {nodo_id} y sus tuberías fueron eliminadas.")
                self.nodo_id_var.set("") 
        except ValueError:
            messagebox.showerror("Error", "El ID de la junta debe ser un número entero.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la junta: {e}")

    def accion_agregar_arista(self):
        try:
            u = int(self.arista_u_var.get())
            v = int(self.arista_v_var.get())
            cap = int(self.arista_cap_var.get())
            
            if cap < 0:
                messagebox.showerror("Error", "La capacidad no puede ser negativa.")
                return
            
            self.g.establecer_capacidad(u, v, cap)
            self._update_all_views()
            print(f"Tubería {u} -> {v} establecida con capacidad {cap} L/s.")
            # Limpiar entradas
            self.arista_u_var.set("")
            self.arista_v_var.set("")
            self.arista_cap_var.set("")
            
        except ValueError:
            messagebox.showerror("Error", "U, V y Capacidad deben ser números enteros.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar la tubería: {e}")

    def accion_eliminar_arista(self):
        try:
            u = int(self.arista_u_var.get())
            v = int(self.arista_v_var.get())
            
            self.g.establecer_capacidad(u, v, 0) 
            self._update_all_views()
            print(f"Tubería {u} -> {v} eliminada (capacidad = 0).")
            self.arista_u_var.set("")
            self.arista_v_var.set("")
            self.arista_cap_var.set("")

        except ValueError:
            messagebox.showerror("Error", "U y V deben ser números enteros.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la tubería: {e}")


# =====================================================================
#  BLOQUE: PUNTO DE ENTRADA
# =====================================================================
# Esta es la sección que se ejecuta cuando se ejecuta el archivo .py
# directamente.
# 1. Crea una instancia de la aplicación gráfica ('AppGrafo').
# 2. Llama a 'app.mainloop()'. Esto inicia el bucle de eventos
#    de Tkinter, que mantiene la ventana abierta y esperando
#    las acciones del usuario (clics, teclado, etc.).
# =====================================================================

if __name__ == "__main__":
    app = AppGrafo()
    app.mainloop()