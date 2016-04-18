# Copyright (C) 2014 Jonathon Ogden < jeog.dev@gmail.com > 

import sys as _sys

if _sys.version_info.major < 3:
  _sys.stderr.write("fatal: tosdb is built for python3!\n")
  exit(1)

from distutils.core import setup as _setup
from io import StringIO as _StringIO
from re import match as _match, search as _search

NAME = 'tosdb'
VERSION = '0.3'
DESCRIPTION = "Python Front-End / Wrapper for TOSDataBridge"
AUTHOR = "Jonathon Ogden"
AUTHOR_EMAIL = "jeog.dev@gmail.com"
PACKAGES = ['tosdb', 'tosdb/cli_scripts']  

_AUTO_EXT = '_tosdb' 
_HEADER_PATH = '../include/tos_databridge.h'
_OUTPUT_PATH = NAME + '/' + _AUTO_EXT + '.py'

#string that should bookmark the topics in Topic_Enum_Wrapper::TOPICS<T> 
_MAGIC_TOPIC_STR = 'ksxaw9834hr84hf;esij?><'

#regex for finding our header #define consts 
_REGEX_HEADER_CONST = "#define[\s]+([\w]+)[\s]+.*?([\d][\w]*)" 

#adjust for topics we had to permute to form valid enum vars
TOPIC_VAL_REPLACE = {'HIGH52':'52HIGH','LOW52':'52LOW'}

class TOSDB_SetupError(Exception):
  def __init__(self,*msgs):
    super().__init__(*msgs)  

 
def _pull_consts_from_header(verbose=True):
  consts = {}
  lineno = 0
  with open(_HEADER_PATH,'r') as hfile:    
    hfile.seek(0)    
    for hline in hfile:
      lineno += 1
      try:
        groups = _match(_REGEX_HEADER_CONST,hline).groups()  
      except AttributeError:
        continue    
      try:
        g0, g1 = groups
        val = str(hex(int(g1,16)) if 'x' in g1 else int(g1))
        consts[g0] = val
        if verbose:
          print('',_HEADER_PATH + ':' + str(lineno)+ ': '+ groups[0], val)
      except ValueError:
        raise TOSDB_SetupError("invalid header const value", str(g0))   
      except Exception as e:
        raise TOSDB_SetupError("couldn't extract const from regex match", e.args)   
  return consts     

def _pull_topics_from_header(verbose=True):
  read_flag = False
  topics = []
  lineno = 0
  with open(_HEADER_PATH,'r') as hfile:
    for hline in hfile:
      lineno += 1
      if read_flag:      
        if _MAGIC_TOPIC_STR in hline:
          read_flag = False
          if verbose:
            print('',_HEADER_PATH + ":" + str(lineno+1) + ": topic enum END")  
          break         
        try:
          t = hline.split('=')[0].strip()
        except Exception as e:
          raise TOSDB_SetupError("failed to parse topic enum line", e.args)
        if(not _search('[\W]',t)):
          topics.append(t)         
      else:
        if _MAGIC_TOPIC_STR in hline:
          read_flag = True
          if verbose:
            print('',_HEADER_PATH + ":" + str(lineno-1) + ": topic enum BEGIN") 
  return topics

# build a tosdb/_tosdb.py file from the header extracted vals
def _create__tosdb(consts, topics): 
  topic_dict = dict(zip(topics,topics))
  for key in topic_dict:
    if key in TOPIC_VAL_REPLACE: # don't just .update, check all are valid
      topic_dict[key] = TOPIC_VAL_REPLACE[key]
  with open(_OUTPUT_PATH,'w') as pfile:
    pfile.write('# AUTO-GENERATED BY tosdb/setup.py\n')
    pfile.write('# DO NOT EDIT!\n\n')
    for c in consts:
      pfile.write(c.replace('TOSDB_','',1) + ' = ' + consts[c] + '\n')      
    pfile.write('\n\n')
    pfile.write('from tosdb.meta_enum import MetaEnum\n')
    pfile.write('class TOPICS(metaclass=MetaEnum):\n')
    pfile.write('  fields = ' + str(topic_dict) + '\n')
     

if __name__ == '__main__':           
  sio = _StringIO()
  serr = _sys.stderr
  _sys.stderr = sio
  try:    
    print("pulling constants from " + _HEADER_PATH)
    consts = _pull_consts_from_header()
    print("pulling topic enum from " + _HEADER_PATH) 
    topics = _pull_topics_from_header()
    print('auto-generating ' + _OUTPUT_PATH)
    _create__tosdb(consts, topics)
    print(' checking ' + _OUTPUT_PATH)
    try:
      exec("from " + NAME + " import " + _AUTO_EXT)
    except ImportError as ie:
      print('  fatal: auto-generated ' + _OUTPUT_PATH + ' could not be imported !')
      print('  fatal: ' + ie.args[0])
      exit(1)
    print('  success!')
    _setup(name=NAME, version=VERSION, description=DESCRIPTION, 
           author=AUTHOR, author_email=AUTHOR_EMAIL, packages=PACKAGES)
  finally:
    _sys.stderr = serr    
  if sio.getvalue(): 
    print( '\n', "+ Operation 'completed' with errors:\n")
    print(sio.getvalue())


