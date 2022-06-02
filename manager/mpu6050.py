import I2C
import smbus
import struct

#converted from Jeff Rowberg code https://github.com/jrowberg/i2cdevlib/blob/master/Arduino/MPU6050/MPU6050.h

MPU6050_ADDRESS_AD0_LOW     = 0x68 # address pin low (GND), default for InvenSense evaluation board
MPU6050_ADDRESS_AD0_HIGH    = 0x69 # address pin high (VCC)
MPU6050_DEFAULT_ADDRESS     = MPU6050_ADDRESS_AD0_LOW

MPU6050_RA_XG_OFFS_TC       = 0x00 #[7] PWR_MODE, [6:1] XG_OFFS_TC, [0] OTP_BNK_VLD
MPU6050_RA_YG_OFFS_TC       = 0x01 #[7] PWR_MODE, [6:1] YG_OFFS_TC, [0] OTP_BNK_VLD
MPU6050_RA_ZG_OFFS_TC       = 0x02 #[7] PWR_MODE, [6:1] ZG_OFFS_TC, [0] OTP_BNK_VLD
MPU6050_RA_X_FINE_GAIN      = 0x03 #[7:0] X_FINE_GAIN
MPU6050_RA_Y_FINE_GAIN      = 0x04 #[7:0] Y_FINE_GAIN
MPU6050_RA_Z_FINE_GAIN      = 0x05 #[7:0] Z_FINE_GAIN
MPU6050_RA_XA_OFFS_H        = 0x06 #[15:0] XA_OFFS
MPU6050_RA_XA_OFFS_L_TC     = 0x07
MPU6050_RA_YA_OFFS_H        = 0x08 #[15:0] YA_OFFS
MPU6050_RA_YA_OFFS_L_TC     = 0x09
MPU6050_RA_ZA_OFFS_H        = 0x0A #[15:0] ZA_OFFS
MPU6050_RA_ZA_OFFS_L_TC     = 0x0B
MPU6050_RA_SELF_TEST_X      = 0x0D #[7:5] XA_TEST[4-2], [4:0] XG_TEST[4-0]
MPU6050_RA_SELF_TEST_Y      = 0x0E #[7:5] YA_TEST[4-2], [4:0] YG_TEST[4-0]
MPU6050_RA_SELF_TEST_Z      = 0x0F #[7:5] ZA_TEST[4-2], [4:0] ZG_TEST[4-0]
MPU6050_RA_SELF_TEST_A      = 0x10 #[5:4] XA_TEST[1-0], [3:2] YA_TEST[1-0], [1:0] ZA_TEST[1-0]
MPU6050_RA_XG_OFFS_USRH     = 0x13 #[15:0] XG_OFFS_USR
MPU6050_RA_XG_OFFS_USRL     = 0x14
MPU6050_RA_YG_OFFS_USRH     = 0x15 #[15:0] YG_OFFS_USR
MPU6050_RA_YG_OFFS_USRL     = 0x16
MPU6050_RA_ZG_OFFS_USRH     = 0x17 #[15:0] ZG_OFFS_USR
MPU6050_RA_ZG_OFFS_USRL     = 0x18
MPU6050_RA_SMPLRT_DIV       = 0x19
MPU6050_RA_CONFIG           = 0x1A
MPU6050_RA_GYRO_CONFIG      = 0x1B
MPU6050_RA_ACCEL_CONFIG     = 0x1C
MPU6050_RA_FF_THR           = 0x1D
MPU6050_RA_FF_DUR           = 0x1E
MPU6050_RA_MOT_THR          = 0x1F
MPU6050_RA_MOT_DUR          = 0x20
MPU6050_RA_ZRMOT_THR        = 0x21
MPU6050_RA_ZRMOT_DUR        = 0x22
MPU6050_RA_FIFO_EN          = 0x23
MPU6050_RA_I2C_MST_CTRL     = 0x24
MPU6050_RA_I2C_SLV0_ADDR    = 0x25
MPU6050_RA_I2C_SLV0_REG     = 0x26
MPU6050_RA_I2C_SLV0_CTRL    = 0x27
MPU6050_RA_I2C_SLV1_ADDR    = 0x28
MPU6050_RA_I2C_SLV1_REG     = 0x29
MPU6050_RA_I2C_SLV1_CTRL    = 0x2A
MPU6050_RA_I2C_SLV2_ADDR    = 0x2B
MPU6050_RA_I2C_SLV2_REG     = 0x2C
MPU6050_RA_I2C_SLV2_CTRL    = 0x2D
MPU6050_RA_I2C_SLV3_ADDR    = 0x2E
MPU6050_RA_I2C_SLV3_REG     = 0x2F
MPU6050_RA_I2C_SLV3_CTRL    = 0x30
MPU6050_RA_I2C_SLV4_ADDR    = 0x31
MPU6050_RA_I2C_SLV4_REG     = 0x32
MPU6050_RA_I2C_SLV4_DO      = 0x33
MPU6050_RA_I2C_SLV4_CTRL    = 0x34
MPU6050_RA_I2C_SLV4_DI      = 0x35
MPU6050_RA_I2C_MST_STATUS   = 0x36
MPU6050_RA_INT_PIN_CFG      = 0x37
MPU6050_RA_INT_ENABLE       = 0x38
MPU6050_RA_DMP_INT_STATUS   = 0x39
MPU6050_RA_INT_STATUS       = 0x3A
MPU6050_RA_ACCEL_XOUT_H     = 0x3B
MPU6050_RA_ACCEL_XOUT_L     = 0x3C
MPU6050_RA_ACCEL_YOUT_H     = 0x3D
MPU6050_RA_ACCEL_YOUT_L     = 0x3E
MPU6050_RA_ACCEL_ZOUT_H     = 0x3F
MPU6050_RA_ACCEL_ZOUT_L     = 0x40
MPU6050_RA_TEMP_OUT_H       = 0x41
MPU6050_RA_TEMP_OUT_L       = 0x42
MPU6050_RA_GYRO_XOUT_H      = 0x43
MPU6050_RA_GYRO_XOUT_L      = 0x44
MPU6050_RA_GYRO_YOUT_H      = 0x45
MPU6050_RA_GYRO_YOUT_L      = 0x46
MPU6050_RA_GYRO_ZOUT_H      = 0x47
MPU6050_RA_GYRO_ZOUT_L      = 0x48
MPU6050_RA_EXT_SENS_DATA_00 = 0x49
MPU6050_RA_EXT_SENS_DATA_01 = 0x4A
MPU6050_RA_EXT_SENS_DATA_02 = 0x4B
MPU6050_RA_EXT_SENS_DATA_03 = 0x4C
MPU6050_RA_EXT_SENS_DATA_04 = 0x4D
MPU6050_RA_EXT_SENS_DATA_05 = 0x4E
MPU6050_RA_EXT_SENS_DATA_06 = 0x4F
MPU6050_RA_EXT_SENS_DATA_07 = 0x50
MPU6050_RA_EXT_SENS_DATA_08 = 0x51
MPU6050_RA_EXT_SENS_DATA_09 = 0x52
MPU6050_RA_EXT_SENS_DATA_10 = 0x53
MPU6050_RA_EXT_SENS_DATA_11 = 0x54
MPU6050_RA_EXT_SENS_DATA_12 = 0x55
MPU6050_RA_EXT_SENS_DATA_13 = 0x56
MPU6050_RA_EXT_SENS_DATA_14 = 0x57
MPU6050_RA_EXT_SENS_DATA_15 = 0x58
MPU6050_RA_EXT_SENS_DATA_16 = 0x59
MPU6050_RA_EXT_SENS_DATA_17 = 0x5A
MPU6050_RA_EXT_SENS_DATA_18 = 0x5B
MPU6050_RA_EXT_SENS_DATA_19 = 0x5C
MPU6050_RA_EXT_SENS_DATA_20 = 0x5D
MPU6050_RA_EXT_SENS_DATA_21 = 0x5E
MPU6050_RA_EXT_SENS_DATA_22 = 0x5F
MPU6050_RA_EXT_SENS_DATA_23 = 0x60
MPU6050_RA_MOT_DETECT_STATUS    = 0x61
MPU6050_RA_I2C_SLV0_DO      = 0x63
MPU6050_RA_I2C_SLV1_DO      = 0x64
MPU6050_RA_I2C_SLV2_DO      = 0x65
MPU6050_RA_I2C_SLV3_DO      = 0x66
MPU6050_RA_I2C_MST_DELAY_CTRL   = 0x67
MPU6050_RA_SIGNAL_PATH_RESET    = 0x68
MPU6050_RA_MOT_DETECT_CTRL      = 0x69
MPU6050_RA_USER_CTRL        = 0x6A
MPU6050_RA_PWR_MGMT_1       = 0x6B
MPU6050_RA_PWR_MGMT_2       = 0x6C
MPU6050_RA_BANK_SEL         = 0x6D
MPU6050_RA_MEM_START_ADDR   = 0x6E
MPU6050_RA_MEM_R_W          = 0x6F
MPU6050_RA_DMP_CFG_1        = 0x70
MPU6050_RA_DMP_CFG_2        = 0x71
MPU6050_RA_FIFO_COUNTH      = 0x72
MPU6050_RA_FIFO_COUNTL      = 0x73
MPU6050_RA_FIFO_R_W         = 0x74
MPU6050_RA_WHO_AM_I         = 0x75

