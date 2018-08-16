#include "shapeshifter.hpp"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <cstring>
#include <iomanip>
#include <future>

bool shapeComperatorBackward(const Shape &i, const Shape &j);
bool shapeComperatorIdx(const Shape &i, const Shape &j);


ShapeShifter::ShapeShifter(const std::string& fileName, bool printLog, unsigned int numOfThreads) {
	std::ifstream iFile;		
	char tmp;

	this->fn = fileName;
	this->printLog = printLog;
	this->numOfThreads = numOfThreads;
	this->threadIdSolver = 999;

#ifndef VERBOSE
	this->solution = "";
#endif

	iFile.open(fileName, std::ios::in);

	// Read board layout
	iFile >> this->Modulo;
	iFile >> this->boardX >> tmp >> this->boardY;
	this->numCells = this->boardX * this->boardY;
	this->numFlips = 0;

	// Read board
	this->board = new int* [this->numOfThreads];

	this->board[0] = new int [this->numCells];

	int c = 0;
	std::string line;
	for (unsigned int i = 0; i < this->boardX; ++i) {
		iFile >> line;

		for (unsigned int j = 0; j < this->boardY; ++j) {
			this->board[0][c] = line[j] - '0';
			this->numFlips -= (this->Modulo - this->board[0][c++]) % this->Modulo;
		}
	}

	// Read shapes
	iFile >> this->numShapes;
	this->shapes  = new Shape [this->numShapes];

	std::vector<std::vector<unsigned int> > tmpShape;
	int numPoints;

	for (int s = 0; s < this->numShapes; ++s) {
		this->shapes[s].idx = s;
		iFile >> this->shapes[s].height >> tmp >> this->shapes[s].width;

		tmpShape.resize(this->shapes[s].height);
		numPoints = 0;
		for (unsigned int i = 0; i < this->shapes[s].height; ++i) {
			iFile >> line;
			tmpShape[i].resize(this->shapes[s].width);

			for (unsigned int j = 0; j < this->shapes[s].width; ++j) {
				tmpShape[i][j] = line[j] - '0';
				if (tmpShape[i][j] == 1) {
					numPoints++;
				}
			}
		}

		this->numFlips += numPoints;
		this->shapes[s].numPoints = numPoints;
		this->shapes[s].points = new unsigned int [numPoints];
		numPoints = 0;
		for (unsigned int i = 0; i < this->shapes[s].height; ++i) {
			for (unsigned int j = 0; j < this->shapes[s].width; ++j) {
				if (tmpShape[i][j] == 1) {
					this->shapes[s].points[numPoints++] = this->boardY * i + j;
				}
			}
		}

		this->shapes[s].x = this->boardX - this->shapes[s].height + 1;
		this->shapes[s].y = this->boardY - this->shapes[s].width + 1;
		this->shapes[s].total = this->shapes[s].x * this->shapes[s].y;
		this->shapes[s].equal = 0;


	}

	iFile.close();

	this->numFlips /= this->Modulo;
	std::cerr << "Number of flips: " << this->numFlips << std::endl;

	// Sort from biggest to smallest
	std::sort(this->shapes, this->shapes + this->numShapes, shapeComperatorBackward);

	// Check for equal shapes
	for (int s = this->numShapes - 1; s >= 0; --s) {
		if (s > 0 && this->shapes[s].numPoints == this->shapes[s-1].numPoints &&
			!std::memcmp(this->shapes[s].points, this->shapes[s-1].points, sizeof(this->shapes[s].points[0]) * this->shapes[s].numPoints)) {
			this->shapes[s].equal = &this->shapes[s-1];
		}
	}

	while (this->shapes[0].total % this->numOfThreads) {
		--this->numOfThreads;
	}
	std::cerr << "Number of threads: " << this->numOfThreads << std::endl;
	
	//this->numOfThreads = this->shapes[0].total;
	
	// Duplicate board for multi-threading
	for (unsigned int t = 1; t < this->numOfThreads; ++t) {
		this->board[t] = new int [this->numCells];
		std::memcpy(this->board[t], this->board[0], sizeof(*this->board[0]) * this->numCells);
	}
}

ShapeShifter::~ShapeShifter() {
	for (int s = 0; s < this->numShapes; ++s) {
		for (unsigned int t = 0; t < this->numOfThreads; ++t) {
			delete[] this->shapes[s].positions[t];
		}
		delete[] this->shapes[s].positions;
		delete[] this->shapes[s].position;
		delete[] this->shapes[s].maxFlipsAllowed;
	}
	delete[] this->shapes;

	for (unsigned int t = 0; t < this->numOfThreads; ++t) {
		delete[] this->board[t];
	}
	delete[] this->board;

	delete[] this->threadStatus;
}

