#include "shapeshifter_solver.hpp"

#include <algorithm>
#include <ctime>

extern int start_s;

bool pieceComperatorBackward(std::tuple<unsigned int, const Piece*, unsigned int> i, std::tuple<unsigned int, const Piece*, unsigned int> j) {
	return (std::get<1>(i)->height * std::get<1>(i)->width) > (std::get<1>(j)->height * std::get<1>(j)->width);
}

bool pieceAComperatorBackward1(std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> i, 
							  std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> j) {
	return (std::get<1>(i)->height * std::get<1>(i)->width) > (std::get<1>(j)->height * std::get<1>(j)->width);
}

bool pieceAComperatorBackward3(std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> i, 
							  std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> j) {
	return (std::get<3>(i) < std::get<3>(j));
}


ShapeShifter::ShapeShifter(const std::string& fileName) {
	std::ifstream iFile;
	std::string line;
	char tmp;
	unsigned int height, width;

	this->fn = fileName;

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
	this->pieces.reserve(this->numOfPieces);
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

	this->sol.resize(this->numOfPieces);

	this->total_boards_scanned = 0;
	this->total_recursive_calls = 0;

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
}

void ShapeShifter::Solve(const std::string &algorithm) {
	bool isFound = false;

	if (!algorithm.compare("bf")) {
		isFound = this->SolveBF();
	}
	else if (!algorithm.compare("bf_prune")) {
		isFound = this->SolveBFPrune();
	}
	else if (!algorithm.compare("bd")) {
		isFound = this->SolveBD();
	}

	else if (!algorithm.compare("bf_all")) {
		this->SolveBFAll();
	}
	else if (!algorithm.compare("bf_prune_all")) {
		this->SolveBFPruneAll();
	}

	if (isFound) {
		std::cout << "Found!!!" << std::endl;
	}
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

		for (unsigned int a = 0; a < this->pieces[p]->height; ++a) {
			for (unsigned int b = 0; b < this->pieces[p]->width; ++b) {
				sum += this->pieces[p]->p[a][b];
			}
		}

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
	int deltaWeight;

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

			deltaWeight = 0;

			for (unsigned int a = 0; a < std::get<1>(p)->height; ++a) {
				for (unsigned int b = 0; b < std::get<1>(p)->width; ++b) {
					this->board[i + a][j + b] = (this->board[i + a][j + b] + std::get<1>(p)->p[a][b]) % this->X;

					if (std::get<1>(p)->p[a][b] != 0) {
						if (this->board[i + a][j + b] == 1)
							deltaWeight += (this->X - 1);
						else
							deltaWeight--;
					}
				}
			}

			this->sol[std::get<0>(p)].first = i;
			this->sol[std::get<0>(p)].second = j;

			this->weight += deltaWeight;
			if (this->SolveBFPruneHelper(l + 1, augmentedPieces, partialCover))
				return true;

			this->weight -= deltaWeight;

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

bool ShapeShifter::SolveBD() {
	unsigned long long multA = 1, multB = 1;

	std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> *augmentedPieces = 
			new std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> [this->numOfPieces];

	for (unsigned int p = 0; p < this->numOfPieces; ++p) {
		int sum = 0;

		for (unsigned int a = 0; a < this->pieces[p]->height; ++a) {
			for (unsigned int b = 0; b < this->pieces[p]->width; ++b) {
				sum += this->pieces[p]->p[a][b];
			}
		}

		augmentedPieces[p] = std::make_tuple(p, this->pieces[p], sum, -1, -1);
	}

	std::sort(augmentedPieces, augmentedPieces + this->numOfPieces, pieceAComperatorBackward1);

	this->half = 0;

	for (unsigned int p = 0; p < this->numOfPieces; ++p) {
		std::get<4>(augmentedPieces[p]) = (this->boardSize[0] - std::get<1>(augmentedPieces[p])->height + 1) * 
					 					  (this->boardSize[1] - std::get<1>(augmentedPieces[p])->width + 1);
		if (multA <= multB * 1000) {
			std::get<3>(augmentedPieces[p]) = 0;
			multA *= std::get<4>(augmentedPieces[p]);
			this->half += 1;
		}
		else {
			std::get<3>(augmentedPieces[p]) = 1;
			multB *= std::get<4>(augmentedPieces[p]);
		}
	}

	std::sort(augmentedPieces, augmentedPieces + this->numOfPieces, pieceAComperatorBackward3);

	int *partialCover = new int [this->half];
	int totalCover = 0;
	bool flag;

	for (unsigned int p = 0; p < this->half; ++p) {
		totalCover += std::get<2>(augmentedPieces[p]);
	}

	for (unsigned int p = 0; p < this->half; ++p) {
		partialCover[p] = totalCover;
		totalCover -= std::get<2>(augmentedPieces[p]);
	}

	this->middleBoard = new unsigned int* [this->boardSize[0]];
	for (unsigned int i = 0; i < this->boardSize[0]; ++i) {
		this->middleBoard[i] = new unsigned int [this->boardSize[1]];

		for (unsigned int j = 0; j < this->boardSize[1]; ++j)
			this->middleBoard[i][j] = 0;
	}

	std::cout << "Searching backward..." << std::endl;
	this->middlePos.resize(this->numOfPieces - this->half);
	this->SolveBDBackwardHelper(this->half, augmentedPieces);
	std::cout << "\rSearching backward... Done" << std::endl;

	std::cout << "Searching forward..." << std::endl;
	flag = this->SolveBDForwardHelper(0, augmentedPieces, partialCover);
	std::cout << "\rSearching forward... Done" << std::endl;

	delete augmentedPieces;
	delete partialCover;

	return flag;
}
	/*int 


		self.middle_weights = {}
		self.middle_weight = 0


		self.max_middle_weight = max(self.middle_weights)

	*/


void ShapeShifter::SolveBDBackwardHelper(unsigned int l,
										 const std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> *augmentedPieces) {
	int deltaWeight;
	std::pair<std::size_t, std::size_t> hash (0, 1);
/*
if l == self.num_of_pieces:
			self.middle_weights[self.middle_weight] = True

			return
			*/
	if (l == this->numOfPieces) {
		this->hashMiddleBoard(hash.first);
		this->hashMiddleBoard(hash.second);

		this->middlePositions.insert(std::make_pair(hash, middlePos));

		return;
	}

	const std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> &p = augmentedPieces[l];

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

			deltaWeight = 0;

			for (unsigned int a = 0; a < std::get<1>(p)->height; ++a) {
				for (unsigned int b = 0; b < std::get<1>(p)->width; ++b) {
					if (std::get<1>(p)->p[a][b] != 0) {
						if (this->middleBoard[i + a][j + b] == 1)
							deltaWeight += (this->X - 1);
						else
							deltaWeight--;
					}

					this->middleBoard[i + a][j + b] = (this->middleBoard[i + a][j + b] - std::get<1>(p)->p[a][b] + this->X) % this->X;
				}
			}

			this->middlePos[l - this->half].first = i;
			this->middlePos[l - this->half].second = j;
			this->middleWeight += deltaWeight;

			this->SolveBDBackwardHelper(l + 1, augmentedPieces);

			this->middleWeight -= deltaWeight;

			for (unsigned int a = 0; a < std::get<1>(p)->height; ++a) {
				for (unsigned int b = 0; b < std::get<1>(p)->width; ++b) {
					this->middleBoard[i + a][j + b] = (this->middleBoard[i + a][j + b] + std::get<1>(p)->p[a][b]) % this->X;
				}
			}
		}
	}

	#ifdef VERBOSE
	std::cout << "\x1b[A";;	
	#endif
}

