def min_path(node):
    min_distance = [float("inf")] * routers
    visited = [False] * routers
    min_distance[node] = 0
    #visited[node] = True
    dist_path = [str(node)+"-"] * routers

    for i in range(routers):

        min_dist = float("inf")
        min_node = -1

        for j in range(routers):
            if visited[j] == False and min_distance[j] < min_dist:
                min_dist = min_distance[j]
                min_node = j

        visited[min_node] = True

        for j in range(routers):
            if distance[min_node][j] != -1 and visited[j] == False and min_distance[j] > distance[min_node][j] + min_distance[min_node]:
                    min_distance[j] = distance[min_node][j] + min_distance[min_node]
                    dist_path[j] = dist_path[min_node] + str(j) + "-"

    return min_distance,dist_path


routers = 9
distance = [ [ -1, 4, -1, -1, -1, -1, -1, 8, -1 ],
                        [ 4, -1, 8, -1, -1, -1, -1, 11, -1 ],
                        [ -1, 8, -1, 7, -1, 4, -1, -1, 2 ],
                        [ -1, -1, 7, -1, 9, 14, -1, -1, -1 ],
                        [ -1, -1, -1, 9, -1, 10, -1, -1, -1 ],
                        [ -1, -1, 4, 14, 10, -1, 2, -1, -1 ],
                        [ -1, -1, -1, -1, -1, 2, -1, 1, 6 ],
                        [ 8, 11, -1, -1, -1, -1, 1, -1, 7 ],
                        [ -1, -1, 2, -1, -1, -1, 6, 7, -1 ] ]

distance,symbols = min_path(0)
print(distance)
print(symbols)