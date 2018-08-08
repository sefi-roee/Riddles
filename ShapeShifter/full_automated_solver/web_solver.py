#!/usr/bin/env python

import selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import re, time, sys, signal
import argparse
import subprocess
from threading  import Thread
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def signal_handler(sig, frame):
	global driver

	print('You pressed Ctrl+C!')
	driver.stop_client()
	driver.close()
	sys.exit(0)

def reader(f,buffer):
	while True:
		line=f.readline()
		if line:
			buffer.append(line)
		else:
			break

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

def main():
	global driver

	# Login
	if args.verbose:
		print 'Logging in...',
		sys.stdout.flush()
	driver.get('http://www.neopets.com/login/index.phtml?destination=%2Fmedieval%2Fshapeshifter_index.phtml')

	signal.signal(signal.SIGINT, signal_handler)

	WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.NAME, "username"))
	)
	username = driver.find_elements_by_name("username")[1]
	password = driver.find_elements_by_name("password")[1]

	username.send_keys(args.username)
	password.send_keys(args.password)

	driver.execute_script('document.forms["login"].submit()')
	if args.verbose:
		print 'Done!'
		sys.stdout.flush()

	it = 0

	# Start game
	try:
		WebDriverWait(driver, 5).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/table/tbody/tr/td[2]/center/form/input[2]'))
		)

		e = driver.find_element_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/center/form/input[2]')
		assert (e.get_attribute('value') == 'Start Game!')
		if args.verbose:
			print 'Started a new game!'
			sys.stdout.flush()
		e.click()
	except:
		pass

	# Continue game
	try:
		WebDriverWait(driver, 5).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[1]/table/tbody/tr/td[2]/center/center/form/input'))
		)

		e = driver.find_elements_by_xpath('//*[@id="content"]/div[1]/table/tbody/tr/td[2]/center/center/form/input')[0]
		assert (e.get_attribute('value') == 'Continue Game!')
		if args.verbose:
			print 'Continue game!'
			sys.stdout.flush()
		e.click()
	except:
		pass

	while it < args.l:
		# Move to the next level
		try:
			WebDriverWait(driver, 5).until(
				EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/table/tbody/tr/td[2]/center[2]/form/input'))
			)

			e = driver.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr/td[2]/center[2]/form/input')[0]
			assert (e.get_attribute('value') == 'Move to the next level?!')
			if args.verbose:
				print 'Move to the next level'
				sys.stdout.flush()
			e.click()
		except:
			pass
			
		try:
			if args.verbose:
				print 'Parsing board...', #presence_of_element_located
				sys.stdout.flush()

			WebDriverWait(driver, 10).until(
				EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/table/tbody/tr/td[2]/center[2]/table/tbody/tr/td/table/tbody/tr/td[*]/img'))
			)
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
			if args.verbose:
				print 'Done!'
				sys.stdout.flush()
		except:
			if args.verbose:
				print 'Failed!'
				sys.stdout.flush()
				driver.refresh()

			continue

		next_shapes = []

		for next_shape_e in next_shapes_e:
			next_shapes.append(get_shape_from_e(next_shape_e))

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
		
		if args.parse_only:
			break

		if args.verbose:
			print 'Running solver...',
		linebuffer=[]
		solver = subprocess.Popen(['./shapeshifter',  './board_{:02d}'.format(int(level.split()[-1]))], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		t=Thread(target=reader,args=(solver.stderr,linebuffer))
		t.daemon=True
		t.start()

		# Wait for 2 messages (PID, numOfThreads)
		while len(linebuffer) < 3:
			pass

		if args.verbose:
			print '({})'.format(linebuffer.pop(0).replace('\n','')) # Print PID
			print '{}'.format(level) # Print level number
			numOfFlips = int(linebuffer.pop(0).split(':')[1])
			print 'Number of flips: {}'.format(numOfFlips)
			numOfThreads = int(linebuffer.pop(0).split(':')[1])
			print 'Number of threads: {}'.format(numOfThreads)
			print
			sys.stdout.flush()

		flag = False
		time.sleep(1)
		while solver.poll() == None:
			solver.send_signal(10)
			time.sleep(5)
			if flag:
				if args.verbose:
					print "\033[F" * (numOfThreads + 4),
			else:
				flag = True

			while linebuffer:
				if args.verbose:
					print linebuffer.pop(0),

		solveTime, solution, _ = solver.communicate()[0].split('\n')

		solution = solution.split(';')
		solution = solution[:-1]
		if args.verbose:
			print 'Solution found (In {} secs)'.format(solveTime)
			print '\t'.join(solution)
			print ''
			sys.stdout.flush()

		for i, s in enumerate(solution):
			s = map(int, s.split(','))
			if args.verbose:
				print '\r',
				print '\tPlacing piece {}/{} (at {},{})...'.format(i+1, len(solution), s[0]+1, s[1]+1),
				sys.stdout.flush()

			xpath = '//*[@id="content"]/table/tbody/tr/td[2]/table/tbody/tr[{}]/td[{}]/a/img'.format(s[0] + 1, s[1] + 1)
			element = WebDriverWait(driver, 15).until(
				EC.element_to_be_clickable((By.XPATH, xpath))
			);

			element.click();

		if args.verbose:
			try:
				WebDriverWait(driver, 10).until(
					EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/table/tbody/tr/td[2]/center[2]/form[1]/input'))
				) # Wait for finish
				print ' Done!'
				print '*************************************************************\n'
				sys.stdout.flush()
			except selenium.common.exceptions.TimeoutException:
				print 'You\'ve reached your max neopoints on this game for today!'
				print '*************************************************************\n'
				sys.stdout.flush()

				break

		it += 1

	#driver.quit()
	driver.stop_client()
	driver.close()
	driver.quit()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Automatic solver for shapeshifter game (Interactive with the web site).')
	parser.add_argument("username", help="username in neopets")
	parser.add_argument("password", help="password in neopets")
	parser.add_argument("-l", help="limit number of levels", type=int, default=200)
	parser.add_argument("-po", "--parse-only", help="only parse the board", action="store_true")
	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

	args = parser.parse_args()

	capa = DesiredCapabilities.CHROME
	capa["pageLoadStrategy"] = "none"
	driver = webdriver.Chrome('./chromedriver', desired_capabilities=capa)
	driver.maximize_window()

	if args.verbose:
		startTime = time.clock()

	main()

	if args.verbose:
		elapsedTime = time.clock() - startTime
		print 'Board solved in ({}) is: {} sec'.format(__name__, elapsedTime)