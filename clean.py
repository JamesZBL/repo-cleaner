from pathlib import Path
from functools import reduce
import os

PROJECTS_HOME = '~/repo'
MAVEN_HOME = Path.home().joinpath('.m2')
REPOSITORY_HOME = '{}/repository'.format(MAVEN_HOME)
# REPOSITORY_HOME = '.tmp'

repo_home = Path(REPOSITORY_HOME)
artifacts = ['org.spring.boot:9.9.9.RELEASE:compile', 'org.spring.boot:9.9.10.RELEASE:compile']
in_use_artifact_dirs = []
for artifact in artifacts:
  elements = artifact.split(':')
  artifact_id = elements[0]
  version = elements[1]
  scope = artifact[2]
  artifact_id_dir = artifact_id.replace('.', '/')
  artifact_dir = '{}/{}'.format(artifact_id_dir, version)
  in_use_artifact_dirs.append(artifact_dir)

existing_artifact_dirs = []
for root, folders, files in os.walk(REPOSITORY_HOME):
  for file in files:
    if bool(file.find('.pom')):
      relative_path = str(Path(root).relative_to(REPOSITORY_HOME))
      existing_artifact_dirs.append(relative_path)

existing_artifact_dirs = list(set(existing_artifact_dirs))
existing_artifact_dirs.sort()

for d in existing_artifact_dirs:
  for dd in existing_artifact_dirs:
    if d.startswith(dd):
      existing_artifact_dirs.remove(dd)

def find_root_by_file_name(base_dir, file_name_section, reserve_mode='child'):
  result = []
  for root, folders, files in os.walk(REPOSITORY_HOME):
    for file in files:
      if(bool(file.find('.pom'))):
        relative_path = str(Path(root).relative_to(REPOSITORY_HOME))
        result.append(relative_path)
  result = list(set(result))
  result.sort()
  if 'child' == reserve_mode:
    for d in result:
      for dd in result:
        if d.startswith(dd):
          result.remove(dd)
  elif 'parent' == reserve_mode:
    for dd in result:
      for d in result:
        if d.startswith(dd):
          result.remove(d)
  return result

for i in existing_artifact_dirs:
  print(i)

print(in_use_artifact_dirs)