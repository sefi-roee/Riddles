#pragma once

#include <iostream>
#include <fstream>
#include <string>
#include <utility>

#include "piece.hpp"

class ShapeShifter {
public:
	ShapeShifter(const std::string& fileName);
	~ShapeShifter();

	void Solve(const std::string &algorithm = "bf");

	// Brute-Force solver
	bool SolveBF();

private:
	unsigned int X;
	unsigned int boardSize[2];
	unsigned int **board;
	unsigned int numOfPieces;
	Piece **pieces;
	std::pair<unsigned int, unsigned int> *sol;
	int weight;

	bool SolveBFHelper(unsigned int l);
};