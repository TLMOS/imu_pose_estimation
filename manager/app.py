from paho.mqtt import client as mqtt_client
import time
from mpu6050 import MPU6050
from mpu6050_manager import MPU6050_Manager
import yaml
import os
import shutil
import requests

with open('config.yml', 'r') as f:
    cfg = yaml.safe_load(f)
    
device_id         = cfg['device_id']
mqtt_ip           = cfg['mqtt']['ip']
mqtt_port         = cfg['mqtt']['port']
topic_control     = cfg['mqtt']['topic']['control']
topic_info        = cfg['mqtt']['topic']['info']
client_ip         = cfg['client']['ip']
client_port       = cfg['client']['port']
sensor_ids        = [sensor['id'] for sensor in cfg['sensors']]
sensor_buses      = [sensor['bus'] for sensor in cfg['sensors']]
sensor_addresses  = [sensor['address'] for sensor in cfg['sensors']]
sensor_settings   = [sensor['settings'] for sensor in cfg['sensors']]

def publish(client, topic, msg_type, msg):
    payload = {'type': msg_type, 'device_id': device_id, 'msg': msg}
    payload = yaml.dump(payload)
    result = client.publish(topic, payload)
    
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT Broker!')
        publish(client, topic_info, 'info', 'Connected to MQTT Broker')
    else:
        print('Failed to connect, return code %d\n', rc)
        
def on_message(client, userdata, msg):
    print(f'Received {msg.payload.decode()} from {msg.topic} topic')
    try:
        if msg.topic == topic_control:
            payload = yaml.safe_load(msg.payload.decode())
            cmd = payload['command']
            if cmd == 'ping_sensors':
                sensors = ', '.join(manager.sensors.keys())
                publish(client, topic_info, 'info', f'Connected sensors: {sensors}')
            elif cmd == 'reset_sensor':
                args = payload['args']
                sensor_id = args['sensor_id']
                if sensor_id in manager.sensors:
                    manager.reset_sensor(sensor_id)
                    publish(client, topic_info, 'success', f'Reseted sensor \'{sensor_id}\'')
            elif cmd == 'reset_sensors':
                manager.reset_sensors()
                publish(client, topic_info, 'success', 'Reseted all sensors')
            elif cmd == 'configurate_sensor':
                args = payload['args']
                sensor_id = args['sensor_id']
                if sensor_id in manager.sensors:
                    clock_source           = args['clock_source']
                    dlpf_mode              = args['dlpf_mode']
                    rate                   = args['rate']
                    full_scale_accel_range = args['full_scale_accel_range']
                    full_scale_gyro_range  = args['full_scale_gyro_range']
                    accel_fifo_enabled     = args['accel_fifo_enabled']
                    x_gyro_fifo_enabled    = args['x_gyro_fifo_enabled']
                    y_gyro_fifo_enabled    = args['y_gyro_fifo_enabled']
                    z_gyro_fifo_enabled    = args['z_gyro_fifo_enabled']
                    manager.configurate_sensor(sensor_id, clock_source, dlpf_mode, rate,
                                               full_scale_accel_range, full_scale_gyro_range,
                                               accel_fifo_enabled, x_gyro_fifo_enabled, y_gyro_fifo_enabled, z_gyro_fifo_enabled)
                    with open('config.yml', 'r') as f:
                        cfg = yaml.safe_load(f)
                        i = sensor_ids.index(sensor_id)
                        cfg['sensors'][i]['settings']['clock_source'] = clock_source
                        cfg['sensors'][i]['settings']['dlpf_mode'] = dlpf_mode
                        cfg['sensors'][i]['settings']['rate'] = rate
                        cfg['sensors'][i]['settings']['full_scale_accel_range'] = full_scale_accel_range
                        cfg['sensors'][i]['settings']['full_scale_gyro_range'] = full_scale_gyro_range
                        cfg['sensors'][i]['settings']['accel_fifo_enabled'] = accel_fifo_enabled
                        cfg['sensors'][i]['settings']['x_gyro_fifo_enabled'] = x_gyro_fifo_enabled
                        cfg['sensors'][i]['settings']['y_gyro_fifo_enabled'] = y_gyro_fifo_enabled
                        cfg['sensors'][i]['settings']['z_gyro_fifo_enabled'] = z_gyro_fifo_enabled
                    with open('config.yml', 'w') as f:
                        yaml.dump(cfg, f, sort_keys=False)
                    publish(client, topic_info, 'success', f'Configurated sensor \'{sensor_id}\'')
            elif cmd == 'configurate_sensors':
                args = payload['args']
                clock_source           = args['clock_source']
                dlpf_mode              = args['dlpf_mode']
                rate                   = args['rate']
                full_scale_accel_range = args['full_scale_accel_range']
                full_scale_gyro_range  = args['full_scale_gyro_range']
                accel_fifo_enabled     = args['accel_fifo_enabled']
                x_gyro_fifo_enabled    = args['x_gyro_fifo_enabled']
                y_gyro_fifo_enabled    = args['y_gyro_fifo_enabled']
                z_gyro_fifo_enabled    = args['z_gyro_fifo_enabled']
                manager.configurate_sensors(clock_source, dlpf_mode, rate, full_scale_accel_range, full_scale_gyro_range,
                                           accel_fifo_enabled, x_gyro_fifo_enabled, y_gyro_fifo_enabled, z_gyro_fifo_enabled)
                with open('config.yml', 'r') as f:
                    cfg = yaml.safe_load(f)
                    for i in range(len(sensor_ids)):
                        cfg['sensors'][i]['settings']['clock_source'] = clock_source
                        cfg['sensors'][i]['settings']['dlpf_mode'] = dlpf_mode
                        cfg['sensors'][i]['settings']['rate'] = rate
                        cfg['sensors'][i]['settings']['full_scale_accel_range'] = full_scale_accel_range
                        cfg['sensors'][i]['settings']['full_scale_gyro_range'] = full_scale_gyro_range
                        cfg['sensors'][i]['settings']['accel_fifo_enabled'] = accel_fifo_enabled
                        cfg['sensors'][i]['settings']['x_gyro_fifo_enabled'] = x_gyro_fifo_enabled
                        cfg['sensors'][i]['settings']['y_gyro_fifo_enabled'] = y_gyro_fifo_enabled
                        cfg['sensors'][i]['settings']['z_gyro_fifo_enabled'] = z_gyro_fifo_enabled
                with open('config.yml', 'w') as f:
                    yaml.dump(cfg, f, sort_keys=False)
                publish(client, topic_info, 'success', 'Configurated all sensors')
            elif cmd == 'calibrate_sensor':
                args = payload['args']
                sensor_id = args['sensor_id']
                if sensor_id in manager.sensors:
                    max_iters   = args['max_iters']
                    rough_iters = args['rough_iters']
                    buffer_size = args['buffer_size']
                    epsilon     = args['epsilon'] if 'epsilon' in args else 0.1
                    mu          = args['mu'] if 'mu' in args else 0.5
                    v_threshold = args['v_threshold'] if 'v_threshold' in args else 0.05
                    manager.calibrate_sensor(sensor_id, max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold)
                    publish(client, topic_info, 'success', f'Calibrated sensor \'{sensor_id}\'')
            elif cmd == 'calibrate_sensors':
                args = payload['args']
                max_iters   = args['max_iters']
                rough_iters = args['rough_iters']
                buffer_size = args['buffer_size']
                epsilon     = args['epsilon'] if 'epsilon' in args else 0.1
                mu          = args['mu'] if 'mu' in args else 0.5
                v_threshold = args['v_threshold'] if 'v_threshold' in args else 0.05
                manager.calibrate_sensors(max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold)
                publish(client, topic_info, 'success', 'Calibrated all sensors')
            elif cmd == 'start_session':
                args = payload['args']
                session_name = args['session_name']
                duration     = args['duration']
                manager.start_session(session_name, duration)
                archive_name = f'{session_name}_{device_id}'
                shutil.make_archive(archive_name, 'zip', session_name)
                url = f"http://{client_ip}:{client_port}/upload"
                headers = {'Type':'session_part'}
                files = [('file',(f'{archive_name}.zip', open(f'{archive_name}.zip','rb'),'application/zip'))]
                payload = {'session_name': session_name}
                response = requests.request("POST", url, headers=headers, data=payload, files=files)
                os.remove(f'{archive_name}.zip')
                shutil.rmtree(os.path.join(session_name))
                publish(client, topic_info, 'success', 'Session finished')
    except Exception as e:
        publish(client, topic_info, 'error', 'Unexpected error: ' + str(e))
        
