import streamlit as st
from streamlit_autorefresh import st_autorefresh
from urllib3 import Timeout
from paho.mqtt import client as mqtt_client
import yaml
import shutil
import os
import socket
from datetime import datetime
from session_processor import merge_session, decode_session

#MPU6050 Constants
DLPF_ENUM = {
    '256' : 0,
    '188' : 1,
    '98'  : 2,
    '42'  : 3,
    '20'  : 4,
    '10'  : 5,
    '5'   : 6
}

CLOCK_ENUM = {
        'internal': 0, 
        'pll xgyro': 1,
        'pll ygyro': 2,
        'pll zgyro': 3,
        'pll ext32k': 4,
        'pll ext19m': 5,
        'keep reset': 7
}

GYRO_RANGE_ENUM = {
    '±250 Â°/s' : 0,
    '±500 Â°/s' : 1,
    '±1000 Â°/s' : 2,
    '±2000 Â°/s' : 3
}

ACCEL_RANGE_ENUM = {
    '±2g' : 0,
    '±4g' : 1,
    '±8g' : 2,
    '±16g' : 3 
}

#Config
@st.cache(allow_output_mutation=True)
def init_config():
    with open('config.yml', 'r') as f:
        cfg = yaml.safe_load(f)
        return cfg

cfg = init_config()

device_id            = cfg['device_id']
max_session_duration = cfg['max_session_duration']
refresh_interval     = cfg['refresh_interval']
topic_control        = cfg['mqtt']['topic']['control']
topic_info           = cfg['mqtt']['topic']['info']

def update_config():
    cfg['path']['sessions_path'] = st.session_state.sessions_path
    cfg['mqtt']['ip']            = st.session_state.mqtt_ip
    cfg['mqtt']['port']          = st.session_state.mqtt_port
    with open('config.yml', 'w') as f:
        yaml.dump(cfg, f, sort_keys=False)

#MQTT client
@st.cache(hash_funcs={dict: id})
def mqtt_connect(ip, port, device_id, to_subscribe):    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print('Connected to MQTT Broker!')
        else:
            print('Failed to connect, return code %d\n', rc)
    def on_message(client, userdata, msg):
        if msg.topic in topic_info:
            payload = yaml.safe_load(msg.payload.decode())
            type_, device_id_, text_ = payload['type'], payload['device_id'], payload['msg']
            log.lines.append([type_, device_id_, text_])
    if 'client' in locals() and client:
        client.loop_stop()
    client = mqtt_client.Client(device_id)
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(ip, port)
        for topic in to_subscribe:
            client.subscribe(topic)
        client.loop_start()
    except ConnectionRefusedError as e:
        print('ERROR:', e)
        log.lines.append(['error', device_id, str(e)])
    except socket.timeout as e:
        print('ERROR:', e)
        log.lines.append(['error', device_id, str(e)])
    return client

def publish(client, topic, msg):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f'Sended `{msg}` to topic `{topic}`')
    else:
        print(f'Failed to send message to topic {topic}')
        log.lines.append(['error', device_id, f'Failed to send message to topic {topic}'])

#Autorefresh
st_autorefresh(interval=refresh_interval, key="refresh_console")

#Sidebar log
class Log:
    def __init__(self):
        self.lines = []
        
@st.cache(allow_output_mutation=True)
def init_cache():
    return Log()

log = init_cache()
with st.sidebar:
    for line in log.lines[::-1]:
        formated_line = f'**{line[1]}**: {line[2]}\n'
        if line[0] == 'info':
            st.info(formated_line)
        elif line[0] == 'success':
            st.success(formated_line)
        elif line[0] == 'error':
            st.error(formated_line)

#Title
st.title('IMU Data Collection')

#MQTT Connection block
st.header('MQTT Conncetion')

mqtt_ip_col, mqtt_port_col = st.columns(2)

with mqtt_ip_col:
    mqtt_ip = str(st.text_input("Broker IP", cfg['mqtt']['ip'],
    on_change=update_config, key='mqtt_ip'))

with mqtt_port_col:
    mqtt_port = int(st.text_input("Port", cfg['mqtt']['port'],
    on_change=update_config, key='mqtt_port'))

client = mqtt_connect(mqtt_ip, mqtt_port, device_id, [topic_info])

if client.is_connected():
    st.success('Successfully connected to MQTT broker')
