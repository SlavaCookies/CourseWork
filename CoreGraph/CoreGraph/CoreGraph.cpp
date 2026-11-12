#include "pch.h"
#include "CoreGraph.h"

const int MAX_SIZE = 15;
bool isNode = true;
bool findCoreWrite = false;
bool findCoreWrite1 = false;
bool coreRead = false;
bool coreRead1 = false;
std::vector<int> graphCore;
std::queue<std::vector<int>> queueCores;
std::queue<std::vector<int>> queueCores1;
std::mutex queueMutex;
std::mutex queueMutex1;
std::condition_variable condition;
std::condition_variable condition1;
std::vector<std::vector<int>> queue;
std::vector<std::vector<int>> queue1;

struct graph {
    int node;
    std::vector<int> nodes;
};
static bool fnode(std::vector<int> core, int node)
{
    for (size_t i = 0; i < core.size(); ++i) {
        if (core[i] == node) {
            return true;
        }
    }
    return false;    
}

// Функция проверяет, является ли это множество ядром графа
static bool isCore(std::vector<std::vector<int>> nodesedge, std::vector<int> core) {
    int size = core.size(); // Количество вершин в множестве вершин
    // Если false, то это множество вершин не является ядром графа
    // Если true, то это множество вершин является ядром графа
    bool is_core = true;
    // Проходим по всем элементам множества вершин
    for (int i = 0; i < size; ++i) {
        // Проходим по всем элементам множества вершин
        for (int j = 0; j < size; ++j) {
            // Чтобы не проверять множества из одной вершины
            if (i != j) {
                // Если между вершинами в множестве вершин есть дуга или несколько одинаковых вершин
                // То это множество вершин не является ядром графа
                if (nodesedge.at(core.at(i) - 1).at(core.at(j) - 1) == 1 || core.at(i) == core.at(j)) {
                    is_core = false; // Это множество вершин не является ядром графа
                }
            }
        }
    }

    // Если пройдена первая проверка
    if (is_core) {
        // Определяет, есть ли дуга из множества вершин в вершину графа
        bool node = false;
        int sizenodes = nodesedge.at(0).size(); // Количество вершин в графе
        // Проходим по всем вершинам графа
        for (int i = 0; i < sizenodes; ++i) {
            // Проходим по всем вершинам множества вершин
            for (int j = 0; j < size; ++j) {
                // Если данная вершина не является вершиной из множества вершин
                if (!fnode(core, i + 1)) {
                    // Если из вершины множества есть дуга в вершину графа и для этой вершины из графа
                    // еще не найдена вершина из множества вершин
                    if (nodesedge.at(core.at(j) - 1).at(i) == 1 && !node) {
                        // В вершину графа ведет дуга из множества вершин, тогда
                        // дальше эту вершину из графа не проверяем,
                        // есть ли какая-то дуга в эту вершину из множества
                        node = true;
                        j = size; // Дальше не проверяем данную вершину графа
                    }
                }
                else { // Если эта вершина из множества вершин
                    node = true; // Чтобы дальше проверять вершины графа
                }
            }
            // Если в вершину графа не ведет ни одна дуга из множества вершин
            if (node == false) {
                is_core = false; // Это множество вершин не ядро
                i = sizenodes; // Дальше не проверяем множество вершин
            }
            else {
                node = false; // Говорим, чтобы дальше проверять следующую вершину графа
            }
        }
        // Если false нигде не ставилось и равно true, то это множество вершин является ядром графа
        if (is_core) {
            return true; // Это множество является ядром графа
        }
    }

    return false; // Это множество не является ядром графа
}

