import socket
import inspect
import struct
import sys
import os
import random
import time

filepath = os.path.dirname(os.path.realpath(__file__))[:-4] + 'docs/'
sys.path.append(filepath)
import protocol

HOST = '127.0.0.1'
PORT = 8888

def fun_filter(fun):
    (name, value) = fun
    return name

def send(socket, protocol, request):
    packet = request.SerializeToString()
    body_len = request.ByteSize()
    header = struct.pack('>2I', body_len, protocol)
    packet = header + packet
    return socket.send(packet)

def get(sock):
    try:
        header = sock.recv(8)
        if header:
            (body_len, protocol) = struct.unpack('>2I', header)
            if body_len:
                body = sock.recv(body_len)
                return (protocol, body)
            return None
    except socket.error:
        return None

def login(socket):
    request = protocol.LoginRequest()
    request.phone = '13533332421' 
    send(socket, protocol.LOGIN, request)
    response = get(socket)
    if response:
        res = protocol.HallListResponse()
        res.ParseFromString(response[1])
        print(res)
        join(socket, 1)

def join(socket, lobby_id):
    request = protocol.JoinRoomRequest()
    request.lobby_id = lobby_id
    send(socket, protocol.JOIN_ROOM, request)
    response = get(socket)
    if response:
        res = protocol.JoinRoomResponse()
        res.ParseFromString(response[1])
        for player in res.players:
            print("id:{} name:{} money:{}".format(player.id, player.name, player.money))
        for seat in res.seats:
            print("seat_id:{} player_id:{}".format(seat.id, seat.player_id))
        bet(socket)

def bet(socket):
    request = protocol.BetRequest()
    while True:
        print('start bet')
        request.money = random.randint(1, 8)
        request.type = random.randint(1, 4)
        print(request)
        send(socket, protocol.BET, request)
        response = get(socket)
        if response:
            res = protocol.BetResponse()
            res.ParseFromString(response[1])
            print(res)
        time.sleep(1.5)

if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    while True:
        fun = sys.stdin.readline()
        if fun == '\n':
            client.close()
            break
        fun = fun.strip('\n')
        fun_list = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
        fun_list = map(fun_filter, fun_list)
        if fun in fun_list:
            f = getattr(sys.modules[__name__], fun)
            f(client)

