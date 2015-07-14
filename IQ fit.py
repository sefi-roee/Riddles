import time
import io
import sys

class piece:
      def __init__(self, l, w, p, c):
            self.__length = l
            self.__width = w
            self.__color = c
            self.__p = p

      def Print(self):
            for i in range(self.__length):
                  print ("".join([str(p).ljust(3) for p in self.__p[i]]))
            print ()

      def Length(self):
            return self.__length

      def Width(self):
            return self.__width

      def P(self):
            return self.__p
      
      __length = 0
      __width = 0
      __color = ""
      __p = []

class game:
      def __init__(self):
            pass

      def Print(self):
            print ("**** SMARTGAMES IQ PUZZLER ****")
            for i in range(5):
                  print ("".join([str(p).ljust(3) for p in self.__board[i]]))
            print ()
            print ("Pieces:")

            self.PrintPieces()

      def AddPiece(self, p):
            self.__pieces += [p]
            self.__p = [0 for i in range(len(self.__pieces))]

      def PrintPieces(self):
            for i in range(len(self.__pieces)):
                  if (self.__p[i] == 0):
                        self.__pieces[i].Print()

      def putPiece(self, index, r, c, direction):
            p = self.__pieces[index]
            l = p.Length()
            w = p.Width()

            if (direction == 1): # normal
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[i][j] != 0 and self.__board[r + i][c + j] != 0):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + i][c + j] += p.P()[i][j]
                              
            elif (direction == 2): # inverted horizontal
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[l - 1 - i][j] != 0 and self.__board[r + i][c + j] != 0):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + i][c + j] += p.P()[l - 1 - i][j]
                              
            elif (direction == 3): # inverted vertical
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[i][w - 1 - j] != 0 and self.__board[r + i][c + j] != 0):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + i][c + j] += p.P()[i][w - 1 - j]
                              
            elif (direction == 4): # inverted both
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[l - 1 - i][w - 1 - j] != 0 and self.__board[r + i][c + j] != 0):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + i][c + j] += p.P()[l - 1 - i][w - 1 - j]

            elif (direction == 5): # flipped
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[i][j] != 0 and self.__board[r + j][c + i] != 0):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + j][c + i] += p.P()[i][j]

            elif (direction == 6): # flipped inverted horizontal
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[l - 1 - i][j] != 0 and self.__board[r + j][c + i] != 0):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + j][c + i] += p.P()[l - 1 - i][j]
                              
            elif (direction == 7): # flipped inverted vertical
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[i][w - 1 - j] != 0 and self.__board[r + j][c + i] != 0):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + j][c + i] += p.P()[i][w - 1 - j]
                              
            elif (direction == 8): # flipped inverted both
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[l - 1 - i][w - 1 - j] != 0 and self.__board[r + j][c + i] != 0):
                                    return False
                              
                  for i in range(l):
                        for j in range(w):
                              self.__board[r + j][c + i] += p.P()[l - 1 - i][w - 1 - j]

            else:
                  return False
                                    
            self.__p[index] = (r, c, direction)
            return True
            
      def removePiece(self, index):
            p = self.__pieces[index]
            r, c, direction = self.__p[index]
            l = p.Length()
            w = p.Width()

            if (direction == 1): # normal
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[i][j] != 0 and self.__board[r + i][c + j] != p.P()[i][j]):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + i][c + j] -= p.P()[i][j]
                              
            elif (direction == 2): # inverted horizontal
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[l - 1 - i][j] != 0 and self.__board[r + i][c + j] != p.P()[l - 1 - i][j]):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + i][c + j] -= p.P()[l - 1 - i][j]
                              
            elif (direction == 3): # inverted vertical
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[i][w - 1 - j] != 0 and self.__board[r + i][c + j] != p.P()[i][w - 1 - j]):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + i][c + j] -= p.P()[i][w - 1 - j]
                              
            elif (direction == 4): # inverted both
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[l - 1 - i][w - 1 - j] != 0 and self.__board[r + i][c + j] != p.P()[l - 1 - i][w - 1 - j]):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + i][c + j] -= p.P()[l - 1 - i][w - 1 - j]

            elif (direction == 5): # flipped normal
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[i][j] != 0 and self.__board[r + j][c + i] != p.P()[i][j]):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + j][c + i] -= p.P()[i][j]
                              
            elif (direction == 6): # flipped inverted horizontal
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[l - 1 - i][j] != 0 and self.__board[r + j][c + i] != p.P()[l - 1 - i][j]):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + j][c + i] -= p.P()[l - 1 - i][j]
                              
            elif (direction == 7): # flipped inverted vertical
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[i][w - 1 - j] != 0 and self.__board[r + j][c + i] != p.P()[i][w - 1 - j]):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + j][c + i] -= p.P()[i][w - 1 - j]
                              
            elif (direction == 8): # flipped inverted both
                  for i in range(l):
                        for j in range(w):
                              if (p.P()[l - 1 - i][w - 1 - j] != 0 and self.__board[r + j][c + i] != p.P()[l - 1 - i][w - 1 - j]):
                                    return False

                  for i in range(l):
                        for j in range(w):
                              self.__board[r + j][c + i] -= p.P()[l - 1 - i][w - 1 - j]
                              
            self.__p[index] = 0
            return True

      def closedPoint(self, i, j):
            if ( self.__board[i - 1][j - 1] != 0 and
                  self.__board[i - 1][j] != 0 and
                  self.__board[i - 1][j + 1] != 0 and
                  self.__board[i][j - 1] != 0 and
                  self.__board[i][j] == 0 and # the closed point
                  self.__board[i][j + 1] != 0 and
                  self.__board[i + 1][j - 1] != 0 and
                  self.__board[i + 1][j] != 0 and
                  self.__board[i + 1][j + 1] != 0 ):
                        return True

            return False
            
      def problemDetected(self):
            if (self.__board[0][0] == 0 and
                self.__board[0][1] != 0 and
                self.__board[1][0] != 0 ):
                  return True
            
            for i in range(1, 9):
                  if (self.__board[0][i] == 0 and
                      self.__board[0][i - 1] != 0 and
                      self.__board[0][i + 1] != 0 and
                      self.__board[1][i] != 0 and
                      self.__board[1][i - 1] != 0 and
                      self.__board[1][i + 1] != 0 ):
                        return True

            if (self.__board[0][10] == 0 and
                self.__board[0][9] != 0 and
                self.__board[1][10] != 0 ):
                  return True

            for i in range(1, 3):
                  if (self.__board[i][0] == 0 and
                      self.__board[i - 1][0] != 0 and
                      self.__board[i + 1][0] != 0 and
                      self.__board[i][1] != 0 and
                      self.__board[i - 1][1] != 0 and
                      self.__board[i + 1][1] != 0 ):
                        return True

            if (self.__board[0][4] == 0 and
                self.__board[0][3] != 0 and
                self.__board[1][4] != 0 ):
                  return True
                  
            for i in range(1, 4):
                  for j in range(1, 10):
                        if (self.closedPoint(i, j) == True):
                              return True

            return False
      
      def P(self):
            return self.__p
      
      def solve(self, index):
            if (index == len(self.__pieces)):
                self.Print()
                return True # solved

            if (self.problemDetected() == True):
                  return False
            
            if (self.__p[index] != 0):
                  return self.solve(index + 1)
            
            p = self.__pieces[index]
      
            if (index == 4 or index == 10):
                  for i in range(5 + 1 - p.Length()):
                      for j in range(11 + 1 - p.Width()):
                            if self.putPiece(index, i, j, 1):
                                    t = self.solve(index + 1)
                                    if (t != True):
                                          self.removePiece(index)
                                    else:
                                          return True
                                    
            elif (index == 8):
                  for i in range(5 + 1 - p.Length()):
                      for j in range(11 + 1 - p.Width()):
                            for d in range(1, 5):
                                  if self.putPiece(index, i, j, d):
                                        t = self.solve(index + 1)
                                        if (t != True):
                                              self.removePiece(index)
                                        else:
                                              return True
            else:
                  for i in range(5 + 1 - p.Length()):
                      for j in range(11 + 1 - p.Width()):
                            for d in range(1, 5):
                                  if self.putPiece(index, i, j, d):
                                        t = self.solve(index + 1)
                                        if (t != True):
                                              self.removePiece(index)
                                        else:
                                              return True

                  for i in range(5 + 1 - p.Width()):
                      for j in range(11 + 1 - p.Length()):
                            for d in range(5, 9):
                                  if self.putPiece(index, i, j, d):
                                        t = self.solve(index + 1)
                                        if (t != True):
                                              self.removePiece(index)
                                        else:
                                              return True

            return False
            
      __board = [[0 for i in range(11)] for i in range(5)]
      __pieces = []
      __p = []