MPU6050_SELF_TEST_XA_1_BIT     = 0x07
MPU6050_SELF_TEST_XA_1_LENGTH  = 0x03
MPU6050_SELF_TEST_XA_2_BIT     = 0x05
MPU6050_SELF_TEST_XA_2_LENGTH  = 0x02
MPU6050_SELF_TEST_YA_1_BIT     = 0x07
MPU6050_SELF_TEST_YA_1_LENGTH  = 0x03
MPU6050_SELF_TEST_YA_2_BIT     = 0x03
MPU6050_SELF_TEST_YA_2_LENGTH  = 0x02
MPU6050_SELF_TEST_ZA_1_BIT     = 0x07
MPU6050_SELF_TEST_ZA_1_LENGTH  = 0x03
MPU6050_SELF_TEST_ZA_2_BIT     = 0x01
MPU6050_SELF_TEST_ZA_2_LENGTH  = 0x02

MPU6050_SELF_TEST_XG_1_BIT     = 0x04
MPU6050_SELF_TEST_XG_1_LENGTH  = 0x05
MPU6050_SELF_TEST_YG_1_BIT     = 0x04
MPU6050_SELF_TEST_YG_1_LENGTH  = 0x05
MPU6050_SELF_TEST_ZG_1_BIT     = 0x04
MPU6050_SELF_TEST_ZG_1_LENGTH  = 0x05

MPU6050_TC_PWR_MODE_BIT     = 7
MPU6050_TC_OFFSET_BIT       = 6
MPU6050_TC_OFFSET_LENGTH    = 6
MPU6050_TC_OTP_BNK_VLD_BIT  = 0

MPU6050_VDDIO_LEVEL_VLOGIC  = 0
MPU6050_VDDIO_LEVEL_VDD     = 1

