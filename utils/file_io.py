import os
import json
import pandas as pd

class FileIO:
    def __init__(self, folder_name="data"):
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        self.base_folder = os.path.join(project_root, folder_name)
        print(self.base_folder)

        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
            print(f"📁 Created folder: {self.base_folder}")

    def get_path(self, filename):
        """Generate a dynamic path based on the filename provided"""
        """Example: get_path('macd') -> E:/bitcoin_up_down/data/btc_macd_1m.jsonl"""
        return os.path.join(self.base_folder, filename)

    def load_jsonl_to_df(self, file_path):
        """Loads a JSONL file into a Pandas DataFrame."""
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return pd.read_json(file_path, lines=True)
        return pd.DataFrame()

    def append_row_to_jsonl(self, file_path, row_dict):
        """Appends a single dictionary as a new line in a JSONL file."""
        try:
            with open(file_path, 'a') as f:
                f.write(json.dumps(row_dict) + '\n')
        except Exception as e:
            print(f"❌ FileIO Error (Append to {os.path.basename(file_path)}): {e}")

    def export_full_df_to_jsonl(self, df, file_path):
        """Overwrites/Exports an entire DataFrame to JSONL format."""
        try:
            df.to_json(file_path, orient='records', lines=True)
        except Exception as e:
            print(f"❌ FileIO Error (Export to {os.path.basename(file_path)}): {e}")

    def get_last_timestamp(self, file_path):
        """Efficiently reads the last line to get the latest timestamp (High Speed)."""
        if not os.path.exists(file_path) or os.path.getsize(file_path) <= 0:
            return None
        try:
            with open(file_path, 'rb') as f:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    if f.tell() <= 1: # Reached start of file
                        f.seek(0)
                        break
                    f.seek(-2, os.SEEK_CUR)
                last_line = f.readline().decode()
                return json.loads(last_line).get('timestamp')
        except Exception:
            return None

    def delete_last_row(self, file_path):
        """Deletes the last line of a JSONL file in-place (Truncation)."""
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return

        try:
            with open(file_path, "r+b") as f:
                f.seek(0, os.SEEK_END)
                pos = f.tell()
                
                if pos > 2:
                    f.seek(-2, os.SEEK_CUR)
                    while f.read(1) != b'\n':
                        if f.tell() <= 1:
                            f.seek(0)
                            break
                        f.seek(-2, os.SEEK_CUR)
                    f.truncate()
            print(f"🗑️ Deleted last row from {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Error deleting row: {e}")



def main():
    file_io = FileIO()
    return file_io    

if __name__ == "__main__":
    main()