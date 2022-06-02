import struct
import yaml
import os
import pandas as pd

def merge_session(session_dir):
    session_parts = []
    for file_name in os.listdir(os.path.join(session_dir, 'metadata')):
        if file_name[-17: ] == '_session_info.yml':
            file_path = os.path.join(session_dir, 'metadata', file_name)
            with open(file_path, 'r') as f: 
                session_parts.append(yaml.safe_load(f))
            os.remove(file_path)  
    session_info = {}
    session_info['name'] = session_parts[0]['name']
    session_info['devices'] = dict(zip([part['controller_id'] for part in session_parts],
                                        [list(part['sensors'].keys()) for part in session_parts]))
    session_info['time'] = {
        'start': dict(zip([part['controller_id'] for part in session_parts], 
                            [part['time']['start'] for part in session_parts])),
        'duration': session_parts[0]['time']['duration']
    }
    session_info['sensors'] = {}
    session_info['overflows'] = {}
    session_info['files'] = {}
    session_info['n_packages'] = {}
    for part in session_parts:
        session_info['sensors'].update(part['sensors'])
        session_info['overflows'].update(part['overflows'])
        session_info['files'].update(part['files'])
        session_info['n_packages'].update(part['n_packages'])        
    session_info['crops'] = {}
    start_time_max = max([part['time']['start'] for part in session_parts])
    for controller_id, sensor_ids in session_info['devices'].items():
        delta_t = start_time_max - session_info['time']['start'][controller_id]
        for sensor_id in sensor_ids:
            n = session_info['n_packages'][sensor_id]
            delta_n = int(delta_t * session_info['sensors'][sensor_id]['sample_rate'])
            session_info['crops'][sensor_id] = [delta_n, n]
    n_min = min([crop[1] - crop[0] for crop in session_info['crops'].values()])
    for sensor_id in session_info['sensors']:
        crop = session_info['crops'][sensor_id]
        crop[1] -= (crop[1] - crop[0]) - n_min
        session_info['crops'][sensor_id] = crop 
    session_info_path = os.path.join(session_dir, 'metadata', 'session_info.yml')
    with open(session_info_path, 'w') as f:
        yaml.dump(session_info, f, sort_keys=False)
    
def decode_session(session_dir):
    session_info_path = os.path.join(session_dir, 'metadata', 'session_info.yml')
    with open(session_info_path, 'r') as f: 
        session_info = yaml.safe_load(f)
    file_names = session_info['files']
    source_file_paths = list(map(lambda x:  os.path.join(session_dir, 'raw_data', x), file_names.values()))
    target_file_paths = list(map(lambda x:  os.path.join(session_dir, f'{x}.csv'), file_names.values()))
    for i, sensor_id in enumerate(session_info['sensors']):
        package_length = session_info['sensors'][sensor_id]['package_length']
        accel_factor = session_info['sensors'][sensor_id]['accel_factor']
        gyro_factor = session_info['sensors'][sensor_id]['gyro_factor']
        accel_fifo_enabled = session_info['sensors'][sensor_id]['accel_fifo_enabled']
        x_gyro_fifo_enabled = session_info['sensors'][sensor_id]['x_gyro_fifo_enabled']
        y_gyro_fifo_enabled = session_info['sensors'][sensor_id]['y_gyro_fifo_enabled']
        z_gyro_fifo_enabled = session_info['sensors'][sensor_id]['z_gyro_fifo_enabled']
        crop = session_info['crops'][sensor_id]
        df = []
        with open(source_file_paths[i], 'rb') as f:
            data = list(f.read())
            for j in range(crop[0], crop[1]):
                package = data[j * package_length :  (j + 1) * package_length]
                package_format = '>' + 'h' * (package_length // 2)
                package = struct.unpack(package_format, memoryview(bytearray(package)))
                readings = []
                p = 0
                if accel_fifo_enabled: 
                    readings.append(package[0] * accel_factor)
                    readings.append(package[1] * accel_factor)
                    readings.append(package[2] * accel_factor)
                    p = 3
                if x_gyro_fifo_enabled: 
                    readings.append(package[p] * gyro_factor)
                    p += 1
                if y_gyro_fifo_enabled: 
                    readings.append(package[p] * gyro_factor)
                    p += 1
                if z_gyro_fifo_enabled: 
                    readings.append(package[p] * gyro_factor)
                df.append(readings)
        columns = []
        if accel_fifo_enabled:
            columns += ['accel_x', 'accel_y', 'accel_z']
        if x_gyro_fifo_enabled: 
            columns.append('gyro_x')
        if y_gyro_fifo_enabled: 
            columns.append('gyro_y')
        if z_gyro_fifo_enabled: 
            columns.append('gyro_z')
        df = pd.DataFrame(df, columns=columns)
        df.to_csv(target_file_paths[i], index=False)