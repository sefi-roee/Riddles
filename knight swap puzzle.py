from __future__ import print_function
import time

class state:
   SOL = []
   SOL_MOVES = []
   SOL_LEN = 99999
   
   HISTORY = {}
   MOVES = [((0,0),(1,2)), ((0,0),(2,1)),
         ((1,0),(2,2)), ((1,0),(3,1)),
         ((1,1),(3,0)),
         ((1,2),(0,0)), ((1,2),(2,0)), ((1,2),(3,1)),
         ((1,3),(2,1)),
         ((2,0),(1,2)),
         ((2,1),(0,0)), ((2,1),(1,3)),
         ((2,2),(1,0)), ((2,2),(3,0)),
         ((3,0),(1,1)), ((3,0),(2,2)),
         ((3,1),(1,0)), ((3,1),(1,2)) ]

   def __init__(self, b1, b2, w1, w2, history, movesHistory, count):
      self.__board = [[0 for x in range(4)] for x in range(4)]
      self.__board[b1[0]][b1[1]] = 'B'
      self.__board[b2[0]][b2[1]] = 'B'
      self.__board[w1[0]][w1[1]] = 'W'
      self.__board[w2[0]][w2[1]] = 'W'

      for i in range(1, 4):
         self.__board[0][i] = 'X'
      self.__board[2][3] = 'X'
      for i in range(3, 4):
         self.__board[3][i] = 'X'

      self.__history = history
      self.__movesHistory = movesHistory
      self.__count = count

   def setState(self, s, count):
      self.__board = [[0 for x in range(4)] for x in range(4)]
      for k in s:
         row = k[1]
         col = row[1]
         row = row[0]
         self.__board[row][col] = k[0]
         
      self.__count = count
      
   def getKnights(self):
      p = []

      for i in range(4):
         for j in range(4):
            if self.__board[i][j] == 'B':
               p += [('B',(i,j))]
            elif self.__board[i][j] == 'W':
               p += [('W',(i,j))]

      return p

   def getBlackKnights(self):
      return [k[1] for k in self.getKnights() if k[0] == 'B']

   def getWhiteKnights(self):
      return [k[1] for k in self.getKnights() if k[0] == 'W']
      
   def getAvilableMoves(self):
      knights = self.getKnights()
      moves = []
      
      for k in knights:
         pos = k[1]
         moves += [m for m in state.MOVES if (m[0] == pos and self.__board[m[1][0]][m[1][1]] == 0)]

      return moves

   def solve(self):
      self.__history.extend([tuple(self.getKnights())])
      state.HISTORY[tuple(self.getKnights())] = self.__count

      if self.isSolved() == True:
         if self.__count < state.SOL_LEN:
               state.SOL_LEN = self.__count
               state.SOL = self.__history
               state.SOL_MOVES = self.__movesHistory
         return True

      b = self.getBlackKnights()
      w = self.getWhiteKnights()

      
      flag = False
      
      for move in self.getAvilableMoves():
         last = move[0]
         new  = move[1]
         
         nextMove = state(b[0], b[1], w[0], w[1], self.__history[:], self.__movesHistory[:], self.__count + 1)
         nextMove.__movesHistory.extend([move])
         tmp = nextMove.__board[last[0]][last[1]]
         nextMove.__board[last[0]][last[1]] = nextMove.__board[new[0]][new[1]]
         nextMove.__board[new[0]][new[1]] = tmp

         if tuple(nextMove.getKnights()) in state.HISTORY:
            if state.HISTORY[tuple(nextMove.getKnights())] <= (self.__count + 1):
               continue
         
         if nextMove.solve() == True:
            flag = True

      return flag
         

   def printBoard(self):
      print('   |---1---|---2---|---3---|---4---|')
      print('   |-------|')
      print('   |       |')
      print(' A |  ', self.__board[0][0],'  |')
      print('   |       |')
      print('   |-------|-------|-------|-------|')
      print('   |       |       |       |       |')
      print(' B |  ', self.__board[1][0],'  |',' ', self.__board[1][1],'  |',' ', self.__board[1][2],'  |',' ', self.__board[1][3],'  |')
      print('   |       |       |       |       |')
      print('   |-------|-------|-------|-------|')
      print('   |       |       |       |')
      print(' C |  ', self.__board[2][0],'  |',' ', self.__board[2][1],'  |',' ', self.__board[2][2],'  |')
      print('   |       |       |       |')
      print('   |-------|-------|-------|')
      print('   |       |       |')
      print(' D |  ', self.__board[3][0],'  |',' ', self.__board[3][1],'  |')
      print('   |       |       |')
      print('   |-------|-------|')
      print('Moves: ', self.__count)
      print()
      
   def isSolved(self):
      return ( self.__board[0][0] == 'W' and
               self.__board[2][0] == 'W' and
               self.__board[2][1] == 'B' and
               self.__board[1][3] == 'B' )
   
   __board = 0
   __history = 0
   __movesHistory = 0
   __count = 0
   
class game:
   def __init__(self):
      self.s = state((0,0),(2,0),(2,1),(1,3), [], [], 0)

   def solve(self):
      return self.s.solve()
         
   s = 0

def posToStr(p):
   s = ''
   
   s += chr(p[0] + ord('A'))
   s += chr(p[1] + ord('1'))

   return s

def main():
   g = game()
   g.solve()
   s = state((0,0),(2,0),(2,1),(1,3), [], [], 0)
   
   for i in range(state.SOL_LEN + 1):
      s.setState(state.SOL[i], i)
      s.printBoard()
      
   print('Total moves: ', state.SOL_LEN)   

   print('Moves: ')
   lastPos = 0
   s = ""
   for move in state.SOL_MOVES:
      if move[0] == lastPos:
         s += '->' + posToStr(move[1])
      else:
         print(s)
         s = posToStr(move[0]) + '->' + posToStr(move[1])
         
      lastPos = move[1]
   print(s)
   
startTime = time.clock()
main()
elapsedTime = time.clock() - startTime
print ("Time spent in (", __name__, ") is: ", elapsedTime, " sec")
