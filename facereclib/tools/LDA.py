#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <Manuel.Guenther@idiap.ch>

import bob
import numpy

from .Tool import Tool
from .. import utils

class LDA (Tool):
  """Tool for computing linear discriminant analysis (so-called Fisher faces)"""

  def __init__(
      self,
      lda_subspace_dimension = None, # if set, the LDA subspace will be truncated to the given number of dimensions; by default it is limited to the number of classes in the training set
      pca_subspace_dimension = None, # if set, a PCA subspace truncation is performed before applying LDA; might be integral or float
      distance_function = bob.math.euclidean_distance,
      is_distance_function = True,
      multiple_model_scoring = 'average',
      multiple_probe_scoring = 'average'
  ):
    """Initializes the LDA tool with the given configuration"""

    # call base class constructor and register that the LDA tool performs projection and need the training features split by client
    Tool.__init__(
        self,
        performs_projection = True,
        split_training_features_by_client = True,
        multiple_model_scoring = multiple_model_scoring,
        multiple_probe_scoring = multiple_probe_scoring
    )

    # copy information
    self.m_pca_subspace = pca_subspace_dimension
    self.m_lda_subspace = lda_subspace_dimension
    if self.m_pca_subspace and isinstance(self.m_pca_subspace, int) and self.m_lda_subspace and self.m_pca_subspace < self.m_lda_subspace:
      raise ValueError("The LDA subspace is larger than the PCA subspace size. This won't work properly. Please check your setup!")

    self.m_machine = None
    self.m_distance_function = distance_function
    self.m_factor = -1 if is_distance_function else 1.


  def __read_data__(self, training_files):
    data = []
    for client_files in training_files:
      # at least two files per client are required!
      if len(client_files) < 2:
        utils.warn("Skipping one client since the number of client files is only %d" %len(client_files))
        continue
      data.append(numpy.vstack([feature.flatten() for feature in client_files]))

    # Returns the list of lists of arrays
    return data

  def __train_pca__(self, training_set):
    """Trains and returns a LinearMachine that is trained using PCA"""
    data_list = [feature for client in training_set for feature in client]
    data = numpy.vstack(data_list)

    utils.info("  -> Training LinearMachine using PCA (SVD)")
    t = bob.trainer.SVDPCATrainer()
    machine, eigen_values = t.train(data)

    if isinstance(self.m_pca_subspace, float):
      cummulated = numpy.cumsum(eigen_values) / numpy.sum(eigen_values)
      for index in range(len(cummulated)):
        if cummulated[index] > self.m_pca_subspace:
          self.m_pca_subspace = index
          break
      self.m_pca_subspace = index

    if self.m_lda_subspace and self.m_pca_subspace <= self.m_lda_subspace:
      utils.warn("  ... Extending the PCA subspace dimension from %d to %d" % (self.m_pca_subspace, self.m_lda_subspace + 1))
      self.m_pca_subspace = self.m_lda_subspace + 1
    else:
      utils.info("  ... Limiting PCA subspace to %d dimensions" % self.m_pca_subspace)

    # limit number of pcs
    machine.resize(machine.shape[0], self.m_pca_subspace)
    return machine


  def __perform_pca__(self, machine, training_set):
    """Perform PCA on data"""
    data = []
    for client_features in training_set:
      data.append(numpy.vstack([machine(feature) for feature in client_features]))
    return data


  def train_projector(self, training_features, projector_file):
    """Generates the LDA projection matrix from the given features (that are sorted by identity)"""
    # Initializes an array for the data
    data = self.__read_data__(training_features)

    if self.m_pca_subspace:
      pca_machine = self.__train_pca__(data)
      data = self.__perform_pca__(pca_machine, data)

    utils.info("  -> Training LinearMachine using LDA")
    t = bob.trainer.FisherLDATrainer(self.m_lda_subspace if self.m_lda_subspace else 0)
    self.m_machine, _eigen_values = t.train(data)

    if self.m_pca_subspace:
      # compute combined PCA/LDA projection matrix
      combined_matrix = numpy.dot(pca_machine.weights, self.m_machine.weights)
      # set new weight matrix (and new mean vector) of novel machine
      self.m_machine = bob.machine.LinearMachine(combined_matrix)
      self.m_machine.input_subtract = pca_machine.input_subtract

    self.m_machine.save(bob.io.HDF5File(projector_file, "w"))


  def load_projector(self, projector_file):
    """Reads the UBM model from file"""
    # read PCA projector
    self.m_machine = bob.machine.LinearMachine(bob.io.HDF5File(projector_file))
    # Allocates an array for the projected data
    self.m_projected_feature = numpy.ndarray(self.m_machine.shape[1], numpy.float64)

  def project(self, feature):
    """Projects the data using the stored covariance matrix"""
    # Projects the data
    self.m_machine(feature, self.m_projected_feature)
    # return the projected data
    return self.m_projected_feature

  def enroll(self, enroll_features):
    """Enrolls the model by computing an average of the given input vectors"""
    assert len(enroll_features)
    # just store all the features
    model = numpy.zeros((len(enroll_features), enroll_features[0].shape[0]), numpy.float64)
    for n, feature in enumerate(enroll_features):
      model[n,:] += feature[:]

    # return enrolled model
    return model


  def score(self, model, probe):
    """Computes the distance of the model to the probe using the distance function taken from the config file"""
    # return the negative distance (as a similarity measure)
    if len(model.shape) == 2:
      # we have multiple models, so we use the multiple model scoring
      return self.score_for_multiple_models(model, probe)
    else:
      # single model, single probe (multiple probes have already been handled)
      return self.m_factor * self.m_distance_function(model, probe)
