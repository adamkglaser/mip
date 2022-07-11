from os import listdir
import shutil
from os.path import isfile, join
import argparse
import concurrent.futures
from itertools import repeat
import time
import tifffile
import numpy

def rename_file(input_file, idx_list, frames, idx):

	if idx == len(idx_list)-1:
		im = tifffile.imread(input_file, key=idx_list[idx])
		for i in range(idx_list[idx]+1, frames, 1):
			temp = tifffile.imread(input_file, key=i)
			im = numpy.maximum(im, temp)
		return im
	else:
		im = tifffile.imread(input_file, key=idx_list[idx])
		for i in range(idx_list[idx]+1, idx_list[idx+1], 1):
			temp = tifffile.imread(input_file, key=i)
			im = numpy.maximum(im, temp)
		return im

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input_file', type = str, required = True, help = "input file")
	parser.add_argument('-t', '--threads', type = int, required = True, help = "number of threads")

	args = parser.parse_args()

	im = tifffile.TiffFile(args.input_file)

	frames = len(im.pages)

	idx = numpy.arange(0, frames, int(frames/(args.threads)))

	if idx[-1] == frames:
		idx=idx[:-1]

	mip = numpy.zeros((im.pages[0].shape[0], im.pages[0].shape[1]), dtype = im.pages[0].dtype)

	start_time = time.time()

	with concurrent.futures.ProcessPoolExecutor(max_workers = args.threads) as executor:
	    for result in executor.map(rename_file, repeat(args.input_file), repeat(idx), repeat(frames), range(len(idx))):
	    	mip = numpy.maximum(mip, result)

	end_time = time.time()

	print('Elapsed time: ' + str((end_time - start_time)/60) + ' min')

	tifffile.imwrite('test.tiff', mip.astype('uint16'))
