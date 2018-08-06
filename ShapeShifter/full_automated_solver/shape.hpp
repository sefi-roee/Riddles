#pragma once


struct Shape {
	void Print(unsigned int boardWidth) const;

	unsigned int idx;
	unsigned int numPoints;
	unsigned int *points;
	unsigned int height, width;
	unsigned int x, y;
	unsigned int total;
	int ***positions;
	unsigned int *position;
	int *maxFlipsAllowed;

	Shape *equal;
};