#pragma once
#include <vector>
#ifdef COREGRAPH_EXPORTS
	#define COREGRAPH_API __declspec(dllexport)
#else
	#define COREGRAPH_API __declspec(dllimport)
#endif

extern "C" COREGRAPH_API int* CoreThisGraph(int** graphEdge, int* graphSize, int* coreSize);
extern "C" COREGRAPH_API void FreeMemory(int* core);