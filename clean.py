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

from pathlib import Path
from functools import reduce
import os, subprocess, re, shutil
from common import find_root_by_file_name

PROJECTS_HOME = '/Users/james/r'
MAVEN_HOME = Path.home().joinpath('.m2')
REPOSITORY_HOME = '{}/repository'.format(MAVEN_HOME)
INCLUDES = []

def artifact_relative_dirs(artifact_coordinates):
  result = []
  for artifact in artifact_coordinates:
    sections = artifact.split(':')
    if 5 < len(sections):
      continue
    group_id, artifact_id, package, version, scope = tuple(sections)
    group_id_dir = group_id.replace('.', '/')
    artifact_dir = '{}/{}/{}'.format(group_id_dir, artifact_id, version)
    result.append(artifact_dir)
  return result

def find_in_use_artifacts():
  project_dirs = find_root_by_file_name(PROJECTS_HOME, [r'pom.xml'], 'parent')
  result = []
  for project_home in project_dirs:
    if 0 < len(INCLUDES) and project_home not in INCLUDES:
      continue
    print('Scanning project: {}...'.format(project_home))
    absolute_path = str(Path(PROJECTS_HOME).joinpath(project_home))
    os.chdir(absolute_path)
    process = subprocess.Popen('mvn dependency:tree', stdout=subprocess.PIPE, shell=True)
    out = process.communicate()
    out = str(out)
    lines = out.split('\\n')
    artifacts = find_dependencies_from_lines(lines)
    result.extend(artifacts)
  result = list(set(result))
  result.sort()
  return result

def find_dependencies_from_lines(lines):
  tree_title_patter = re.compile(r'maven-dependency-plugin\:.*\:tree.* @\s.*')
  dependency_patter = re.compile(r'(\|\s)?(\+|\\)-\s(.*\..*\:.*\:.*\:.*\:(compile|provided|test|runtime|system|import))')
  title_found = False
  dependency_found = False
  artifacs = []
  for line in lines:
    title_match = re.search(tree_title_patter, line)
    if title_match is not None:
      title_found = True
    dependency_match = re.search(dependency_patter, line)
    if dependency_match is not None:
      dependency_found = True
      regs = dependency_match.regs
      start, end = regs[len(regs)-2]
      artifacs.append(line[start:end])
  if not title_found:
    print('Maven installed uncorrectly.')
  if title_found and not dependency_found:
    print('No dependency found.')
  return artifacs

def find_plugin_artifacts():
  project_dirs = find_root_by_file_name(PROJECTS_HOME, [r'pom.xml'], 'parent')
  result = []
  for project_home in project_dirs:
    if 0 < len(INCLUDES) and project_home not in INCLUDES:
      continue
    print('Searching plugins in project: {}...'.format(project_home))
    absolute_path = str(Path(PROJECTS_HOME).joinpath(project_home))
    os.chdir(absolute_path)
    process = subprocess.Popen('mvn dependency:resolve-plugins', stdout=subprocess.PIPE, shell=True)
    out = process.communicate()
    out = str(out)
    lines = out.split('\\n')
    jars = find_plugin_artifacts_from_lines(lines)
    result.extend(jars)
  result = list(set(result))
  result.sort()
  return result

def find_plugin_artifacts_from_lines(lines):
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

def find_existing_artifac_dirs():
  return find_root_by_file_name(REPOSITORY_HOME, [r'^.*\.pom$',r'^.*\.jar$'], 'child')

def in_use_artifact_dirs():
  result = []
  artifacts = find_in_use_artifacts()
  artifact_dirs = artifact_relative_dirs(artifacts)
  result.extend(artifact_dirs)
  plugins = find_plugin_artifacts()
  plugin_dirs = artifact_relative_dirs(plugins)
  result.extend(plugin_dirs)
  return result

def ask_and_print_dirs(dirs, name):
  _in = input('Show all {} {}? [y/N]'.format(len(dirs), name))
  if 'y' == _in:
    for d in dirs:
      print(d)

def ask_and_delete_dirs(dirs, name):
  _in = input('Delete all {} {}? [y/N]'.format(len(dirs), name))
  if 'y' == _in:
    for d in dirs:
      absolute_path = str(Path(REPOSITORY_HOME).joinpath(d))
      shutil.rmtree(absolute_path)

existing_artifact_dirs = find_existing_artifac_dirs()
in_use_artifact_dirs = in_use_artifact_dirs()

not_in_use_artifact_dirs = []
for artifact_dir in existing_artifact_dirs:
  if artifact_dir not in in_use_artifact_dirs:
    not_in_use_artifact_dirs.append(artifact_dir)

ask_and_print_dirs(existing_artifact_dirs, 'existing dependencies')
ask_and_print_dirs(in_use_artifact_dirs, 'dependencies in use')
ask_and_print_dirs(not_in_use_artifact_dirs, 'dependencies not in use')
ask_and_delete_dirs(not_in_use_artifact_dirs, 'redundant dependencies')