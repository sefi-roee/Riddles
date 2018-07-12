#include "piece.hpp"

Piece::Piece(unsigned int height, unsigned int width) {
	this->height = height;
	this->width = width;

	this->p = new unsigned char* [height];
	for (unsigned int i = 0; i < this->height; ++i)
		this->p[i] = new unsigned char [width];
}

Piece::~Piece() {
	for (int unsigned i = 0; i < this->height; ++i)
		delete this->p[i];

	delete this->p;
}

