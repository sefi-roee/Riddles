#pragma once

class Piece {
public:
	Piece(unsigned  height, unsigned int width);
	~Piece();

	unsigned int height, width;
	unsigned int **p;
};