#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Wed Oct  3 10:31:51 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

class File:
  """This class defines the minimum interface of a file information that needs to be exported"""

  # The **unique** id of the file
  id = None
  # The id of the client that is attached to the file
  client_id = None
  # The **relative** path of the file according to the base directory of the database.
  path = None



class Database:
  """This class represents the basic API for database access.
  Please use this class as a base class for your database access classes.
  Do not forget to call the constructor of this base class in your derived class."""

  def __init__(self,
               name,
               original_directory,
               original_extension,
               annotation_directory = None,
               annotation_extension = '.pos',
               annotation_type = None,
               protocol = 'Default'
               ):

    self.name = name
    self.original_directory = original_directory
    self.original_extension = original_extension
    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension
    self.annotation_type = annotation_type
    self.protocol = protocol


  ###########################################################################
  ### Helper functions that you might want to use in derived classes
  ###########################################################################
  def sort(self, files):
    """Returns a sorted version of the given list of File's (or other structures that define an 'id' data member).
    The files will be sorted according to their id."""
    return sorted(files, cmp=lambda x,y: cmp(x.id, y.id))

  def arrange_by_client(self, files):
    """Arranges the given list of files by client id.
    This function returns a list of lists of File's."""
    client_files = {}
    for file in files:
      if file.client_id not in client_files:
        client_files[file.client_id] = []
      client_files[file.client_id].append(file)

    files_by_clients = []
    for client in sorted(client_files.keys()):
      files_by_clients.append(client_files[client])
    return files_by_clients



  ###########################################################################
  ### Interface functions that you need to implement in your class.
  ###########################################################################

  def all_files(self):
    """Returns all files of the database"""
    raise NotImplementedError("Please implement this function in derived classes")


  def training_files(self, step, arrange_by_client = False):
    """Returns all training File objects for the given step (might be 'train_extractor', 'train_projector', 'train_enroller'), and arranges them by client, if desired"""
    raise NotImplementedError("Please implement this function in derived classes")


  def model_ids(self, group = 'dev'):
    """Returns a list of model ids for the given group"""
    raise NotImplementedError("Please implement this function in derived classes")


  def client_id_from_model_id(self, model_id):
    """Returns the client id for the given model id"""
    raise NotImplementedError("Please implement this function in derived classes")


  def enroll_files(self, model_id, group = 'dev'):
    """Returns a list of enrollment File objects for the given model id and the given group"""
    raise NotImplementedError("Please implement this function in derived classes")


  def probe_files(self, model_id = None, group = 'dev'):
    """Returns a list of probe File object in a specific format that should be compared with the model belonging to the given model id of the specified group"""
    raise NotImplementedError("Please implement this function in derived classes")



class DatabaseZT (Database):
  """This class defines additional API functions that are required to compute ZT score normalization.
  During construction, please call the constructor of the base class 'Database' directly."""

  def t_model_ids(self, group = 'dev'):
    """Returns a list of T-Norm model ids for the given group"""
    raise NotImplementedError("Please implement this function in derived classes")

  def t_enroll_files(self, model_id, group = 'dev'):
    """Returns a list of enrollment files for the given T-Norm model id and the given group"""
    raise NotImplementedError("Please implement this function in derived classes")

  def z_probe_files(self, model_id = None, group = 'dev'):
    """Returns a list of Z-probe objects in a specific format that should be compared with the model belonging to the given model id of the specified group"""
    raise NotImplementedError("Please implement this function in derived classes")