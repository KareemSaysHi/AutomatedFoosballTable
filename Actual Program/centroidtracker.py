from scipy.spatial import distance as dist
import numpy as np

class CentroidTracker():
    def __init__(self):
        self.objects = dict()
        
        #self.objects looks like:
        #{
        # objectId: centroid
        # 1: (11, 12)
        # 2: (21, 22)
        # 3: (31, 32)
        # }

    def register(self, centroid, id):
        self.objects[id] = centroid

    def update(self, centroids):
        inputCentroids = centroids
        #[
        # [12, 13],
        # [22, 23],
        # [32, 33]
        # ]

        #if we aren't tracking any objects yet
        #register them

        if len(inputCentroids) == 0:
            return self.objects

        else:
            objectIds = list(self.objects.keys()) #[1, 2, 3]
            objectCentroids = list(self.objects.values()) #[(11, 12), (21, 22), (31, 32)]
            print("object centroids:")
            print(objectCentroids)

            print("input centroids:")
            print(inputCentroids)

            D = dist.cdist(np.array(objectCentroids), inputCentroids, 'euclidean')
            #D = [
            # [d_i1j1, d_i1j2, d_i1j3, ...]
            # [d_i2j1, d_i2j2, d_i2j3, ...]
            # ...
            # ]

            rows = D.min(axis=1).argsort() #minimim j for each i, then argsort

            #[1 0 2] smallest in row 1 (object id 1), second smallest in row 2, ...

            #D.min = [d_i1ja, d_i2jb, d_i1jc, d_i1jd, ...]
    
            #rows = [index of smallest d_ixjy, index of second smallest d_ixjy, ...]

            cols = D.argmin(axis=1)[rows] #minimumj for each i, actually sorted

            #rows = [smallest d_ixjy, second smallest d_ixjy, ...]

            #row, col equal to (this is the id with the smallest distance from the thing, this is the column that matches up with this distance)
            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):
                #(row, col) = (
                # index of kth smallest d_ixjy
                # kth smallest d_ixjy
                # )
                if row in usedRows or col in usedCols:
                    continue

                objectId = objectIds[row]
                self.objects[objectId] = inputCentroids[col]

                usedRows.add(row)
                usedCols.add(col)

        return self.objects

            #code should automatically use old pos if the other one not found