void threadWrite(std::vector<graph> nodes, // Граф
    int sizeNodes, // Количество вершин, которые берем в очередь сначала
    std::queue<std::vector<int>>& queueCores, // Сслыка на очередь множеств вершин
    std::mutex& queueMutex, // Мьютекс для синхронизации данных
    std::condition_variable& condition, // Условная переменная
    bool& findCoreWrite, // Если все множества составлены, то true, ссылка на глобальную переменную
    std::vector<std::vector<int>>& queue, // Здесь будут все множества(просто сохраняем все множества)
    int thread // Определяет, как распрделить вершины между двумя потоками
) {
    int size = nodes.size(); // Количество вершин в графе

    // Размер множетсва, на котором будем строить другие множества
    int n = 1;
    std::vector<int> core; // Множество вершин
    // Множество вершин, используется для уникальности, если в coreUnique что-то добавляется
    // то добавляется и в core
    std::set<int> coreUnique;

    // Сюда будем записывать множества вершин, которые построили, чтобы потом записать их в cores
    std::vector<std::vector<int>> coresCreated;
    // Если в это множество что-то добавляется, то добавляется и в coresnow
    std::set<std::set<int>> coresCreatedUnique;

    // Здесь множества вершин, на которых будем строить другие множества вершин
    std::vector<std::vector<int>> cores;
    // Если сюда что-то добавляется, то добавляется и cores
    std::set<std::set<int>> coresUnique;

    // Индекс начальной вершины графа
    int beginNode = 0;
    // Индекс конечной вершины графа
    int endNode = 0;

    // Если это первый поток записи
    if (thread == 0) {
        beginNode = 0; // Начало графа
        endNode = sizeNodes; // Половина вершин
    }
    else { // Если второй потоки записи
        beginNode = sizeNodes + 1; // Индекс начала второй половины
        endNode = size; // Последняя вершина в графе
    }
    // Проходим по всем вершинам основного графа от начальной вершины до конечной вершины
    for (int i = beginNode; i < endNode; ++i) {
        // Если можем добавить вершину в множество вершин, проверка уникальности
        bool isUnique = coresUnique.insert({ nodes.at(i).node }).second;
        if (isUnique) {
            // Добавляем множество вершин в cores, на котором будем потом строить другие множества
            cores.push_back({ nodes.at(i).node });
        }
        // Синхронизируем запись множества вершин в очередь этих множеств
        {
            std::unique_lock<std::mutex> lock(queueMutex); // Синхронизация
            // Если количество элементов в очереди больше maxsize и ядро еще не найдено,
            // то поток записи ждет, пока не свободится место в очереди множеств вершин         
            condition.wait(lock, [&queueCores]() {
                return !(queueCores.size() >= MAX_SIZE) || !isNode; });
            if (isUnique) {
                // Запись множества вершин в очередь этих множеств
                queueCores.push({ nodes.at(i).node });
                queue.push_back({ nodes.at(i).node }); // Сохраняем множество
            }
        }
        condition.notify_one(); // Освобождаем поток чтения из блокировки
    }
    // Пока ядро ориетированного графа не найдено и размер множества, на котором строим множества вершин
    // Не равен количеству вершин в графе, то строим множества вершин
    while (isNode && (n < size)) {
        // Проходим по всем множества вершин в cores
        for (int i = 0; i < cores.size(); ++i) {
            // Берем множество вершин из cores, на котором будем строить другие множества вершин
            core = cores.at(i);
            auto iter = coresUnique.begin(); // Итератор на первый элемент множества set
            coreUnique = *iter; // Берем первый элемент множества
            coresUnique.erase(iter); // Удаляем первый элемент множества
            // Проходим по всем вершинам графа
            for (int j = 0; j < size; ++j) {
                // Если можно добавить вершину в множество вершин, проверка уникальности
                bool isUnique = coreUnique.insert(nodes.at(j).node).second;
                // Если можно добавить множество вершин в coresnow
                // Например: чтобы не было такого, что в coresnow [ [1,5], [5,1], [1,2,4,5], [1,2,5,4]]
                bool isUnique1 = false;
                if (isUnique) {
                    // Добавляем в множество вершин вершину
                    core.push_back(nodes.at(j).node);

                    isUnique1 = coresCreatedUnique.insert(coreUnique).second;
                    if (isUnique1) {
                        // Добавляем в coresnow множество вершин, которое
                        // только что получили из другого множества вершин
                        coresCreated.push_back(core);
                    }
                }
                // Синхронизируем добавление множества вершин в очередь этих множеств 
                {
                    std::unique_lock<std::mutex> lock(queueMutex); // Синхронизация 
                    // Если количество элементов в очереди больше maxsize и ядро еще не найдено, 
                    // то поток записи ждет, пока не освободится место в очереди множеств вершин
                    condition.wait(lock, [&queueCores]() {
                        return !(queueCores.size() >= MAX_SIZE) || !isNode; });
                    // Если мы добавили новое множество в coresnow,
                    // то добавим множество в очередь множеств
                    if (isUnique1) {
                        queueCores.push(core); // Добавление множества вершин в очередь этих множеств
                        queue.push_back(core); // Сохраняем множество
                    }
                }
                if (!isNode) { // Если ядро графа найдено, то заканчиваем составлять множества
                    j = size;
                    i = cores.size();
                }
                condition.notify_one(); // Освобождаем поток чтения из блокировки
                // Если в множество вершин что-то добавляли
                if (isUnique) {
                    // Удаляем добавленную вершину из множества set
                    coreUnique.erase(core.at(core.size() - 1));
                    core.pop_back(); // Удаляем вершину из множества вершин
                }
            }
        }
        n++; // Увеличиваем размер множеств, на которых строим другие множества
        cores.clear(); // Очищаем множество множеств cores
        cores = coresCreated; // Приравниваем к cores coresnow
        // Очищаем множество множества вершин coresnow, чтобы записывать другие множества, на
        // будем составлять другие множества
        coresCreated.clear();
        // Теперь проверяем уникальность множеств по другим множествам, которые только что составили и
        // записали в множество множеств coresnowUnique
        coresUnique = coresCreatedUnique;
        coresCreatedUnique.clear(); // Очищаем множество
    }
    findCoreWrite = true; // Говорим, что поток записал всевозможные множества вершин
    condition.notify_one(); // Освобождаем поток чтения из блокировки
}

