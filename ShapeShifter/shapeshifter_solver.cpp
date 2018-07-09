#include "shapeshifter_solver.hpp"

ShapeShifter::ShapeShifter(const std::string& fileName, bool verbose) {
	std::ifstream iFile;
	std::string line;
	char tmp;
	unsigned int height, width;

	this->verbose = verbose;

	iFile.open(fileName, std::ios::in);

	iFile >> this->X;
	iFile >> this->boardSize[0] >> tmp >> boardSize[1];

	this->board = new unsigned int* [this->boardSize[0]];
	for (unsigned int i = 0; i < this->boardSize[0]; ++i)
		this->board[i] = new unsigned int [this->boardSize[1]];

	for (unsigned int i = 0; i < this->boardSize[0]; ++i) {
		iFile >> line;

		for (unsigned int j = 0; j < this->boardSize[1]; ++j) {
			this->board[i][j] = line[j] - '0';
		}
	}

	iFile >> this->numOfPieces;
	this->pieces = new Piece* [this->numOfPieces];
	for (unsigned int p = 0; p < this->numOfPieces; ++p) {
		iFile >> height >> tmp >> width;
		this->pieces[p] = new Piece(height, width);

		for (unsigned int i = 0; i < height; ++i) {
			iFile >> line;

			for (unsigned int j = 0; j < width; ++j) {
				this->pieces[p]->p[i][j] = line[j] - '0';
			}
		}
	}

	iFile.close();

	if (verbose) {
		std::cout << "Loading from file '" << fileName << "'..." << std::endl;
		std::cout << "Modulo: " << this->X << std::endl;
		std::cout << "Board size: " << this->boardSize[0] << "x" << this->boardSize[1] << std::endl;

		std::cout << "Board:" << std::endl;
		for (unsigned int i = 0; i < this->boardSize[0]; ++i) {
			std::cout << "\t";
			for (unsigned int j = 0; j < this->boardSize[1]; ++j) {
				std::cout << this->board[i][j] << " ";
			}
			std::cout << std::endl;
		}

		std::cout << "Total pieces: " << this->numOfPieces << std::endl;
		for (unsigned int p = 0; p < this->numOfPieces; ++p) {
			std::cout << "\t" << "Piece #" << p << ":" << std::endl;
			for (unsigned int i = 0; i < this->pieces[p]->height; ++i) {
				std::cout << "\t\t";
				for (unsigned int j = 0; j < this->pieces[p]->width; ++j) {
					std::cout << this->pieces[p]->p[i][j] << " ";
				}
				std::cout << std::endl;
			}
		}
	}
}

ShapeShifter::~ShapeShifter() {
	for (unsigned int i = 0; i < this->boardSize[0]; ++i)
		delete this->board[i];
	delete this->board;

	for (unsigned int i = 0; i < this->numOfPieces; ++i)
		delete this->pieces[i];
	delete this->pieces;

}

void ShapeShifter::Solve(const std::string &algorithm) {
	if (algorithm.compare("bf")) {
		this->SolveBF();
	}
}
