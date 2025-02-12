import enum 
import sqlite3
import sys
import os

#import common utils
internalbindir = os.path.dirname(os.path.abspath(__file__))
patoolPath = internalbindir + "/../common"
sys.path.append(patoolPath)
import common
#from  ..common import *

from . import HTMLGenerator
#########################################################################################################
class Stats:
  def __init__(self):
    self.totalCount = 0
    self.totalSize = 0
    self.startTime = common.mstime()
    self.filesCount = 0
    self.filesSize = 0
#########################################################################################################
class Formats(enum.Enum):
  json = 0
  stdout = 1
  html = 2
  sqlite = 3
  invalid = 4

  @staticmethod
  def parce(value) -> enum.Enum:
      if value == None:
        return Formats.invalid
      for m, mm in Formats.__members__.items():
        if m == value.lower():
          return mm
      return Formats.invalid

  @staticmethod
  def ext(val) -> str:
      extentions = {
        Formats.json: ".json",
        Formats.stdout: ".txt",
        Formats.html: ".htm",
        Formats.sqlite: ".sqlite"
      }
      if val != Formats.invalid:
        return extentions[val]
      print("invalid format" + val.name)
      return ""
#########################################################################################################
class DBEngine:
  def __init__(self):
    self.connection = None
    self.cursor = None
    self.path = ""

  def open(self, path:str):
    self.path = path
    self.connection = sqlite3.connect(path)
    self.cursor = self.connection.cursor()
    self.makeDb()

  def checkDb(self):
    if not self.cursor or not self.connection:
      raise Exception('dbEngine', 'not opened')

  def makeDb(self):
    self.checkDb()
    self.cursor.execute("""
      CREATE TABLE 'files' (
        'path' TEXT NOT NULL UNIQUE,
        'hash'  TEXT NOT NULL,
        'size' INTEGER NOT NULL);
    """)
    self.cursor.execute("""
      CREATE TABLE 'result' (
      'groupId' TEXT NOT NULL,
      'path'  TEXT NOT NULL,
      'size'  INTEGER NOT NULL);
    """)

    self.cursor.execute("""CREATE INDEX 'hash_i' ON 'files' ('hash');""")
    self.connection.commit()

  def close(self):
    self.cursor = None
    if self.connection:
      self.connection.close()
    self.connection = None

  def notUniqueHashes(self):
    self.checkDb()
    rc = []
    for row in self.cursor.execute("SELECT DISTINCT hash FROM files GROUP BY hash HAVING COUNT(*) > 1"):
      rc.append(row[0])
    return rc

  def filesByHash(self, hash: str):
    self.checkDb()
    rc = []
    for row in self.cursor.execute("SELECT path, size FROM files  WHERE hash='" + hash + "';"):
      rc.append((row[0], row[1]))
    return rc

  def writeFileInfo(self, path: str, hash: str, size: int):
    self.checkDb()
    self.cursor.execute("INSERT INTO files VALUES (?,?,?)", (path, hash, size))
    self.connection.commit()

  def writeGroupRecord(self, hash: str, fname: str, size: int):
    self.checkDb()
    self.cursor.execute("INSERT INTO result VALUES (?,?,?)", (hash, fname, size))
    self.connection.commit()