MPU6050_CFG_EXT_SYNC_SET_BIT    = 5
MPU6050_CFG_EXT_SYNC_SET_LENGTH = 3
MPU6050_CFG_DLPF_CFG_BIT    = 2
MPU6050_CFG_DLPF_CFG_LENGTH = 3

MPU6050_EXT_SYNC_DISABLED       = 0x0
MPU6050_EXT_SYNC_TEMP_OUT_L     = 0x1
MPU6050_EXT_SYNC_GYRO_XOUT_L    = 0x2
MPU6050_EXT_SYNC_GYRO_YOUT_L    = 0x3
MPU6050_EXT_SYNC_GYRO_ZOUT_L    = 0x4
MPU6050_EXT_SYNC_ACCEL_XOUT_L   = 0x5
MPU6050_EXT_SYNC_ACCEL_YOUT_L   = 0x6
MPU6050_EXT_SYNC_ACCEL_ZOUT_L   = 0x7

MPU6050_DLPF_BW_256         = 0x00
MPU6050_DLPF_BW_188         = 0x01
MPU6050_DLPF_BW_98          = 0x02
MPU6050_DLPF_BW_42          = 0x03
MPU6050_DLPF_BW_20          = 0x04
MPU6050_DLPF_BW_10          = 0x05
MPU6050_DLPF_BW_5           = 0x06

MPU6050_GCONFIG_FS_SEL_BIT      = 4
MPU6050_GCONFIG_FS_SEL_LENGTH   = 2

MPU6050_GYRO_FS_250         = 0x00
MPU6050_GYRO_FS_500         = 0x01
MPU6050_GYRO_FS_1000        = 0x02
MPU6050_GYRO_FS_2000        = 0x03

MPU6050_ACONFIG_XA_ST_BIT           = 7
MPU6050_ACONFIG_YA_ST_BIT           = 6
MPU6050_ACONFIG_ZA_ST_BIT           = 5
MPU6050_ACONFIG_AFS_SEL_BIT         = 4
MPU6050_ACONFIG_AFS_SEL_LENGTH      = 2
MPU6050_ACONFIG_ACCEL_HPF_BIT       = 2
MPU6050_ACONFIG_ACCEL_HPF_LENGTH    = 3

MPU6050_ACCEL_FS_2          = 0x00
MPU6050_ACCEL_FS_4          = 0x01
MPU6050_ACCEL_FS_8          = 0x02
MPU6050_ACCEL_FS_16         = 0x03

MPU6050_DHPF_RESET          = 0x00
MPU6050_DHPF_5              = 0x01
MPU6050_DHPF_2P5            = 0x02
MPU6050_DHPF_1P25           = 0x03
MPU6050_DHPF_0P63           = 0x04
MPU6050_DHPF_HOLD           = 0x07

MPU6050_TEMP_FIFO_EN_BIT    = 7
MPU6050_XG_FIFO_EN_BIT      = 6
MPU6050_YG_FIFO_EN_BIT      = 5
MPU6050_ZG_FIFO_EN_BIT      = 4
MPU6050_ACCEL_FIFO_EN_BIT   = 3
MPU6050_SLV2_FIFO_EN_BIT    = 2
MPU6050_SLV1_FIFO_EN_BIT    = 1
MPU6050_SLV0_FIFO_EN_BIT    = 0

MPU6050_MULT_MST_EN_BIT     = 7
MPU6050_WAIT_FOR_ES_BIT     = 6
MPU6050_SLV_3_FIFO_EN_BIT   = 5
MPU6050_I2C_MST_P_NSR_BIT   = 4
MPU6050_I2C_MST_CLK_BIT     = 3
MPU6050_I2C_MST_CLK_LENGTH  = 4

MPU6050_CLOCK_DIV_348       = 0x0
MPU6050_CLOCK_DIV_333       = 0x1
MPU6050_CLOCK_DIV_320       = 0x2
MPU6050_CLOCK_DIV_308       = 0x3
MPU6050_CLOCK_DIV_296       = 0x4
MPU6050_CLOCK_DIV_286       = 0x5
MPU6050_CLOCK_DIV_276       = 0x6
MPU6050_CLOCK_DIV_267       = 0x7
MPU6050_CLOCK_DIV_258       = 0x8
MPU6050_CLOCK_DIV_500       = 0x9
MPU6050_CLOCK_DIV_471       = 0xA
MPU6050_CLOCK_DIV_444       = 0xB
MPU6050_CLOCK_DIV_421       = 0xC
MPU6050_CLOCK_DIV_400       = 0xD
MPU6050_CLOCK_DIV_381       = 0xE
MPU6050_CLOCK_DIV_364       = 0xF

MPU6050_I2C_SLV_RW_BIT      = 7
MPU6050_I2C_SLV_ADDR_BIT    = 6
MPU6050_I2C_SLV_ADDR_LENGTH = 7
MPU6050_I2C_SLV_EN_BIT      = 7
MPU6050_I2C_SLV_BYTE_SW_BIT = 6
MPU6050_I2C_SLV_REG_DIS_BIT = 5
MPU6050_I2C_SLV_GRP_BIT     = 4
MPU6050_I2C_SLV_LEN_BIT     = 3
MPU6050_I2C_SLV_LEN_LENGTH  = 4

MPU6050_I2C_SLV4_RW_BIT         = 7
MPU6050_I2C_SLV4_ADDR_BIT       = 6
MPU6050_I2C_SLV4_ADDR_LENGTH    = 7
MPU6050_I2C_SLV4_EN_BIT         = 7
MPU6050_I2C_SLV4_INT_EN_BIT     = 6
MPU6050_I2C_SLV4_REG_DIS_BIT    = 5
MPU6050_I2C_SLV4_MST_DLY_BIT    = 4
MPU6050_I2C_SLV4_MST_DLY_LENGTH = 5

