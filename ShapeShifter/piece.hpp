#pragma once

class Piece {
public:
	Piece(unsigned int height, unsigned int width);
	~Piece();

	unsigned int height, width;
	unsigned char **p;
};