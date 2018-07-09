shapeshifter_solver: shapeshifter_solver.o piece.o shapeshifter_main.cpp
	g++ -Wall -Werror -pedantic -o shapeshifter_solver shapeshifter_solver.o piece.o shapeshifter_main.cpp

shapeshifter_solver.o: shapeshifter_solver.hpp shapeshifter_solver.cpp
	g++ -c -Wall -Werror -pedantic -I/. shapeshifter_solver.cpp

piece.o: piece.hpp piece.cpp
	g++ -c -Wall -Werror -pedantic -I/. piece.cpp