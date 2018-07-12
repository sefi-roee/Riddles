#pragma once

#include <iostream>
#include <fstream>
#include <string>
#include <utility>
#include <tuple>
#include <vector>
#include <unordered_map>

#include "piece.hpp"

struct pair_hash {
    template <class T1, class T2>
    std::size_t operator () (const std::pair<T1,T2> &p) const {
        auto h1 = p.first;
        auto h2 = p.second;

        // Mainly for demonstration purposes, i.e. works but is overly simple
        // In the real world, use sth. like boost.hash_combine
        return h1 ^ h2;  
    }
};

class ShapeShifter {
public:
	ShapeShifter(const std::string& fileName);
	~ShapeShifter();

	void Solve(const std::string &algorithm = "bf");

	bool SolveBF();			// Brute-Force solver
	bool SolveBFPrune();	// Brute-Force solver with pruning
	bool SolveBD();			// Bi-Directional solver

	void SolveBFAll();		// Brute-Force solver (finds all solutions)
	void SolveBFPruneAll();	// Brute-Force solver (finds all solutions)

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
	unsigned int half;
	unsigned int **middleBoard;
	std::vector<std::pair<unsigned int, unsigned int>> middlePos;
	int middleWeight;
	std::unordered_map< std::pair<std::size_t, std::size_t>, std::vector<std::pair<unsigned int, unsigned int>>, pair_hash> middlePositions;

	bool SolveBFHelper(unsigned int l);
	bool SolveBFPruneHelper(unsigned int l, const std::tuple<unsigned int, const Piece*, unsigned int> *augmentedPieces, const int *partialCover);

	void SolveBDBackwardHelper(unsigned int l, const std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> *augmentedPieces);
	bool SolveBDForwardHelper(unsigned int l, const std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> *augmentedPieces,
							  const int *partialCover);
	bool SolveBFAllHelper(unsigned int l);
	bool SolveBFPruneAllHelper(unsigned int l, const std::tuple<unsigned int, const Piece*, unsigned int> *augmentedPieces, const int *partialCover);

	std::size_t hashBoard(std::size_t &seed);
	std::size_t hashMiddleBoard(std::size_t &seed);
};