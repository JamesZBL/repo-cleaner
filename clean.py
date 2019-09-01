from pathlib import Path
from functools import reduce
import os, subprocess, re

PROJECTS_HOME = '/Users/james/r'
MAVEN_HOME = Path.home().joinpath('.m2')
REPOSITORY_HOME = '{}/repository'.format(MAVEN_HOME)
# REPOSITORY_HOME = '.tmp'

def artifact_relative_dirs(artifact_coordinates):
  result = []
  for artifact in artifacts:
    elements = artifact.split(':')
    artifact_id = elements[0]
    version = elements[1]
    artifact_id_dir = artifact_id.replace('.', '/')
    artifact_dir = '{}/{}'.format(artifact_id_dir, version)
    result.append(artifact_dir)
  return result

def find_root_by_file_name(base_dir, file_name_section, reserve_mode='child'):
  result = []
  for root, folders, files in os.walk(base_dir):
    for file in files:
      if -1 < file.find(file_name_section):
        relative_path = str(Path(root).relative_to(base_dir))
        result.append(relative_path)
  result = list(set(result))
  result.sort()
  if 'child' == reserve_mode:
    for d in result:
      for dd in result:
        if d != dd and d.startswith(dd):
          result.remove(dd)
  elif 'parent' == reserve_mode:
    trash = []
    for d in result:
      for dd in result:
        if d != dd and dd.startswith('{}/'.format(d)):
          trash.append(dd)
    filterd = []
    for d in result:
      if d not in trash:
        filterd.append(d)
    result = filterd
  return result

def find_in_use_artifacts():
  project_dirs = find_root_by_file_name(PROJECTS_HOME, 'pom.xml', 'parent')
  result = []
  for project_home in project_dirs:
    print(project_home)
    absolute_path = str(Path(PROJECTS_HOME).joinpath(project_home))
    os.chdir(absolute_path)
    process = subprocess.Popen('mvn dependency:tree', stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    out = str(out)
    code = process.wait()
    lines = out.split('\\n')
    artifacts = find_dependencies_from_lines(lines)
    result.extend(artifacts)
  return result

def find_dependencies_from_lines(lines):
  tree_title_patter = re.compile(r'maven-dependency-plugin\:.*\:tree.* @\sgen')
  dependency_patter = re.compile(r'(\|\s)?(\+|\\)-\s(.*\..*\:.*\:(compile|provided|test|runtime|system|import))')
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
  return artifacs

existing_artifact_dirs = find_root_by_file_name(REPOSITORY_HOME, '.pom', 'child')
artifacts = find_in_use_artifacts()
in_use_artifact_dirs = artifact_relative_dirs(artifacts)

for i in existing_artifact_dirs:
  print(i)

# print(in_use_artifact_dirs)