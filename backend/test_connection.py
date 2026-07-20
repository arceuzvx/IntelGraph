from actian_vectorai import VectorAIClient

with VectorAIClient("localhost:6574") as client:
    info = client.health_check()

    print("Connected!")
    print(info)