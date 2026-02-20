from typing import Set, Dict

class GlobalState:
    def __init__(self):
        # Private variables (prefixed with _)
        self._delta_sec = 0
        self._res_count = 0
        self._active_clob_streams = set()
        self._user_channel_ts = None
        self._rolling_timestamps = {'current': "", 'next': ""}
        self._is_pricediff_finished = False
        self._price_diff = 0

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

state = GlobalState()