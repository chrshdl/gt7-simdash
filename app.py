import socketio

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio, static_files={
  '/': './public/'
})

@sio.event
async def connect(sid, env):
  print(f'{sid} connected')

@sio.event
async def disconnect(sid):
  print(f'{sid} disconnected')

@sio.event
async def telemetry(sid, data):
  print('telemetry data from', sid)
  await sio.emit('telemetry_result', {'car_speed': 40})
