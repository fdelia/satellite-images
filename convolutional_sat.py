#
# This is taken from the official cifar10 exampe from tensorflow. 
# Credits for the build of this model goes to them.
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# import gzip
import os
import sys
import time
import random

from six.moves import urllib
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf
import numpy
import cv2
import math

#
# remove alpha channel with this
# gm convert -background color -extent 0x0 +matte src.png dst.png
#

IMAGE_SIZE = 52
NUM_CHANNELS = 3
PIXEL_DEPTH = 255
NUM_LABELS = 4
# VALIDATION_SIZE = 200  # Size of the validation set. / set as one third now
TEST_SIZE = 100  # Size of test set (at the end), is new data for the network
SEED = 66478  # Set to None for random seed.
BATCH_SIZE = 64 # 64
NUM_EPOCHS = 10 # ok with 100, starts being ok with 15~20
EVAL_BATCH_SIZE = 64 #64
EVAL_FREQUENCY = 100  # Number of steps between evaluations.
WEBCAM_MULT = 5 # multiplier for webcam resolution (higher = better, 1 = 128x72)
  

# configs
if 'train' in sys.argv:
  tf.app.flags.DEFINE_boolean('run_only', False, 'True = only activate images, False = train network')
else:
  if len(sys.argv) < 2: sys.argv.append('app/images_input/zurich.jpeg')
  IMG_PATH = sys.argv[1]
  tf.app.flags.DEFINE_boolean('run_only', True, 'True = only activate images, False = train network')

tf.app.flags.DEFINE_boolean("self_test", False, "True if running a self test.")
FLAGS = tf.app.flags.FLAGS




def get_images_and_labels(max_num_images):
  images = []
  labels = []
  filenameLabels = []

  for label in range(0, NUM_LABELS):
    path = 'images_cropped/' + str(label) + '/'
    filenameLabels += [(path+f, label) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
  
  random.shuffle(filenameLabels)

  counter = 0
  for path, label in filenameLabels:
      if counter >= max_num_images:
        break

      _, filename = os.path.split(path)
      if filename.find('.') == 0:
        continue

      if not os.path.isfile(path):
        continue

      # im_org = Image.open(path)  # .convert("L")  # Convert to greyscale
      im_org = cv2.imread(path)
      im = numpy.asarray(im_org, numpy.float32)
      
      if im.shape != (IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS):
        # print('    wrong shape: '+filename)
        # print(im.shape)
        continue
   
      images.append(im)
      labels = numpy.append(labels, [label])
      counter += 1

      # augmentation, flip vertically
      im2 = cv2.flip(im_org,1)
      im2 = numpy.asarray(im2, numpy.float32)
      images.append(im2)
      labels = numpy.append(labels, [label])
      counter += 1        

      # augmentation, rotate 180
      im2 = cv2.flip(im_org, -1)
      im2 = numpy.asarray(im2, numpy.float32)
      images.append(im2)
      labels = numpy.append(labels, [label])
      counter += 1        

      # augmentation, rotate 90
      # if label==1:
      # im2 = im_org.rotate(90, expand=0)
      (h, w) = im_org.shape[:2]
      M = cv2.getRotationMatrix2D((w/2, h/2), 90, 1.0)
      im2 = cv2.warpAffine(im_org, M, (w, h))
      im2 = numpy.asarray(im2, numpy.float32)
      images.append(im2)
      labels = numpy.append(labels, [label])
      counter += 1                


      if counter%1000 == 0:
        print('   loaded '+str(int(counter/1000)*1000)+' images') 


  if len(images) != len(labels):
    raise ValueError ('len(images) != len(labels) , something went wrong!')

  print('finally loaded '+str(len(images))+' images') 

  images = numpy.asarray(images, numpy.float32)
  images = (images - (PIXEL_DEPTH / 2.0)) / PIXEL_DEPTH
  images = images.reshape(counter, IMAGE_SIZE, IMAGE_SIZE, 3)

  labels = numpy.asarray(labels, numpy.int)

  return images, labels


def sliding_window(image, stepSize, windowSize):
  # slide a window across the image
  for y in xrange(0, image.shape[0] - windowSize[1], stepSize):
    for x in xrange(0, image.shape[1] - windowSize[0], stepSize): # it doesnt make sense to crop at x=640 ???
      # yield the current window
      # x -= int(windowSize[1] / 2)
      yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])


