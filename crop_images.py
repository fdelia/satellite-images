#
# Crop hxw parts out of images_input/ images for neural network training.
# Save the crops into images_cropped/image_filename/label/
#

import os, sys, json
import cv2


IMAGE_SIZE = 52
ZERO_IMG_RADIUS = int(IMAGE_SIZE / 2)
(winX, winY) = (IMAGE_SIZE, IMAGE_SIZE)

if len(sys.argv) < 2: sys.argv.append('app/images_input/zurich.jpeg')
img_path = sys.argv[1]
POI_path = sys.argv[1] + '_POI.txt'
if not os.path.isfile(POI_path): raise Exception('given POI-file not found')
if not os.path.isfile(img_path): raise Exception('image file not found')

image = cv2.imread(img_path)
_, image_filename = os.path.split(img_path)


# remove 0-label images first!
print('...remove 0-label images...')
path = 'images_cropped/0/'
[os.remove(path + f) for f in os.listdir(path)]


# crop images
print('...start cropping...')
counter = 0
with open(POI_path) as data_file:
  POIs = json.load(data_file)
  print('found POIs: ' + str(len(POIs)))

  for POI in POIs:
    # x and y are in the center! not in the left top corner
    label, x, y = POI

    # corrections
    if x < int(winX / 2): x = winX / 2
    if y < int(winY / 2): y = winY / 2
    # x and y are switched in cv2/.shape
    if x > int(image.shape[1] - winX / 2): x = image.shape[1] - winX / 2
    if y > int(image.shape[0] - winY / 2): x = image.shape[0] - winY / 2

    crop = image[y - winY/2 : y + winY/2, x - winX/2 : x + winX/2]    
    # crop = cv2.resize(crop, (40, 40))
    cv2.imwrite('images_cropped/'+ str(label) + '/' + image_filename + '_'+str(x)+'_'+str(y)+'.png', crop) 
    counter += 1


print('cropped images: ' + str(counter))


counter2 = 0
counterNearPOI = 0
# skip first 10 crops at top left because of label in image
for i in range(10, counter * 2):
  x0 = winX/2 * (i + 1) % image.shape[1]
  y0 = winY/2 * ((i * winY/2)  // image.shape[1] + 1)


  if x0 < winX/2 or y0 < winY/2: continue
  if y0 >= image.shape[0]: break

  # print(i)
  # print (str(x0) + ' ' + str(y0))

  # check if there is a the radius
  nearPOI = False
  for POI in POIs:
    label, x, y = POI
    # radius... how big shall it be? -> param, to determine
    if ( (x - x0)**2 + (y - y0)**2 ) ** 0.5 < ZERO_IMG_RADIUS:
      nearPOI = True
      break
    
  if nearPOI:
    counterNearPOI += 1
    continue

  crop = image[y0 - winY/2 : y0 + winY/2, x0 - winX/2 : x0 + winX/2]  
  cv2.imwrite('images_cropped/0/' + image_filename + '_'+str(x0)+'_'+str(y0)+'.png', crop)     
  counter2 += 1

print('0-images: ' + str(counter2))
print('(near POI: ' + str(counterNearPOI) + ')')