bool ShapeShifter::Solve() {
	int **tmpPositions;

	// Prepare for threads
	for (int s = this->numShapes - 1; s >= 0; --s) {
		this->shapes[s].position = new unsigned int [this->numOfThreads];
		this->shapes[s].maxFlipsAllowed = new int [this->numOfThreads];

		for (unsigned int t = 0; t < this->numOfThreads; ++t) {
			this->shapes[s].position[t] = 0;
			this->shapes[s].maxFlipsAllowed[t] = 0;
		}
	}

	this->threadStatus = new bool [this->numOfThreads];
	for (unsigned int t = 0; t < this->numOfThreads; ++t) {
		this->threadStatus[t] = false;
	}

	// Generate shapes positions
	for (int s = this->numShapes - 1; s >= 0; --s) {
		this->shapes[s].positions = new int ** [this->numOfThreads];

		for (unsigned int t = 0; t < this->numOfThreads; ++t) {
			this->shapes[s].positions[t]  = new int* [this->shapes[s].total * (this->shapes[s].numPoints + 1)];
			tmpPositions = this->shapes[s].positions[t];

			for (unsigned int k = 0; k < this->shapes[s].total; ++k) {
				for (unsigned int p = 0; p < this->shapes[s].numPoints; ++p) {
					*tmpPositions++  = this->board[t]  + (k / this->shapes[s].y) * this->boardY + (k % this->shapes[s].y) + this->shapes[s].points[p];
				}
				*tmpPositions++  = 0;
			}
		}
	}

	this->isSolved = false;
	//std::future<bool> *flags = new std::future<bool> [this->numOfThreads];
	std::thread *flags = new std::thread [this->numOfThreads];
	for (unsigned int t = 0; t < this->numOfThreads; ++t) {
		//auto forward = std::async(std::launch::async, &ShapeShifter::SolveHelper, this, 0);
		//std::async(std::launch::async, &ShapeShifter::SolveHelper, this, t);
		flags[t] = std::thread(&ShapeShifter::SolveHelper, this, t);
		//flags[t] = std::async(&ShapeShifter::SolveHelper, this, t);
		//t1.join();
	}

	for (unsigned int t = 0; t < this->numOfThreads; ++t) {
		//std::cout << flags[t].get();
		flags[t].join();
	}

	std::cerr << "Solved in thread #" << this->threadIdSolver << std::endl;
	//delete flags;

	return false;
}

void ShapeShifter::Print() const {
	std::cout << "Modulo: " << this->Modulo << std::endl;
	std::cout << "Dimensions: " << this->boardX << "x" << this->boardY << std::endl;
	for (unsigned int i = 0; i < this->boardX; ++i) {
		for (unsigned int j = 0; j < this->boardY; ++j) {
			std::cout << this->board[0][this->boardY * i + j] << " ";
		}
		std::cout << std::endl;
	}

	std::cout << "Num of Shapes: " << this->numShapes << std::endl;
	std::cout << "Shapes (sorted by number of squares):" << std::endl;
	for (int s = 0; s < this->numShapes; ++s) {
		this->shapes[s].Print(this->boardY);
	}

	std::cout << "Total number of flips: " << this->numFlips << std::endl;
}

void ShapeShifter::PrintSolution() const {
	std::sort(this->shapes, this->shapes + this->numShapes, shapeComperatorIdx);

	if (!this->isSolved) {
		std::cout << "No solution found" << std::endl;

		return;
	}

	std::cout << std::endl << "Solution found:" << std::endl;
	for (int s = 0; s < this->numShapes; ++s) {
		std::cout << "Shape #" << this->shapes[s].idx << "\t" << this->shapes[s].position[this->threadIdSolver] / this->shapes[s].y << "," 
															  << this->shapes[s].position[this->threadIdSolver] % this->shapes[s].y << std::endl; // FIX THIS
	}
}

#ifndef VERBOSE
std::string ShapeShifter::GetSolutionString()  {
	unsigned int x, y;

	if (this->solution.compare(""))
		return this->solution;

	std::sort(this->shapes, this->shapes + this->numShapes, shapeComperatorIdx);

	for (int s = 0; s < this->numShapes; ++s) {

		x = this->shapes[s].position[this->threadIdSolver] / this->shapes[s].y; // FIX THIS
		y = this->shapes[s].position[this->threadIdSolver] % this->shapes[s].y;
		this->solution += std::to_string(x) + "," + std::to_string(y) + ";";
	}

	return this->solution;
}
#endif

#define PBSTR std::string("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
#define PBAST std::string("******************************************************************************************")
#define PBSPC std::string("                                                                                          ")
#define PBWIDTH 90

#ifndef VERBOSE
void printProgress (unsigned int id, double percentageA, double percentageB, bool stat)
{
    double val = (percentageA * 100);
    int lpad = (int) (percentageA * PBWIDTH);
    int mpad = (int) (percentageB * PBWIDTH) - lpad;
    int rpad = PBWIDTH - mpad - lpad;
    std::setprecision(6);

    std::cerr << "Thread #" << std::setw(3) << std::left << id << std::setw(15) << std::right << val << "% [" << PBSTR.substr(0, lpad) << PBAST.substr(0,mpad) << PBSPC.substr(0, rpad) << "]" << " Status: ";

    if (stat == false)
    	std::cerr << "RUNNING" << std::endl;
    else
    	std::cerr << "FINISHED" << std::endl;
}