MPU6050_MST_PASS_THROUGH_BIT    = 7
MPU6050_MST_I2C_SLV4_DONE_BIT   = 6
MPU6050_MST_I2C_LOST_ARB_BIT    = 5
MPU6050_MST_I2C_SLV4_NACK_BIT   = 4
MPU6050_MST_I2C_SLV3_NACK_BIT   = 3
MPU6050_MST_I2C_SLV2_NACK_BIT   = 2
MPU6050_MST_I2C_SLV1_NACK_BIT   = 1
MPU6050_MST_I2C_SLV0_NACK_BIT   = 0

MPU6050_INTCFG_INT_LEVEL_BIT        = 7
MPU6050_INTCFG_INT_OPEN_BIT         = 6
MPU6050_INTCFG_LATCH_INT_EN_BIT     = 5
MPU6050_INTCFG_INT_RD_CLEAR_BIT     = 4
MPU6050_INTCFG_FSYNC_INT_LEVEL_BIT  = 3
MPU6050_INTCFG_FSYNC_INT_EN_BIT     = 2
MPU6050_INTCFG_I2C_BYPASS_EN_BIT    = 1
MPU6050_INTCFG_CLKOUT_EN_BIT        = 0

MPU6050_INTMODE_ACTIVEHIGH  = 0x00
MPU6050_INTMODE_ACTIVELOW   = 0x01

MPU6050_INTDRV_PUSHPULL     = 0x00
MPU6050_INTDRV_OPENDRAIN    = 0x01

MPU6050_INTLATCH_50USPULSE  = 0x00
MPU6050_INTLATCH_WAITCLEAR  = 0x01

MPU6050_INTCLEAR_STATUSREAD = 0x00
MPU6050_INTCLEAR_ANYREAD    = 0x01

MPU6050_INTERRUPT_FF_BIT            = 7
MPU6050_INTERRUPT_MOT_BIT           = 6
MPU6050_INTERRUPT_ZMOT_BIT          = 5
MPU6050_INTERRUPT_FIFO_OFLOW_BIT    = 4
MPU6050_INTERRUPT_I2C_MST_INT_BIT   = 3
MPU6050_INTERRUPT_PLL_RDY_INT_BIT   = 2
MPU6050_INTERRUPT_DMP_INT_BIT       = 1
MPU6050_INTERRUPT_DATA_RDY_BIT      = 0

# TODO: figure out what these actually do
# UMPL source code is not very obivous
MPU6050_DMPINT_5_BIT            = 5
MPU6050_DMPINT_4_BIT            = 4
MPU6050_DMPINT_3_BIT            = 3
MPU6050_DMPINT_2_BIT            = 2
MPU6050_DMPINT_1_BIT            = 1
MPU6050_DMPINT_0_BIT            = 0

MPU6050_MOTION_MOT_XNEG_BIT     = 7
MPU6050_MOTION_MOT_XPOS_BIT     = 6
MPU6050_MOTION_MOT_YNEG_BIT     = 5
MPU6050_MOTION_MOT_YPOS_BIT     = 4
MPU6050_MOTION_MOT_ZNEG_BIT     = 3
MPU6050_MOTION_MOT_ZPOS_BIT     = 2
MPU6050_MOTION_MOT_ZRMOT_BIT    = 0

MPU6050_DELAYCTRL_DELAY_ES_SHADOW_BIT   = 7
MPU6050_DELAYCTRL_I2C_SLV4_DLY_EN_BIT   = 4
MPU6050_DELAYCTRL_I2C_SLV3_DLY_EN_BIT   = 3
MPU6050_DELAYCTRL_I2C_SLV2_DLY_EN_BIT   = 2
MPU6050_DELAYCTRL_I2C_SLV1_DLY_EN_BIT   = 1
MPU6050_DELAYCTRL_I2C_SLV0_DLY_EN_BIT   = 0

MPU6050_PATHRESET_GYRO_RESET_BIT    = 2
MPU6050_PATHRESET_ACCEL_RESET_BIT   = 1
MPU6050_PATHRESET_TEMP_RESET_BIT    = 0

MPU6050_DETECT_ACCEL_ON_DELAY_BIT       = 5
MPU6050_DETECT_ACCEL_ON_DELAY_LENGTH    = 2
MPU6050_DETECT_FF_COUNT_BIT             = 3
MPU6050_DETECT_FF_COUNT_LENGTH          = 2
MPU6050_DETECT_MOT_COUNT_BIT            = 1
MPU6050_DETECT_MOT_COUNT_LENGTH         = 2

MPU6050_DETECT_DECREMENT_RESET  = 0x0
MPU6050_DETECT_DECREMENT_1      = 0x1
MPU6050_DETECT_DECREMENT_2      = 0x2
MPU6050_DETECT_DECREMENT_4      = 0x3

MPU6050_USERCTRL_DMP_EN_BIT             = 7
MPU6050_USERCTRL_FIFO_EN_BIT            = 6
MPU6050_USERCTRL_I2C_MST_EN_BIT         = 5
MPU6050_USERCTRL_I2C_IF_DIS_BIT         = 4
MPU6050_USERCTRL_DMP_RESET_BIT          = 3
MPU6050_USERCTRL_FIFO_RESET_BIT         = 2
MPU6050_USERCTRL_I2C_MST_RESET_BIT      = 1
MPU6050_USERCTRL_SIG_COND_RESET_BIT     = 0

