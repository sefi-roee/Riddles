import time
import sys
import argparse


class ShapeShifter:
    '''ShapeShifter game object'''

    def __init__(self, fn, verbose = False):
        self.verbose = verbose
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
	            self.weight = sum([((self.X - self.board[i][j]) % self.X) for i in range(self.board_size[0]) for j in range(self.board_size[1])])

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

    def solve(self, alg):
        if alg == 'bf':
        	return self.solve_bf()
        elif alg == "bf_prune":
            return self.solve_bf_prune()

    def solve_bf(self):
        sol = self.solve_bf_helper(0, [])

        return sol

    def solve_bf_helper(self, l, pos):
        if l == self.num_of_pieces:
            if self.weight == 0:
                print ('Solution:')
                for p in pos:
                    print ('Piece #{}, Pos: {},{}'.format(p[0], p[1][0], p[1][1]))
                return pos

            return False

        p = self.pieces[l]
        
        if self.verbose:
            position_tot = (self.board_size[0] - len(p) + 1) * (self.board_size[1] - len(p[0]) + 1)
            position_cur = 0
            print ''

        for i in range(self.board_size[0] - len(p) + 1):
            for j in range(self.board_size[1] - len(p[0]) + 1):
                if self.verbose:
                    position_cur += 1
                    print '\r{}/{}...'.format(position_cur, position_tot),
                    sys.stdout.flush()

            	delta_weight = 0

                for a in range(len(p)):
                    for b in range(len(p[0])):
                        self.board[i + a][j + b] = (self.board[i + a][j + b] + p[a][b]) % self.X
                        if p[a][b] != 0:
	                        if self.board[i + a][j + b] == 0:
	                        	delta_weight -= (self.X - 1)
	                        else:
	                        	delta_weight += 1

                self.weight += delta_weight
                sol = self.solve_bf_helper(l + 1, pos + [(l, (i, j))])
                if sol:
                    return sol
                self.weight -= delta_weight

                for a in range(len(p)):
                    for b in range(len(p[0])):
                        self.board[i + a][j + b] = (self.board[i + a][j + b] - p[a][b]) % self.X

        if self.verbose:
            sys.stdout.write('\033[F') # Move cursor up on line

    def solve_bf_prune(self):
        self.augmented_pieces = [(i, p, sum(map(sum,p))) for i,p in enumerate(self.pieces)] # Add piece "coverage capacity"
        self.augmented_pieces = list(reversed(sorted(self.augmented_pieces, key=lambda p: len(p[1]) * len(p[1][0])))) # Sorting in order to prune as early as possible

        cover_acc = sum([p[2] for p in self.augmented_pieces])

        self.partial_cover = []
        for p in self.augmented_pieces:
            self.partial_cover.append(cover_acc)
            cover_acc -= p[2]

        sol = self.solve_bf_prune_helper(0, [])

        return sol

    def solve_bf_prune_helper(self, l, pos):
        if l == self.num_of_pieces:
            if self.weight == 0:
                print ('Solution:')
                for p in sorted(pos):
                    print ('Piece #{}, Pos: {},{}'.format(p[0], p[1][0], p[1][1]))
                return pos

            return False

        # Prune if not enough "coverage capacity" left
        if self.partial_cover[l] < self.weight:
            return False

        p_i, p, cover = self.augmented_pieces[l]
        
        if self.verbose:
            position_tot = (self.board_size[0] - len(p) + 1) * (self.board_size[1] - len(p[0]) + 1)
            position_cur = 0
            print ''

        for i in range(self.board_size[0] - len(p) + 1):
            for j in range(self.board_size[1] - len(p[0]) + 1):
                if self.verbose:
                    position_cur += 1
                    print '\r{}/{}...'.format(position_cur, position_tot),
                    sys.stdout.flush()

                delta_weight = 0

                for a in range(len(p)):
                    for b in range(len(p[0])):
                        self.board[i + a][j + b] = (self.board[i + a][j + b] + p[a][b]) % self.X
                        if p[a][b] != 0:
                            if self.board[i + a][j + b] == 0:
                                delta_weight -= (self.X - 1)
                            else:
                                delta_weight += 1

                self.weight += delta_weight
                sol = self.solve_bf_prune_helper(l + 1, pos + [(p_i, (i, j))])
                if sol:
                    return sol
                self.weight -= delta_weight

                for a in range(len(p)):
                    for b in range(len(p[0])):
                        self.board[i + a][j + b] = (self.board[i + a][j + b] - p[a][b]) % self.X

        if self.verbose:
            sys.stdout.write('\033[F') # Move cursor up on line

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automatic solver for shapeshifter game.')
    parser.add_argument('file_name', help='grid file name')
    parser.add_argument('alg', help='algorithm (bf)')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    startTime = time.clock()
    game = ShapeShifter(args.file_name, verbose = args.verbose)
    print game
    game.solve(args.alg)
    elapsedTime = time.clock() - startTime
    print 'Time spent in ({}) is: {} sec'.format(__name__, elapsedTime)

