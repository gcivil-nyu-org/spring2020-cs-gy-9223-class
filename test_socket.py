import socket

print("localhost:80")
print(socket.getaddrinfo("localhost", 80))

print("localhost:443")
print(socket.getaddrinfo("localhost", 443))
