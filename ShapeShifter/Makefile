CXX=g++ -DVERBOSE
CXXFLAGS=-std=c++11 -Wall -Werror -pedantic

shapeshifter_solver: shapeshifter_solver.o piece.o shapeshifter_main.cpp
	$(CXX) $(CXXFLAGS) -o shapeshifter_solver shapeshifter_solver.o piece.o shapeshifter_main.cpp

shapeshifter_solver.o: shapeshifter_solver.hpp shapeshifter_solver.cpp
	$(CXX) $(CXXFLAGS) -c -I/. shapeshifter_solver.cpp

piece.o: piece.hpp piece.cpp
	$(CXX) $(CXXFLAGS) -c -I/. piece.cpp

clean:
	\rm -f shapeshifter_solver.o piece.o shapeshifter_solver