def extract_labels(filename, num_images):
  """Extract the labels into a vector of int64 label IDs."""
  print('Extracting', filename)
  with gzip.open(filename) as bytestream:
    bytestream.read(8)
    buf = bytestream.read(1 * num_images)
    labels = numpy.frombuffer(buf, dtype=numpy.uint8).astype(numpy.int64)
  return labels


def fake_data(num_images):
  """Generate a fake dataset that matches the dimensions of MNIST."""
  data = numpy.ndarray(
      shape=(num_images, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS),
      dtype=numpy.float32)
  labels = numpy.zeros(shape=(num_images,), dtype=numpy.int64)
  for image in xrange(num_images):
    label = image % 2
    data[image, :, :, 0] = label - 0.5
    labels[image] = label
  return data, labels


def error_rate(predictions, labels):
  """Return the error rate based on dense predictions and sparse labels."""
  return 100.0 - (
      100.0 *
      numpy.sum(numpy.argmax(predictions, 1) == labels) /
      predictions.shape[0])


def main(argv=None):  # pylint: disable=unused-argument
  if FLAGS.self_test or FLAGS.run_only:
    if FLAGS.run_only: print ('Running on cam input.')
    else: print('Running self-test.')

    train_data, train_labels = fake_data(256)
    validation_data, validation_labels = fake_data(EVAL_BATCH_SIZE)
    test_data, test_labels = fake_data(EVAL_BATCH_SIZE)
    num_epochs = 1
  else:
    # Extract it into numpy arrays.
    train_data, train_labels = get_images_and_labels(50*1000)

    test_data = train_data[:TEST_SIZE, ...]
    test_labels = train_labels[:TEST_SIZE, ...]

    train_data = numpy.delete(train_data, range(1, TEST_SIZE), axis=0)
    train_labels = numpy.delete(train_labels, range(1, TEST_SIZE), axis=0)

    print('training labels: ' + str(len(train_labels)))
    print('test labels: ' + str(len(test_labels)))

    VALIDATION_SIZE = int(len(train_labels) / 3)
    print('validation size: ' + str(VALIDATION_SIZE))

    # Generate a validation set.
    validation_data = train_data[:VALIDATION_SIZE, ...]
    validation_labels = train_labels[:VALIDATION_SIZE]
    train_data = train_data[VALIDATION_SIZE:, ...]
    train_labels = train_labels[VALIDATION_SIZE:]
    num_epochs = NUM_EPOCHS
  train_size = train_labels.shape[0]

  # This is where training samples and labels are fed to the graph.
  # These placeholder nodes will be fed a batch of training data at each
  # training step using the {feed_dict} argument to the Run() call below.
  train_data_node = tf.placeholder(
      tf.float32,
      shape=(BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))
  train_labels_node = tf.placeholder(tf.int64, shape=(BATCH_SIZE,))
  eval_data = tf.placeholder(
      tf.float32,
      shape=(EVAL_BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))

  # The variables below hold all the trainable weights. They are passed an
  # initial value which will be assigned when we call:
  # {tf.initialize_all_variables().run()}
  conv1_weights = tf.Variable(
      tf.truncated_normal([5, 5, NUM_CHANNELS, 32],  # 5x5 filter, depth 32.
                          stddev=0.1,
                          seed=SEED))
  conv1_biases = tf.Variable(tf.zeros([32]))
  conv2_weights = tf.Variable(
      tf.truncated_normal([5, 5, 32, 64], # was ok with 64
                          stddev=0.1,
                          seed=SEED))
  conv2_biases = tf.Variable(tf.constant(0.1, shape=[64]))
  fc1_weights = tf.Variable(  # fully connected, depth 512.
      tf.truncated_normal(
          [IMAGE_SIZE // 4 * IMAGE_SIZE // 4 * 64, 512], # was ok with 512
          stddev=0.1,
          seed=SEED))
  fc1_biases = tf.Variable(tf.constant(0.1, shape=[512]))
  fc2_weights = tf.Variable(
      tf.truncated_normal([512, NUM_LABELS],
                          stddev=0.1,
                          seed=SEED))
  fc2_biases = tf.Variable(tf.constant(0.1, shape=[NUM_LABELS]))

  # We will replicate the model structure for the training subgraph, as well
  # as the evaluation subgraphs, while sharing the trainable parameters.
  def model(data, train=False):
    """The Model definition."""
    # 2D convolution, with 'SAME' padding (i.e. the output feature map has
    # the same size as the input). Note that {strides} is a 4D array whose
    # shape matches the data layout: [image index, y, x, depth].
    conv = tf.nn.conv2d(data,
                        conv1_weights,
                        strides=[1, 1, 1, 1],
                        padding='SAME')
    # Bias and rectified linear non-linearity.
    relu = tf.nn.relu(tf.nn.bias_add(conv, conv1_biases))
    # Max pooling. The kernel size spec {ksize} also follows the layout of
    # the data. Here we have a pooling window of 2, and a stride of 2.
    pool = tf.nn.max_pool(relu,
                          ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1],
                          padding='SAME')
    conv = tf.nn.conv2d(pool,
                        conv2_weights,
                        strides=[1, 1, 1, 1],
                        padding='SAME')
    relu = tf.nn.relu(tf.nn.bias_add(conv, conv2_biases))
    pool = tf.nn.max_pool(relu,
                          ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1],
                          padding='SAME')
    # Reshape the feature map cuboid into a 2D matrix to feed it to the
    # fully connected layers.
    pool_shape = pool.get_shape().as_list()
    reshape = tf.reshape(
        pool,
        [pool_shape[0], pool_shape[1] * pool_shape[2] * pool_shape[3]])
    # Fully connected layer. Note that the '+' operation automatically
    # broadcasts the biases.
    hidden = tf.nn.relu(tf.matmul(reshape, fc1_weights) + fc1_biases)
    # Add a 50% dropout during training only. Dropout also scales
    # activations such that no rescaling is needed at evaluation time.
    if train:
      hidden = tf.nn.dropout(hidden, 0.5, seed=SEED)
    return tf.matmul(hidden, fc2_weights) + fc2_biases

  # Training computation: logits + cross-entropy loss.
  logits = model(train_data_node, True)
  cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
      logits, train_labels_node)
  # cross_entropy = tf.Print(cross_entropy, [cross_entropy], 'crossE ')
  loss = tf.reduce_mean(cross_entropy)

  # L2 regularization for the fully connected parameters.
  regularizers = (tf.nn.l2_loss(fc1_weights) + tf.nn.l2_loss(fc1_biases) +
                  tf.nn.l2_loss(fc2_weights) + tf.nn.l2_loss(fc2_biases))
  # Add the regularization term to the loss.
  loss += 5e-4 * regularizers

  # Optimizer: set up a variable that's incremented once per batch and
  # controls the learning rate decay.
  batch = tf.Variable(0)
  # Decay once per epoch, using an exponential schedule starting at 0.01.
  learning_rate = tf.train.exponential_decay(
      0.01,                # Base learning rate.
      batch * BATCH_SIZE,  # Current index into the dataset.
      train_size,          # Decay step.
      0.95,                # Decay rate.
      staircase=True)
  # Use simple momentum for the optimization.
  optimizer = tf.train.MomentumOptimizer(learning_rate,
                                         0.9).minimize(loss,
                                                       global_step=batch)

  # Predictions for the current training minibatch.
  # logits = tf.Print(logits, [logits], 'logits: ')
  train_prediction = tf.nn.softmax(logits)

  # Predictions for the test and validation, which we'll compute less often.
  eval_prediction = tf.nn.softmax(model(eval_data))

  # Small utility function to evaluate a dataset by feeding batches of data to
  # {eval_data} and pulling the results from {eval_predictions}.
  # Saves memory and enables this to run on smaller GPUs.
  def eval_in_batches(data, sess):
    """Get all predictions for a dataset by running it in small batches."""
    size = data.shape[0]
    if size < EVAL_BATCH_SIZE:
      raise ValueError("batch size for evals larger than dataset: %d" % size)
    predictions = numpy.ndarray(shape=(size, NUM_LABELS), dtype=numpy.float32)
    for begin in xrange(0, size, EVAL_BATCH_SIZE):
      end = begin + EVAL_BATCH_SIZE
      if end <= size:
        predictions[begin:end, :] = sess.run(
            eval_prediction,
            feed_dict={eval_data: data[begin:end, ...]})
      else:
        batch_predictions = sess.run(
            eval_prediction,
            feed_dict={eval_data: data[-EVAL_BATCH_SIZE:, ...]})
        predictions[begin:, :] = batch_predictions[begin - size:, :]
    return predictions

  # Create a local session to run the training.
  start_time = time.time()
  saver = tf.train.Saver()

  with tf.Session() as sess:
    # Run all the initializers to prepare the trainable parameters.
    tf.initialize_all_variables().run()
    print('Initialized!')


    ##### Run only #####
    if FLAGS.run_only:
      print ('load checkpoint')
      saver.restore(sess, "conv_mnist_model.ckpt")

      eval_data = tf.placeholder(tf.float32, shape=(1, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))
      eval_prediction = tf.nn.softmax(model(eval_data))

      def detect_in_image(image, mult):
        (winW, winH) = (IMAGE_SIZE * mult, IMAGE_SIZE * mult)

        clone = image.copy()
        # handX1 = []; handY1 = []; posPreds1 = []; hand1_weights= []
        # handX2 = []; handY2 = []; posPreds2 = []

        # use step size 9 for drone
        counter = 0
        for (x, y, window) in sliding_window(image, stepSize=int(IMAGE_SIZE/2 * 0.8) * mult, windowSize=(winW, winH)):
          if window.shape[0] != winH or window.shape[1] != winW:
            continue
       
          if mult > 1: window = cv2.resize(window, (IMAGE_SIZE, IMAGE_SIZE)) # (40, 40) 

          data = numpy.asarray(window, numpy.float32)#.reshape(IMAGE_SIZE, IMAGE_SIZE, 3)
          data = (data - (PIXEL_DEPTH / 2.0)) / PIXEL_DEPTH

          predictions = sess.run(eval_prediction, feed_dict={eval_data: [data]})

          # for dev
          printPred = True
          minPred = 0.01

          if predictions[0].argmax(axis=0) == 1 and predictions[0][1] > minPred:
            cv2.rectangle(clone, (x, y), (x + winW, y + winH), (0, 0, 250), 1)
            if printPred: print(predictions[0])

          if predictions[0].argmax(axis=0) == 2 and predictions[0][1] > minPred:
            cv2.rectangle(clone, (x, y), (x + winW, y + winH), (0, 250, 0), 1)
            if printPred: print(predictions[0])

          if predictions[0].argmax(axis=0) == 2 and predictions[0][1] > minPred:
            cv2.rectangle(clone, (x, y), (x + winW, y + winH), (250, 0, 0), 1)
            if printPred: print(predictions[0])

          counter += 1
          if counter % 1000 == 0: print('processed ' + str(counter) + ' windows')
          if counter > 10*1000: break

        return clone
       


      image = cv2.imread(IMG_PATH)

      running = True
      while running:
        # start = time.time()
        processed_img = detect_in_image(image, 1)
        # end = time.time()
        # print (end - start)
        cv2.imwrite('output.jpeg', processed_img)

        small = cv2.resize(processed_img, (2000, 2000))
        cv2.imshow('satellite image', small)
        key = cv2.waitKey(3*60*1000)

        if key == ord('c') or key == 0x1b:
          print('stopping')
          running = False
          continue



    ### Train ###
    else:
      # Loop through training steps.
      for step in xrange(int(num_epochs * train_size) // BATCH_SIZE):
        # Compute the offset of the current minibatch in the data.
        # Note that we could use better randomization across epochs.
        offset = (step * BATCH_SIZE) % (train_size - BATCH_SIZE)
        batch_data = train_data[offset:(offset + BATCH_SIZE), ...]
        batch_labels = train_labels[offset:(offset + BATCH_SIZE)]
        # This dictionary maps the batch data (as a numpy array) to the
        # node in the graph it should be fed to.
        feed_dict = {train_data_node: batch_data,
                     train_labels_node: batch_labels}
        # Run the graph and fetch some of the nodes.
        _, l, lr, predictions = sess.run(
            [optimizer, loss, learning_rate, train_prediction],
            feed_dict=feed_dict)
        if step % EVAL_FREQUENCY == 0:
          elapsed_time = time.time() - start_time
          start_time = time.time()

          print('Step %d (epoch %.2f), %.1f ms' %
                (step, float(step) * BATCH_SIZE / train_size,
                 1000 * elapsed_time / EVAL_FREQUENCY))
          print('Minibatch loss: %.3f, learning rate: %.6f' % (l, lr))
          print('Minibatch error: %.1f%%' % error_rate(predictions, batch_labels))
          print('Validation error: %.1f%%' % error_rate(
              eval_in_batches(validation_data, sess), validation_labels))
          sys.stdout.flush()
      # Finally print the result!
      test_error = error_rate(eval_in_batches(test_data, sess), test_labels)
      print('Test error: %.1f%%' % test_error)

      save_path = saver.save(sess, "conv_mnist_model.ckpt")
      print("Model saved in file: %s" % save_path)

      if FLAGS.self_test:
        print('test_error', test_error)
        assert test_error == 0.0, 'expected 0.0 test_error, got %.2f' % (
            test_error,)

      

if __name__ == '__main__':
  tf.app.run()