MPU6050_PWR1_DEVICE_RESET_BIT   = 7
MPU6050_PWR1_SLEEP_BIT          = 6
MPU6050_PWR1_CYCLE_BIT          = 5
MPU6050_PWR1_TEMP_DIS_BIT       = 3
MPU6050_PWR1_CLKSEL_BIT         = 2
MPU6050_PWR1_CLKSEL_LENGTH      = 3

MPU6050_CLOCK_INTERNAL          = 0x00
MPU6050_CLOCK_PLL_XGYRO         = 0x01
MPU6050_CLOCK_PLL_YGYRO         = 0x02
MPU6050_CLOCK_PLL_ZGYRO         = 0x03
MPU6050_CLOCK_PLL_EXT32K        = 0x04
MPU6050_CLOCK_PLL_EXT19M        = 0x05
MPU6050_CLOCK_KEEP_RESET        = 0x07

MPU6050_PWR2_LP_WAKE_CTRL_BIT       = 7
MPU6050_PWR2_LP_WAKE_CTRL_LENGTH    = 2
MPU6050_PWR2_STBY_XA_BIT            = 5
MPU6050_PWR2_STBY_YA_BIT            = 4
MPU6050_PWR2_STBY_ZA_BIT            = 3
MPU6050_PWR2_STBY_XG_BIT            = 2
MPU6050_PWR2_STBY_YG_BIT            = 1
MPU6050_PWR2_STBY_ZG_BIT            = 0

MPU6050_WAKE_FREQ_1P25      = 0x0
MPU6050_WAKE_FREQ_2P5       = 0x1
MPU6050_WAKE_FREQ_5         = 0x2
MPU6050_WAKE_FREQ_10        = 0x3

MPU6050_BANKSEL_PRFTCH_EN_BIT       = 6
MPU6050_BANKSEL_CFG_USER_BANK_BIT   = 5
MPU6050_BANKSEL_MEM_SEL_BIT         = 4
MPU6050_BANKSEL_MEM_SEL_LENGTH       =5

MPU6050_WHO_AM_I_BIT        = 6
MPU6050_WHO_AM_I_LENGTH     = 6

MPU6050_DMP_MEMORY_BANKS        = 8
MPU6050_DMP_MEMORY_BANK_SIZE    = 256
MPU6050_DMP_MEMORY_CHUNK_SIZE   = 16

MPU6050_DEFAULT_GYRO_OUTPUT_RATE = 8000
MPU6050_DLPF_GYRO_OUTPUT_RATE = 1000

MPU6050_GYRO_OFFSET_FACTOR = 4
MPU6050_ACCEL_OFFSET_FACTOR = 8

MPU6050_TEMP_FACTOR = 1.0 / 340.0
MPU6050_TEMP_OFFSET = 36.53

