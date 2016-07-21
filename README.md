# Processing satellite images

## Installation
* `npm install` for the labeling tool
* Needed dependencies for the neural network: Tensorflow (please see the install instructions on their [page](https://www.tensorflow.org/)), Numpy (install with pip), OpenCV2 (install with brew/pip)

## Start
* Clone the repository, `cd satellite-images`
* Put the images to be labeled into "app/images_input"
* In main directory: `node server.js` starts the labeling tool
* In your browser go to [http://localhost:8080/](http://localhost:8080/)
* Mark the points / label things
* Then in main directory: `python crop_images.py path/to/your/img.png` will crop images into "images_cropped"
* Now `python convolutional_sat.py train` will train the neural network and save it under "conv_mnist_model.ckpt", can take some time
* `python convolutional_sat.py path/to/your/img.png` uses the saved network to run on an image and label it, produces an "output.jpeg"

## I tried:
* Didn't work with 40x40 pixel images (feeded to the network)
* 60x60 pixels, more augmentation with rotations: not bad, but it recognices too much (where there is nothing)

## Todo
* Switch to hdfs. Does tensorflow support it?


Need to read some papers about this subject.