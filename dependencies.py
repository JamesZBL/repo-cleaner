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

import re, logging

def find_dependencies_from_lines(lines):
  tree_title_patter = re.compile(r'maven-dependency-plugin\:.*\:tree.* @\s.*')
  dependency_patter = re.compile(r'\s+([\w\.]*\:.*\:.*\:.*\:(compile|provided|test|runtime|system|import))')
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
    logging.info('Maven installed uncorrectly.')
  if title_found and not dependency_found:
    logging.info('No dependency found.')
  return artifacs