else:
    st.error('Cannot connect to MQTT broker')

#Sessions block
st.header('Manage sessions')
sessions_path = st.text_input("Sessions path", cfg['path']['sessions_path'],
    on_change=update_config, key='sessions_path')
session_name = st.text_input("Session name")
session_dir = os.path.join(sessions_path, session_name)

if session_name:
    if os.path.isdir(session_dir):
        session_info_path = os.path.join(sessions_path, session_name, 'metadata', 'session_info.yml')
        if os.path.isfile(session_info_path):
            with open(session_info_path, 'r') as f:
                info = yaml.safe_load(f)
            check = True
            for file_name in info['files'].values():
                if not os.path.isfile(os.path.join(session_dir, f'{file_name}.csv')):
                    check = False
                    break
            if check:
                st.success('Session is merged and decoded')
            else:
                st.info('Session is merged, but encoded')
            with st.expander("Session metadata"):
                info_col1, info_col2, info_col3 = st.columns(3)
                with info_col1:
                    st.write('Duration: ' + str(info['time']['duration']))
                    start = datetime.utcfromtimestamp(min(info['time']['start'].values()))
                    st.write('Date: ' + start.strftime('%Y-%m-%d'))
                    st.write('Start: ' + start.strftime('%H:%M:%S'))
                    st.write('Overflows: ' + str((sum(map(len, info['overflows'].values())))))
                for device, sensors in info['devices'].items():
                    with info_col2:
                        st.write('- ' + device)
                    for sensor in sensors:
                        with info_col3:
                            st.write('- ' + sensor)
            if not check:
                if st.button("Decode session"):
                    decode_session(session_dir)
                    st.experimental_rerun()
        else:
            st.info('Session parts aren\'t merged')
            if st.button("Merge session parts"):
                merge_session(session_dir)
                st.experimental_rerun()
            if st.button("Merge and decode"):
                merge_session(session_dir)
                decode_session(session_dir)
                st.experimental_rerun()

        if st.button("Delete session"):
            shutil.rmtree(session_dir)
            st.experimental_rerun()

    if not os.path.isdir(session_dir) and client.is_connected():
        with st.form("New session"):
            st.subheader('New session')
            duration = float(st.number_input("Duration", min_value=0, max_value=max_session_duration, value=1))
            submitted = st.form_submit_button("Start session")
            if submitted:
                if duration:
                    if os.path.isdir(session_dir):
                        shutil.rmtree(session_dir)
                    st.info('Session started. Please wait...')
                    payload = {'command': 'start_session', 'args': {'session_name': session_name, 'duration' : duration} }
                    payload = yaml.dump(payload)
                    publish(client, topic_control, payload)
                else:
                    st.error('Duration should be greater then zero')
else:
    st.caption('Enter session name, to create new session or manage the existing one')

