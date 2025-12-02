# DailyInspectionCSV.py
import csv
import os
import tempfile
from datetime import datetime, date

class DailyInspectionCSV:
    def __init__(self, folder='.', filename_prefix='inspection'):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)
        self.filename_prefix = filename_prefix
        self._header = None

    def _date_str(self, d=None):
        d = d or date.today()
        return d.isoformat()

    def _filename_for_date(self, d=None):
        return os.path.join(self.folder, f"{self.filename_prefix}_{self._date_str(d)}.csv")

    def _normalize(self, s):
        """Normalize a header name for fuzzy matching (ignore spaces, #, case)."""
        return ''.join(ch for ch in str(s).lower() if ch.isalnum())

    def create_daily_file(self, positions, for_date=None, overwrite=False, allow_merge=True):
        """
        positions: int (จำนวน) หรือ list ของชื่อคอลัมน์
        overwrite: ถ้า True เขียนทับไฟล์เดิม (ข้อมูลเดิมหาย)
        allow_merge: ถ้าไฟล์มี header ไม่ตรงกัน และ allow_merge=True จะเพิ่มคอลัมน์ใหม่ต่อขวาโดยไม่ลบข้อมูลเดิม
        """
        if isinstance(positions, int):
            pos_names = [f"Position#{i+1}" for i in range(positions)]
        else:
            pos_names = list(positions)

        filename = self._filename_for_date(for_date)
        header = ['S/N', 'Date', 'Time'] + pos_names + ['Status']

        if os.path.exists(filename) and not overwrite:
            # อ่าน header ปัจจุบัน
            with open(filename, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    existing_header = next(reader)
                except StopIteration:
                    existing_header = []

            if existing_header == header:
                self._header = header
                return filename

            # ถ้า header ต่างกัน: พยายาม merge ถ้า allow_merge True
            if allow_merge:
                self._merge_headers(filename, existing_header, header)
                # หลัง merge ให้โหลด header ใหม่
                with open(filename, newline='', encoding='utf-8') as f:
                    self._header = next(csv.reader(f))
                return filename

            # ไม่อนุญาต merge -> raise (พฤติกรรมเดิม)
            raise ValueError(f"ไฟล์ {filename} มี header ไม่ตรงกัน\nไฟล์มี: {existing_header}\nต้องการ: {header}")

        # สร้างหรือเขียนทับ header ใหม่
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        self._header = header
        return filename

    def _merge_headers(self, filename, existing_header, wanted_header):
        """
        รวม wanted_header เข้ากับ existing_header:
        - ถ้ามีชื่อที่ต่างกันแต่ normalize แล้วเท่ากัน จะถือว่าเป็นคอลัมน์เดียวกัน (map)
        - ถ้ามีคอลัมน์ใหม่จาก wanted_header จะเพิ่มต่อขวา และเติม '' ให้แถวเก่า
        ปลอดภัย: จะเขียนไฟล์ชั่วคราวแล้ว replace เดิม
        """
        # Normalize maps
        existing_norm = {self._normalize(h): h for h in existing_header}
        wanted_norm = {self._normalize(h): h for h in wanted_header}

        # ถ้า existing มีทั้งหมดที่ wanted ต้องการ (หลัง normalize) -> nothing to do
        all_match = True
        for wn in wanted_norm:
            if wn not in existing_norm:
                all_match = False
                break
        if all_match:
            # แต่วิธีการจัดลำดับของ wanted อาจต่างจาก existing; เราจะใช้ existing order แล้วถ้ามี wanted column ที่ไม่อยู่ใน existing ให้ต่อขวา
            new_header = existing_header.copy()
        else:
            # สร้าง new_header: เริ่มจาก existing แล้วเพิ่ม wanted columns ที่ไม่มี
            new_header = existing_header.copy()
            for wn, wname in wanted_norm.items():
                if wn not in existing_norm:
                    new_header.insert(-1, wname)  # ก่อน 'Status' เสมอ
        # ถ้า new_header เท่ากับ existing_header -> ไม่มีอะไรต้องทำ
        if new_header == existing_header:
            return

        # อ่านข้อมูลทั้งหมดของไฟล์เดิม
        rows = []
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            # skip existing header
            try:
                next(reader)
            except StopIteration:
                pass
            for row in reader:
                rows.append(row)

        # สร้าง index mapping ของ existing header columns
        # เพื่อรักษาค่าเดิมให้เข้ากับตำแหน่งใหม่
        # map existing column idx -> new_header idx
        idx_map = {}
        for i, eh in enumerate(existing_header):
            n = self._normalize(eh)
            # find first index in new_header with same normalized name
            for j, nh in enumerate(new_header):
                if self._normalize(nh) == n:
                    idx_map[i] = j
                    break

        # สร้าง new_rows ด้วยจำนวนคอลัมน์เท่ากับ len(new_header)
        new_rows = []
        for r in rows:
            new_r = [''] * len(new_header)
            # คัดลอกค่าจาก existing ไปตำแหน่งใหม่ตาม idx_map (ถ้า row สั้นกว่าจำนวนคอลัมน์ ให้ไม่ error)
            for i in range(len(r)):
                if i in idx_map:
                    new_r[idx_map[i]] = r[i]
            new_rows.append(new_r)

        # เขียนไปยังไฟล์ชั่วคราว แล้ว replace
        fd, tmp_path = tempfile.mkstemp(dir=self.folder, text=True)
        os.close(fd)
        try:
            with open(tmp_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(new_header)
                writer.writerows(new_rows)
            os.replace(tmp_path, filename)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def append_row(self, sn, position_values, status, for_date=None, time_value=None, create_if_missing=False):
        """
        append_row(..., create_if_missing=False)
        ถ้า create_if_missing=True และไฟล์ยังไม่มี จะสร้างไฟล์ใหม่แบบ default (จำนวน position ตาม position_values ถ้าเป็น list)
        """
        filename = self._filename_for_date(for_date)
        if not os.path.exists(filename):
            if create_if_missing:
                # ถ้า position_values เป็น list ให้ใช้จำนวนเท่ากับ len(list)
                if isinstance(position_values, (list, tuple)):
                    self.create_daily_file(len(position_values), for_date=for_date)
                else:
                    # ถ้าเป็น dict และไฟล์ยังไม่มี ให้ใช้ keys ของ dict เป็นชื่อ column
                    if isinstance(position_values, dict):
                        posnames = list(position_values.keys())
                        self.create_daily_file(posnames, for_date=for_date)
                    else:
                        raise FileNotFoundError("ไฟล์ยังไม่มี และไม่สามารถเดาจำนวน position จาก position_values ได้")
            else:
                raise FileNotFoundError(f"ไฟล์วันที่ {self._date_str(for_date)} ยังไม่มี ให้เรียก create_daily_file() ก่อนหรือใช้ create_if_missing=True")

        # โหลด header ถ้ายังไม่ได้โหลด
        if self._header is None:
            with open(filename, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    self._header = next(reader)
                except StopIteration:
                    raise ValueError("ไฟล์ว่างไม่มี header")

        dstr = self._date_str(for_date)
        if time_value is None:
            tstr = datetime.now().strftime("%H:%M:%S")
        else:
            if isinstance(time_value, datetime):
                tstr = time_value.strftime("%H:%M:%S")
            else:
                tstr = str(time_value)

        pos_headers = self._header[3:-1]  # ตัด S/N,Date,Time และ Status ออก

        # แปลง position_values ให้เป็น list ตาม pos_headers
        row_positions = []
        if isinstance(position_values, dict):
            for ph in pos_headers:
                # รองรับ fuzzy key: ถ้า key ไม่ตรง แต่ normalize แล้วเท่ากับหนึ่งใน keys ของ dict ให้ใช้
                if ph in position_values:
                    row_positions.append(position_values.get(ph, ''))
                else:
                    # พยายามหา key ที่ normalize แล้วตรง
                    found = False
                    for k in position_values:
                        if self._normalize(k) == self._normalize(ph):
                            row_positions.append(position_values.get(k, ''))
                            found = True
                            break
                    if not found:
                        row_positions.append('')
        else:
            vals = list(position_values)
            if len(vals) != len(pos_headers):
                raise ValueError(f"จำนวนค่า position ไม่ตรงกับ header ({len(vals)} != {len(pos_headers)})")
            row_positions = vals

        row = [sn, dstr, tstr] + row_positions + [status]

        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        return filename