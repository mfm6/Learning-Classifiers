# Run some setup code for this notebook.

import matplotlib.pyplot as plt
import numpy as np

from sklearn import neighbors
from cs231n.data_utils import load_CIFAR10
from cs231n.classifiers import KNearestNeighbor

# Load the raw CIFAR-10 data.
cifar10_dir = 'cs231n/datasets/cifar-10-batches-py'

X_train, y_train, X_test, y_test = load_CIFAR10(cifar10_dir)

# Flags to run different parts
visualize_images = True
compare_loop_vs_vect = True
run_speed_test = True
run_cross_validation = True

# As a sanity check, we print out the size of the training and test data.
print('Training data shape: ', X_train.shape)
print('Training labels shape: ', y_train.shape)
print('Test data shape: ', X_test.shape)
print('Test labels shape: ', y_test.shape)

# Visualize some examples from the dataset.
# We show a few examples of training images from each class.
if visualize_images:
    classes = ['plane', 'car', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']
    num_classes = len(classes)
    samples_per_class = 20
    for y, cls in enumerate(classes):
        idxs = np.flatnonzero(y_train == y)
        idxs = np.random.choice(idxs, samples_per_class, replace=False)
        for i, idx in enumerate(idxs):
            plt_idx = i * num_classes + y + 1
            plt.subplot(samples_per_class, num_classes, plt_idx)
            plt.imshow(X_train[idx].astype('uint8'))
            plt.axis('off')
            if i == 0:
                plt.title(cls)
    plt.show()

# Subsample the data for more efficient code execution in this exercise
num_training = 5000
mask = list(range(num_training))
X_train = X_train[mask]
y_train = y_train[mask]

num_test = 500
mask = list(range(num_test))
X_test = X_test[mask]
y_test = y_test[mask]

# Reshape the image data into rows
X_train = np.reshape(X_train, (X_train.shape[0], -1))
X_test = np.reshape(X_test, (X_test.shape[0], -1))
print(X_train.shape, X_test.shape)

# Create a kNN classifier instance.
# Remember that training a kNN classifier is a noop:
# the Classifier simply remembers the data and does no further processing
classifier = KNearestNeighbor()
classifier.train(X_train, y_train)
dists = classifier.compute_distances_two_loops(X_test)
y_test_pred = classifier.predict_labels(dists, k=5)

# Compute and print the fraction of correctly predicted examples
num_correct = np.sum(y_test_pred == y_test)
accuracy = float(num_correct) / num_test
print('Got %d / %d correct => accuracy: %f' % (num_correct, num_test, accuracy))

#############################################################################
# For comparison purposes
# Set k=5
clf = neighbors.KNeighborsClassifier(10)
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

# Compute and print the fraction of correctly predicted examples
num_correct = np.sum(pred == y_test)
accuracy = float(num_correct) / num_test
print('Sklearn.KNeighborsClassifier Got %d / %d correct => \
      accuracy: %f' % (num_correct, num_test, accuracy))
#############################################################################

# Now lets speed up distance matrix computation by using partial vectorization
# with one loop. Implement the function compute_distances_one_loop and run the
# code below:
if compare_loop_vs_vect:
    dists_one = classifier.compute_distances_one_loop(X_test)

    # To ensure that our vectorized implementation is correct, we make sure
    # that it agrees with the naive implementation. There are many ways to
    # decide whether two matrices are similar; one of the simplest is the
    # Frobenius norm. The Frobenius norm of two matrices is the square root
    # of the squared sum of differences of all elements; in other words,
    # reshape the matrices into vectors and compute the Euclidean distance
    # between them.
    difference = np.linalg.norm(dists - dists_one, ord='fro')
    print('Difference was: %f' % (difference, ))
    if difference < 0.001:
        print('Good! The distance matrices are the same')
    else:
        print('Uh-oh! The distance matrices are different')

    dists_two = classifier.compute_distances_no_loops(X_test)

    # To ensure that our vectorized implementation is correct, we make sure
    # that it agrees with the naive implementation. There are many ways to
    # decide whether two matrices are similar; one of the simplest is the
    # Frobenius norm. The Frobenius norm of two matrices is the square root of
    # the squared sum of differences of all elements; in other words, reshape
    # the matrices into vectors and compute the Euclidean distance between them.
    difference = np.linalg.norm(dists - dists_two, ord='fro')
    print('Difference was: %f' % (difference, ))
    if difference < 0.001:
        print('Good! The distance matrices are the same')
    else:
        print('Uh-oh! The distance matrices are different')

#############################################################################
# Speed-test. Let's compare how fast the implementations are
if run_speed_test:

    def time_function(f, *args):
        """
        Call a function f with args and return the time (in seconds) that it
        took to execute.
        """
        import time
        tic = time.time()
        f(*args)
        toc = time.time()
        return toc - tic

    two_loop_time = time_function(classifier.compute_distances_two_loops,
                                  X_test)
    print('Two loop version took %f seconds' % two_loop_time)

    one_loop_time = time_function(classifier.compute_distances_one_loop, X_test)
    print('One loop version took %f seconds' % one_loop_time)

    no_loop_time = time_function(classifier.compute_distances_no_loops, X_test)
    print('No loop version took %f seconds' % no_loop_time)
#############################################################################


#############################################################################
# Cross-validation
if run_cross_validation:
    num_folds = 5
    k_choices = [1, 3, 5, 8, 10, 12, 15, 20, 50, 100]

    X_train_folds = []
    y_train_folds = []
    # Split up the training data into folds.
    X_train_folds = np.array_split(X_train, num_folds)
    y_train_folds = np.array_split(y_train, num_folds)

    # A dictionary holding the accuracies for different values of k that we find
    # when running cross-validation. After running cross-validation,
    # k_to_accuracies[k] should be a list of length num_folds giving the
    # different accuracy values that we found when using that value of k.
    k_to_accuracies = {}

    ############################################################################
    # Perform k-fold cross validation to find the best value of k. For each
    # possible value of k, run the k-nearest-neighbor algorithm num_folds times,
    # where in each case you use all but one of the folds as training data and
    # the last fold as a validation set. Store the accuracies for all fold and
    # all values of k in the k_to_accuracies dictionary.
    ############################################################################
    num_test = int(num_training / 5)
    classifier = KNearestNeighbor()
    for k in k_choices:
        for folds in range(num_folds):
            classifier = KNearestNeighbor()
            X_train_fold = X_train_folds[0:folds] + X_train_folds[folds+1:]
            X_train_fold = np.asarray(X_train_fold).reshape(-1, 3072)
            y_train_fold = y_train_folds[0:folds] + y_train_folds[folds+1:]
            y_train_fold = np.asarray(y_train_fold).reshape(-1)

            classifier.train(X_train_fold,
                             y_train_fold)
            x_test = np.asarray(X_train_folds[folds])
            y_test = np.asarray(y_train_folds[folds])
            dists = classifier.compute_distances_no_loops(x_test)
            y_test_pred = classifier.predict_labels(dists, k=k)

            # Compute and print the fraction of correctly predicted examples
            num_correct = np.sum(y_test_pred == y_test)
            accuracy = float(num_correct) / num_test
            print('Got %d / %d correct => accuracy: %f' %
                  (num_correct, num_test, accuracy))
            k_to_accuracies[k] = k_to_accuracies.get(k, []) + [accuracy]

    # Print out the computed accuracies
    for k in sorted(k_to_accuracies):
        for accuracy in k_to_accuracies[k]:
            print('k = %d, accuracy = %f' % (k, accuracy))

    # plot the raw observations
    for k in k_choices:
        accuracies = k_to_accuracies[k]
        plt.scatter([k] * len(accuracies), accuracies)

    # plot the trend line with error bars that correspond to standard deviation
    accuracies_mean = \
        np.array([np.mean(v) for k, v in sorted(k_to_accuracies.items())])
    accuracies_std = \
        np.array([np.std(v) for k, v in sorted(k_to_accuracies.items())])
    plt.errorbar(k_choices, accuracies_mean, yerr=accuracies_std)
    plt.title('Cross-validation on k')
    plt.xlabel('k')
    plt.ylabel('Cross-validation accuracy')
    plt.show()


# Based on the cross-validation results above, choose the best value for k,
# retrain the classifier using all the training data, and test it on the
# test data.
# You should be able to get above 28% accuracy on the test data.
best_k = 10

classifier = KNearestNeighbor()
classifier.train(X_train, y_train)
y_test_pred = classifier.predict(X_test, k=best_k)

# Compute and display the accuracy
num_correct = np.sum(y_test_pred == y_test)
accuracy = float(num_correct) / num_test
print('With best K Got %d / %d correct => accuracy: %f' % (num_correct,
                                                           num_test, accuracy))
