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


def early_join_init_run(sorted_r, sorted_s):
    return (sorted_r, sorted_s)

def early_join_merged_run(sorted_r, sorted_s):
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

        res.append(early_join_init_run(sorted_r, sorted_s))

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
        
        res.append(early_join_merged_run(sorted_r, sorted_s))
        
        #write sorted_r and sorted_s to external memory
        writefile("sorted_r.txt", sorted_r)
        writefile("sorted_s.txt", sorted_s)

        Q.append((sorted_r, sorted_s)) 

R = loaddata("r.txt")
# print(R)

S = loaddata("s.txt")
# print(S)

pmj(R, S, 8, 10, 0, 0)


