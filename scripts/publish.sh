#!/bin/bash

# 发布脚本

# 检查版本号参数
if [ -z "$1" ]; then
  echo "请提供版本号，例如: ./publish.sh 0.1.1"
  exit 1
fi

VERSION=$1

echo "准备发布版本 $VERSION"

# 1. 更新setup.py中的版本号
# 注意：这需要您手动更新setup.py中的版本号

# 2. 清理旧的构建文件
echo "清理旧的构建文件..."
rm -rf build/ dist/ src/*.egg-info

# 3. 构建新版本
echo "构建新版本..."
python -m build

# 4. 检查构建的包
echo "检查构建的包..."
twine check dist/*

# 5. 上传到PyPI
echo "上传到PyPI..."
twine upload dist/*

# 6. 创建Git标签
echo "创建Git标签..."
git tag v$VERSION
git push origin main --tags

echo "版本 $VERSION 发布完成！"
