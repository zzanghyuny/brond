import json, time, urllib.request, urllib.parse, sys
UA = "brandongsan-map/1.0 (contact: brandongsan.com)"
Q = {
 'ben_thanh': 'Chợ Bến Thành', 'opera': 'Nhà hát Thành phố Hồ Chí Minh', 'binh_tay': 'Chợ Bình Tây',
 'crescent': 'Crescent Mall', 'thao_dien': 'Thảo Điền', 'thu_thiem_sq': 'Cầu Thủ Thiêm 2',
 'tsn': 'Sân bay Tân Sơn Nhất', 'long_thanh': 'Cảng hàng không quốc tế Long Thành', 'shtp': 'Khu Công nghệ cao Thành phố Hồ Chí Minh',
 'thu_dau_mot': 'Thủ Dầu Một', 'vung_tau': 'Vũng Tàu', 'suoi_tien': 'Bến xe Suối Tiên', 'landmark81': 'Landmark 81',
 'nha_be': 'Nhà Bè', 'long_binh': 'Long Bình, Thủ Đức', 'kis': 'Trường Quốc tế Hàn Quốc Thành phố Hồ Chí Minh',
 'ba_son': 'Cầu Ba Son', 'new_city_bd': 'Thành phố mới Bình Dương', 'can_gio': 'Cần Giờ', 'thu_duc': 'Thủ Đức',
}
out = {}
for k, q in Q.items():
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(dict(q=q, format='jsonv2', limit=1, countrycodes='vn'))
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30))
        if r: out[k] = dict(lat=float(r[0]['lat']), lon=float(r[0]['lon']), name=r[0]['display_name'][:90]); print(k, out[k])
        else: print(k, 'NONE')
    except Exception as e: print(k, 'ERR', e)
    time.sleep(1.3)
json.dump(out, open('places.json', 'w'), ensure_ascii=False, indent=1)
