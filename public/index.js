const sio = io();

sio.on('connect', () => {
  console.log('connected');
  sio.emit('telemetry', {car_speed: 0})
})

sio.on('disconnect', () => {
  console.log('disconnected');
})

sio.on('telemetry_result', (data) => {
  console.log(data)
})