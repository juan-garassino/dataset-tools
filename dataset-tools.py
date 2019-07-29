import argparse
import numpy as np
import os
import imutils
import cv2

# print(cv2.__version__)

def parse_args():
	desc = "Tools to normalize an image dataset" 
	parser = argparse.ArgumentParser(description=desc)

	parser.add_argument('--verbose', action='store_true',
		help='Boolean flag indicating if statements should be printed to the console.')

	parser.add_argument('--input_folder', type=str,
		default='./input/',
		help='Directory path to the inputs folder. (default: %(default)s)')

	parser.add_argument('--output_folder', type=str,
		default='./output/',
		help='Directory path to the outputs folder. (default: %(default)s)')

	parser.add_argument('--process_type', type=str,
		default='resize',
		help='Process to use. ["resize","square","crop_to_square","canny","pix2pix"] (default: %(default)s)')

	parser.add_argument('--max_size', type=int, 
		default=512,
		help='Maximum width or height of the output images. (default: %(default)s)')

	parser.add_argument('--direction', type=str,
		default='AtoB',
		help='Paired Direction. For use with pix2pix process. ["AtoB","BtoA"] (default: %(default)s)')

	# parser.add_argument('--blur_size', type=int, 
	# 	default=3,
	# 	help='Blur size. For use with "canny" process. (default: %(default)s)')

	parser.add_argument('--mirror', action='store_true',
		help='Adds mirror augmentation.')

	parser.add_argument('--rotate', action='store_true',
		help='Adds 90deg rotation augmentation.')

	args = parser.parse_args()
	return args


