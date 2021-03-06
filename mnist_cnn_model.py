"""
MNIST handwritten digit classification with a convolutional neural network.

"""
import tensorflow as tf

def weight(shape):
    init = tf.truncated_normal_initializer(stddev=0.1)
    return tf.get_variable('W', shape, initializer=init)

def bias(shape):
    init = tf.constant_initializer(0.1)
    return tf.get_variable('b', shape, initializer=init)

def conv(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1], padding='SAME')

def inference(x, keep_prob):
    # Reshape input
    x = tf.reshape(x, [-1, 28, 28, 1])

    # First convolutional + pooling layer
    with tf.variable_scope('conv1'):
        W = weight([5, 5, 1, 32])
        b = bias([32])
    x = conv(x, W) + b
    x = tf.nn.relu(x)
    x = max_pool(x) # 14x14

    # Second convolutional + pooling layer
    with tf.variable_scope('conv2'):
        W = weight([5, 5, 32, 64])
        b = bias([64])
    x = conv(x, W) + b
    x = tf.nn.relu(x)
    x = max_pool(x) # 7x7

    # Flatten feature planes
    x = tf.reshape(x, [-1, 7*7*64])

    # Fully connected layer
    with tf.variable_scope('fc'):
        W = weight([7*7*64, 1024])
        b = bias([1024])
    x = tf.matmul(x, W) + b
    x = tf.nn.relu(x)

    # Dropout
    x = tf.nn.dropout(x, keep_prob)

    # Softmax layer
    with tf.variable_scope('softmax'):
        W = weight([1024, 10])
        b = bias([10])
    x = tf.matmul(x, W) + b

    return x

class Model(object):
    def __init__(self, learning_rate=None):
        # Seed the TF random number generator for reproducible initialization
        tf.set_random_seed(0)

        # For feeding in data
        self.x = x = tf.placeholder(tf.float32, [None, 784])
        self.y = y = tf.placeholder(tf.float32, [None, 10])

        # Dropout
        self.keep_prob = tf.placeholder(tf.float32)

        # Logits
        logits = inference(x, self.keep_prob)

        # Prediction
        predict_op  = tf.argmax(logits, 1)
        correct_op  = tf.equal(predict_op, tf.argmax(y, 1))
        accuracy_op = tf.reduce_mean(tf.cast(correct_op, tf.float32))
        self.predict_op  = predict_op
        self.accuracy_op = accuracy_op

        if learning_rate is None:
            return

        #-----------------------------------------------------------------------
        # For training only
        #-----------------------------------------------------------------------

        # Loss function
        loss = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits)
        loss = tf.reduce_mean(loss)

        # Learning rate
        learning_rate = 1e-4

        # Optimizer
        optimizer = tf.train.AdamOptimizer(learning_rate)
        self.train_op = optimizer.minimize(loss)

        # For TensorBoard
        tf.summary.scalar('loss', loss)

    def predict(self, sess, images):
        feed_dict = {self.x: images, self.keep_prob: 1.0}
        return sess.run(self.predict_op, feed_dict)
