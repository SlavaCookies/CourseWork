import tkinter as tk # Библиотека для создания формы
import CoreGraphApp as cga # Файл, в котором находится функция для решения задачи
import random
import math
import GraphImportExport # Файл, в котором находятся функции для импорта и экспорта файлов графа
from tkinter import filedialog, messagebox # Для выбора файлов и отображения сообщений
import os
import sys

# Основной класс для создания интерфейса, а также функционал приложения
class CoreGraphGUI:
    # Конструктор
    def __init__(self):
        self.root = tk.Tk() # форма
        self.root.title("Нахождение ядра графа")
        self.root.geometry("1000x590")
       
        # Устанавливаем иконку для приложения графа
        ICON_RELATIVE_PATH = r"Assets\graph_icon.ico"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_abs_path = os.path.join(current_dir, ICON_RELATIVE_PATH)
        self.root.iconbitmap(icon_abs_path)
        
        self.vertixes = [] # Список вершин
        self.edges = [] # Список ребер
        self.vertexes_radius = 20 # Радиус вершины
        # Максимальное расстояние от точки до дуги, которое нужно, чтобы удалить дугу на холсте canvas
        self.distance_edge = 5
        self.need_vertixes = [] # Список вершин ядра ориентированного графа
        self.need_edges = [] # Список дуг ядра ориентированного графа
        self.vertex_count = tk.StringVar(value="8")
        self.edges_count = tk.StringVar(value="10")

        self.create_ui() # Метод для создания UI-элелементов
        self.bind_events() # Прикрепляем события для определенных действий

        self.mode = 'add_vertex' # Стартовый режим, добавление вершин
        self.selected_vertex = None # Выбранная вершина
        self.core_finded = False
        self.color = None
        self.width = 0
        self.height = 0
        
    def create_ui(self):
        # Левая панель, для кнопок
        self.left_frame = tk.Frame(self.root, bg="lightgray", width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_frame.pack_propagate(False)
        # Правая панель, для холста canvas
        self.right_frame = tk.Frame(self.root, bg='white')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Создаем Элементы управления
        self.create_control_elements()
        
        # Создаем холст для графа
        self.create_canvas()
        
        # Создаем меню в самом верху, где будут, "Файл", "Спаравка"
        self.create_menu()

    # Функция для получения данных о списке вершин
    def get_graph_data(self):
        # Возвращает данные графа для экспорта
        return {
            'vertixes': self.vertixes.copy()
        }

    # Метод для создания кнопок
    def create_control_elements(self):
        # Панель управления слева
        title = tk.Label(self.left_frame, text="Управление графом", font=("Arial", 14, "bold"), bg="lightgray")
        title.pack(pady=10)

        # Кнопки 
        tk.Button(self.left_frame, text="Добавить вершину", command=self.set_add_vertex_mode, 
                  bg="lightblue", width=25).pack(pady=5)
        tk.Button(self.left_frame, text="Добавить направленное ребро", command=self.set_add_directed_edge_mode,
                  bg="lightgreen", width=25).pack(pady=5)
        tk.Button(self.left_frame, text="Удалить вершину", command=self.set_delete_vertex_mode,
                  bg="lightblue", width=25).pack(pady=5)
        tk.Button(self.left_frame, text="Удалить направленное ребро", command=self.set_delete_directed_edge_mode,
                  bg="lightgreen", width=25).pack(pady=5)
        # Разделитель
        tk.Frame(self.left_frame, height=2, bg="darkgray").pack(fill=tk.X, pady=10)
        # Кнопки алгоритмов
        tk.Button(self.left_frame, text="Найти ядро графа", command=self.find_core, bg="orange", width=25).pack(pady=5)
        tk.Button(self.left_frame, text="Сгенерировать граф", command=self.generate_graph, bg="purple", fg="white",
                  width=25).pack(pady=5)
        tk.Button(self.left_frame, text="Очистить холст", command=self.clear_canvas, bg="red", width=25).pack(pady=5)

        # Информационная модель
        tk.Frame(self.left_frame, height=2, bg="darkgray").pack(fill=tk.X, pady=10) 
        self.status_label = tk.Label(self.left_frame, text="Режим: Добавление вершин", bg="lightgray", wraplength=250)
        self.status_label.pack(pady=5)

        # Статистика графа
        self.stats_label = tk.Label(self.left_frame, text="Вершин: 0\nРебере: 0", bg="lightgray", justify=tk.LEFT)
        self.stats_label.pack(pady=5)
        self.add_generation_panel_graph()
    
    def add_generation_panel_graph(self):
        # Добавляем панель с двумя полями ввода

        # Создаем фрейм для панели генерации
        gen_frame = tk.Frame(self.left_frame, bg="lightgray")
        gen_frame.pack(pady=10, fill=tk.X, padx=5)

        # Заголовок
        tk.Label(gen_frame, text="Параметры генерации:", font=("Arial", 10), bg="lightgray").pack(anchor="w", pady=5)

        # Поле для количества вершин
        vertex_frame = tk.Frame(gen_frame, bg="lightgray")
        vertex_frame.pack(fill=tk.X, pady=2)

        tk.Label(vertex_frame, text="Вершин:", bg="lightgray", width=8).pack(side=tk.LEFT)

        self.vertex_entry = tk.Entry(vertex_frame, textvariable=self.vertex_count, width=10, justify="center")
        self.vertex_entry.pack(side=tk.LEFT, padx=5)

        # Поле для количества ребер
        edge_frame = tk.Frame(gen_frame, bg="lightgray")
        edge_frame.pack(fill=tk.X, pady=5)

        tk.Label(edge_frame, text="Ребер:", bg="lightgray", width=8).pack(side=tk.LEFT)

        self.edges_entry = tk.Entry(edge_frame, textvariable=self.edges_count, width=10, justify="center")
        self.edges_entry.pack(side=tk.LEFT, padx=5)

    # Метод для создания меню в верху программы, где будут "Файл", "Справка"
    def create_menu(self):
        # Создание меню в верхней части окна
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)

        file_menu.add_command(label="Импортировать", command=self.import_from_graphml)
        file_menu.add_command(label="Экспортировать", command=self.export_to_graphml)
        file_menu.add_command(label="Экспортировать ядро", command=self.export_core_to_graphml)
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Справка", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.show_programm)

    # Метод для создания холста canvas
    def create_canvas(self):
        # Создания холста для рисования
        self.canvas = tk.Canvas(self.right_frame, bg="white", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Привязываем события мыши
        self.canvas.bind("<Button-1>", self.on_canvas_click) # Левый клик
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag) # Нажать на левую кнопку
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release) # Отпускание левой кнопки

        # Переменные для перетаскивания
        self.dragging = False # Режим перетаскивания
        self.dragged_vertex = None # Вершина, которую перетаскиваем
    
    # Метод импорта
    def import_from_graphml(self):
        # Импорт графа из GraphML
        filename = filedialog.askopenfilename(
            filetypes=[("Graph files", "*.graphml"), ("All files", "*.*")]
        )
        if filename:
            self.vertixes = []
            self.edges = []
            self.need_vertixes = []
            self.need_edges = []
            # Импортируем файл
            succes = self.graph_import_export.import_from_graphml(filename)
            if succes:
                messagebox.showinfo("Успех", f"Граф имортирован из {filename}")
    
    # Метод экспорта
    def export_to_graphml(self):
        # Экспорт в GraphML 
        filename = filedialog.asksaveasfilename(
            defaultextension =".graphml",
            filetypes=[("GraphML files", "*.graphml"), ("All files", "*.*")]
        )
        if filename:
            # Копируем список вершин для экспорта
            vertixes = self.vertixes.copy()
            # Копируем список дег для экспорта
            edges = self.edges.copy()
            # Экспортируем файл
            success = self.graph_import_export.export_to_graphml(vertixes, edges, filename)
            if success:
                messagebox.showinfo("Успех", f"Граф экспортирован в {filename}")
    
    # Метод экспорта ядра ориентированного графа
    def export_core_to_graphml(self):
        filename = filedialog.asksaveasfilename(
            defaultextension = ".graphml",
            filetypes = [("GraphML files", "*.graphml"), ("All files", "*.*")]
        )
        if filename:
            # Копируем список вершин ядра ориентированного графа
            vertixes = self.need_vertixes.copy()
            # Копируем список дуг ядра ориентированного графа
            edges = self.need_edges.copy()
            # экспортируем файл
            success = self.graph_import_export.export_to_graphml(vertixes, edges, filename, True)
            if success:
                messagebox.showinfo("Успех", f"Ядро графа экспортировано в {filename}")
    
    # Метод, показывающий справку о программе
    def show_help(self):
        messagebox.showinfo("Справка", 
                            "Добавить вершину - после нажатия на эту кнопку включается режим " 
                            "добавления вершин, чтобы добавить вершину, нужно кликнуть на белую область, холст.\n\n" 
                            "Удалить вершину - после нажатия включается режим удаления вершин," 
                            "чтобы удалить вершину, нужно нажать на любую вершину.\n\n" 
                            "Добавить направленное ребро - после нажатия включается режим добавления ребер, чтобы" 
                            " добавить ребро, нажмите на любую вершину, она будет выделена," 
                            "а после нажмите на другую вершину.\n\n" 
                            "Удалить направленное ребро - после нажатия включается режим удаления ребер, чтобы" 
                            " удалить ребро, нажмите на него.\n\n" 
                            "Найти ядро графа - находит ядро графа, изображенном на холсте.\n\n" 
                            "Сгенерировать граф - генерирует случайный граф.\n\n" 
                            "Очистить холст - очищаем холст."
        )
    
    def show_programm(self):
        messagebox.showinfo("О программе", "Нахождение ядра ориентированного графа.")
    
    # Привязываем событие на изменение размера окна
    def bind_events(self): 
        self.root.bind('<Configure>', self.on_resize_window) 

    # Метод, срабатывающий при изменении размера окна
    def on_resize_window(self, event): 
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
    
    # Метод устанвавливает режим добавления вершин
    def set_add_vertex_mode(self):
        self.mode = 'add_vertex'
        self.canvas.config(cursor="crosshair") # Меняем курсор
        self.status_label.config(text="Режим: Добавление вершин\nКликините на холст")

    # Метод устанавливает режим добавления ребер
    def set_add_directed_edge_mode(self):
        self.mode = 'add_directed_edge'
        self.selected_vertex = None
        self.canvas.config(cursor="hand2") # Меняем курсор
        self.status_label.config(text="Режим: Добавление направленного ребра\nВыберите начальную вершину")

    # Метод уставнваливает режим удаления вершин
    def set_delete_vertex_mode(self):
        self.mode = 'delete_vertex'
        self.canvas.config(cursor="crosshair") # Меняем курсор
        self.status_label.config(text="Режим: Удаление вершин\nКликните на вершину")
    
    # Метод устанавливает режим удаления ребер
    def set_delete_directed_edge_mode(self):
        self.mode = 'delete_directed_edge'
        self.selected_vertex = None
        self.canvas.config(cursor="hand2") # Меняем курсор
        self.status_label.config(text="Режим: Удаление направленного ребра\nВыберите любое ребро графа")

    # Метод, который обрабатывает клик на холсте canvas
    def on_canvas_click(self, event):
        x, y = event.x, event.y # Координаты клика
        
        if self.mode == 'add_vertex': # Режим добавления вершин
            if not self.is_click_on_vertex(x, y): # Проверяем, нажали ли на вершину
                self.add_vertex(x, y) # Добавляем вершину
                self.update_stats() # Обновляем статистику и сам граф

        elif self.mode == 'add_directed_edge': # Режим добавления ребер
            # Проверяем, нажали ли мы на вершину
            clicked_vertex = self.get_vertex_at(x, y)
            # Если нажали на вершину 
            if clicked_vertex:
                if self.color is None:
                    self.color = self.canvas.itemcget(clicked_vertex[0], "fill")
                if self.selected_vertex is None: # Если начальная вершины не выбрана
                    self.selected_vertex = clicked_vertex # Начальная вершина
                    self.highlight_vertex(clicked_vertex) # Подсвечиваем эту вершину
                    # Обновление статистика и самого графа
                    mode_text = "направленного"
                    self.status_label.config(text=f"Режим: Добавление {mode_text} ребра\nВыберите вторую вершину")
                else: # Выбрана не начальная вершина
                    is_edge_added = False
                    is_edge_created = False
                    # Если вторая вершина, на которую нажали, не равна самой себе
                    if self.selected_vertex != clicked_vertex:
                        for edge in self.edges[:]:
                            edge_id, from_vertex, to_vertex, edge_type = edge
                            if from_vertex[0] == self.selected_vertex[0] and to_vertex[0] == clicked_vertex[0]:
                                is_edge_created = True
                                break

                        if not is_edge_created:
                            # Добавляем ребро
                            self.add_directed_edge(self.selected_vertex, clicked_vertex)
                            is_edge_added = True
                            # Обновляем статистику и сам граф
                            self.update_stats()
                    
                    # Снимаем выделение с вершины
                    self.unhighlight_vertex(self.selected_vertex, self.color, is_edge_added)
                    self.selected_vertex = None # Очищаем выбранную начальную вершину
                    self.color = None
                    #self.set_add_vertex_mode() # Переходим в режим добавления вершин
        # Режим удаления вершин
        elif self.mode == 'delete_vertex':
            # Проверяем, что нажали на вершину
            clicked_vertex = self.get_vertex_at(x, y)
            # Если нажали не вершину
            if clicked_vertex:
                #   id         x        y        id
                vertex_id, x_vertex, y_vertex, text_id = clicked_vertex
                edges_to_delete = [] # Список дуг для удаления
                # Проходим по всем дугам и проверяем, связаны ли они с удаляемой вершиной
                for edge in self.edges[:]:
                    #  id     vertex1      vertex2    type
                    edge_id, from_vertex, to_vertex, edge_type = edge
                    if from_vertex[0] == vertex_id or to_vertex[0] == vertex_id:
                        edges_to_delete.append(edge)

                # Проходим по всем дугам, которые связаны с удаляемой вершиной и удаляем их
                for edge_id, from_vertex, to_vertex, edge_type in edges_to_delete:
                    self.canvas.delete(edge_id)
                    if (edge_id, from_vertex, to_vertex, edge_type) in self.edges:
                        self.edges.remove((edge_id, from_vertex, to_vertex, edge_type))
                # Удаление вершины
                self.canvas.delete(vertex_id)
                self.canvas.delete(text_id)
                if (vertex_id, x_vertex, y_vertex, text_id) in self.vertixes:
                    self.vertixes.remove((vertex_id, x_vertex, y_vertex, text_id))
                
                # Обновление статистики и самого графа
                self.update_stats()
        # Режим удаления ребер графа 
        elif self.mode == 'delete_directed_edge':
            # Проходим по всем дугам и проверяем, к какой из них клик ближе всех
            # Удаляется только одно ребро, которое будет первым, если таких дуг несколько
            for edge in self.edges[:]:
                edge_id, from_vertex, to_vertex, edge_type = edge
                # Считаем расстояние от точки до дуги
                distance = self.distance_point_to_edge(x=(x, y),
                                                  y=(from_vertex[1], from_vertex[2]), 
                                                  z=(to_vertex[1], to_vertex[2]))
                # Если расстояние меньше или равно 5, то удаляем эту дугу
                if distance <= self.distance_edge:
                    self.canvas.delete(edge_id)
                    self.edges.remove((edge_id, from_vertex, to_vertex, edge_type))
                    # Обновляем статистику и весь граф
                    self.update_stats()
                    break

    # Функция считает расстояние от точки до прямой
    def distance_point_to_edge(self, x, y, z):
        x_point, y_point = x # Точка, от которой ищем расстояние
        x_edge_first, y_edge_first = y # Первая точка прямой
        x_edge_second, y_edge_second = z # Вторая точка прямой
        # Считаем числитель |(x0 - x1) * (y2 - y1) - (y0 - y1) * (x2 - x1)|
        s = abs((x_point - x_edge_first) * (y_edge_second - y_edge_first) -
                        (y_point - y_edge_first) * (x_edge_second - x_edge_first))
        # Считаем знаменатель sqrt((x2 - x1)^2 + (y2 - y1)^2)
        t = math.sqrt( (x_edge_second - x_edge_first)**2 + (y_edge_second - y_edge_first)**2 )
        return s / t # Считаем |(x0 - x1) * (y2 - y1) * (y0 - y1) * (x2 - x1)| / sqrt((x2 - x1)^2 + (y2 - y1)^2)

    # Метода обрабатывающий перетаскивание вершин
    def on_canvas_drag(self, event):
        # Если выбран режим перетаскивания и выбрана вершина для перетаскивания
        if self.dragging and self.dragged_vertex:
            x, y = event.x, event.y # Координаты события

            # Обновляем позицию вершины
            vertex_id, old_x, old_y, text_id = self.dragged_vertex
            #color = self.canvas.itemcget(vertex_id, "fill")
            # Перемещаем круг
            self.canvas.coords(vertex_id, 
                               x - self.vertexes_radius, y - self.vertexes_radius,
                               x + self.vertexes_radius, y + self.vertexes_radius)
            # Перемещаем текст
            self.canvas.coords(text_id, x, y)
            # Обновляем координаты в списке
            idx = self.vertixes.index(self.dragged_vertex)
            self.vertixes[idx] = (vertex_id, x, y, text_id)
            self.dragged_vertex = (vertex_id, x, y, text_id)
            ##self.canvas.itemconfig(vertex_id, fill=f"{color}")
            # Обновляем связанные ребра
            self.update_connected_edges(self.dragged_vertex)

    # Метод обработки события отпускания мыши
    def on_canvas_release(self, event):
        self.dragging = False # Выключаем режим перетаскивания
        self.dragged_vertex = None # Очищаем вершину для перетаскивания 
    
    # Функция, которая проверяет, было ли нажато вершину
    def is_click_on_vertex(self, x, y):
        # Проходим по всем вершинам
        for vertex in self.vertixes:
            _, vx, vy, _ = vertex
            # Считаем расстояние
            distance = ((vx - x) ** 2 + (vy - y) ** 2) ** 0.5
            # Если расстояние меньше радиуса 
            if distance <= self.vertexes_radius:
                # Начинаем перетаскивание
                self.dragging = True
                self.dragged_vertex = vertex
                return True
        return False

    # Получаем вершину по координатам
    def get_vertex_at(self, x, y):
        # Проходим по всем вершинам
        for vertex in self.vertixes:
            vertex_id, vx, vy, text_id = vertex
            # Считаем расстояние
            distance = ((vx - x) ** 2 + (vy - y) ** 2) ** 0.5
            # Если растояние меньше радиуса
            if distance <= self.vertexes_radius:
                return vertex
    
        return None
    
    # Метод для добавления вершин
    def add_vertex(self, x, y): 
        # Доблавяем вершину
        vertex_id = self.canvas.create_oval(
            x - self.vertexes_radius, y - self.vertexes_radius,
            x + self.vertexes_radius, y + self.vertexes_radius,
            fill="lightblue", outline="darkblue", width=2,
            tags="vertex"
        )

        # Номер вершины
        vertex_num = len(self.vertixes) + 1
        # Создаем номер на вершине
        text_id = self.canvas.create_text(x, y, text=str(vertex_num), font=("Arial", 12, "bold"), fill="black",
                                          tags="vertex_text")
        
        # Добавляем вершину 
        self.vertixes.append((vertex_id, x, y, text_id))
        # Обновление статистики и самого графа
        self.update_stats()
    
    # Метод добавления дуги на графе
    def add_directed_edge(self, from_vertex, to_vertex, color="red", update_stats=True):
        # Начальная вершина
        _, x1, y1, _ = from_vertex
        # Конечная вершина
        _, x2, y2, _ = to_vertex

        # Корректируем координаты для стрелки
        start_x, start_y, end_x, end_y = self.adjust_edge_coordinates(x1, y1, x2, y2)
        # Создаем линию, дугу в граф
        edge_id = self.canvas.create_line(
            start_x, start_y, end_x, end_y, 
            fill=f"{color}", width=2,      
            arrow=tk.LAST,
            arrowshape=(10, 12, 5),
            tags="directed_edge"
        )
        # Добавляем дугу 
        self.edges.append((edge_id, from_vertex, to_vertex, 'directed'))
        # Обновляем статистику и весь граф
        self.update_stats(update_stats)

    # Функция для корректировки координат для стрелки в дугах
    def adjust_edge_coordinates(self, x1, y1, x2, y2):
        # x1, x2 - координаты первой вершины
        # y1, y2 - координаты второй вершины
        dx = x2 - x1
        dy = y2 - y1

        # Расстояние
        distance = (dx**2 + dy**2) ** 0.5

        # Корректируем координаты
        if distance > 0:
            start_x = x1 + (dx / distance) * self.vertexes_radius
            start_y = y1 + (dy / distance) * self.vertexes_radius
            end_x = x2 - (dx / distance) * self.vertexes_radius
            end_y = y2 - (dy / distance) * self.vertexes_radius
            return start_x, start_y, end_x, end_y
        
        return x1, y1, x2, y2 # Координаты не меняются в графе
    
    # Выделение вершины
    def highlight_vertex(self, vertex):
        vertex_id, _, _, _ = vertex
        self.canvas.itemconfig(vertex_id, fill="green") # Перекрашиваем вершину в нужный цвет

    # Снимаем выделение вершины
    def unhighlight_vertex(self, vertex, color, edge_added):
        vertex_id, _, _, _ = vertex
        if edge_added:
            self.canvas.itemconfig(vertex_id, fill="lightblue")
        else:
            self.canvas.itemconfig(vertex_id, fill=f"{color}")

    # Метод обновляет все связанные с вершиной ребра
    def update_connected_edges(self, vertex):
        vertex_id, x, y, text_id = vertex
        edges_to_redraw = [] # Список вершин для перерисовки

        # Проходим по всем дугам
        for edge in self.edges[:]:
            edge_id, from_vertex, to_vertex, edge_type = edge
            # Проверяем, что индекс начальной вершины или конечной вершины равен индексу вершины, которую перетаскиваем
            if from_vertex[0] == vertex_id or to_vertex[0] == vertex_id:
                color = self.canvas.itemcget(edge_id, "fill")
                edges_to_redraw.append((edge_id, from_vertex, to_vertex, edge_type, color))
        
        # Проходим по всем ребрам, которые надо перерисовать
        for edge_id, from_vertex, to_vertex, edge_type, color_edge in edges_to_redraw:
            self.canvas.delete(edge_id) # Удаляем дугу
            if (edge_id, from_vertex, to_vertex, edge_type) in self.edges:
                self.edges.remove((edge_id, from_vertex, to_vertex, edge_type))
            
            # Обновляем координаты для вершин дуги
            if from_vertex[0] == vertex_id:
                from_vertex = vertex
            if to_vertex[0] == vertex_id:
                to_vertex = vertex

            # Добавляем дугу, то есть перерисовываем
            self.add_directed_edge(from_vertex, to_vertex, color_edge, False)

    # Метод обновления статистики и всего графа
    def update_stats(self, update_stats=True):
        # Обновляет статистику
        self.stats_label.config(text=f"Вершин: {len(self.vertixes)}\nРебер: {len(self.edges)}")
        # Перекрашиваем все вершины и дуги в изначальный цвет, если были перекрашены после нахождения ядра
        # если мы указываем на то, что нужно менять цвет
        if update_stats and self.core_finded:
            for vertex in self.vertixes:
                vertex_id, x, y, text_id = vertex
                self.canvas.itemconfig(vertex_id, fill="lightblue")
            for edge in self.edges:
                edge_id, from_vertex, to_vertex, edge_type = edge
                self.canvas.itemconfig(edge_id, fill="red")
            self.core_finded = False
    
    # Функция нахрждения ядра ориентированного графа
    def find_core(self):
        self.set_add_vertex_mode() # Переходим в режим добавления вершин
        messagebox.showinfo("Ожидание", "Пожалуйста подождите, пока найдется ядро ориентированного графа")
        self.need_vertixes = []
        self.need_edges = []
        # Используем функцию для нахождения ядра ориентированного графа
        core_with_id = cga.core_this_graph(self.vertixes, self.edges)
        core = [] # Ядро
        if core_with_id != list([-1, -1, -1, -1, -1]):
            self.core_finded = True
            # Проходим по всем вершинам ядра
            for vertex in core_with_id:
                vertex_id, x, y, text_id, vertex_number = vertex
                # Перекрашиваем вершины, чтобы выделить ядро
                self.canvas.itemconfig(vertex_id, fill='orange')
                # Добавляем вершину в список вершин ядра
                self.need_vertixes.append((vertex_id, x, y, text_id))

                # Проходим по всем дугам
                for edge in self.edges[:]:
                    edge_id, from_vertex, to_vertex, edge_type = edge
                    # Есть ли начальная вершина в дуге, если да, то добавляем в список вершин ядра
                    is_need_add_from_vertex = True
                    # Есть ли конечная вершина в дуге, если да, то добавляем в список вершин ядра
                    # это нужно, чтобы можно было нарисовать дуги, которые идут из вершин ядра
                    is_need_add_to_vertex = True
                
                    # Если начальной вершиной в дуге является вершина из ядра, то перекрашиваем 
                    if from_vertex[0] == vertex_id:
                        self.canvas.itemconfig(edge_id, fill='orange')
                        self.need_edges.append(edge)
                    
                        # Проходим по всем вершинам и проверяем, являлется ли она начальной вершиной
                        # или конечной вершиной в дуге, если да, то добавляется в список вершин,
                        #  для отрисовки ядра графа
                        for v in self.need_vertixes:
                            v_id, v_x, v_y, v_text_id = v
                            if v_id == from_vertex[0]:
                                is_need_add_from_vertex = False
                            if v_id == to_vertex[0]:
                                is_need_add_to_vertex = False
                    
                        # Добавляем вершину в список вершин
                        if is_need_add_from_vertex:
                            self.need_vertixes.append(from_vertex)
                        if is_need_add_to_vertex:
                            self.need_vertixes.append(to_vertex)
                core.append(vertex_number+1) # Добавляем номер вершины в список вершин ядра для отображения
        else:
            self.core_finded = False
            messagebox.showinfo("Сообщение", "В данном графе нету ядра")
        #print(f"Ядро ориентированного графа: {core}, размер ядра: {len(core)}")

    # Функция генерации графа на холсте
    def generate_graph(self):

        try:
            vertex_count = int(self.vertex_count.get())
            edges_count = int(self.edges_count.get())

            if vertex_count < 1:
                messagebox.showerror("Ошибка", "Количество вершин должно быть положительным.")
                return
            
            if edges_count < 0:
                messagebox.showerror("Ошибка","Количество ребер не должно быть отрицательным.")
                return
            
            # Максимальное количество ребер графа для стольких вершин данного графа
            max_possible_edges = vertex_count * (vertex_count - 1)
            # Если ребер больше, чем может быть, то уменьшаем до максимального числа
            if edges_count > max_possible_edges:
                messagebox.showinfo("Информация", f"Максимум ребер для {vertex_count} вершин: {max_possible_edges}. " + 
                                    f"Нарисуются только не более {max_possible_edges} ребер.")
                edges_count = max_possible_edges
                self.edges_count.set(str(edges_count))

            self.clear_canvas() # Очищаем холст canvas

            # Генерируем вершины в случайных позициях
            for _ in range(vertex_count):
                x = random.randint(50, self.width)
                y = random.randint(50, self.height - 100)
                self.add_vertex(x, y)
        
            # Генерируем случайные ребра
            for i in range(edges_count):
                if len(self.vertixes) >= 2:
                    v1 = random.choice(self.vertixes)
                    v2 = random.choice(self.vertixes)
                    if v1 != v2:
                        self.add_directed_edge(v1, v2)
        
            # Обновляем статистику и весь граф
            self.update_stats()
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите числа в поля ввода.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {e}")
    
    # Инициализируем объект для импорта и экпорта файлов с графом
    def create_import_export(self, app):
        self.graph_import_export = GraphImportExport.GraphImportExport(app)

    # Метод очистки холста canvas
    def clear_canvas(self):
        # Очищаеи холст
        self.canvas.delete("all")
        self.vertixes.clear()
        self.edges.clear()
        self.update_stats()
        self.set_add_vertex_mode()                   
    

#app = CoreGraphGUI()
#graph_import_export = GraphImportExport.GraphImportExport(app)
#app.root.mainloop()






















































































































