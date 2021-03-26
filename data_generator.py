import numpy as np


def writefile(filename, data):
    r_file = open(filename, "w")
    np.savetxt(r_file, data, fmt='%1.f')
    r_file.close()


vals = np.random.randint(10, size=(50, 2))
writefile("r.txt", vals)

vals = np.random.randint(10, size=(50, 2))
writefile("s.txt", vals)