def menu():
      print ("1.......place piece")
      print ("2.......remove piece")
      print ("3.......solve")
      print ("4.......exit")
      print ("choose: ", end="")
      c = int(sys.stdin.readline())

      return c
      
def main():
      c = 0
      g = game()
      
      g.AddPiece(piece(2, 3, [[1, 1, 1],        [1, 0, 0]],                         "orange"))
      g.AddPiece(piece(2, 4, [[2, 2, 2, 2],     [2, 0, 0, 0]],                      "blue"))
      g.AddPiece(piece(2, 4, [[3, 3, 3, 0],     [0, 0, 3, 3]],                      "green"))
      g.AddPiece(piece(2, 3, [[4, 4, 4],        [4, 4, 0]],                         "red"))
      g.AddPiece(piece(3, 3, [[0, 5, 0],        [5, 5, 5],        [0, 5, 0]],       "gray"))
      g.AddPiece(piece(1, 4, [[6, 6, 6, 6]],                                        "purple"))
      g.AddPiece(piece(2, 3, [[7, 7, 7],        [7, 0, 7]],                         "yellow"))
      g.AddPiece(piece(3, 3, [[8, 8, 0],        [0, 8, 8],        [0, 0, 8]],       "meganta"))
      g.AddPiece(piece(2, 2, [[9, 9],           [9, 0]],                            "white"))
      g.AddPiece(piece(3, 3, [[10, 10, 10],     [0, 0, 10],        [0, 0, 10]],     "cyan"))
      g.AddPiece(piece(2, 2, [[11, 11],         [11, 11]],                          "greenish"))
      g.AddPiece(piece(2, 4, [[12, 12, 12, 12], [0, 12, 0, 0]],                     "pinkish"))

      while (c != 4):
            g.Print()
            c = menu()

            if (c == 1):
                  print ("Enter piece number: ", end="")
                  n = int(sys.stdin.readline())
                  if (g.P()[n - 1] != 0):
                        pass
                  else:
                        print ("Enter position (r,c, direction): ", end="")
                        r,c,direction = [int(d) for d in sys.stdin.readline().split(',')]
                        if (g.putPiece(n - 1, r, c, direction)):
                              pass
                        
            elif (c == 2):
                  print ("Enter piece number: ", end="")
                  n = int(sys.stdin.readline())
                  if (g.P()[n - 1] != 0):
                        g.removePiece(n - 1)
                        
            elif (c == 3):
                  startTime = time.clock()
                  if (g.solve(0) == False):
                        print ("Can't solve this board")
                  elapsedTime = time.clock() - startTime
                  print ("Time spent in (", __name__, ") is: ", elapsedTime, " sec")
                 
if __name__ == "__main__":
      main()
