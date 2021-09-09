import random
import asyncio
import socketio

sio = socketio.AsyncClient()


@sio.event
async def connect():
    print('connection established')


@sio.event
async def my_response(data):
    await asyncio.sleep(45000/15000)
    print('message received with ', data)
    latitude = random.uniform(-90.0, 90.0)
    longitude = random.uniform(-180.0, 180.0)
    await sio.emit('location receiver', {'latitude': latitude, 'longitude': longitude})


@sio.event
async def disconnect():
    print('disconnected from server')


async def main():
    await sio.connect('http://localhost', headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXJpYWwiOiIwMDAwMDAwMDYxYzhlZGE3In0.p5Aw-ImOuJ_jrEHwpQrl47BtFJtT8-IX1BY_5HrgDrY'})
    await sio.wait()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
