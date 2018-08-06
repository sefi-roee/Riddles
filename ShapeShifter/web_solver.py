#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import re, time, sys
import argparse
from shapeshifter_solver import ShapeShifter


def print_elem(b, delim = '', tabs = 0):
	r = ''
	for line in b:
		r += '\t'*tabs + delim.join(map(str, line)) + '\n'

	return r

def get_shape_from_e(e):
	r = None
	rows = e.find_elements_by_xpath('tbody/tr')

	for i, row in enumerate(rows):
		cols = row.find_elements_by_xpath('td')

		for j, col in enumerate(cols):
			if r == None:
				r = [[0 for _ in range(len(cols))] for _ in range(len(rows))]

			try:
				if col.find_element_by_xpath('img').get_attribute('src') == 'http://images.neopets.com/medieval/shapeshifter/square.gif':
					r[i][j] = 1
			except NoSuchElementException:
				pass

	return r

driver = webdriver.Chrome('./chromedriver')

driver.get('http://www.neopets.com/login/index.phtml?destination=%2Fmedieval%2Fshapeshifter_index.phtml')

username = driver.find_elements_by_name("username")[1]
password = driver.find_elements_by_name("password")[1]

username.send_keys('roee_sefi')
password.send_keys('kjdX20kd!')

driver.execute_script('document.forms["login"].submit()')

# Start game
try:
	e = driver.find_element_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/center/form/input[2]')
	assert (e.get_attribute('value') == 'Start Game!')
	print 'Started a new game!'
	e.click()
except AssertionError:
	pass

# Continue game
try:
	e = driver.find_elements_by_xpath('//*[@id="content"]/div[1]/table/tbody/tr/td[2]/center/center/form/input')[0]
	assert (e.get_attribute('value') == 'Continue Game!')
	print 'Game continued!'
	e.click()
except:
	pass

# Move to the next level
try:
	e = driver.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/center[2]/form/input')[0]
	assert (e.get_attribute('value') == 'Move to the next level?!')
	print 'Moving to the next level!'
	e.click()
except:
	pass
	
level = driver.find_element_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/center[1]/b/big').text

# Get group mapping
group_e = driver.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/center[2]/table/tbody/tr/td/table/tbody/tr/td[*]/img')
group = {}
group[group_e[0].get_attribute('src')] = 1

for i in range(2, len(group_e) - 3, 2):
	group[group_e[i].get_attribute('src')] = i // 2 + 1
group[group_e[-3].get_attribute('src')] = 0

# Get level board
board_e = driver.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/table/tbody/tr[*]/td[*]')
size = board_e[-1].find_element_by_xpath('a').get_attribute('onmouseover')
size = map(lambda x: int(x) + 1, re.findall(r'\d+', size))
board = [[0 for _ in range(size[0])] for _ in range(size[1])]

for e in board_e:
	ind = map(int, re.findall(r'\d+', e.find_element_by_xpath('a').get_attribute('onmouseover')))
	board[ind[1]][ind[0]] = group[e.find_element_by_xpath('a/img').get_attribute('src')]


active_shape_e = driver.find_element_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/center[3]/table/tbody/tr/td/table')
active_shape = get_shape_from_e(active_shape_e)

next_shapes_e = driver.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/center[3]/center/table/tbody/tr/td[*]/table')
if next_shapes_e == []:
	next_shapes_e = driver.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/center[3]/center/table')

next_shapes = []

for next_shape_e in next_shapes_e:
	next_shapes.append(get_shape_from_e(next_shape_e))

print 'Level: {}'.format(level)
print 'Board size: {},{}'.format(size[1], size[0])
print 'Board:'
print print_elem(board, ' ', 1)
print 'Shapes:'
print print_elem(active_shape, ' ', 1)
for next_shape in next_shapes:
	print print_elem(next_shape, ' ', 1)
	print ''

with open('./board_{:02d}'.format(int(level.split()[-1])), 'w') as out_file:
	print >>out_file, len(group)
	print >>out_file, '{}x{}'.format(size[1], size[0])
	print >>out_file, print_elem(board),
	print >>out_file, 1 + len(next_shapes)
	print >>out_file, '{}x{}'.format(len(active_shape), len(active_shape[0]))
	print >>out_file, print_elem(active_shape),

	for next_shape in next_shapes:
		print >>out_file, '{}x{}'.format(len(next_shape), len(next_shape[0]))
		print >>out_file, print_elem(next_shape),

parser = argparse.ArgumentParser(description='Automatic solver for shapeshifter game (Interactive with the web site).')
parser.add_argument('alg', help='algorithm (bf/bf_prune/bi/bc/bf_i)')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()

startTime = time.clock()
solver = ShapeShifter('./board_{:02d}'.format(int(level.split()[-1])), args.verbose)
print (solver)
#sol = solver.solve('bf_prune')
sol = solver.solve(args.alg)
#sol = sorted(sol, key=lambda x: x[0])

if sol == None:
	print 'No solution found'
	sys.exit(1)

print 'Solution found'
for i, s in enumerate(sol):
	print '\r',
	print '\tPlacing piece {}/{}...'.format(i+1, len(sol)),
	sys.stdout.flush()
	driver.find_element_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/table/tbody/tr[{}]/td[{}]/a/img'.format(s[0] + 1, s[1] + 1)).click()

print ' Done!'

elapsedTime = time.clock() - startTime
print 'Board solved in ({}) is: {} sec'.format(__name__, elapsedTime)
