# Copyright 2019 JamesZBL

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from config import *
from common import find_root_by_file_name

def find_plugin_artifacts_from_lines(lines):
  version = None
  strategy = { 
    3: find_in_3_x,
    2: find_in_2_x
  }
  dependency_version_line_patter = re.compile(r'.*maven-dependency-plugin\:(((([0-9])\.)+)[0-9])\:resolve-plugins.*\@.*$')
  for line in lines:
    match = re.search(dependency_version_line_patter, line)
    if match is not None:
      start, end = match.regs[4]
      version = int(line[start:end])
      try:
        return strategy[version](lines)
      except KeyError:
        not_supported_version(version)
  return []

def not_supported_version(v):
  print('Version {} is not supported.'.format(v))

def find_in_3_x(lines):
  plugin_jar_dep_pattern = re.compile(r'\[INFO\]\s+(.*\:.*\:jar\:.*)$')
  result = []
  for line in lines:
    match = re.search(plugin_jar_dep_pattern, line)
    if match:
      regs = match.regs
      start, end = regs[len(regs) - 1]
      artifact = line[start:end] + ':runtime'
      result.append(artifact)
  return result

def find_in_2_x(lines):
  jars = []
  # Plugin Resolved: jooq-codegen-maven-3.11.12.jar
  # Plugin Dependency Resolved: jooq-codegen-3.11.12.jar
  jar_patterns = [r'Plugin Resolved\:\s(.*\.jar)', r'Plugin Dependency Resolved\:\s(.*\.jar)']
  for line in lines:
    for pattern in jar_patterns:
      match = re.search(pattern, line)
      if match is not None:
        start, end = match.regs[1]
        jar = line[start:end]
        jars.append(jar)
  jar_dirs = find_root_by_file_name(REPOSITORY_HOME, jars, reg=False)
  return map(artifacts_from_jar_dirs ,jar_dirs)

def artifacts_from_jar_dirs(d):
  # fixme group 目录是多级，不能按 / 划分 group，按倒数第 n 个划分
  ss = str(d).split('/')
  sections = [ss[0],ss[1],'jar',ss[2],'COMPILE']
  return ':'.join(sections)