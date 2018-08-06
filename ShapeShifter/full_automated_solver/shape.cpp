#include "shape.hpp"
#include <iostream>


void Shape::Print(unsigned int boardWidth) const {
	std::cout << "\tIndex: " << this->idx << std::endl;
	if (this->equal)
		std::cout << "\tEqual: " << this->equal->idx << std::endl;
	std::cout << "\tPoints (" << this->numPoints << "): ";
	for (unsigned int i = 0; i < this->numPoints; ++i)
		std::cout << this->points[i] << " ";
	std::cout << std::endl;
	std::cout << "\tDim: " << this->height << "," << this->width << std::endl;

	unsigned int p = 0;
	for (unsigned int i = 0; i < this->height; ++i) {
		std::cout << "\t\t\t";
		for (unsigned int j = 0; j < this->width; ++j) {
			if (p > this->numPoints || i * boardWidth + j < this->points[p]) {
				std::cout << " ";
			}
			else {
				std::cout << "*";
				++p;
			}
		}
		std::cout << std::endl;
	}
}