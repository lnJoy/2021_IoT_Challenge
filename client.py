import json
import random
import asyncio
import socketio

sio = socketio.AsyncClient()

cnt = 0

@sio.event
async def connect():
    print('connection established')


async def location_sender():
    latitude = random.uniform(37.5, 37.6)
    longitude = random.uniform(126.7, 126.9)
    await sio.emit('location receiver', {'latitude': latitude, 'longitude': longitude})


@sio.event
async def my_response(data):
    await asyncio.sleep(45000/15000)
    global cnt
    if cnt >= 200:
        cnt = 1
    f = open('status.json', 'r')
    status = bool(json.load(f)['status'])
    f.close()
    print('message received with ', data)
    try:
        if data['emergency']:
            cnt = 0
            await location_sender()
        else:
            cnt += 1
            await sio.emit('status receiver', {'status': status, 'cnt': cnt})
    except:
        await sio.emit('status receiver', {'status': status, 'cnt': cnt})


@sio.event
async def disconnect():
    print('disconnected from server')


async def main():
    await sio.connect('http://192.168.43.179', headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXJpYWwiOiIwMDAwMDAwMDYxYzhlZGE3In0.p5Aw-ImOuJ_jrEHwpQrl47BtFJtT8-IX1BY_5HrgDrY'})
    await sio.wait()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
