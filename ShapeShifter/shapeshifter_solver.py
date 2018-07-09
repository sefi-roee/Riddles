import time
import sys
import argparse
from copy import deepcopy


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
		elif alg == 'bi':
			return self.solve_bi_directional()
		elif alg == 'bc':
			return self.solve_board_coverage()
		elif alg == 'bf_i':
			return self.solve_bf_informed_prune()

	def solve_bf(self):
		self.pos = [0 for i in range(self.num_of_pieces)]

		sol = self.solve_bf_helper(0)

		return sol

	def solve_bf_helper(self, l):
		if l == self.num_of_pieces:
			if self.weight == 0:
				print 'Solution:'
				for i, p in enumerate(self.pos):
					print 'Piece #{}, Pos: {},{}'.format(i, p[0], p[1])
				return self.pos

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

				self.pos[l] = (i, j)
				self.weight += delta_weight
				sol = self.solve_bf_helper(l + 1)
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

		self.pos = [0 for i in range(self.num_of_pieces)]

		sol = self.solve_bf_prune_helper(0)

		return sol

	def solve_bf_prune_helper(self, l):
		if l == self.num_of_pieces:
			if self.weight == 0:
				#pos = sorted(pos, key=lambda p: p[0])
				print 'Solution:'
				for i, p in enumerate(self.pos):
					print 'Piece #{}, Pos: {},{}'.format(i, p[0], p[1])
				return self.pos

			return False

		# Prune if not enough "coverage capacity" left
		if self.partial_cover[l] < self.weight:
			return False

		p_i, p, p_cover = self.augmented_pieces[l]
		
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
							if self.board[i + a][j + b] == 1:
								delta_weight += (self.X - 1)
							else:
								delta_weight -= 1

				self.pos[p_i] = (i, j)
				self.weight += delta_weight
				sol = self.solve_bf_prune_helper(l + 1)
				if sol:
					return sol
				self.weight -= delta_weight

				for a in range(len(p)):
					for b in range(len(p[0])):
						self.board[i + a][j + b] = (self.board[i + a][j + b] - p[a][b]) % self.X

		if self.verbose:
			sys.stdout.write('\033[F') # Move cursor up on line

	def solve_bi_directional(self):
		#self.augmented_pieces = [(i, p, sum(map(sum,p))) for i,p in enumerate(self.pieces)] # Add piece "coverage capacity"
		#self.augmented_pieces = list(sorted(self.augmented_pieces, key=lambda p: len(p[1]) * len(p[1][0]))) # Sorting in order to prune as early as possible

		self.augmented_pieces = [[i, p, sum(map(sum,p)), -1, -1] for i,p in enumerate(self.pieces)] # Add piece "coverage capacity"
		self.augmented_pieces = list(sorted(self.augmented_pieces, key=lambda p: len(p[1]) * len(p[1][0]))) # Sorting in order to prune as early as possible
		#self.augmented_pieces = [[i, p, sum(map(sum,p))] for i,p in enumerate(self.pieces)] # Add piece "coverage capacity"
		#self.augmented_pieces = list(reversed(sorted(self.augmented_pieces, key=lambda p: len(p[1]) * len(p[1][0])))) # Sorting in order to prune as early as possible

		mult_a = 1
		mult_b = 1
		self.half = 0

		for i in range(self.num_of_pieces):
			if mult_a <= mult_b * 1000:
				self.augmented_pieces[i][3] = 0
				mult_a *= (self.board_size[0] - len(self.augmented_pieces[i][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[i][1][0]) + 1)
				self.augmented_pieces[i][4] = (self.board_size[0] - len(self.augmented_pieces[i][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[i][1][0]) + 1)				
				self.half += 1
			else:
				self.augmented_pieces[i][3] = 1
				mult_b *= (self.board_size[0] - len(self.augmented_pieces[i][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[i][1][0]) + 1)
				self.augmented_pieces[i][4] = (self.board_size[0] - len(self.augmented_pieces[i][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[i][1][0]) + 1)

		for i in range(self.num_of_pieces):
			print self.augmented_pieces[i]
		
		self.augmented_pieces = list(sorted(self.augmented_pieces, key=lambda p: p[3]))
		self.augmented_pieces = [(p[0], p[1], p[2]) for p in self.augmented_pieces]

		#self.half = (self.num_of_pieces + 1) // 2
		'''begin = 0
		end = self.num_of_pieces - 1
		begin_size = 1
		end_size = 1

		while begin < end:
			if begin_size > end_size:
				end_size *= (self.board_size[0] - len(self.augmented_pieces[end][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[end][1][0]) + 1)
				end -= 1
			else:
				begin_size *= (self.board_size[0] - len(self.augmented_pieces[begin][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[begin][1][0]) + 1)
				begin += 1'''

		'''tmp = 1
		self.half = self.num_of_pieces - 1
		while tmp < 30000 and self.half > 0:
			tmp *= (self.board_size[0] - len(self.augmented_pieces[self.half][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[self.half][1][0]) + 1)
			self.half -= 1'''

		#self.half = self.num_of_pieces # This makes it just simple brute-force with pruning

		cover_acc = sum([p[2] for p in self.augmented_pieces[:self.half]])

		self.partial_cover = []
		for p in self.augmented_pieces[:self.half]:
			self.partial_cover.append(cover_acc)
			cover_acc -= p[2]

		self.middle_board = [[0 for _ in range(self.board_size[1])] for _ in range(self.board_size[0])]
		self.middle_boards = {}
		self.middle_weights = {}
		self.middle_weight = 0

		print 'Searching backward...'
		self.middle_pos = [0 for _ in range(self.half, self.num_of_pieces)]
		self.solve_bi_directional_backward_helper(self.half)
		print 'Searching backward... Done'

		self.max_middle_weight = max(self.middle_weights)

		print 'Searching forward...'
		self.pos = [0 for _ in range(self.half)]
		sol = self.solve_bi_directional_forward_helper(0)
		print 'Searching forward... Done'

		return sol

	def solve_bi_directional_backward_helper(self, l):
		if l == self.num_of_pieces:
			self.middle_boards[hash(str(self.middle_board))] = self.middle_pos[:]
			self.middle_weights[self.middle_weight] = True

			return

		p_i, p, p_cover = self.augmented_pieces[l]
		
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
						if p[a][b] != 0:
							if self.board[i + a][j + b] == 1:
								delta_weight += (self.X - 1)
							else:
								delta_weight -= 1
						self.middle_board[i + a][j + b] = (self.middle_board[i + a][j + b] - p[a][b]) % self.X

				self.middle_pos[l - self.half] = (i, j)
				self.middle_weight += delta_weight
				self.solve_bi_directional_backward_helper(l + 1)
				self.middle_weight -= delta_weight

				for a in range(len(p)):
					for b in range(len(p[0])):
						self.middle_board[i + a][j + b] = (self.middle_board[i + a][j + b] + p[a][b]) % self.X

		if self.verbose:
			sys.stdout.write('\033[F') # Move cursor up on line

	def solve_bi_directional_forward_helper(self, l):
		if l == self.half:
			if hash(str(self.board)) in self.middle_boards:
				pos = self.pos + self.middle_boards[hash(str(self.board))]
				pos = [(self.augmented_pieces[i][0], p) for i, p in enumerate(pos)]
				pos = map(lambda p: p[1], sorted(pos, key=lambda p: p[0]))
				
				print 'Solution:'
				for i, p in enumerate(pos):
					print 'Piece #{}, Pos: {},{}'.format(i, p[0], p[1])
				return pos

			return False

		# Prune if not enough "coverage capacity" left
		if self.weight - self.partial_cover[l] > self.max_middle_weight:
			return False

		p_i, p, p_cover = self.augmented_pieces[l]

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
							if self.board[i + a][j + b] == 1:
								delta_weight += (self.X - 1)
							else:
								delta_weight -= 1

				self.pos[l] = (i, j)
				self.weight += delta_weight
				sol = self.solve_bi_directional_forward_helper(l + 1)
				if sol:
					return sol
				self.weight -= delta_weight

				for a in range(len(p)):
					for b in range(len(p[0])):
						self.board[i + a][j + b] = (self.board[i + a][j + b] - p[a][b]) % self.X

		if self.verbose:
			sys.stdout.write('\033[F') # Move cursor up on line

	def solve_bi_directional_without_cache(self):
		self.augmented_pieces = [[i, p, sum(map(sum,p)), -1, -1] for i,p in enumerate(self.pieces)] # Add piece "coverage capacity"
		self.augmented_pieces = list(sorted(self.augmented_pieces, key=lambda p: len(p[1]) * len(p[1][0]))) # Sorting in order to prune as early as possible
		
		mult_a = 1
		mult_b = 1
		self.half = 0

		for i in range(self.num_of_pieces):
			if mult_a <= mult_b * 1000:
				self.augmented_pieces[i][3] = 0
				mult_a *= (self.board_size[0] - len(self.augmented_pieces[i][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[i][1][0]) + 1)
				self.augmented_pieces[i][4] = (self.board_size[0] - len(self.augmented_pieces[i][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[i][1][0]) + 1)				
				self.half += 1
			else:
				self.augmented_pieces[i][3] = 1
				mult_b *= (self.board_size[0] - len(self.augmented_pieces[i][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[i][1][0]) + 1)
				self.augmented_pieces[i][4] = (self.board_size[0] - len(self.augmented_pieces[i][1]) + 1) * (self.board_size[1] - len(self.augmented_pieces[i][1][0]) + 1)

		for i in range(self.num_of_pieces):
			print self.augmented_pieces[i]
		
		self.augmented_pieces = list(sorted(self.augmented_pieces, key=lambda p: p[3]))
		self.augmented_pieces = [(p[0], p[1], p[2]) for p in self.augmented_pieces]

		cover_acc = sum([p[2] for p in self.augmented_pieces[:self.half]])

		self.partial_cover = []
		for p in self.augmented_pieces[:self.half]:
			self.partial_cover.append(cover_acc)
			cover_acc -= p[2]

		self.middle_board = [[0 for _ in range(self.board_size[1])] for _ in range(self.board_size[0])]
		self.middle_boards = {}
		#self.middle_weights = {}
		#self.middle_weight = 0

		print 'Searching backward...'
		self.middle_pos = [0 for _ in range(self.half, self.num_of_pieces)]
		self.solve_bi_directional_without_cache_backward_helper(self.half)
		print 'Searching backward... Done'

		self.max_middle_weight = max(self.middle_weights)

		print 'Searching forward...'
		self.pos = [0 for _ in range(self.half)]
		sol = self.solve_bi_directional_without_cache_forward_helper(0)
		print 'Searching forward... Done'

		return sol

	def solve_bi_directional_without_cache_backward_helper(self, l):
		if l == self.num_of_pieces:
			self.middle_boards[hash(str(self.middle_board))] = True
			self.middle_weights[self.middle_weight] = True

			return

		p_i, p, p_cover = self.augmented_pieces[l]
		
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
						if p[a][b] != 0:
							if self.board[i + a][j + b] == 1:
								delta_weight += (self.X - 1)
							else:
								delta_weight -= 1
						self.middle_board[i + a][j + b] = (self.middle_board[i + a][j + b] - p[a][b]) % self.X

				self.middle_pos[l - self.half] = (i, j)
				self.middle_weight += delta_weight
				self.solve_bi_directional_without_cache_backward_helper(l + 1)
				self.middle_weight -= delta_weight

				for a in range(len(p)):
					for b in range(len(p[0])):
						self.middle_board[i + a][j + b] = (self.middle_board[i + a][j + b] + p[a][b]) % self.X

		if self.verbose:
			sys.stdout.write('\033[F') # Move cursor up on line

	def solve_bi_directional_without_cache_forward_helper(self, l):
		if l == self.half:
			if hash(str(self.board)) in self.middle_boards:
				return True

			return False

		# Prune if not enough "coverage capacity" left
		if self.weight - self.partial_cover[l] > self.max_middle_weight:
			return False

		p_i, p, p_cover = self.augmented_pieces[l]

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
							if self.board[i + a][j + b] == 1:
								delta_weight += (self.X - 1)
							else:
								delta_weight -= 1

				self.pos[l] = (i, j)
				self.weight += delta_weight
				sol = self.solve_bi_directional_without_cache_forward_helper(l + 1)
				if sol:
					return sol
				self.weight -= delta_weight

				for a in range(len(p)):
					for b in range(len(p[0])):
						self.board[i + a][j + b] = (self.board[i + a][j + b] - p[a][b]) % self.X

		if self.verbose:
			sys.stdout.write('\033[F') # Move cursor up on line

	def solve_board_coverage(self):
		self.super_pieces = [None for _ in range(2 ** self.num_of_pieces)]
		self.super_piece = [[0 for _ in range(self.board_size[1])] for _ in range(self.board_size[0])]
		self.cur_super_piece = 0

		print 'Generating super pieces...',
		self.solve_board_coverage_generate_super_pieces(0, set(), 0, 0)
		self.super_pieces = list(reversed(sorted(self.super_pieces, key = lambda sp: len(sp[0]))))
		print 'Done'

		self.coverage_capacity = [sum(map(sum,p)) for p in self.pieces]
		self.sol = [set() for _ in range(self.board_size[0] * self.board_size[1])]
		return self.solve_board_coverage_helper(0, set(range(self.num_of_pieces)), sum(self.coverage_capacity))

	def solve_board_coverage_generate_super_pieces(self, l, indices, max_height, max_width):
		if l == self.num_of_pieces:
			self.super_pieces[self.cur_super_piece] = (indices, max_height, max_width, [self.super_piece[i][:max_width] for i in range(max_height)])
			self.cur_super_piece += 1

			return

		p = self.pieces[l]

		for a in range(len(p)):
			for b in range(len(p[0])):
				self.super_piece[a][b] = (self.super_piece[a][b] + p[a][b]) % self.X

		self.solve_board_coverage_generate_super_pieces(l + 1, indices.union([l]), max(max_height, len(p)), max(max_width, len(p[0])))

		for a in range(len(p)):
			for b in range(len(p[0])):
				self.super_piece[a][b] = (self.super_piece[a][b] - p[a][b]) % self.X

		self.solve_board_coverage_generate_super_pieces(l + 1, indices, max_height, max_width)

	def solve_board_coverage_helper(self, l, candidates, coverage_capacity):
		if self.weight > coverage_capacity:
			return False

		if l == self.board_size[0] * self.board_size[1]:
			return False

		#print '\t'*l + 'l: {}, candidates: {}, weight: {}'.format(l, candidates, self.weight)
		if candidates == set():
			#print '\t'*l + '                      AAA'
			#print self.board
			if self.weight == 0:
				print 'Solution:'
				#print self.sol
				pos = [0 for _ in range(self.num_of_pieces)]
				for i, pieces in enumerate(self.sol):
					for p in pieces:
						print 'Piece #{}, Pos: {},{}'.format(p, i // self.board_size[1], i % self.board_size[1])
						pos[p] = (i // self.board_size[1], i % self.board_size[1])

				return pos

			return False

		i = l // self.board_size[1]
		j = l % self.board_size[1]

		if self.verbose:
			position_cur = 0
			print ''

		sp = [sp for sp in self.super_pieces if i + sp[1] <= self.board_size[0] and j + sp[2] <= self.board_size[1] and sp[0].issubset(candidates)]

		for p_indices, p_height, p_width, p in sp:
			if self.verbose:
				position_cur += 1
				print '\r{}/{}...'.format(position_cur, len(sp)),
				sys.stdout.flush()

			'''if i + p_height > self.board_size[0] or \
			   j + p_width > self.board_size[1]:
			   continue

			if not p_indices.issubset(candidates):
				continue'''

			if p == []:
				tmp = 0
			else:
				tmp = p[0][0]

			if (self.board[i][j] + tmp) % self.X != 0: # Prune if cell isn't solved
				continue

			start_weight = 0
			end_weight = 0
			for a in range(p_height):
				for b in range(p_width):
					start_weight += (self.X - self.board[i + a][j + b]) % self.X
					self.board[i + a][j + b] = (self.board[i + a][j + b] + p[a][b]) % self.X
					end_weight += (self.X - self.board[i + a][j + b]) % self.X
					
			delta_weight = end_weight - start_weight
			#print '\t'*l + 'put: {} on {}, new weight: {}'.format(p_indices, l, self.weight + delta_weight)
			#print '\t'*l + str(self.board)
			self.weight += delta_weight
			self.sol[l] = p_indices
			sol = self.solve_board_coverage_helper(l + 1, candidates.difference(p_indices), coverage_capacity - sum([self.coverage_capacity[p_i] for p_i in p_indices]))
			if sol:
				return sol
			self.weight -= delta_weight

			
			#print '\t'*l + 'remove: {} from {}, new weight: {}'.format(p_indices, l, self.weight)
			for a in range(p_height):
				for b in range(p_width):
					self.board[i + a][j + b] = (self.board[i + a][j + b] - p[a][b]) % self.X
			#print '\t'*l + str(self.board)

		if self.verbose:
			sys.stdout.write('\033[F') # Move cursor up on line

	def solve_bf_informed_prune(self):
		self.augmented_pieces = [(i, p, sum(map(sum,p))) for i,p in enumerate(self.pieces)] # Add piece "coverage capacity"
		self.augmented_pieces = list(reversed(sorted(self.augmented_pieces, key=lambda p: len(p[1]) * len(p[1][0])))) # Sorting in order to prune as early as possible

		cover_acc = sum([p[2] for p in self.augmented_pieces])

		self.partial_cover = []
		for p in self.augmented_pieces:
			self.partial_cover.append(cover_acc)
			cover_acc -= p[2]

		self.pos = [0 for i in range(self.num_of_pieces)]

		sol = self.solve_bf_informed_prune_helper(0)

		return sol

	def solve_bf_informed_prune_helper(self, l):
		if l == self.num_of_pieces:
			if self.weight == 0:
				#pos = sorted(pos, key=lambda p: p[0])
				print 'Solution:'
				for i, p in enumerate(self.pos):
					print 'Piece #{}, Pos: {},{}'.format(i, p[0], p[1])
				return self.pos

			return False

		# Prune if not enough "coverage capacity" left
		if self.partial_cover[l] < self.weight:
			return False

		p_i, p, p_cover = self.augmented_pieces[l]
		
		if self.verbose:
			position_tot = (self.board_size[0] - len(p) + 1) * (self.board_size[1] - len(p[0]) + 1)
			position_cur = 0
			print ''

		# Prioritize positions according to wegiht lose
		positions = [None for _ in range((self.board_size[0] - len(p) + 1) * (self.board_size[1] - len(p[0]) + 1))]
		positions_i = 0
		for i in range(self.board_size[0] - len(p) + 1):
			for j in range(self.board_size[1] - len(p[0]) + 1):
				delta_weight = 0

				for a in range(len(p)):
					for b in range(len(p[0])):
						tmp = (self.board[i + a][j + b] + p[a][b]) % self.X
						if p[a][b] != 0:
							if tmp == 1:
								delta_weight += (self.X - 1)
							else:
								delta_weight -= 1

				positions[positions_i] = (delta_weight, i, j)
				positions_i += 1
		positions = sorted(positions, key=lambda p: p[0])

		for delta_weight, i, j in positions:
			if self.verbose:
				position_cur += 1
				print '\r{}/{}...'.format(position_cur, position_tot),
				sys.stdout.flush()

			for a in range(len(p)):
				for b in range(len(p[0])):
					self.board[i + a][j + b] = (self.board[i + a][j + b] + p[a][b]) % self.X

			self.pos[p_i] = (i, j)
			self.weight += delta_weight
			sol = self.solve_bf_prune_helper(l + 1)
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
	parser.add_argument('alg', help='algorithm (bf/bf_prune/bi/bc/bf_i)')
	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

	args = parser.parse_args()

	startTime = time.clock()
	game = ShapeShifter(args.file_name, verbose = args.verbose)
	print game
	game.solve(args.alg)
	elapsedTime = time.clock() - startTime
	print 'Time spent in ({}) is: {} sec'.format(__name__, elapsedTime)

