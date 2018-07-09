#pragma once

#include <iostream>
#include <fstream>
#include <string>
#include <utility>

#include "piece.hpp"

class ShapeShifter {
public:
	ShapeShifter(const std::string& fileName, bool verbose = false);
	~ShapeShifter();

	void Solve(const std::string &algorithm = "bf");

	void SolveBF();

private:
	bool verbose;
	unsigned int X;
	unsigned int boardSize[2];
	unsigned int **board;
	unsigned int numOfPieces;
	Piece **pieces;
};