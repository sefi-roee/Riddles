#include "shapeshifter.hpp"
#include <iostream>
#include <ctime>
#include <iomanip>
#include <chrono>

#ifndef VERBOSE
#include <unistd.h>
#include <csignal>
static void printStatus(int sig);
#endif

int start_s, stop_s;
auto start = std::chrono::high_resolution_clock::now();
ShapeShifter* ss;

int main(int argc, char **argv) {
#ifndef VERBOSE
	signal(SIGUSR1, printStatus);
	std::cerr << "PID: " << getpid() << std::endl;
#endif

	start_s=clock();
	//start = std::chrono::high_resolution_clock::now();

	ShapeShifter solver(argv[1], false, 24);

	ss = &solver;

#ifdef VERBOSE
	solver.Print();
	std::cout << std::endl << "Searching for a solution... " << std::endl << std::endl;
#endif

	solver.Solve();

#ifdef VERBOSE
	solver.PrintSolution();
#endif

#ifndef VERBOSE
	std::cout << (std::chrono::high_resolution_clock::now() - start).count() / 1e9 << std::endl;
	std::cout << solver.GetSolutionString() << std::endl;
#endif

	stop_s=clock();
	//elapsed = std::chrono::high_resolution_clock::now() - start;

#ifdef VERBOSE
	std::cerr << "\rRunning time: " << std::setw(8) << std::left << (std::chrono::high_resolution_clock::now() - start).count() / 1e9 << "s" << std::endl;
	std::cerr << "\rCPU time: " << std::setw(8) << std::left << (clock()-start_s)/double(CLOCKS_PER_SEC) << "s" << std::endl;
#endif

	return 0;
}

#ifndef VERBOSE
void printStatus(int sig) {
	auto elapsed = std::chrono::high_resolution_clock::now() - start;

	std::cerr << "\r**************** STATUS ****************" << std::endl;
	std::cerr << "\rRunning time: " << std::setw(8) << std::left << elapsed.count() / 1e9 << "s" << std::endl;
	std::cerr << "\rCPU time: " << std::setw(8) << std::left << (clock()-start_s)/double(CLOCKS_PER_SEC) << "s" << std::endl;
	ss->Status();
	std::cerr << "\r****************************************" << std::endl;
}
#endif