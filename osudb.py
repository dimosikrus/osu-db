import struct
import io

class OsuDBReader:
    @staticmethod
    def read_uleb128(stream):
        result = 0
        shift = 0
        while True:
            byte = stream.read(1)
            if not byte:
                break
            byte = ord(byte)
            result |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        return result

    @staticmethod
    def read_string(stream):
        if stream.read(1) == b'\x0b':
            length = OsuDBReader.read_uleb128(stream)
            return stream.read(length).decode('utf-8')
        return ""

    @staticmethod
    def read_timing_point(stream):
        return {
            'bpm': struct.unpack('<d', stream.read(8))[0],
            'offset': struct.unpack('<d', stream.read(8))[0],
            'uninherited': struct.unpack('<?', stream.read(1))[0]
        }

    @staticmethod
    def read_beatmap(stream:io.BufferedIOBase, version):
        beatmap = {}
        
        beatmap['artist'] = OsuDBReader.read_string(stream)
        beatmap['artist_unicode'] = OsuDBReader.read_string(stream)
        beatmap['title'] = OsuDBReader.read_string(stream)
        beatmap['title_unicode'] = OsuDBReader.read_string(stream)
        beatmap['creator'] = OsuDBReader.read_string(stream)
        beatmap['version'] = OsuDBReader.read_string(stream)
        beatmap['audio_file'] = OsuDBReader.read_string(stream)
        beatmap['md5_hash'] = OsuDBReader.read_string(stream)
        beatmap['osu_file'] = OsuDBReader.read_string(stream)
        
        # Чтение основных параметров
        beatmap['ranked_status'] = struct.unpack('<B', stream.read(1))[0]
        beatmap['num_circles'] = struct.unpack('<H', stream.read(2))[0]
        beatmap['num_sliders'] = struct.unpack('<H', stream.read(2))[0]
        beatmap['num_spinners'] = struct.unpack('<H', stream.read(2))[0]
        beatmap['last_modified'] = struct.unpack('<q', stream.read(8))[0]
        
        if version < 20140609:
            beatmap['ar'] = struct.unpack('<B', stream.read(1))[0]
            beatmap['cs'] = struct.unpack('<B', stream.read(1))[0]
            beatmap['hp'] = struct.unpack('<B', stream.read(1))[0]
            beatmap['od'] = struct.unpack('<B', stream.read(1))[0]
        else:
            beatmap['ar'] = struct.unpack('<f', stream.read(4))[0]
            beatmap['cs'] = struct.unpack('<f', stream.read(4))[0]
            beatmap['hp'] = struct.unpack('<f', stream.read(4))[0]
            beatmap['od'] = struct.unpack('<f', stream.read(4))[0]
        
        beatmap['slider_velocity'] = struct.unpack('<d', stream.read(8))[0]
        
        for _ in ["std","taiko","ctb","mania"]:
            param_count = struct.unpack('<I', stream.read(4))[0]
            for i in range(0,param_count):
                mod = struct.unpack('<I', stream.read(4))[0]
                struct.unpack('<H', stream.read(2))[0]
                stars = struct.unpack('<f', stream.read(4))[0]
        
        beatmap['drain_time'] = struct.unpack('<I', stream.read(4))[0]
        beatmap['total_time'] = struct.unpack('<I', stream.read(4))[0]
        beatmap['preview_time'] = struct.unpack('<I', stream.read(4))[0]

        beatmap['timing_points'] = []
        for _ in range(struct.unpack('<I', stream.read(4))[0]):
            beatmap['timing_points'].append(OsuDBReader.read_timing_point(stream))

        beatmap['beatmap_id']         = struct.unpack('<I', stream.read(4))[0]
        beatmap['beatmap_set_id']     = struct.unpack('<I', stream.read(4))[0]
        beatmap['thread_id']          = struct.unpack('<I', stream.read(4))[0]
        beatmap['grade_standard']     = struct.unpack('<B', stream.read(1))[0]
        beatmap['grade_taiko']        = struct.unpack('<B', stream.read(1))[0]
        beatmap['grade_ctb']          = struct.unpack('<B', stream.read(1))[0]
        beatmap['grade_mania']        = struct.unpack('<B', stream.read(1))[0]
        beatmap['local_offset']       = struct.unpack('<H', stream.read(2))[0]
        beatmap['stack_leniency']     = struct.unpack('<f', stream.read(4))[0]
        beatmap['gameplay_mode']      = struct.unpack('<B', stream.read(1))[0]
        beatmap['song_source']        = OsuDBReader.read_string(stream)
        beatmap['song_tags']          = OsuDBReader.read_string(stream)
        beatmap['online_offset']      = struct.unpack('<H', stream.read(2))[0]
        beatmap['title_font']         = OsuDBReader.read_string(stream)
        beatmap['is_unplayed']        = struct.unpack('<?', stream.read(1))[0]
        beatmap['last_played']        = struct.unpack('<Q', stream.read(8))[0]
        beatmap['is_osz2']            = struct.unpack('<?', stream.read(1))[0]
        beatmap['folder_name']        = OsuDBReader.read_string(stream)
        beatmap['last_checked']       = struct.unpack('<Q', stream.read(8))[0]
        beatmap['ignore_sounds']      = struct.unpack('<?', stream.read(1))[0]
        beatmap['ignore_skin']        = struct.unpack('<?', stream.read(1))[0]
        beatmap['disable_storyboard'] = struct.unpack('<?', stream.read(1))[0]
        beatmap['disable_video']      = struct.unpack('<?', stream.read(1))[0]
        beatmap['visual_override']    = struct.unpack('<?', stream.read(1))[0]
        beatmap['last_modified2']     = struct.unpack('<I', stream.read(4))[0]
        beatmap['scroll_speed']       = struct.unpack('<B', stream.read(1))[0]
        return beatmap

    @staticmethod
    def read_db(file_path, includemodstars:bool=False):
        with open(file_path, 'rb') as f:
            stream = io.BytesIO(f.read())

            version = struct.unpack('<I', stream.read(4))[0]
            folder_count = struct.unpack('<I', stream.read(4))[0]
            account_unlocked = struct.unpack('<?', stream.read(1))[0]
            unlock_date = struct.unpack('<q', stream.read(8))[0]
            player_name = OsuDBReader.read_string(stream)
            num_beatmaps = struct.unpack('<I', stream.read(4))[0]
            
            beatmaps = []
            for _ in range(num_beatmaps):
                beatmaps.append(OsuDBReader.read_beatmap(stream, version, includemodstars))
            
            return {
                'version': version,
                'folder_count': folder_count,
                'account_unlocked': account_unlocked,
                'unlock_date': unlock_date,
                'player_name': player_name,
                'beatmaps': beatmaps
            }