void ShapeShifter::Status() const {
	double percentageA, percentageB, weight;

	for (unsigned int t = 0; t < this->numOfThreads; ++t) {
		percentageA = 0;
		weight = 1.0;

		for (int s = 0; s < this->numShapes; ++s) {
			weight /= this->shapes[s].total; // FIX THIS
			percentageA += this->shapes[s].position[t] * weight;
		}

		percentageB = (t + 1.0) / this->numOfThreads;

		printProgress(t, percentageA, percentageB, this->threadStatus[t]);
	}
}
#endif

bool ShapeShifter::SolveHelper(unsigned int threadID) {
	int curShape;
	Shape *shape;
	register int **positions;
	unsigned int position;
	register int flips;

	// Set all flips to first shape
	this->shapes[0].maxFlipsAllowed[threadID] = this->numFlips;

	// Point to first shape
	curShape = 0;
	shape = this->shapes + curShape;
	flips = shape->maxFlipsAllowed[threadID];
	position = threadID * (shape->total / this->numOfThreads);
	positions = shape->positions[threadID] + (position * (shape->numPoints + 1));

	while (!isSolved) {
		while (1) { // Add shapes to board
			do {
#ifdef VERBOSE
				std::cout << "\r" << position + 1 << "/" << shape->total << "    ";
#endif
				 // Check if current shape point can be added
				if ( (**positions == 0) && (--flips < 0)) {
					break;
				}
			} while (*++positions); // Move to the next shape's point, until terminating 0

			if (*positions) { // Couldn't put all shape
				break;
			}
#ifdef VERBOSE
			std::cout << std::endl;
#endif
			positions -= shape->numPoints; // Move to the beginning of the current position

			while (!isSolved) { // Add shape to board
				if (*positions == 0) { // Finished put shape
					break;
				}

				//**positions = (**positions + 1) % this->Modulo;
				++(**positions);
				if (**positions == this->Modulo)
					**positions = 0;
				++positions;
			}

			// Save shape position
			shape->position[threadID] = position;

			// All shapes successfully added 
			if (curShape == this->numShapes - 1) {
				this->isSolved = true;
				this->threadIdSolver = threadID;
				this->threadStatus[threadID] = true;

				return true;
			}

			// Move to next shape
			shape = shapes + (++curShape);

			position = 0;
			if (shape->equal) { // Don't search multiple times for similar shapes
				position = shape->equal->position[threadID];
			}
			positions = shape->positions[threadID] + (position * (shape->numPoints + 1));
			shape->maxFlipsAllowed[threadID] = flips;
		}

		while (!isSolved) { // Coudn't add shape, move to next position
			++position;

			if (curShape == 0 && position == (threadID + 1) * (shape->total / this->numOfThreads)) { // Check if needed
				this->threadStatus[threadID] = true;

				return false;
			}

			if (position < shape->total) { // Just go to next position and try over
				positions = shape->positions[threadID] + (position * (shape->numPoints + 1));
				flips = shape->maxFlipsAllowed[threadID];
				break;
			}

			// No more legal positions, move previous shape
			--curShape;

#ifdef VERBOSE
			std::cout << "\x1b[A";
#endif	
			if (curShape < 0) {
				this->threadStatus[threadID] = true;

				return false;
			}
			
			// Go to relevant shape and update parameters
			shape = this->shapes + curShape;
			position = shape->position[threadID];
			positions = shape->positions[threadID] + (position) * (shape->numPoints + 1);
			flips = shape->maxFlipsAllowed[threadID];

			// Remove shape
			do {
				if (--**positions < 0) {
					**positions = this->Modulo - 1;
				}
			} while (*++positions);
			++positions; // Skip 0 pointer
		}
	}

	this->threadStatus[threadID] = true;

	return false;
}

bool shapeComperatorBackward(const Shape &i, const Shape &j) {
	return (i.numPoints > j.numPoints);
}

bool shapeComperatorIdx(const Shape &i, const Shape &j) {
	return (i.idx < j.idx);
}


/*
extern "C" {
	const char *AAAAA(const char* s)  {
		static std::string cc;
		ShapeShifter solver(s);

		solver.Solve();
		solver.Solution();

		cc = solver.solution;

		return cc.c_str();
	}
}


#include <boost/python.hpp>
using namespace boost::python;

BOOST_PYTHON_MODULE(shapeshifter) {
	class_<ShapeShifter>("ShapeShifter", init<std::string>())
        .def("Solve", &ShapeShifter::Solve)
        .def("Solution", &ShapeShifter::Solution)
        .def("PrintSolution", &ShapeShifter::PrintSolution)
        .def_readwrite("solution", &ShapeShifter::solution)
    ;
}*/