def image_resize(image, width = None, height = None, max = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    if max is not None:
    	if w > h:
    		# produce
    		r = max / float(w)
    		dim = (max, int(h * r))
    	elif h > w:
    		r = max / float(h)
    		dim = (int(w * r), max)
    	else :
    		dim = (max, max)

    else: 
	    # if both the width and height are None, then return the
	    # original image
	    if width is None and height is None:
	        return image

	    # check to see if the width is None
	    if width is None:
	        # calculate the ratio of the height and construct the
	        # dimensions
	        r = height / float(h)
	        dim = (int(w * r), height)

	    # otherwise, the height is None
	    else:
	        # calculate the ratio of the width and construct the
	        # dimensions
	        r = width / float(w)
	        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def crop_to_square(img):
	(h, w) = img.shape[:2]
	if w > h:
		# crop width
		diff = int((w-h)/2)
		cropped = img[0:h, diff:diff+h]
		return cropped
	elif h > w:
		# crop height
		diff = int((h-w)/2)
		cropped = img[diff:diff+w, 0:w]
		return cropped
	else:
		return img

def makeResize(img,filename,scale,flip=False,rotate=False):

	remakePath = args.output_folder + str(scale)+"/"
	if not os.path.exists(remakePath):
		os.makedirs(remakePath)

	img_copy = img.copy()
	img_copy = image_resize(img_copy, max = scale)
	new_file = os.path.splitext(filename)[0] + ".jpg"
	# new_file = str(count) + ".jpg"
	# save out 256
	cv2.imwrite(os.path.join(remakePath, new_file), img_copy)

	if (flip):
		flip = img_copy.copy()
		flip = cv2.flip(flip, 1)
		flip_file = os.path.splitext(filename)[0] + "-flipped.jpg"
		cv2.imwrite(os.path.join(remakePath, flip_file), flip)
	if(rotate):
		r = img_copy.copy() 
		r = imutils.rotate_bound(r, 90)
		r_file = os.path.splitext(filename)[0] + "-rot90.jpg"
		cv2.imwrite(os.path.join(remakePath, r_file), r)

		r = imutils.rotate_bound(r, 90)
		r_file = os.path.splitext(filename)[0] + "-rot180.jpg"
		cv2.imwrite(os.path.join(remakePath, r_file), r)

		r = imutils.rotate_bound(r, 90)
		r_file = os.path.splitext(filename)[0] + "-rot270.jpg"
		cv2.imwrite(os.path.join(remakePath, r_file), r)


def makeSquare(img,filename,scale,flip=False):
	sqPath = args.output_folder + "sq-"+str(scale)+"/"
	if not os.path.exists(sqPath):
		os.makedirs(sqPath)

	bType = cv2.BORDER_REPLICATE
	img_sq = img.copy()
	img_sq = image_resize(img_sq, max = scale)

	(h, w) = img_sq.shape[:2]
	if(h > w):
		# pad left/right
		# print("pad left/right")
		diff = h-w
		if(diff%2 == 0):
			# print("even")
			img_sq = cv2.copyMakeBorder(img_sq, 0, 0, int(diff/2), int(diff/2), bType)
		else:
			# print("odd")
			img_sq = cv2.copyMakeBorder(img_sq, 0, 0, int(diff/2)+1, int(diff/2), bType)
	elif(w > h):
		# pad top/bottom
		print("pad top/bottom")
		diff = w-h
		if(diff%2 == 0):
			# print("even")
			img_sq = cv2.copyMakeBorder(img_sq, int(diff/2), int(diff/2), 0, 0, bType)
		else:
			# print("odd")
			img_sq = cv2.copyMakeBorder(img_sq, int(diff/2), int(diff/2)+1, 0, 0, bType)

	new_file = os.path.splitext(filename)[0] + "-sq.jpg"
	cv2.imwrite(os.path.join(sqPath, new_file), img_sq)

	if(flip):
		flip_img = img_sq.copy()
		flip_img = cv2.flip(flip_img, 1)
		flip_file = os.path.splitext(filename)[0] + "-flipped-sq.jpg"
		cv2.imwrite(os.path.join(sqPath, flip_file), flip_img)

	
	

def makeCanny(img,filename,scale,medianBlurScale=3):
	make_path = args.output_folder + "canny-"+str(scale)+"/"
	if not os.path.exists(make_path):
		os.makedirs(make_path)

	img_copy = img.copy()
	img_copy = image_resize(img_copy, max = scale)
	gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
	# gray = cv2.GaussianBlur(gray, (1, 1), 0)
	# gray = cv2.medianBlur(gray,medianBlurScale)
	gray = cv2.Canny(gray,100,300)

	# save out
	new_file = os.path.splitext(filename)[0] + ".jpg"
	# new_file = str(count) + ".jpg"
	cv2.imwrite(os.path.join(make_path, new_file), gray)

def makeSquareCrop(img,filename,scale,flip=False):
	make_path = args.output_folder + "sq-"+str(scale)+"/"
	if not os.path.exists(make_path):
		os.makedirs(make_path)

	img_copy = img.copy()
	img_copy = crop_to_square(img_copy)
	img_copy = image_resize(img_copy, max = scale)

	new_file = str(count) + ".jpg"
	cv2.imwrite(os.path.join(make_path, new_file), img_copy)

	if(flip):
		flip_img = img_copy.copy()
		flip_img = cv2.flip(flip_img, 1)
		# flip_file = str(count+int(1)) + ".jpg"
		flip_file = os.path.splitext(filename)[0] + "-flipped.jpg"
		cv2.imwrite(os.path.join(make_path, flip_file), flip_img)


def makePix2Pix(img,filename,direction="BtoA",value=[0,0,0]):
	img_p2p = img.copy()
	(h, w) = img_p2p.shape[:2]
	bType = cv2.BORDER_CONSTANT
	
	make_path = args.output_folder + "pix2pix-"+str(h)+"/"
	if not os.path.exists(make_path):
		os.makedirs(make_path)

	
	if(direction is "BtoA"):
		img_p2p = cv2.copyMakeBorder(img_p2p, 0, 0, w, 0, bType, None, value)
		# new_file = str(count) + ".jpg"
		new_file = os.path.splitext(filename)[0] + ".jpg"
		cv2.imwrite(os.path.join(make_path, new_file), img_p2p)


def processImage(img,filename):
	if args.process_type == "resize":	
		makeResize(img,filename,args.max_size,args.mirror,args.rotate)
	if args.process_type == "square":
		makeSquare(img,filename,args.max_size)
	if args.process_type == "crop_to_square":
		makeSquareCrop(img,filename,args.max_size,args.mirror)
	if args.process_type == "canny":
		makeCanny(img,filename,args.max_size)
	if args.process_type == "pix2pix":
		makePix2Pix(img,filename)

def main():
	global args
	global count
	count = int(0)
	args = parse_args()

	for root, subdirs, files in os.walk(args.input_folder):
		print('--\nroot = ' + root)

		for subdir in subdirs:
			print('\t- subdirectory ' + subdir)

		for filename in files:
			file_path = os.path.join(root, filename)
			print('\t- file %s (full path: %s)' % (filename, file_path))
			
			img = cv2.imread(file_path)

			if hasattr(img, 'copy'):
				processImage(img,filename)
				count = count + int(2)


if __name__ == "__main__":
	main()
	# path1024 = end_path + "1024/"
	# path256 = end_path + "256/"

	# if not os.path.exists(path1024):
	# 	os.makedirs(path1024)
	# if not os.path.exists(path256):
	# 	os.makedirs(path256)

	# for root, dirs, files in os.walk(start_path, topdown=False):
	# 	for name in files:
	# 		print(os.path.join(root, name))

	
			


	# cv2.imshow( "Image", img )
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()