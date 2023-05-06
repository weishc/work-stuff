import random


def rotate(list, i):	
	return list[i % len(list)]


def create_rows(start_num):
	return [i % 9 for i in range(start_num,start_num + 9)]


seed = [i for i in range(1, 10)]
random.shuffle(seed)
cols = [i for i in range(9)]
grid = []


for r in range(3):
	for c in range(3):
		start_num = rotate(cols,c * 3 + r * 10)
		row = [seed[i] for i in create_rows(start_num)]
		grid.append(row)


del_list = [i for i in range(9 * 9)]
random.shuffle(del_list)


for i in range(60):
	del_num = del_list[i]
	grid[del_num // 9][del_num % 9] = 0


for i in grid:
	print (i)