if __name__ == '__main__':
    while True:
        try:
            manager = MPU6050_Manager(device_id, sensor_ids, sensor_buses, sensor_addresses)
            for i, sensor_id in enumerate(sensor_ids):
                clock_source           = sensor_settings[i]['clock_source']
                dlpf_mode              = sensor_settings[i]['dlpf_mode']
                rate                   = sensor_settings[i]['rate']
                full_scale_accel_range = sensor_settings[i]['full_scale_accel_range']
                full_scale_gyro_range  = sensor_settings[i]['full_scale_gyro_range']
                accel_fifo_enabled     = sensor_settings[i]['accel_fifo_enabled']
                x_gyro_fifo_enabled    = sensor_settings[i]['x_gyro_fifo_enabled']
                y_gyro_fifo_enabled    = sensor_settings[i]['y_gyro_fifo_enabled']
                z_gyro_fifo_enabled    = sensor_settings[i]['z_gyro_fifo_enabled']
                manager.configurate_sensor(sensor_id, clock_source, dlpf_mode, rate,
                                               full_scale_accel_range, full_scale_gyro_range,
                                               accel_fifo_enabled, x_gyro_fifo_enabled, y_gyro_fifo_enabled, z_gyro_fifo_enabled)
            
            client = mqtt_client.Client(device_id)
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(mqtt_ip, mqtt_port)
            client.subscribe(topic_control)

            client.loop_forever()
        except Exception as e:
            print(e)
            time.sleep(5)
