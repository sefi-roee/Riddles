#include <iostream>
#include <ctime>

#include "shapeshifter_solver.hpp"

int main(int argc, char **argv) {
	int start_s, stop_s;

	if (argc != 2) {
		exit(1);
	}

	start_s=clock();

	ShapeShifter solver(argv[1]);
	solver.Solve();

	stop_s=clock();
	std::cout << "time: " << (stop_s-start_s)/double(CLOCKS_PER_SEC) << std::endl;

	return 0;
}