#pragma once

#include <iostream>
#include <fstream>
#include <string>
#include <utility>
#include <tuple>
#include <vector>

#include "piece.hpp"

class ShapeShifter {
public:
	ShapeShifter(const std::string& fileName);
	~ShapeShifter();

	void Solve(const std::string &algorithm = "bf");

	bool SolveBF();			// Brute-Force solver
	bool SolveBFPrune();	// Brute-Force with pruning

	void SolveBFAll();

private:
	std::string fn;
	unsigned int X;
	unsigned int boardSize[2];
	unsigned int **board;
	unsigned int numOfPieces;
	std::vector<Piece *> pieces;
	int weight;

	std::vector<std::pair<unsigned int, unsigned int>> sol;
	std::vector<std::vector<std::pair<unsigned int, unsigned int>>> solutions;

	unsigned int total_boards_scanned, total_recursive_calls;

	bool SolveBFHelper(unsigned int l);
	bool SolveBFPruneHelper(unsigned int l, const std::tuple<unsigned int, const Piece*, unsigned int> *augmentedPieces, const int *partialCover);

	bool SolveBFAllHelper(unsigned int l);
};