// Первый поток чтения множеств вершин
void threadRead(std::vector<std::vector<int>> nodesedge, // Матрица смежности
    std::queue<std::vector<int>>& queueCores, // Очередь в которой находятся множества вершин
    std::mutex& queueMutex, // Мьютекс для синхронизации данных
    std::condition_variable& condition, // Условная переменная первой группы потоков
    //std::condition_variable& condition1, // Условная переменная второй гурппы потков
    // Ссылка на глобальную переменную, которая означает, что поток записи записал все множества
    // если true
    bool& findcorewrite,
    // Ссылка на глобальную переменную, которая означает, что поток записи записал все множества и
    // поток чтения прочитал все множества, если true
    bool& findcoreread)
{
    std::vector<int> core; // Множество вершин
    // Пока ядро графа не найдено и пока оно ищется
    while (isNode && !findcoreread) {
        // Синхронизация считывания множества вершин из множества
        {
            // Синхронизация
            std::unique_lock<std::mutex> lock(queueMutex);
            // Если очередь пуста и поток все еще записывает множества вершин
            // То блокируем поток чтения и ждем, пока в очереди не появится множество вершин
            condition.wait(lock, [&queueCores, &findcorewrite] {
                return !queueCores.empty() || findcorewrite; });

            // Если очередь не пуста
            if (!queueCores.empty()) {
                core = queueCores.front(); // Берем первый элемент из очереди множества вершин
                queueCores.pop(); // Удаляем первый элемент из очереди множества вершин
            }
            else {
                // Если поток записи записал все возможные множества вершин, 
                // то этот поток дальше вершины не записывает
                if (findcorewrite) {
                    findcoreread = true;
                }
            }
        }
        // Если проверены все множества, то в этом графе ядра нету
        if (coreRead && coreRead1) {
            isNode = false;
        }
        condition.notify_one();

        // Проверка на ядро ориентированного графа
        if (isCore(nodesedge, core)) { // Если множество вершин является ядром графа
            // Синхронизация добавления в coreGraph ядра графа и завершение всех потоков
            {
                // Синхронизация
                std::unique_lock<std::mutex> lock(queueMutex);
                // Присваиваем в coreGraph множество вершин, которое является ядром ориентированного графа
                graphCore = core;
                // Завершаем все потоки записи и чтения
                isNode = false;
            }
            condition.notify_one();
            //condition1.notify_one();
        }
    }
}

