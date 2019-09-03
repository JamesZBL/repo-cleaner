# Repo Cleaner

构建工具仓库依赖清理工具

## 1. 支持的工具
* Maven
* 开发中 ...

## 2. 配置
```python
# 项目根目录的父目录（父目录中存储多个项目）
PROJECTS_HOME = '/path/to/your/projects/home'
# Maven 配置根目录（默认 ${HOME}/.m2）
MAVEN_HOME = '/path/to/your/mave/home'
# Maven 本地仓库根目录（默认 ${HOME}/.m2/repository）
REPOSITORY_HOME = '/path/to/your/maven/repository'
# 扫描哪些项目，如果为空则全部扫描
INCLUDES = ['project_1', 'project_2']
```

## 3. 运行
```bash
$ python3 clean.py
```