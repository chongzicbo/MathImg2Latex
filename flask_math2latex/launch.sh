#!/bin/bash
cd /data/bocheng/dev/mywork/MathImg2Latex/flask_math2latex
nohup /data/bocheng/software/installed/miniconda3/envs/test/bin/python server.py >logs/mathimg2latex.log 2>&1 &