class MPU6050_Base:
    ZERO_REGISTER = [
        MPU6050_RA_FF_THR,
        MPU6050_RA_FF_DUR,
        MPU6050_RA_MOT_THR,
        MPU6050_RA_MOT_DUR,
        MPU6050_RA_ZRMOT_THR,
        MPU6050_RA_ZRMOT_DUR,
        MPU6050_RA_I2C_MST_CTRL,
        MPU6050_RA_I2C_SLV0_ADDR,
        MPU6050_RA_I2C_SLV0_REG,
        MPU6050_RA_I2C_SLV0_CTRL,
        MPU6050_RA_I2C_SLV1_ADDR,
        MPU6050_RA_I2C_SLV1_REG,
        MPU6050_RA_I2C_SLV1_CTRL,
        MPU6050_RA_I2C_SLV2_ADDR,
        MPU6050_RA_I2C_SLV2_REG,
        MPU6050_RA_I2C_SLV2_CTRL,
        MPU6050_RA_I2C_SLV3_ADDR,
        MPU6050_RA_I2C_SLV3_REG,
        MPU6050_RA_I2C_SLV3_CTRL,
        MPU6050_RA_I2C_SLV4_ADDR,
        MPU6050_RA_I2C_SLV4_REG,
        MPU6050_RA_I2C_SLV4_DO,
        MPU6050_RA_I2C_SLV4_CTRL,
        MPU6050_RA_I2C_SLV4_DI,
        MPU6050_RA_I2C_SLV0_DO,
        MPU6050_RA_I2C_SLV1_DO,
        MPU6050_RA_I2C_SLV2_DO,
        MPU6050_RA_I2C_SLV3_DO,
        MPU6050_RA_I2C_MST_DELAY_CTRL,
        MPU6050_RA_SIGNAL_PATH_RESET,
        MPU6050_RA_MOT_DETECT_CTRL]
    
    def __init__(self, bus_id, address=MPU6050_DEFAULT_ADDRESS):
        self.bus_id = bus_id
        self.address = address
        self._bus = smbus.SMBus(self.bus_id)

    def test_connection(self):
        try:
            return self.get_device_id() == 0x34
        except OSError:
            return False
    
    def get_device_id(self):
        return I2C.read_bits(self._bus, self.address, MPU6050_RA_WHO_AM_I, MPU6050_WHO_AM_I_BIT, MPU6050_WHO_AM_I_LENGTH)
          
    def get_rate(self):
        return I2C.read_byte(self._bus, self.address, MPU6050_RA_SMPLRT_DIV)

    def set_rate(self, rate):
        I2C.write_byte(self._bus, self.address, MPU6050_RA_SMPLRT_DIV, rate)
    
    def get_clock_source(self):
        return I2C.read_bits(self._bus, self.address, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CLKSEL_BIT, MPU6050_PWR1_CLKSEL_LENGTH)
    
    def set_clock_source(self, source):
        I2C.write_bits(self._bus, self.address, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CLKSEL_BIT, MPU6050_PWR1_CLKSEL_LENGTH, source)
    
    def get_full_scale_gyro_range(self):
        return I2C.read_bits(self._bus, self.address, MPU6050_RA_GYRO_CONFIG, MPU6050_GCONFIG_FS_SEL_BIT, MPU6050_GCONFIG_FS_SEL_LENGTH)
    
    def set_full_scale_gyro_range(self, range):
        I2C.write_bits(self._bus, self.address, MPU6050_RA_GYRO_CONFIG, MPU6050_GCONFIG_FS_SEL_BIT, MPU6050_GCONFIG_FS_SEL_LENGTH, range)
        
    def get_full_scale_accel_range(self):
        return I2C.read_bits(self._bus, self.address, MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_AFS_SEL_BIT, MPU6050_ACONFIG_AFS_SEL_LENGTH)
    
    def set_full_scale_accel_range(self, range):
        I2C.write_bits(self._bus, self.address, MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_AFS_SEL_BIT, MPU6050_ACONFIG_AFS_SEL_LENGTH, range)
        
    def get_sleep_enabled(self):
        return I2C.read_bit(self._bus, self.address, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_SLEEP_BIT)
    
    def set_sleep_enabled(self, enabled):
        I2C.write_bits(self._bus, self.address, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_SLEEP_BIT, 1, enabled)
        
    def get_dlpf_mode(self):
        return I2C.read_bits(self._bus, self.address, MPU6050_RA_CONFIG, MPU6050_CFG_DLPF_CFG_BIT, MPU6050_CFG_DLPF_CFG_LENGTH)

    def set_dlpf_mode(self, mode):
        I2C.write_bits(self._bus, self.address, MPU6050_RA_CONFIG, MPU6050_CFG_DLPF_CFG_BIT, MPU6050_CFG_DLPF_CFG_LENGTH, mode)
    
    def get_temp_sensor_enabled(self):
        return I2C.read_bit(self._bus, self.address, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_TEMP_DIS_BIT) == 0 # 1 is actually disabled here

    def set_temp_sensor_enabled(self, enabled):
        # 1 is actually disabled here
        I2C.write_bit(self._bus, self.address, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_TEMP_DIS_BIT, not enabled)
    
    def get_temp_fifo_enabled(self):
        return I2C.read_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_TEMP_FIFO_EN_BIT)

    def set_temp_fifo_enabled(self, enabled):
        I2C.write_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_TEMP_FIFO_EN_BIT, enabled)

    def get_x_gyro_fifo_enabled(self):
        return I2C.read_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_XG_FIFO_EN_BIT)

    def set_x_gyro_fifo_enabled(self, enabled):
        I2C.write_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_XG_FIFO_EN_BIT, enabled)

    def get_y_gyro_fifo_enabled(self):
        return I2C.read_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_YG_FIFO_EN_BIT)

    def set_y_gyro_fifo_enabled(self, enabled):
        I2C.write_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_YG_FIFO_EN_BIT, enabled)

    def get_z_gyro_fifo_enabled(self):
        return I2C.read_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_ZG_FIFO_EN_BIT)

    def set_z_gyro_fifo_enabled(self, enabled):
        I2C.write_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_ZG_FIFO_EN_BIT, enabled)

    def get_accel_fifo_enabled(self):
        return I2C.read_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_ACCEL_FIFO_EN_BIT)

    def set_accel_fifo_enabled(self, enabled):
        I2C.write_bit(self._bus, self.address, MPU6050_RA_FIFO_EN, MPU6050_ACCEL_FIFO_EN_BIT, enabled)

    def get_motion_6(self):
        buffer = I2C.read_bytes(self._bus, self.address, MPU6050_RA_ACCEL_XOUT_H, 14)
        buffer = struct.unpack('>hhhhhhh', memoryview(bytearray(buffer)))
        ax, ay, az, _, gx, gy, gz = buffer
        return ax, ay, az, gx, gy, gz

    def get_acceleration(self):
        buffer = I2C.read_bytes(self._bus, self.address, MPU6050_RA_ACCEL_XOUT_H, 6)
        buffer = struct.unpack('>hhh', memoryview(bytearray(buffer)))
        x, y, z = buffer
        return x, y, z

    def get_acceleration_x(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_ACCEL_XOUT_H)

    def get_acceleration_y(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_ACCEL_YOUT_H)

    def get_acceleration_z(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_ACCEL_ZOUT_H)

    def get_temperature(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_TEMP_OUT_H)

    def get_rotation(self, x, y, z):
        buffer = I2C.read_bytes(self._bus, self.address, MPU6050_RA_GYRO_XOUT_H, 6)
        buffer = struct.unpack('>hhh', memoryview(bytearray(buffer)))
        x, y, z = buffer
        return x, y, z

    def get_rotation_x(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_GYRO_XOUT_H)

    def get_rotation_y(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_GYRO_YOUT_H)

    def get_rotation_z(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_GYRO_ZOUT_H)

    def get_fifo_enabled(self):
        return I2C.read_bit(self._bus, self.address, MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_EN_BIT)

    def set_fifo_enabled(self, enabled):
        I2C.write_bit(self._bus, self.address, MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_EN_BIT, enabled)
        
    def reset_fifo(self):
        I2C.write_bit(self._bus, self.address, MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_RESET_BIT, True)

    def reset_sensors(self):
        I2C.write_bit(self._bus, self.address, MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_SIG_COND_RESET_BIT, True)

    def reset(self):
        I2C.write_bit(self._bus, self.address, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_DEVICE_RESET_BIT, True)
        for reg in self.ZERO_REGISTER:
            I2C.write_byte(self._bus, self.address, reg, 0)

    def get_fifo_count(self):
        buffer = I2C.read_bytes(self._bus, self.address, MPU6050_RA_FIFO_COUNTH, 2)
        return ((buffer[0]) << 8) | buffer[1]

    def get_fifo_byte(self):
        return I2C.read_byte(self._bus, self.address, MPU6050_RA_FIFO_R_W)

    def get_fifo_bytes(self, length):
        return I2C.read_bytes(self._bus, self.address, MPU6050_RA_FIFO_R_W, length)
    
    def get_accel_offset_x(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_XA_OFFS_H)
    
    def set_accel_offset_x(self, offset):
        return I2C.write_signed_word(self._bus, self.address, MPU6050_RA_XA_OFFS_H, offset)
    
    def get_accel_offset_y(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_YA_OFFS_H)
    
    def set_accel_offset_y(self, offset):
        return I2C.write_signed_word(self._bus, self.address, MPU6050_RA_YA_OFFS_H, offset)
    
    def get_accel_offset_z(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_ZA_OFFS_H)
    
    def set_accel_offset_z(self, offset):
        return I2C.write_signed_word(self._bus, self.address, MPU6050_RA_ZA_OFFS_H, offset)
    
    def get_gyro_offset_x(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_XG_OFFS_USRH)
    
    def set_gyro_offset_x(self, offset):
        return I2C.write_signed_word(self._bus, self.address, MPU6050_RA_XG_OFFS_USRH, offset)
    
    def get_gyro_offset_y(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_YG_OFFS_USRH)
    
    def set_gyro_offset_y(self, offset):
        return I2C.write_signed_word(self._bus, self.address, MPU6050_RA_YG_OFFS_USRH, offset)
    
    def get_gyro_offset_z(self):
        return I2C.read_signed_word(self._bus, self.address, MPU6050_RA_ZG_OFFS_USRH)
    
    def set_gyro_offset_z(self, offset):
        return I2C.write_signed_word(self._bus, self.address, MPU6050_RA_ZG_OFFS_USRH, offset)
    
