from actian_vectorai import VectorAIClient

with VectorAIClient("localhost:6574") as client:
    print("Collections:")
    print(dir(client.collections))

    print("\nPoints:")
    print(dir(client.points))