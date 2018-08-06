#pragma once

#include <string>
#include <vector>
#include "shape.hpp"


class ShapeShifter {
public:
	ShapeShifter(const std::string& fileName, bool printLog = false, unsigned int numOfThreads = 1);
	~ShapeShifter();

	void Print() const;
	bool Solve();
	void PrintSolution() const;

#ifndef VERBOSE
	std::string GetSolutionString();
	void Status() const;
#endif
	
private:
	bool SolveHelper(unsigned int threadID);

	std::string fn;
	bool printLog;

	int Modulo;
	unsigned int boardX, boardY;
	unsigned int numCells;
	int **board;

	int numShapes;
	Shape *shapes;

	int numFlips;
	int isSolved;

	unsigned int numOfThreads;
	unsigned int threadIdSolver;
	bool *threadStatus;

#ifndef VERBOSE
	std::string solution;
#endif
};