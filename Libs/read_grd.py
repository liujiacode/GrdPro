# -*-coding:utf-8-*-

import os


def read_grd(grd_file):
    if not os.path.isfile(grd_file):
        raise ValueError("Invalid grd file path.")

    file = open(grd_file)
    data = file.read().split('\n')
    file.close()

    category = data[0]
    data2 = data[2].split(' ')
    while '' in data2:
        data2.remove('')
    data4 = data[4].split(' ')
    while '' in data4:
        data4.remove('')
    a, b, c, alpha, beta, gamma = [float(i) for i in data2]
    step, i_from, i_to, j_from, j_to, k_from, k_to = [int(i) for i in data4]
    grd_data = [float(i) for i in data[5:-1]]
    del data
    if len(grd_data) != ((i_to - i_from) / step + 1)*((j_to - j_from) / step + 1)*((k_to - k_from) / step + 1):
        raise ValueError("Invalid grd data length.")

    return category, (a, b, c, alpha, beta, gamma), (step, i_from, i_to, j_from, j_to, k_from, k_to), grd_data
