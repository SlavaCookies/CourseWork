from ctypes import *
import os
import sys

# Находим путь для библиотеки DLL
dll_path = os.path.join(os.path.dirname(__file__), 'CoreGraph.dll')
my_dll = CDLL(dll_path) # Загружаем DLL

# Определяем функции
my_dll.CoreThisGraph.argtypes = [POINTER(POINTER(c_int)),
                                 POINTER(c_int),
                                 POINTER(c_int)]
my_dll.CoreThisGraph.restype = POINTER(c_int)
my_dll.FreeMemory.argtypes = [POINTER(c_int)]
my_dll.FreeMemory.restype = None

if not os.path.exists(dll_path):
    print(f"Ошибка: DLL не найдена по пути {dll_path}")
    sys.exit(1)
# Функция для создания матрицы для дальнейшего использования её в функции C++
def create_matrix(rows_cols, data):
    matrix_ptr = (POINTER(c_int) * rows_cols)()

    for i in range(rows_cols):
        if i < len(data):
            row_data = (c_int * rows_cols)(*data[i])
        
        matrix_ptr[i] = cast(row_data, POINTER(c_int))
    
    return matrix_ptr

# Функция, которая находит ядро
def core_this_graph(vertixes, edges):
    if len(vertixes) != 0:
        # Инициализация матрицы
        matrix_from_graph = [[0] * len(vertixes) for _ in range(len(vertixes))]
        vertixes_numbers = [] # Список вершин
        # Заполняем список вершин, полученными вершинами и добавляем номер-индекс вершины
        for i in range(len(vertixes)):
            vertex_id, x, y, text_id = vertixes[i]
            vertixes_numbers.append((vertex_id, x, y, text_id, i))
        # Составляем матрицу смежности ориентированного графа
        for edge in edges[:]:
            edge_id, from_vertex, to_vertex, edge_type = edge
            # Получаем индекс начальной вершины
            number_from_vertex_id = number_from_vertex(from_vertex, vertixes_numbers)
            # Получаем индекс конечной вершины
            number_to_vertex_id = number_from_vertex(to_vertex, vertixes_numbers)
            # Создание матрицы смежности ориентированного графа
            if number_from_vertex_id != None and number_to_vertex_id != None:
                matrix_from_graph[number_from_vertex_id][number_to_vertex_id] = 1
    
        # Создание матрицы для функции C++
        a_ptr = create_matrix(len(matrix_from_graph), matrix_from_graph)
        a_size = c_int(len(matrix_from_graph)) # Размер матрицы
        b_size = c_int(0) # Инициализируем размер множества ядра
        # Находим ядро графа
        b_ptr = my_dll.CoreThisGraph(a_ptr, byref(a_size), byref(b_size))
        b_list = [] # Представление ядра в виде списка
        b_list = [b_ptr[i] for i in range(b_size.value)]
        my_dll.FreeMemory(b_ptr)

        if b_list[0] != -1:
            # Возвращаем результат в виде списка вершин (vertex_id, x, y, text_id, номер вершины)
            b_list_with_id = []
            for i in range(len(b_list)):
                vertex = id_from_vertex(b_list[i]-1, vertixes_numbers)
                vertex_id, x, y, text_id = vertex
                b_list_with_id.append((vertex_id, x, y, text_id, b_list[i]-1))
            return b_list_with_id
        else:
            return list([-1, -1, -1, -1, -1])
    else:
        return list([-1, -1, -1, -1, -1])
    
# Функция для получения номера вершины
def number_from_vertex(from_vertex, vertixes_numbers):
    for i in range(len(vertixes_numbers)):
        vertex_id, _, _, _, vertex_number = vertixes_numbers[i]
        if vertex_id == from_vertex[0]:
            return vertex_number
    return None

# Функция для получения индекса вершины
def id_from_vertex(number_vertex, vertixes_numbers):
    for i in range(len(vertixes_numbers)):
        vertex_id, x, y, text_id, vertex_number = vertixes_numbers[i]
        if vertex_number == number_vertex:
            return (vertex_id, x, y, text_id)
    return None




























