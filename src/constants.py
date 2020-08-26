# WINDOW CONST
WINDOW_WIDTH = 800  # In pixel
WINDOW_HEIGHT = 800

# NIDAQMX READ CONST
CHANNEL_COUNT = 2
READ_DATA_MIN_VALUE = -10   # Acceptable minimum value in reading
READ_DATA_MAX_VALUE = 10    # Acceptable maximum value in reading
READ_DATA_SAMPLE_RATE = 5000    # In Hz
READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH = 100
WINDOW_REFRESH_TIME = 10    # In ms
MAX_DELAY = 1           # Make sure this is GREATER (not equal to) your maximum delay condition
CLOCK_FREQUENCY = 50    # 
DELAY_BUFFER_LEN = int(MAX_DELAY * CLOCK_FREQUENCY)
NUM_LO = 9

# TARGET & CURSOR CONST
CURSOR_SCALE = 100  # Used in calculation to g
RADIUS = 200    # Movement radius in 1 amplitude; in pixel

# SCORING CONST
SCORE_CONST = 0.5

# TRIAL CONST
START_PHASE = 1
TRACK_PHASE = 2
SCORE_PHASE = 3
REST_PHASE = 4
END_PHASE = 5