class GlobalState:
    def __init__(self):
        # initiator
        self._working_hours_countdown = 0

        # market_manager
        self._delta_sec = 0
        self._res_count = 0
        self._active_clob_streams = set()
        self._user_channel_ts = None
        self._rolling_timestamps = {'current': "", 'next': ""}
        self._is_pricediff_finished = False
        self._price_diff = 0.0

        self._events_metadata = []

        # self._events_metadata = [{
        #     "timestamp": "5555555555555",
        #     "condition_id" : "555555555555",
        #     "asset_ids": ['55555', '11111'],
        #     "channel_type": "market"
        # }, {}, {}]

    # --- working_hour_countdown ---
    @property
    def working_hours_countdown(self):
        return self._working_hours_countdown

    @working_hours_countdown.setter
    def working_hours_countdown(self, value: int):
        self._working_hours_countdown = value

    # --- working_hour_countdown ---
    @property
    def events_metadata(self):
        return self._events_metadata
    
    @events_metadata.setter
    def events_metadata(self, value:dict):
        if value is None : return
        self._events_metadata.append(value)
    
    # --- delta_sec ---
    @property
    def delta_sec(self): 
        return self._delta_sec
    
    @delta_sec.setter
    def delta_sec(self, value: int):
        self._delta_sec = value

    # --- res_count ---
    @property
    def res_count(self): 
        return self._res_count
    
    @res_count.setter
    def res_count(self, value: int):
        self._res_count = value

    # --- active_clob_streams ---
    @property
    def active_clob_streams(self): 
        return self._active_clob_streams
    
    @active_clob_streams.setter
    def active_clob_streams(self, value: set):
        # Logic to ensure you don't exceed your 3-leg limit
        if len(value) > 3:
            print("⚠️ Warning: Attempted to exceed 3-leg limit!")
        self._active_clob_streams = value

    # --- price_diff ---
    @property
    def price_diff(self): 
        return self._price_diff
    
    @price_diff.setter
    def price_diff(self, value: float):
        self._price_diff = value

    # --- rolling_timestamps ---
    @property
    def rolling_timestamps(self): 
        return self._rolling_timestamps
    
    @rolling_timestamps.setter
    def rolling_timestamps(self, value: dict):
        self._rolling_timestamps = value

    # --- user_channel_ts ---
    @property
    def user_channel_ts(self): 
        return self._user_channel_ts
    
    @user_channel_ts.setter
    def user_channel_ts(self, value):
        self._user_channel_ts = value

    # --- is_pricediff_finished ---
    @property
    def is_pricediff_finished(self):
        return self._is_pricediff_finished
    
    @is_pricediff_finished.setter
    def is_pricediff_finished(self, value: bool):
        self._is_pricediff_finished = value


    @property
    def events_metadata(self):
        return self._events_metadata
    
    @events_metadata.setter
    def events_metadata(self, value):
        if value is None: return
        self._events_metadata.append(value)


state = GlobalState()