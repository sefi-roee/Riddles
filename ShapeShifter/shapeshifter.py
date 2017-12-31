import time
import sys
import argparse


class shapeshifter:
    '''ShapeShifter game object'''

    def __init__(self, fn):
    	try:
	        with open(fn, 'r') as f:
	            # Read X
	            self.X = int(f.readline())
	            if self.X < 2 or self.X > 9:
	                raise ValueError

	            # Read board
	            self.board_size = f.readline().replace('\n', '').split('x')
	            if len(self.board_size) != 2:
	                raise ValueError

	            self.board_size = list(map(int, self.board_size))
	            self.board = [list(f.readline().replace('\n', '')) for _ in range(self.board_size[0])]
	            self.board = [list(map(int, line)) for line in self.board]

	            # Read number of pieces
	            self.num_of_pieces = int(f.readline())

	            # Read pieces
	            self.pieces = []
	            for p in range(self.num_of_pieces):
	                piece_size = f.readline().replace('\n', '').split('x')
	                if len(piece_size) != 2:
	                    raise ValueError

	                piece = [list(f.readline().replace('\n', '')) for _ in range(int(piece_size[0]))]
	                piece = [list(map(int, line)) for line in piece]
	                # Need to validate piece
	                self.pieces.append(piece)
        except IOError:
	    	print ('unable to parse file {}'.format(fn))
	    	sys.exit()

    def __str__(self):
        s = ''
        s += 'Board ({}x{}):\n'.format(self.board_size[0], self.board_size[1])
        for i in range(self.board_size[0]):
             s += '####' * (self.board_size[1]) + '#' + '\n'
             s += '# ' + ' # '.join(map(str, self.board[i])) + ' #' + '\n'
        s += '####' * (self.board_size[1]) + '#' + '\n'

        s += '\n'
        s += 'Number of pieces: {}\n'.format(self.num_of_pieces)

        for p in range(self.num_of_pieces):
            s += 'Piece #{} ({}x{}):'.format(p, len(self.pieces[p]), len(self.pieces[p][0])) + '\n'
            for i in range(len(self.pieces[p])):
                 s += '####' * (len(self.pieces[p][0])) + '#' + '\n'
                 s += '# ' + ' # '.join([('1' if t == 1 else ' ') for t in self.pieces[p][i]]) + ' #' + '\n'
            s += '####' * (len(self.pieces[p][0])) + '#' + '\n'
            s += '\n'

        return s

    def solve(self):
        pieces = [(len(self.pieces[i]) * len(self.pieces[i][0]), i, self.pieces[i]) for i in range(len(self.pieces))]
        pieces = list(sorted(pieces))
        self.solve_helper(pieces, len(pieces) - 1, [])

    def solve_helper(self, pieces, l, pos):
        if l == -1:
            if sum([self.board[i][j] for i in range(self.board_size[0]) for j in range(self.board_size[1])]) == 0:
                print ('Solution:')
                for p in sorted(pos):
                    print ('Piece #{}, Pos: {},{}'.format(p[0], p[1][0], p[1][1]))
                return True

            return False

        flips_req = sum([((self.X - self.board[i][j]) % self.X) for i in range(self.board_size[0]) for j in range(self.board_size[1])])
        flips_have = 0
        for i in range(l, -1, -1):
            for r in range(len(pieces[i][2])):
                for c in range(len(pieces[i][2][0])):
                    flips_have += pieces[i][2][r][c]
        flips_have = flips_have

        eq = False
        if flips_have < flips_req != 0:
            return False
        elif flips_have == flips_req:
            eq = True
            
        p_i, p = pieces[l][1], pieces[l][2]

        if l > 6:
            print(l)
        for i in range(self.board_size[0] - len(p) + 1):
            for j in range(self.board_size[1] - len(p[0]) + 1):
                if eq == True:
                    br = False
                    for a in range(len(p)):
                        for b in range(len(p[0])):
                            if self.board[i + a][j + b] == 0 and p[a][b] == 1:
                                br = True
                                break
                        if br == True:
                            break
                                
                    if br == True:
                        continue
                            
                for a in range(len(p)):
                    for b in range(len(p[0])):
                        self.board[i + a][j + b] = (self.board[i + a][j + b] + p[a][b]) % self.X

                if self.solve_helper(pieces, l - 1, pos + [(p_i, (i, j))]):
                    return True

                for a in range(len(p)):
                    for b in range(len(p[0])):
                        self.board[i + a][j + b] = (self.board[i + a][j + b] - p[a][b]) % self.X
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automatic solver for shapeshifter game.')
    parser.add_argument('file_name', help='grid file name')

    args = parser.parse_args()

    startTime = time.clock()
    game = shapeshifter(args.file_name)
    print (game)
    game.solve()
    elapsedTime = time.clock() - startTime
    print ("Time spent in (", __name__, ") is: ", elapsedTime, " sec")

