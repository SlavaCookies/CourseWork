import xml.etree.ElementTree as ET
from xml.dom import minidom

class GraphImportExport:
    def __init__(self, graph_app):
        # graph_app экземпляр CoreGraphGUI
        self.graph_app = graph_app
    

    def export_to_graphml(self, vertixes, edges, filename="graph.graphml", core=False):
        # Экспорт графа в GraphML формат
        self.vertixes = vertixes
        self.edges = edges
        self.vertixes_map = {}
        
        # Создаем корневой элемент
        root = ET.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
    
        # Определяем атрибуты для вершин
        node_key = ET.SubElement(root, "key")
        node_key.set("id", "v_label")
        node_key.set("attr.name", "label")
        node_key.set("attr.type", "string")
        node_key.set("for", "node")
    
        # Опеределяем ключ для позиций
        pos_key = ET.SubElement(root, "key")
        pos_key.set("id", "pos")
        pos_key.set("attr.name", "position")
        pos_key.set("attr.type", "string")
        pos_key.set("for", "node")
    
        # Определяем атрибуты для ребер
        edge_key = ET.SubElement(root, "key")
        edge_key.set("id", "e_directed")
        edge_key.set("attr.name", "directed")
        edge_key.set("attr.type", "boolean")
        edge_key.set("for", "edge")
    
        graph = ET.SubElement(root, "graph")
        graph.set("id", "G")
        graph.set("edgedefault", "directed")
    
        # Вершины
        for i, vertex in enumerate(self.vertixes):
            vertex_id, x, y, text_id = vertex
            node = ET.SubElement(graph, "node", id=f"n{i}")
            self.vertixes_map.setdefault(f"{vertex_id}", i)
        
            # Данные вершины (метка)
            data_label = ET.SubElement(node, "data")
            data_label.set("key", "v_label")  # Соответствует id ключа
            data_label.text = f"Вершина {i+1}"
        
            # Позиция
            data_pos = ET.SubElement(node, "data")
            data_pos.set("key", "pos")
            data_pos.text = f"{x},{y}"
    
        # Ребра
        edge_counter = 0
        for edge in self.edges:
            edge_id, from_vertex, to_vertex, edge_type = edge
        
            # Находим индексы вершин
            from_idx = self.get_vertex_index(from_vertex)
            to_idx = self.get_vertex_index(to_vertex)

            if from_idx is not None and to_idx is not None:
                edge_elem = ET.SubElement(graph, "edge", 
                                          id=f"e{edge_counter}",
                                          source=f"n{from_idx}",
                                          target=f"n{to_idx}")
            
                # Тип ребра
                data = ET.SubElement(edge_elem, "data")
                data.set("key", "e_directed")
                data.text = "true" if edge_type == "directed" else "false"
            
                edge_counter += 1

        # Форматируем и сохраняем
        try:
            xml_str = ET.tostring(root, encoding='utf-8')
            parsed = minidom.parseString(xml_str)
            pretty_xml = parsed.toprettyxml(indent="  ")
        
            with open(filename, "w", encoding="utf-8") as f:
                f.write(pretty_xml)
        
            return True
        
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
            return False
        
    def import_from_graphml(self, filename="graph.graphml"):
        # Простой импорт графа
        try:
        
            # Читаем файл
            tree = ET.parse(filename)
            root = tree.getroot()
        
            # Очищаем
            self.graph_app.clear_canvas()
        
            # Находим все вершины и их координаты
            vertices_map = {}  # node_id -> (x, y)
        
            # Проходим по всем элементам, ищем node
            for elem in root.iter():
                # Проверяем, это node или нет (игнорируем namespace)
                tag_name = elem.tag
                if '}' in tag_name:
                    tag_name = tag_name.split('}')[1]  # убираем namespace
            
                if tag_name == 'node':
                    node_id = elem.get('id')
                    x, y = 100, 100  # по умолчанию
                
                    # Ищем координаты в дочерних элементах
                    for child in elem:
                        if child.tag.endswith('}data') or child.tag == 'data':
                            key = child.get('key')
                            if key and ('pos' in key or 'position' in key):
                                if child.text and ',' in child.text:
                                    try:
                                        coords = child.text.split(',')
                                        x = float(coords[0].strip())
                                        y = float(coords[1].strip())
                                    except:
                                        pass
                
                    vertices_map[node_id] = (x, y)
        
            # Создаем вершины на Canvas
            vertex_objects = {}  # node_id -> наш объект вершины
        
            for node_id, (x, y) in vertices_map.items():
                self.graph_app.add_vertex(x, y)
                data = self.graph_app.get_graph_data()
                vertixes = data['vertixes']
                if vertixes:
                    vertex_objects[node_id] = vertixes[-1]
        
            # Создаем ребра
        
            for elem in root.iter():
                tag_name = elem.tag
                if '}' in tag_name:
                    tag_name = tag_name.split('}')[1]
            
                if tag_name == 'edge':
                    source = elem.get('source')
                    target = elem.get('target')
                
                    if source in vertex_objects and target in vertex_objects:
                        self.graph_app.add_directed_edge(vertex_objects[source], vertex_objects[target])
        
            return True
        
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
        
    def get_vertex_index(self, vertex):
        if not vertex:
            return None

        target_id = vertex[0]
        return self.vertixes_map[f"{target_id}"]
        


        