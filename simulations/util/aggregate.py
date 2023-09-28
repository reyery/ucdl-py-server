
def aggregate(input_array, agg_size, agg_type, ignore_val = None):
    result = []
    for i in range(round(len(input_array) / agg_size)):
        row = []
        for j in range(round(len(input_array[i]) / agg_size)):
            agg_val = 0
            count = 0
            xVal = i * agg_size
            yVal = j * agg_size
            for x in range(agg_size):
                for y in range(agg_size):
                    if ignore_val is not None and input_array[xVal + x][yVal + y] == ignore_val: continue
                    agg_val += input_array[xVal + x][yVal + y]
                    count += 1
            if agg_type == 'mean':
                if count == 0:
                    agg_val = ignore_val
                else:
                    agg_val = agg_val / count
            row.append(agg_val)
        result.append(row)
    return result