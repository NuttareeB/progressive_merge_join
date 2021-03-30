import numpy as np

def loaddata(filename):
    return np.genfromtxt(filename,dtype=str)

def writefile(filename, data):
    r_file = open(filename, "w")
    np.savetxt(r_file, data, fmt="%s")
    r_file.close()

def quicksort(arr, key):
    if len(arr) < 2:
        return arr
    
    # print("arr:", arr)

    pivot = arr[0, key]
    pivot_list = arr[0]
    left = np.array([x for x in arr if x[key] < pivot])
    right = np.array([x for x in arr[1:] if x[key] >= pivot])
    
    sorted_left = quicksort(left, key)
    sorted_right = quicksort(right, key)
    
    if sorted_right.size == 0:
        return np.concatenate((sorted_left, [pivot_list]))
    elif sorted_left.size == 0:
        return np.concatenate(([pivot_list], sorted_right))
    else:
        return np.concatenate((sorted_left, [pivot_list], sorted_right))

class SweepArea:
    def __init__(self, x, key):
        self.X = x
        self.key = key

    def insert(self, v):
        self.X = self.X.append(v)
    
    def query(self, v, v_key):
        # remove elements that less than v
        i = 0
        while self.X[i][self.key] < v[v_key]:
            self.X = self.X[1:]
            i += 1
        
        result = []

        i = 0
        while self.X[i][self.key] == v[v_key]:
            result.append((self.X[i], v))
        
        return result


def early_join_init_run(sorted_r, sorted_s, key_R, key_S):
    RES = []
    R_m = SweepArea([], key_R)
    S_m = SweepArea([], key_S)
    
    while len(sorted_r) > 0 or len(sorted_s) > 0:
        r = []
        s = []
        if len(sorted_r) > 0:
            r = sorted_r[0]
        if len(sorted_s) > 0:
            s = sorted_s[0]
        
        if len(sorted_s) == 0 or (len(sorted_r) > 0 and r[key_R] <= s[key_S]):
            R_m.insert(r)
            RES.append(S_m.query(r, key_R))
            sorted_r = sorted_r[1:]
        else:
            S_m.insert(s)
            RES.append(R_m.query(s, key_S))
            sorted_s = sorted_s[1:]

    return RES

def early_join_merged_run(q, sorted_r, sorted_s, key_R, key_S):
    return (sorted_r, sorted_s)

"""
input: 
    - R and S
    - memory_size
    - max fan-in of merge F
"""
def pmj(R, S, mem_size, max_fan_in, key_R, key_S):
    Q = []
    res = []

    #phase1
    while len(R) != 0 or len(S) != 0:
        #get subset of R and S as r and s where |r| + |s| <= mem_size
        r = R[:mem_size//2]
        s = S[:mem_size//2]

        #remove subset from the main R and S
        R = R[mem_size//2:]
        S = S[mem_size//2:]

        #sort both partitions
        sorted_r = quicksort(r, key_R)
        sorted_s = quicksort(s, key_S)

        res.append(early_join_init_run(sorted_r, sorted_s, key_R, key_S))

        #write sorted_r and sorted_s to external memory
        writefile("sorted_r.txt", sorted_r)
        writefile("sorted_s.txt", sorted_s)

        Q.append((sorted_r, sorted_s))
    
    #phase2
    while len(Q) > 1:
        q = Q[:max_fan_in//2]
        Q = Q[max_fan_in//2:]

        sorted_r = []
        sorted_s = []
        
        res.append(early_join_merged_run(q, sorted_r, sorted_s, key_R, key_S))
        
        #write sorted_r and sorted_s to external memory
        writefile("sorted_r.txt", sorted_r)
        writefile("sorted_s.txt", sorted_s)

        Q.append((sorted_r, sorted_s)) 

R = loaddata("r.txt")
# print(R)

S = loaddata("s.txt")
# print(S)

pmj(R, S, 8, 10, 0, 0)


