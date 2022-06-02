from mpu6050 import MPU6050
from contextlib import ExitStack
import struct
import yaml
import os
import time

class MPU6050_Manager: 
    def __init__(self, controller_id, sensor_ids, bus_ids, addresses=None):
        self.controller_id = controller_id
        self.sensors = {}
        for i in range(len(sensor_ids)):
            if addresses: 
                sensor = MPU6050(sensor_ids[i], bus_ids[i], addresses[i])
            else: 
                sensor = MPU6050(sensor_ids[i], bus_ids[i])
            self.sensors[sensor_ids[i]] = sensor
    
    def reset_sensor(self, sensor_id):
        self.sensors[sensor_id].reset()
    
    def reset_sensors(self):
        for sensor in self.sensors.values():
            sensor.reset()
            
    def configurate_sensor(self, sensor_id, clock_source, dlpf_mode, rate, full_scale_accel_range, full_scale_gyro_range,
                            accel_fifo_enabled, x_gyro_fifo_enabled, y_gyro_fifo_enabled, z_gyro_fifo_enabled):
        sensor = self.sensors[sensor_id]
        sensor.clock_source = clock_source
        sensor.dlpf_mode = dlpf_mode
        sensor.rate = rate
        sensor.full_scale_accel_range = full_scale_accel_range
        sensor.full_scale_gyro_range = full_scale_gyro_range
        sensor.accel_fifo_enabled = accel_fifo_enabled
        sensor.x_gyro_fifo_enabled = x_gyro_fifo_enabled
        sensor.y_gyro_fifo_enabled = y_gyro_fifo_enabled
        sensor.z_gyro_fifo_enabled = z_gyro_fifo_enabled
    
    def configurate_sensors(self, clock_source, dlpf_mode, rate, full_scale_accel_range, full_scale_gyro_range,
                            accel_fifo_enabled, x_gyro_fifo_enabled, y_gyro_fifo_enabled, z_gyro_fifo_enabled):
        for sensor_id in self.sensors: 
            self.configurate_sensor(sensor_id, clock_source, dlpf_mode, rate, full_scale_accel_range, full_scale_gyro_range,
                            accel_fifo_enabled, x_gyro_fifo_enabled, y_gyro_fifo_enabled, z_gyro_fifo_enabled)
            
    def get_temperature(self, sensor_id):
        return self.sensors[sensor_id].get_temperature()
    
    def get_temperatures(self):
        temperatures = {}
        for sensor_id, sensor in self.sensors.items(): 
            temperatures[sensor_id] = sensor.get_temperature()
        return temperatures
    
    def calibrate_sensor(self, sensor_id, max_iters, rough_iters, buffer_size, epsilon=0.1, mu=0.5, v_threshold=0.05):
        self.sensors[sensor_id].calibrate(max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold)
    
    def calibrate_sensors(self, max_iters, rough_iters, buffer_size, epsilon=0.1, mu=0.5, v_threshold=0.05):
        for sensor in self.sensors.values():
            sensor.calibrate(max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold)
    
    def start_session(self, session_name, duration):
        dir_path = session_name
        metadata_path = os.path.join(dir_path, 'metadata')
        raw_data_path = os.path.join(dir_path, 'raw_data')
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        if not os.path.isdir(metadata_path):
            os.mkdir(metadata_path)
        if not os.path.isdir(raw_data_path):
            os.mkdir(raw_data_path)
        session_info = {}
        session_info['name'] = session_name
        session_info['controller_id'] = self.controller_id
        session_info['time'] = {
            'start': None,
            'duration': duration
        }
        session_info['sensors'] = {}
        session_info['overflows'] = {}
        session_info['files'] = {}
        for sensor_id, sensor in self.sensors.items():
            session_info['sensors'][sensor_id] = {
                'clock_source': sensor.clock_source,
                'dlpf_mode': sensor.dlpf_mode,
                'rate': sensor.rate,
                'sample_rate': sensor.sample_rate,
                'full_scale_accel_range': sensor.full_scale_accel_range,
                'full_scale_gyro_range': sensor.full_scale_gyro_range,
                'accel_factor': sensor.accel_factor,
                'gyro_factor': sensor.gyro_factor,
                'accel_fifo_enabled': sensor.accel_fifo_enabled,
                'x_gyro_fifo_enabled': sensor.x_gyro_fifo_enabled,
                'y_gyro_fifo_enabled': sensor.y_gyro_fifo_enabled,
                'z_gyro_fifo_enabled': sensor.z_gyro_fifo_enabled,
                'package_length':  sensor.package_length
            }
            session_info['overflows'][sensor_id] = []
            session_info['files'][sensor_id] = 'sensor_{}'.format(sensor_id)
        file_paths = list(map(lambda x:  os.path.join(raw_data_path, x), session_info['files'].values()))
        package_length = [sensor.package_length for sensor in self.sensors.values()]
        packages_per_read = [(32 // length if length != 0 else 0) for length in package_length]
        with ExitStack() as stack: 
            files = [stack.enter_context(open(fpath, 'wb')) for fpath in file_paths]
            count = [0 for i in range(len(self.sensors))]
            time_start = time.time()
            for sensor in self.sensors.values():
                sensor.reset_fifo()
            while time.time() - time_start < duration:
                for i, sensor in enumerate(self.sensors.values()):
                    if package_length[i] > 0: 
                        fifo_count = sensor.get_fifo_count()
                        if fifo_count == 1024: 
                            session_info['overflows'][sensor.id].append(time.time() - time_start)
                            print('!!!')
                        if fifo_count > package_length[i] * packages_per_read[i]:
                            package = sensor.get_fifo_bytes(package_length[i] * packages_per_read[i])
                            files[i].write(bytes(package))
                            count[i] += packages_per_read[i]
        session_info['time']['start'] = time_start
        session_info['n_packages'] = dict(zip(list(self.sensors.keys()), count))
        session_info_path = os.path.join(metadata_path, f'{self.controller_id}_session_info.yml')
        with open(session_info_path, 'w') as f: 
            yaml.dump(session_info, f, sort_keys=False)