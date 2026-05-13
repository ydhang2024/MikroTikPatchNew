#!/usr/bin/python3
import sys
from mikro import mikro_softwareid_decode, mikro_kcdsa_sign, mikro_base64_encode, mikro_encode

def generate_l6_license(software_id_str, private_key_hex):
    MIKRO_LICENSE_HEADER = '-----BEGIN MIKROTIK SOFTWARE KEY------------'
    MIKRO_LICENSE_FOOTER = '-----END MIKROTIK SOFTWARE KEY--------------'

    try:
        private_key = bytes.fromhex(private_key_hex)
    except ValueError:
        raise Exception("私钥格式不正确，必须是十六进制字符串。")

    try:
        software_id = mikro_softwareid_decode(software_id_str)
    except Exception:
        raise Exception("Software ID 格式错误！")

    # 构造授权数据 (L6等级)
    lic = software_id.to_bytes(6, 'little')
    lic += (7).to_bytes(1, 'little')  # ROS Version
    lic += (22).to_bytes(1, 'little') # License Level 6
    lic += b'\0' * 8 

    sig = mikro_kcdsa_sign(lic, private_key)
    lic_b64 = mikro_base64_encode(mikro_encode(lic) + sig, True)
    
    mid = len(lic_b64) // 2
    return f"{MIKRO_LICENSE_HEADER}\n{lic_b64[:mid]}\n{lic_b64[mid:]}\n{MIKRO_LICENSE_FOOTER}"

if __name__ == "__main__":
    # 检查参数数量
    if len(sys.argv) < 3:
        print("用法: python3 keygen.py <SoftwareID> <PrivateKey>")
        sys.exit(1)
    
    sw_id = sys.argv[1]
    priv_key = sys.argv[2]

    try:
        print(generate_l6_license(sw_id, priv_key))
    except Exception as e:
        print(f"[-] 生成失败: {e}")
        sys.exit(1)