# Command block
if client.is_connected():
    st.header('Commands')

    with st.expander("Ping sensors"):
        if st.button("Ping sensors"):
            payload = {"command":"ping_sensors"}
            payload = yaml.dump(payload)
            publish(client, topic_control, payload)
            st.info(f"Command sended: Ping sensors")

    with st.expander("Reset sensors"):
        sensor_id_reset = st.text_input("Sensor id", key='sensor_id_reset')
        if st.button("Reset sensor by id"):
            if sensor_id_reset:
                payload = {"command":"reset_sensor", "args":{'sensor_id':sensor_id_reset}}
                payload = yaml.dump(payload)
                publish(client, topic_control, payload)
                st.info(f"Command sended: Reset sensor \'{sensor_id_reset}\'")
            else:
                st.error('Sensor id must be specified!')
        if st.button("Reset all sensors"):
            payload = {"command":"reset_sensors"}
            payload = yaml.dump(payload)
            publish(client, topic_control, payload)
            st.info(f"Command sended: Reset all sensors")

    with st.expander("Calibrate sensors"):
        cal_col1, cal_col2 = st.columns(2)
        with cal_col2:
            max_iters = st.number_input("Number of iterations", 5, 500, 100)
            rough_iters = st.number_input("Number of \"rough\" iterations", 0, int(max_iters), 5)
            buffer_size = st.number_input("Buffer size", 1, 500, 150)
        with cal_col1:
            sensor_id_cal = st.text_input("Sensor id", key='sensor_id_calibrate')
            if st.button("Calibrate sensor by id"):
                if sensor_id_cal:
                    payload = {
                        "command": "calibrate_sensor",
                            "args": {
                                'sensor_id': sensor_id_cal,
                                'max_iters': max_iters,
                                'rough_iters': rough_iters,
                                'buffer_size': buffer_size
                                }
                        }
                    payload = yaml.dump(payload)
                    publish(client, topic_control, payload)
                    st.info(f'Command sended: Calibrate sensor \'{sensor_id_cal}\'')
                else:
                    st.error('Sensor id must be specified!')
            if st.button('Calibrate all sensors'):
                payload = {
                    "command":"calibrate_sensors", 
                        "args": {
                            'max_iters': max_iters, 
                            'rough_iters': rough_iters,
                            'buffer_size':buffer_size
                            }
                        }
                payload = yaml.dump(payload)
                publish(client, topic_control, payload)
                st.info(f'Command sended: Calibrate all sensors')
        st.caption('Higher number of iterations and larger buffer size will lead to higher accuracy, yet lower calibration speed')

    with st.expander("Configurate sensors"):            
        clock_type = st.selectbox("Clock source", CLOCK_ENUM.keys())
        dlpf = st.selectbox("DLPF mode", DLPF_ENUM.keys())
        rate_col1, rate_col2 = st.columns(2)
        with rate_col1:
            rate = st.number_input("Sample rate divider", 0, 255, 9)
        with rate_col2: 
            gyro_rate = 8000 if dlpf == '256' else 1000   
            st.metric("Sample rate", gyro_rate / (rate + 1))
        conf_col1, conf_col2 = st.columns(2)
        with conf_col1:
            accel_range = st.selectbox("Accel range", ACCEL_RANGE_ENUM.keys())
            gyro_range = st.selectbox("Gyro range", GYRO_RANGE_ENUM.keys())
        with conf_col2:
            accel_fifo_enabled = st.checkbox("Accel fifo enabled", True)
            x_gyro_fifo_enabled = st.checkbox("X gyro fifo enabled", True)
            y_gyro_fifo_enabled = st.checkbox("Y gyro fifo enabled", True)
            z_gyro_fifo_enabled = st.checkbox("Z gyro fifo enabled", True)
        sensor_id_conf = st.text_input("Sensor id", key='sensor_id_conf')
        if st.button("Configurate sensor by id"):
            if sensor_id_conf:
                payload = {
                    "command": "configurate_sensor",
                    "args": {
                        'sensor_id': sensor_id_conf,
                        'clock_source': CLOCK_ENUM[clock_type],
                        'dlpf_mode': DLPF_ENUM[dlpf],
                        'rate': rate,
                        'full_scale_accel_range': ACCEL_RANGE_ENUM[accel_range],
                        'full_scale_gyro_range': GYRO_RANGE_ENUM[gyro_range],
                        'accel_fifo_enabled': accel_fifo_enabled,
                        'x_gyro_fifo_enabled': x_gyro_fifo_enabled, 
                        'y_gyro_fifo_enabled': y_gyro_fifo_enabled,
                        'z_gyro_fifo_enabled': z_gyro_fifo_enabled
                        }
                    }
                payload = yaml.dump(payload)
                publish(client, topic_control, payload) 
                st.info(f'Command sended: Configurate sensor \'{sensor_id_conf}\'')
            else:
                st.error("Sensor id must be specified!")
        if st.button("Configurate all sensors"):
            payload = {
                "command": "configurate_sensors",
                "args": {
                    'clock_source': CLOCK_ENUM[clock_type],
                    'dlpf_mode': DLPF_ENUM[dlpf],
                    'rate': rate,
                    'full_scale_accel_range': ACCEL_RANGE_ENUM[accel_range],
                    'full_scale_gyro_range': GYRO_RANGE_ENUM[gyro_range],
                    'accel_fifo_enabled': accel_fifo_enabled,
                    'x_gyro_fifo_enabled': x_gyro_fifo_enabled,
                    'y_gyro_fifo_enabled': y_gyro_fifo_enabled,
                    'z_gyro_fifo_enabled': z_gyro_fifo_enabled
                    }
                }
            payload = yaml.dump(payload)
            publish(client, topic_control, payload)
            st.info('Command sended: Configurate all sensors')