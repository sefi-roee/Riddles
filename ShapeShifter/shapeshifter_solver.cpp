#include "shapeshifter_solver.hpp"

#include <algorithm>

bool pieceComperatorBackward(std::tuple<unsigned int, const Piece*, unsigned int> i, std::tuple<unsigned int, const Piece*, unsigned int> j) {
	return (std::get<1>(i)->height * std::get<1>(i)->width) > (std::get<1>(j)->height * std::get<1>(j)->width);
}

ShapeShifter::ShapeShifter(const std::string& fileName) {
	std::ifstream iFile;
	std::string line;
	char tmp;
	unsigned int height, width;

	iFile.open(fileName, std::ios::in);

	iFile >> this->X;
	iFile >> this->boardSize[0] >> tmp >> boardSize[1];

	this->board = new unsigned int* [this->boardSize[0]];
	this->weight = 0;
	for (unsigned int i = 0; i < this->boardSize[0]; ++i)
		this->board[i] = new unsigned int [this->boardSize[1]];

	for (unsigned int i = 0; i < this->boardSize[0]; ++i) {
		iFile >> line;

		for (unsigned int j = 0; j < this->boardSize[1]; ++j) {
			this->board[i][j] = line[j] - '0';
			this->weight += (this->board[i][j] - this->X) % this->X;
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

	this->sol = new std::pair<unsigned int, unsigned int> [this->numOfPieces];

	iFile.close();

	#ifdef VERBOSE
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
		std::cout << "\t" << "Piece #" << p << "(" << this->pieces[p]->height << "x" << this->pieces[p]->width << "):" << std::endl;
		for (unsigned int i = 0; i < this->pieces[p]->height; ++i) {
			std::cout << "\t\t";
			for (unsigned int j = 0; j < this->pieces[p]->width; ++j) {
				std::cout << this->pieces[p]->p[i][j] << " ";
			}
			std::cout << std::endl;
		}
	}
	#endif
}

ShapeShifter::~ShapeShifter() {
	for (unsigned int i = 0; i < this->boardSize[0]; ++i)
		delete this->board[i];
	delete this->board;

	for (unsigned int i = 0; i < this->numOfPieces; ++i)
		delete this->pieces[i];
	delete this->pieces;

	delete this->sol;
}

void ShapeShifter::Solve(const std::string &algorithm) {
	bool isFound;

	if (!algorithm.compare("bf")) {
		isFound = this->SolveBF();
	}
	else if (!algorithm.compare("bf_prune")) {
		isFound = this->SolveBFPrune();
	}

	if (isFound)
		std::cout << "Found!!!" << std::endl;
}

bool ShapeShifter::SolveBF() {
	return this->SolveBFHelper(0);
}

bool ShapeShifter::SolveBFHelper(unsigned int l) {
	int delta_weight;

	if (l == this->numOfPieces) {
		if (this->weight == 0) {
			std::cout << "Solution found!" << std::endl;

			for (unsigned int i = 0; i < this->numOfPieces; ++i) {
				std::cout << "Piece #" << i << ", Pos: " << this->sol[i].first << "," << this->sol[i].second << std::endl;
			}

			return true;
		}
		else {
			return false;
		}
	}

	const Piece *p = this->pieces[l];

	#ifdef VERBOSE
	unsigned int totPositions = (this->boardSize[0] - p->height + 1) * (this->boardSize[1] - p->width + 1);
	unsigned int curPosition  = 0;
	std::cout << std::endl;	
	#endif

	for (unsigned int i = 0; i < this->boardSize[0] - p->height + 1; ++i) {
		for (unsigned int j = 0; j < this->boardSize[1] - p->width + 1; ++j) {
			#ifdef VERBOSE
			curPosition++;
			std::cout << "\r" << curPosition << "/" << totPositions << "...";
			#endif

			delta_weight = 0;

			for (unsigned int a = 0; a < p->height; ++a) {
				for (unsigned int b = 0; b < p->width; ++b) {
					this->board[i + a][j + b] = (this->board[i + a][j + b] + p->p[a][b]) % this->X;

					if (p->p[a][b] != 0) {
						if (this->board[i + a][j + b] == 1)
							delta_weight += (this->X - 1);
						else
							delta_weight--;
					}
				}
			}

			this->sol[l].first = i;
			this->sol[l].second = j;

			this->weight += delta_weight;
			if (this->SolveBFHelper(l + 1))
				return true;

			this->weight -= delta_weight;

			for (unsigned int a = 0; a < p->height; ++a) {
				for (unsigned int b = 0; b < p->width; ++b) {
					this->board[i + a][j + b] = (this->board[i + a][j + b] - p->p[a][b] + this->X) % this->X;
				}
			}
		}
	}

	#ifdef VERBOSE
	std::cout << "\x1b[A";;	
	#endif

	return false;
}

bool ShapeShifter::SolveBFPrune() {
	std::tuple<unsigned int, const Piece*, unsigned int> *augmentedPieces = new std::tuple<unsigned int, const Piece*, unsigned int> [this->numOfPieces];
	int *partialCover = new int [this->numOfPieces];
	int totalCover = 0;
	bool flag;

	for (unsigned int p = 0; p < this->numOfPieces; ++p) {
		int sum = 0;

		//augmentedPieces[p].first = this->pieces[p];
		for (unsigned int a = 0; a < this->pieces[p]->height; ++a) {
			for (unsigned int b = 0; b < this->pieces[p]->width; ++b) {
				sum += this->pieces[p]->p[a][b];
			}
		}

		//augmentedPieces[p].second = sum;
		augmentedPieces[p] = std::make_tuple(p, this->pieces[p], sum);
		totalCover += sum;
	}

	std::sort(augmentedPieces, augmentedPieces + this->numOfPieces, pieceComperatorBackward);

	for (unsigned int p = 0; p < this->numOfPieces; ++p) {
		partialCover[p] = totalCover;
		totalCover -= std::get<2>(augmentedPieces[p]);
	}

	flag = this->SolveBFPruneHelper(0, augmentedPieces, partialCover);

	delete augmentedPieces;
	delete partialCover;

	return flag;
}

bool ShapeShifter::SolveBFPruneHelper(unsigned int l, const std::tuple<unsigned int, const Piece*, unsigned int> *augmentedPieces, const int *partialCover) {
	int delta_weight;

	if (l == this->numOfPieces) {
		if (this->weight == 0) {
			std::cout << "Solution found!" << std::endl;

			for (unsigned int i = 0; i < this->numOfPieces; ++i) {
				std::cout << "Piece #" << i << ", Pos: " << this->sol[i].first << "," << this->sol[i].second << std::endl;
			}

			return true;
		}
		else {
			return false;
		}
	}

	if (partialCover[l] < this->weight)
		return false;

	const std::tuple<unsigned int, const Piece*, unsigned int> &p = augmentedPieces[l];
	
	#ifdef VERBOSE
	unsigned int totPositions = (this->boardSize[0] - std::get<1>(p)->height + 1) * (this->boardSize[1] - std::get<1>(p)->width + 1);
	unsigned int curPosition  = 0;
	std::cout << std::endl;	
	#endif

	for (unsigned int i = 0; i < this->boardSize[0] - std::get<1>(p)->height + 1; ++i) {
		for (unsigned int j = 0; j < this->boardSize[1] - std::get<1>(p)->width + 1; ++j) {
			#ifdef VERBOSE
			curPosition++;
			std::cout << "\r" << curPosition << "/" << totPositions << "...";
			#endif

			delta_weight = 0;

			for (unsigned int a = 0; a < std::get<1>(p)->height; ++a) {
				for (unsigned int b = 0; b < std::get<1>(p)->width; ++b) {
					this->board[i + a][j + b] = (this->board[i + a][j + b] + std::get<1>(p)->p[a][b]) % this->X;

					if (std::get<1>(p)->p[a][b] != 0) {
						if (this->board[i + a][j + b] == 1)
							delta_weight += (this->X - 1);
						else
							delta_weight--;
					}
				}
			}

			this->sol[std::get<0>(p)].first = i;
			this->sol[std::get<0>(p)].second = j;

			this->weight += delta_weight;
			if (this->SolveBFPruneHelper(l + 1, augmentedPieces, partialCover))
				return true;

			this->weight -= delta_weight;

			for (unsigned int a = 0; a < std::get<1>(p)->height; ++a) {
				for (unsigned int b = 0; b < std::get<1>(p)->width; ++b) {
					this->board[i + a][j + b] = (this->board[i + a][j + b] - std::get<1>(p)->p[a][b] + this->X) % this->X;
				}
			}
		}
	}

	#ifdef VERBOSE
	std::cout << "\x1b[A";;	
	#endif

	return false;
}