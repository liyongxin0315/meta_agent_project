#!/bin/bash
# 自动信任GitHub并推送，全程无任何输入
ssh-keyscan github.com >> ~/.ssh/known_hosts 2>&1
git push -u origin master