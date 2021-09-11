import json
import random
import asyncio
import socketio

sio = socketio.AsyncClient()


@sio.event
async def connect():
    print('connection established')


async def location_sender():
    latitude = random.uniform(37.5, 37.6)
    longitude = random.uniform(126.7, 126.9)
    await sio.emit('location receiver', {'latitude': latitude, 'longitude': longitude})


@sio.event
async def my_response(data):
    # print(data)
    await asyncio.sleep(45000/15000)
    f = open('status.json', 'r')
    status = bool(json.load(f)['status'])
    f.close()
    print('message received with ', data)
    try:
        if data['emergency']:
            await location_sender()
        else:
            await sio.emit('status receiver', {'status': status})
    except:
        await sio.emit('status receiver', {'status': status})


@sio.event
async def disconnect():
    print('disconnected from server')


async def main():
    await sio.connect('http://61.73.71.185', headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXJpYWwiOiJkYWQwMDFiYjczNWY5OWMwIn0.7R7KxwN9WT1HMlUOe4500aDPrKfPhvS0z9Wr8AaIB8s'})
    await sio.wait()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