void CoreGraphStart() {
    isNode = true;
    findCoreWrite = false;
    findCoreWrite1 = false;
    coreRead = false;
    coreRead1 = false;
    //queueMutex.unlock();
    //queueMutex1.unlock();
    graphCore.clear();
    while (!queueCores.empty()) {
        queueCores.pop();
    }
    while (!queueCores1.empty()) {
        queueCores1.pop();
    }
    condition.notify_all();
    condition1.notify_all();
    queue.clear();
    queue1.clear();

}
COREGRAPH_API int* CoreThisGraph(int** graphEdge, int* graphSize, int* coreSize)
{   
    CoreGraphStart();
    int sizeGraph = *graphSize;
    int countNodes = 0;
    if (sizeGraph == 1) {
        int* coreFind = new int[1] {1};
        *coreSize = 1;
        return coreFind;
    }
    std::vector<graph> graphEdit;
    std::vector<std::vector<int>> nodesEdge = {};

    for (size_t i = 0; i < sizeGraph; ++i) {
        std::vector<int> nodes = {};
        for (size_t j = 0; j < sizeGraph; ++j) {
            nodes.push_back(graphEdge[i][j]);
        }
        nodesEdge.push_back(nodes);
    }

    for (size_t i = 0; i < sizeGraph; ++i) {
        graph nodeFromGraph = { i + 1, {} };
        for (size_t j = 0; j < sizeGraph; ++j) {
            if (nodesEdge[i][j] == 1) {
                nodeFromGraph.nodes.push_back(nodesEdge[i][j]);
            }
        }
        graphEdit.push_back(nodeFromGraph);
    }

    countNodes = sizeGraph / 2 == 0 ? sizeGraph / 2 : (sizeGraph / 2) + 1;

    std::thread threadWriter(
        threadWrite, 
        graphEdit, countNodes,
        std::ref(queueCores), 
        std::ref(queueMutex), 
        std::ref(condition), 
        std::ref(findCoreWrite),
        std::ref(queue), 0);

    std::thread threadWriter1(
        threadWrite,
        graphEdit, sizeGraph - countNodes,
        std::ref(queueCores1),
        std::ref(queueMutex1),
        std::ref(condition1),
        std::ref(findCoreWrite1),
        std::ref(queue1), 1);

    std::thread threadReader(threadRead,
        nodesEdge,
        std::ref(queueCores),
        std::ref(queueMutex),
        std::ref(condition),
        std::ref(findCoreWrite),
        std::ref(coreRead));

    std::thread threadReader1(threadRead,
        nodesEdge,
        std::ref(queueCores1),
        std::ref(queueMutex1),
        std::ref(condition1),
        std::ref(findCoreWrite1),
        std::ref(coreRead1));
    
    threadWriter.join();
    threadWriter1.join();
    threadReader.join();
    threadReader1.join();

    if (graphCore.empty()) {
        graphCore.push_back(-1);
        int* coreFind = new int[1] {-1};
        *coreSize = 1;
        return coreFind;
    }
    else {
        int* coreFind = new int[graphCore.size()];
        std::memcpy(coreFind, graphCore.data(), graphCore.size() * sizeof(int));
        *coreSize = graphCore.size();
        return coreFind;
    }

    return new int [1] {-1};
}

COREGRAPH_API void FreeMemory(int* core)
{
    delete[] core;
}