bool ShapeShifter::SolveBDForwardHelper(unsigned int l, const std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> *augmentedPieces,
										const int *partialCover) {
	int deltaWeight;
	std::pair<std::size_t, std::size_t> hash (0, 1);

	if (l == this->half) {
		this->hashBoard(hash.first);
		this->hashBoard(hash.second);

		auto it = this->middlePositions.find(hash);

		if (it != this->middlePositions.end()) {
			for(unsigned int p = 0; p < this->numOfPieces - this->half; ++p) {
				this->sol[std::get<0>(augmentedPieces[p + this->half])].first = it->second[p].first;
				this->sol[std::get<0>(augmentedPieces[p + this->half])].second = it->second[p].second;
			}

			std::cout << "Solution found!" << std::endl;

			for (unsigned int i = 0; i < this->numOfPieces; ++i) {
				std::cout << "Piece #" << i << ", Pos: " << this->sol[i].first << "," << this->sol[i].second << std::endl;
			}
			
			return true;
		}

		return false;
	}

	const std::tuple<unsigned int, const Piece*, unsigned int, unsigned int, unsigned int> &p = augmentedPieces[l];

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

			deltaWeight = 0;

			for (unsigned int a = 0; a < std::get<1>(p)->height; ++a) {
				for (unsigned int b = 0; b < std::get<1>(p)->width; ++b) {
					this->board[i + a][j + b] = (this->board[i + a][j + b] - std::get<1>(p)->p[a][b] + this->X) % this->X;

					if (std::get<1>(p)->p[a][b] != 0) {
						if (this->board[i + a][j + b] == 1)
							deltaWeight += (this->X - 1);
						else
							deltaWeight--;
					}
					
				}
			}

			this->sol[std::get<0>(p)].first = i;
			this->sol[std::get<0>(p)].second = j;
			this->weight += deltaWeight;

			if (this->SolveBDForwardHelper(l + 1, augmentedPieces, partialCover))
				return true;

			this->weight -= deltaWeight;

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

/*
if l == self.half:
			if hash(str(self.board)) in self.middle_boards:
				pos = self.pos + self.middle_boards[hash(str(self.board))]
				pos = [(self.augmented_pieces[i][0], p) for i, p in enumerate(pos)]
				pos = map(lambda p: p[1], sorted(pos, key=lambda p: p[0]))
				
				print 'Solution:'
				for i, p in enumerate(pos):
					print 'Piece #{}, Pos: {},{}'.format(i, p[0], p[1])
				return pos

			return False

		# Prune if not enough "coverage capacity" left
		if self.weight - self.partial_cover[l] > self.max_middle_weight:
			return False*/





void ShapeShifter::SolveBFAll() {
	std::ofstream oFile;
	unsigned int totSolutions = 0;
	unsigned int curSolution = 0;

	this->SolveBFAllHelper(0);

	std::sort(this->solutions.begin(), this->solutions.end());

	totSolutions = this->solutions.size();
	oFile.open(this->fn + "_sol_bf_all_c++", std::ios::out);

	for (unsigned int i = 0; i < totSolutions && i < 10000; ++i) {
		curSolution++;
		//std::cout << "Solution (" << curSolution << "/" << totSolutions << "):" << std::endl;
		oFile     << "Solution (" << curSolution << "/" << totSolutions << "):" << std::endl;

		for (unsigned int j = 0; j < this->solutions[i].size(); ++j) {
			//std::cout << "    Piece #" << j << ", Pos: " << this->solutions[i][j].first << "," << this->solutions[i][j].second << std::endl;
			oFile     << "    Piece #" << j << ", Pos: " << this->solutions[i][j].first << "," << this->solutions[i][j].second << std::endl;
		}
	}
	
	std::cout << "\nTotal boards scanned: " << this->total_boards_scanned << std::endl;
	std::cout << "Total recursive calls: " << this->total_recursive_calls << std::endl;
	oFile     << "\nTotal boards scanned: " << this->total_boards_scanned << std::endl;
	oFile     << "Total recursive calls: " << this->total_recursive_calls << std::endl;
	oFile     << "Total time: " << (clock()-start_s)/double(CLOCKS_PER_SEC) << " secs" << std::endl;

	oFile.close();
}

bool ShapeShifter::SolveBFAllHelper(unsigned int l) {
	int delta_weight;

	this->total_recursive_calls++;

	if (l == this->numOfPieces) {
		if (this->weight == 0) {
			this->solutions.push_back(this->sol);
		}

		this->total_boards_scanned++;

		return false;
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

			this->SolveBFAllHelper(l + 1);

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

void ShapeShifter::SolveBFPruneAll() {
	std::tuple<unsigned int, const Piece*, unsigned int> *augmentedPieces = new std::tuple<unsigned int, const Piece*, unsigned int> [this->numOfPieces];
	int *partialCover = new int [this->numOfPieces];
	int totalCover = 0;

	for (unsigned int p = 0; p < this->numOfPieces; ++p) {
		int sum = 0;

		for (unsigned int a = 0; a < this->pieces[p]->height; ++a) {
			for (unsigned int b = 0; b < this->pieces[p]->width; ++b) {
				sum += this->pieces[p]->p[a][b];
			}
		}

		augmentedPieces[p] = std::make_tuple(p, this->pieces[p], sum);
		totalCover += sum;
	}

	std::sort(augmentedPieces, augmentedPieces + this->numOfPieces, pieceComperatorBackward);

	for (unsigned int p = 0; p < this->numOfPieces; ++p) {
		partialCover[p] = totalCover;
		totalCover -= std::get<2>(augmentedPieces[p]);
	}

	std::ofstream oFile;
	unsigned int totSolutions = 0;
	unsigned int curSolution = 0;

	this->SolveBFPruneAllHelper(0, augmentedPieces, partialCover);

	std::sort(this->solutions.begin(), this->solutions.end());

	totSolutions = this->solutions.size();
	oFile.open(this->fn + "_sol_bf_prune_all_c++", std::ios::out);

	for (unsigned int i = 0; i < totSolutions && i < 10000; ++i) {
		curSolution++;
		oFile     << "Solution (" << curSolution << "/" << totSolutions << "):" << std::endl;

		for (unsigned int j = 0; j < this->solutions[i].size(); ++j) {
			oFile     << "    Piece #" << j << ", Pos: " << this->solutions[i][j].first << "," << this->solutions[i][j].second << std::endl;
		}
	}

	std::cout << "\nTotal boards scanned: " << this->total_boards_scanned << std::endl;
	std::cout << "Total recursive calls: " << this->total_recursive_calls << std::endl;
	oFile     << "\nTotal boards scanned: " << this->total_boards_scanned << std::endl;
	oFile     << "Total recursive calls: " << this->total_recursive_calls << std::endl;
	oFile     << "Total time: " << (clock()-start_s)/double(CLOCKS_PER_SEC) << " secs" << std::endl;

	oFile.close();

	delete augmentedPieces;
	delete partialCover;
}

bool ShapeShifter::SolveBFPruneAllHelper(unsigned int l, const std::tuple<unsigned int, const Piece*, unsigned int> *augmentedPieces, const int *partialCover) {
	int delta_weight;

	this->total_recursive_calls++;

	if (l == this->numOfPieces) {
		if (this->weight == 0) {
			this->solutions.push_back(this->sol);
		}

		this->total_boards_scanned++;

		return false;
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
			
			SolveBFPruneAllHelper(l + 1, augmentedPieces, partialCover);

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

std::size_t ShapeShifter::hashBoard(std::size_t &seed) {
	for (unsigned int i = 0; i < this->boardSize[0]; ++i) {
		for (unsigned int j = 0; j < this->boardSize[1]; ++j) {
			seed ^= this->board[i][j] + 0x9e3779b9 + (seed<<6) + (seed>>2);
		}
	}

	return seed;
}

std::size_t ShapeShifter::hashMiddleBoard(std::size_t &seed) {
	for (unsigned int i = 0; i < this->boardSize[0]; ++i) {
		for (unsigned int j = 0; j < this->boardSize[1]; ++j) {
			seed ^= this->middleBoard[i][j] + 0x9e3779b9 + (seed<<6) + (seed>>2);
		}
	}

	return seed;
}