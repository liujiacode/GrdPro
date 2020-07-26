#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from Libs.read_grd import read_grd
import numpy
import math
import sys
import getopt

__str__ = """
名称    : DMol3 density.grd 文件切片工具.

原理    : 将密度数据导入为三维向量数组array[z, y, x];
          定义平行于xy平面的切片向量[abs_xy_from, abs_xy_to], 其中:
              abs_xy_from = (abs_x_from, abs_y_from) 为起始绝对坐标(非格点坐标),
              abs_xy_to = (abs_x_to, abs_y_to) 为终止绝对坐标,
              且须满足条件abs_x_from <= abs_x_to, abs_y_from <= abs_y_to, 值类型为整型或浮点型;
          以切片向量为基础建立垂直于xy平面的切面,并以sqrt(x_step ** 2 + y_step ** 2)步长划分近似积分区域,
          得到step_num + 1组积分值数组;
          函数返回(文件信息, 切片向量, 积分步长, 积分步数, 积分值数组)

注意    : 1) 请沿晶格a, b, c方向建立坐标系(可能不是直角坐标系),并使用此坐标建立切片向量;
          2) 选取切片向量时请注意使from值小于to值;
          3) 请谨慎使用格点步长大于1的计算数据.

使用方法: clip -i <density.grd> -f <from point> -t <to point> [-o <result file>, -h]

参数    : (1) -h / --help
             查看命令帮助.
          (2) -i / --input <density.grd>
             导入数据. 后接导入包含数据文本的"绝对路径".
          (3) -o / --output <result file>
             导出结果. 后接导出包含结果文本的"绝对路径".
          (4) -f / --from <from point>
             切片向量(向量须平行于xy平面)起始点坐标. 后接"x,y"(无括号和空格,即"-f x,y"或"--from x,y").
          (5) -t / --to <to point>
             切片向量(向量须平行于xy平面)终止点坐标. 后接"x,y".
          
"""


def clip(data_file, abs_xy_from, abs_xy_to):
    if not os.path.isfile(data_file):
        raise ValueError("Invalid data file path.")

    category, lattice_constants, step_args, grd_data = read_grd(data_file)
    a, b, c, alpha, beta, gamma = lattice_constants
    step, i_from, i_to, j_from, j_to, k_from, k_to = step_args
    reshape_size = ((k_to - k_from) // step + 1, (j_to - j_from) // step + 1, (i_to - i_from) // step + 1)
    data_array = numpy.reshape(numpy.array(grd_data), reshape_size)

    if not isinstance(abs_xy_from, tuple) or not isinstance(abs_xy_to, tuple):
        raise ValueError("Invalid point.")

    x_from = abs_xy_from[0] * 1.0 / a * (i_to - i_from)
    x_to = abs_xy_to[0] * 1.0 / a * (i_to - i_from)
    y_from = abs_xy_from[1] * 1.0 / b * (j_to - j_from)
    y_to = abs_xy_to[1] * 1.0 / b * (j_to - j_from)

    x_from = int(x_from // step * step)
    x_to = int(x_to // step * step)
    y_from = int(y_from // step * step)
    y_to = int(y_to // step * step)

    if x_from < i_from or x_from > i_to or y_from < j_from or y_from > j_to:
        raise ValueError("Invalid range of xy_from point.")
    if x_to < i_from or x_to > i_to or y_to < j_from or y_to > j_to:
        raise ValueError("Invalid range of xy_to point.")

    step_num = max(x_to - x_from, y_to - y_from) // step
    x_step = (x_to - x_from) * 1.0 / step_num
    y_step = (y_to - y_from) * 1.0 / step_num

    profit_data = []
    for i in range(step_num + 1):
        profit_data.append(sum(data_array[:, int(y_from + y_step * i) // step, int(x_from + x_step * i) // step]))

    data_info = (category, lattice_constants, step_args)
    clip_vector = [(x_from, y_from), (x_to, y_to)]
    clip_step_length = math.sqrt(x_step ** 2 + y_step ** 2)
    clip_step_num = step_num + 1

    return data_info, clip_vector, clip_step_length, clip_step_num, profit_data


if __name__ == '__main__':
    opt_args = getopt.getopt(sys.argv[1:], "hi:o:f:t:", ["help", "input=", "output=", "from=", "to="])[0]
    input_file = ""
    output_file = ""
    xy_from = ()
    xy_to = ()
    for opt, arg in opt_args:
        if opt in ("-h", "--help"):
            print(__str__)
            exit(0)
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
        elif opt in ("-f", "--from"):
            xy_from = tuple(float(i) for i in arg.split(','))
        elif opt in ("-t", "--to"):
            xy_to = tuple(float(i) for i in arg.split(','))
        else:
            raise ValueError("Invalid opt.")

    if not os.path.isfile(input_file):
        raise ValueError("Invalid input file.")

    if len(xy_from) != 2:
        raise ValueError("Invalid from point.")

    if len(xy_to) != 2:
        raise ValueError("Invalid to point.")

    data_result = clip(input_file, xy_from, xy_to)
    context = "Category : " + str(data_result[0][0])
    context += "\nLattice constants : \n    a = {:0}, b = {:1}, c = {:2}, alpha = {:3}, beta = {:4}, gamma = {:5}".format(
        *data_result[0][1])
    context += "\nGrid : \n    interval = {:0}, x_from_to = {:1} -> {:2}, y_from_to = {:3} -> {:4}, z_from_to = {:5} -> {:6}, ".format(
        *data_result[0][2])
    context += "\nClip vector : {0}".format(data_result[1])
    context += "\nClip interval : {0}".format(data_result[2])
    context += "\nTotal : {0}".format(data_result[3])
    context += "\nResult array : \n"
    for result_digit in data_result[4]:
        context += str(result_digit)
        context += '\n'

    if output_file:
        with open(output_file, 'w') as f:
            f.write(context)
    else:
        print(context)
