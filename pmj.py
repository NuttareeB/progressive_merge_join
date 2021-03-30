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
        self.X.append(v)
    
    def query(self, v, v_key, except_sequence_i = -1):
        # remove elements that less than v

        i = 0
        while i < len(self.X) and self.X[i][self.key] < v[v_key]:
            self.X = self.X[1:]
            i += 1
        
        result = []

        for i in range(len(self.X)):
            if except_sequence_i == i:
                continue
            if self.X[i][self.key] == v[v_key]:
                result.append((self.X[i], v))

        return result


def early_join_init_run(sorted_r, sorted_s, key_R, key_S):
    RES = []
    R_M = SweepArea([], key_R)
    S_M = SweepArea([], key_S)
    
    while len(sorted_r) > 0 or len(sorted_s) > 0:
        r = []
        s = []
        if len(sorted_r) > 0:
            r = sorted_r[0]
        if len(sorted_s) > 0:
            s = sorted_s[0]
        
        if len(sorted_s) == 0 or (len(sorted_r) > 0 and r[key_R] <= s[key_S]):
            R_M.insert(r)
            RES.append(S_M.query(r, key_R))
            sorted_r = sorted_r[1:]
        else:
            S_M.insert(s)
            RES.append(R_M.query(s, key_S))
            sorted_s = sorted_s[1:]

    return RES

def early_join_merged_run(q, sorted_r, sorted_s, key_R, key_S):
    RES = []
    R_M = SweepArea([], key_R)
    S_M = SweepArea([], key_S)

    R_m = [r for r, s in q]
    S_m = [s for r, s in q]
    
    while any([len(r) > 0 for r in R_m]) or any([len(s) > 0 for s in S_m]):
        r = []
        s = []

        r_i = -1
        s_j = -1

        for i, rm in enumerate(R_m):
            if len(rm) > 0 and (len(r) == 0 or rm[0][key_R] < r[key_R]):
                r = rm[0]
                r_i = i
        for j, sm in enumerate(S_m):
            if len(sm) > 0 and (len(s) == 0 or sm[0][key_S] < s[key_S]):
                s = sm[0]
                s_j = j
        
        if s_j == -1 or (r_i > -1 and r[key_R] <= s[key_S]):
            R_M.insert(r)
            RES.append(S_M.query(r, key_R, r_i))
            R_m = R_m[:r_i] + R_m[r_i + 1:]
            sorted_r.append(r)
        else:
            S_M.insert(s)
            RES.append(R_M.query(s, key_S, s_j))
            S_m = S_m[:s_j] + S_m[s_j + 1:]
            sorted_s.append(s)

    return RES

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

    print(np.array(res))

R = loaddata("r.txt")
# print(R)

S = loaddata("s.txt")
# print(S)

pmj(R, S, 8, 10, 0, 0)

