from kb import get,search
import json,sys
def info(no):
    m=get('land-complex/complex/main',단지기본일련번호=no)['dataBody']['data']
    return {k:m.get(k) for k in ['단지명','준공년월','총세대수','시공사명','세대당주차대수비율','건폐율내용','용적률내용','최고층수','도로기본주소','wgs84위도','wgs84경도']}
def types(no):
    d=get('land-complex/complex/typInfo',단지기본일련번호=no)['dataBody']['data']
    return [(x['면적일련번호'],x['전용면적'],x['공급면적'],x['세대수']) for x in d]
def sise(no,seq):
    d=get('land-price/price/BasePrcInfoNew',단지기본일련번호=no,면적일련번호=seq)['dataBody']['data']['시세']
    return [(x['전용면적'],x['매매일반거래가'],x['매매평균가'],x['시세기준년월일']) for x in d]
if __name__=='__main__':
    for k in sys.argv[1:]:
        print('##',k)
        for no,nm,ad in search(k)[:8]:
            try: i=info(no); print(' ',no,nm,'|',ad,'|',i['준공년월'],i['총세대수'],i['시공사명'])
            except Exception as e: print(' ',no,nm,'ERR')
