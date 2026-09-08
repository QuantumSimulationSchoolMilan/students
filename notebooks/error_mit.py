import numpy as np

## Estimates the single qubit calibration matrices from a set of calibration
## counts provided in input. This routine assumes independent read-out noise
## on each qubit and requires two calibration results corresponding to measurements
## on the all '0' state and on the all '1' state.
## Return a list of calibration matrices
def get_single_qubit_ro_probs(calibration_counts):
    # extract keys in counts for first circuit
    keys_list0 = [key for key in calibration_counts[0].keys()]
    # get number of qubits in counts
    num_qubits0 = len(keys_list0[0])
    print(f"_Found {num_qubits0} qubits in first calibration circuit counts")
    ## cycle over qubits
    cmatrices = []
    for qq in range(num_qubits0):
        ## we use the first calibration circuit for p00 and p10
        tot_counts0 = sum([calibration_counts[0][kk] for kk in keys_list0])
        p_00 = 0
        for key in keys_list0:
            ## qubits are labelled starting from the right in qiskit
            if key[num_qubits0-1-qq]=='0':
                p_00 += calibration_counts[0][key]
        ## now we normalize with all counts
        p_00 /= tot_counts0
        # probability of measuring qubit 0 in 1 when starting in 0 is simply
        p_01 = 1.-p_00
        ## we now use the second calibration circuit for p11 and p01
        keys_list1 = [key for key in calibration_counts[1].keys()]
        num_qubits1 = len(keys_list0[0])
        if num_qubits0 != num_qubits1:
            raise Exception("Number of qubits in calibration circuits do not match")
        tot_counts1 = sum([calibration_counts[1][kk] for kk in keys_list1])
        p_11 = 0
        for key in keys_list1:
            ## qubits are labelled starting from the right in qiskit
            if key[num_qubits1-1-qq]=='1':
                p_11 += calibration_counts[1][key]
        ## now we normalize with all counts
        p_11 /= tot_counts1
        # probability of measuring qubit 0 in 1 when starting in 0 is simply
        p_10 = 1.-p_11
        ## make confusion matrix for this qubit
        cmatrix = np.array([[p_00,p_10],
                            [p_01,p_11]])
        # add to the list
        cmatrices.append(cmatrix)

    return cmatrices

## Uses the calibration matrices for num_qubits qubits provided in input
## to directly mitigate the read out error on the measured counts raw_counts.
## Returns a new list of counts with the result of error mitigation
def get_mit_counts(raw_counts, num_qubits,cal_matrices):
    ## since we are applying this iteratively we need to update the 'raw_counts' as we go
    raw_counts_now = raw_counts
    # cycle over qubits
    for qnow in range(num_qubits):
        ## start a fresh mitigated counts every cycle
        mit_counts = {}
        # retrieve correct calibration matrix
        cal_mat_now = cal_matrices[qnow]
        # compute inverse
        inv_cal_now = np.linalg.inv(cal_mat_now)
        # cycle over counts
        for cc in raw_counts_now:
            # check if current qubit is set
            if cc[num_qubits-1-qnow]=='0':
                raw_vec = np.array([1,0])
            else:
                raw_vec = np.array([0,1])
            # produce corrected vector
            mit_vec = inv_cal_now@raw_vec
            # assign new mitigated counts
            ## start with 0
            lcc = list(cc)
            lcc[num_qubits-1-qnow]='0'
            newcc = ''.join(lcc)
            ## check if present
            if newcc in mit_counts:
                ## then we add
                mit_counts[newcc] += raw_counts_now[cc]*mit_vec[0]
            else:
                ## we make new one
                mit_counts[newcc] = raw_counts_now[cc]*mit_vec[0]
            ## then we do 1
            lcc[num_qubits-1-qnow]='1'
            newcc = ''.join(lcc)
            ## check if present
            if newcc in mit_counts:
                ## then we add
                mit_counts[newcc] += raw_counts_now[cc]*mit_vec[1]
            else:
                ## we make new one
                mit_counts[newcc] = raw_counts_now[cc]*mit_vec[1]
        raw_counts_now = mit_counts
    return mit_counts

## Removes negative counts from a count dictionary by spreading the negative contributions
## on the remaining bit-strings moving iteratively from the most negative count in
## ascending order.
## Return a new dictionary of counts with only positive definite values and same normalization
def fix_negative(in_counts,verbose=False):
    counts_now = in_counts.copy()
    # extract keys into list
    key_list = []
    for kk in counts_now:
        key_list.append(kk)
    num_strings = len(key_list)
    # make ordered array for counts
    count_array  = np.zeros(num_strings)
    for idx in range(num_strings):
        count_array[idx] = counts_now[key_list[idx]]
    sorted_array = np.sort(count_array)
    # and matching one for keys
    sorted_key_list = [key_list[kk] for kk in np.argsort(count_array)]
    # now go from smallest negative value and push weigth forward untill no more negative counts
    for idx in range(num_strings):
        if verbose:
            print(idx,sorted_array)
        if sorted_array[idx]<0:
            remaining_strings = num_strings-1-idx
            sorted_array[idx+1:] += sorted_array[idx]/remaining_strings
            sorted_array[idx] = 0.0
        else:
            ## if we finished all negative ones we can exit
            break
    # fix counts
    for idx in range(num_strings):
        counts_now[sorted_key_list[idx]] = sorted_array[idx]
    # and return it
    return counts_now