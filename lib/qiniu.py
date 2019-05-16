from qiniu import Auth, put_file, etag
import qiniu.config
from swiper import config
from common import keys


## 需要填写你的 Access Key 和 Secret Key
access_key = config.QN_AK
secret_key = config.QN_SK


def upload_qiniu(uid, filepath):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = config.QN_BUCKET
    # 上传后保存的文件名
    key = keys.AVATAR_KEY % uid
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, filepath)
    


