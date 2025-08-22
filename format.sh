#!/bin/bash
# sudo apt install clang-format cmake-format 
# clang-format, version v15 is required
find ./ -regex '.*\.cc\|.*\.cpp\|.*\.h\|.*\.hpp\|.*\.proto' -and -not -regex '.*\.pb\.cc\|.*\.pb\.h' | xargs clang-format -i --style=file
echo "clang-format done"