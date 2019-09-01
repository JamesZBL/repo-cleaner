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
import os, re

def find_root_by_file_name(base_dir, file_name_sections, reserve_mode='child', reg=True):
  result = []
  for root, folders, files in os.walk(base_dir):
    if reg:
      match = 0
      for file in files:
        for section in file_name_sections:
          if re.match(section, file):
            match += 1
      if len(file_name_sections) == match:
        relative_path = str(Path(root).relative_to(base_dir))
        result.append(relative_path)
    else:
      for file in files:
        for filename in file_name_sections:
          if file == filename:
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