class MPU6050:
    def __init__(self, sensor_id, bus_id, address=MPU6050_DEFAULT_ADDRESS):
        self.id = sensor_id
        self._mpu6050 = MPU6050_Base(bus_id, address)
        self._mpu6050.set_sleep_enabled(False)
        self._mpu6050.set_fifo_enabled(True)
        self._accel_fifo_enabled = self._mpu6050.get_accel_fifo_enabled()
        self._x_gyro_fifo_enabled = self._mpu6050.get_x_gyro_fifo_enabled()
        self._y_gyro_fifo_enabled = self._mpu6050.get_y_gyro_fifo_enabled()
        self._z_gyro_fifo_enabled = self._mpu6050.get_z_gyro_fifo_enabled()
        self._dlpf_mode = self._mpu6050.get_dlpf_mode()
        self._full_scale_accel_range = self._mpu6050.get_full_scale_accel_range()
        self._full_scale_gyro_range = self._mpu6050.get_full_scale_gyro_range()
        self._clock_source = self._mpu6050.get_clock_source()
        self._rate = self._mpu6050.get_rate()
        if self._dlpf_mode == MPU6050_DLPF_BW_256:
            self._gyro_output_rate = MPU6050_DEFAULT_GYRO_OUTPUT_RATE
        else:
            self._gyro_output_rate = MPU6050_DLPF_GYRO_OUTPUT_RATE
    
    def reset(self):
        self._mpu6050.reset()
        self._mpu6050.set_sleep_enabled(False)
        self._mpu6050.set_fifo_enabled(True)
        self._accel_fifo_enabled = False
        self._x_gyro_fifo_enabled = False
        self._y_gyro_fifo_enabled = False
        self._z_gyro_fifo_enabled = False
        self._dlpf_mode = MPU6050_DLPF_BW_256
        self._full_scale_accel_range = MPU6050_ACCEL_FS_2
        self._full_scale_gyro_range = MPU6050_GYRO_FS_250
        self._clock_source = MPU6050_CLOCK_INTERNAL
        self._rate = 0
        self._gyro_output_rate = MPU6050_DEFAULT_GYRO_OUTPUT_RATE
    
    @staticmethod
    def accel_range_to_factor(range_):
        if range_ == MPU6050_ACCEL_FS_2:
            return 2 / 32768.0
        elif range_ == MPU6050_ACCEL_FS_4:
            return 4 / 32768.0
        elif range_ == MPU6050_ACCEL_FS_8:
            return 8 / 32768.0
        elif range_ == MPU6050_ACCEL_FS_16:
            return 16 / 32768.0
        
    @staticmethod
    def gyro_range_to_factor(range_):
        if range_ == MPU6050_GYRO_FS_250:
            return 250 / 32768.0
        elif range_ == MPU6050_GYRO_FS_500:
            return 500 / 32768.0
        elif range_ == MPU6050_GYRO_FS_1000:
            return 1000 / 32768.0
        elif range_ == MPU6050_GYRO_FS_2000:
            return 2000 / 32768.0
    
    @property
    def rate(self):
        return self._mpu6050.get_rate()
    
    @rate.setter
    def rate(self, rate):
        self._rate = rate
        self._mpu6050.set_rate(rate)
    
    @property
    def sample_rate(self):
        return self._gyro_output_rate / (1 + self._rate)
    
    @property
    def clock_source(self):
        return self._clock_source
        
    @clock_source.setter
    def clock_source(self, source):
        self._clock_source = source
        self._mpu6050.set_clock_source(source)
    
    @property
    def full_scale_gyro_range(self):
        return self._full_scale_gyro_range
       
    @full_scale_gyro_range.setter
    def full_scale_gyro_range(self, range_):
        self._full_scale_gyro_range = range_
        self._mpu6050.set_full_scale_gyro_range(range_)
    
    @property
    def full_scale_accel_range(self):
        return self._full_scale_accel_range
    
    @full_scale_accel_range.setter
    def full_scale_accel_range(self, range_):
        self._full_scale_accel_range = range_
        self._mpu6050.set_full_scale_accel_range(range_)
    
    @property
    def gyro_factor(self):
        return MPU6050.gyro_range_to_factor(self._full_scale_gyro_range)

    @property
    def accel_factor(self):
        return MPU6050.accel_range_to_factor(self._full_scale_accel_range)
    
    @property
    def dlpf_mode(self):
        return self._dlpf_mode
    
    @dlpf_mode.setter
    def dlpf_mode(self, mode):
        self._dlpf_mode = mode
        self._mpu6050.set_dlpf_mode(mode)
        if mode == MPU6050_DLPF_BW_256:
            self._gyro_output_rate = MPU6050_DEFAULT_GYRO_OUTPUT_RATE
        else:
            self._gyro_output_rate = MPU6050_DLPF_GYRO_OUTPUT_RATE
    
    def get_temperature(self):
        return self._mpu6050.get_temperature() * MPU6050_TEMP_FACTOR + MPU6050_TEMP_OFFSET
    
    def _calibrate_axis(self, get_x, set_offset, offset_factor, max_iters, rough_iters, buffer_size,
                         epsilon, mu, v_threshold, target=0):
        v = 0
        offset = 0
        set_offset(0)
        for i in range(max_iters):
            delta = sum([get_x() for i in range(buffer_size)]) 
            delta /= buffer_size
            delta -= target
            if i < rough_iters:
                offset += mu * v - delta
            else:
                offset += mu * v - delta * epsilon
            v = mu * v - delta * epsilon
            if abs(delta) < offset_factor and abs(v) < v_threshold:
                break
            set_offset(int(offset / offset_factor))
            
    def calibrate(self, max_iters, rough_iters, buffer_size, epsilon=0.1, mu=0.5, v_threshold=0.05):
        self._calibrate_axis(self._mpu6050.get_acceleration_x, self._mpu6050.set_accel_offset_x, MPU6050_ACCEL_OFFSET_FACTOR,
                               max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold)
        self._calibrate_axis(self._mpu6050.get_acceleration_y, self._mpu6050.set_accel_offset_y, MPU6050_ACCEL_OFFSET_FACTOR,
                               max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold)
        self._calibrate_axis(self._mpu6050.get_acceleration_z, self._mpu6050.set_accel_offset_z, MPU6050_ACCEL_OFFSET_FACTOR,
                               max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold,
                               target=-16384)
        self._calibrate_axis(self._mpu6050.get_rotation_x, self._mpu6050.set_gyro_offset_x, MPU6050_GYRO_OFFSET_FACTOR,
                               max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold)
        self._calibrate_axis(self._mpu6050.get_rotation_y, self._mpu6050.set_gyro_offset_y, MPU6050_GYRO_OFFSET_FACTOR,
                               max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold)
        self._calibrate_axis(self._mpu6050.get_rotation_z, self._mpu6050.set_gyro_offset_z, MPU6050_GYRO_OFFSET_FACTOR,
                               max_iters, rough_iters, buffer_size, epsilon, mu, v_threshold)
    
    @property
    def x_gyro_fifo_enabled(self):
        return self._x_gyro_fifo_enabled
    
    @x_gyro_fifo_enabled.setter
    def x_gyro_fifo_enabled(self, enabled):
        self._x_gyro_fifo_enabled = enabled
        self._mpu6050.set_x_gyro_fifo_enabled(enabled)
    
    @property
    def y_gyro_fifo_enabled(self):
        return self._y_gyro_fifo_enabled
    
    @y_gyro_fifo_enabled.setter
    def y_gyro_fifo_enabled(self, enabled):
        self._y_gyro_fifo_enabled = enabled
        self._mpu6050.set_y_gyro_fifo_enabled(enabled)
    
    @property
    def z_gyro_fifo_enabled(self):
        return self._z_gyro_fifo_enabled
    
    @z_gyro_fifo_enabled.setter
    def z_gyro_fifo_enabled(self, enabled):
        self._z_gyro_fifo_enabled = enabled
        self._mpu6050.set_z_gyro_fifo_enabled(enabled)
    
    @property
    def accel_fifo_enabled(self):
        return self._accel_fifo_enabled
    
    @accel_fifo_enabled.setter
    def accel_fifo_enabled(self, enabled):
        self._accel_fifo_enabled = enabled
        self._mpu6050.set_accel_fifo_enabled(enabled)
    
    @property
    def package_length(self):
        package_byte_length = 0
        if self._accel_fifo_enabled:
            package_byte_length += 6
        if self._x_gyro_fifo_enabled:
            package_byte_length += 2
        if self._y_gyro_fifo_enabled:
            package_byte_length += 2
        if self._z_gyro_fifo_enabled:
            package_byte_length += 2
        return package_byte_length
    
    def get_fifo_count(self):
        return self._mpu6050.get_fifo_count()

    def get_fifo_byte(self):
        return self._mpu6050.get_fifo_byte()

    def get_fifo_bytes(self, length):
        return self._mpu6050.get_fifo_bytes(length)
    
    def reset_fifo(self):
        self._mpu6050.reset_fifo()