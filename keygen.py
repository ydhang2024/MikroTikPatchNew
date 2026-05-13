#!/usr/bin/python3
import sys

# 尝试导入底层微架构支持库 (你原有的 mikro.py)
try:
    from mikro import mikro_softwareid_decode, mikro_kcdsa_sign, mikro_base64_encode, mikro_encode
except ImportError:
    print("[-] 错误：找不到 mikro 模块！请确保本脚本和 mikro.py 在同一个目录下。")
    sys.exit(1)

# 尝试自动加载 creallavesX2 生成的私钥文件
try:
    import pryvatekey
    PRIVATE_KEY_HEX = pryvatekey.klaveprivada()
    print(f"[+] 成功从 pryvatekey.py 加载私钥: {PRIVATE_KEY_HEX[:16]}........")
except ImportError:
    print("[-] 找不到 pryvatekey.py 文件！")
    PRIVATE_KEY_HEX = "1F99C1C4E13A4C8A61897022C6BD83CF0B848D51F1F0B398E52329E5250A502F"

def generate_l6_license(software_id_str, private_key_hex):
    MIKRO_LICENSE_HEADER = '-----BEGIN MIKROTIK SOFTWARE KEY------------'
    MIKRO_LICENSE_FOOTER = '-----END MIKROTIK SOFTWARE KEY--------------'

    try:
        private_key = bytes.fromhex(private_key_hex)
    except ValueError:
        raise Exception("私钥格式不正确，必须是十六进制字符串。")

    # 1. 解析 Software ID
    try:
        software_id = mikro_softwareid_decode(software_id_str)
    except Exception:
        raise Exception("Software ID 格式错误！请检查是否输入正确 (例如: ABCD-1234)。")

    # 2. 构造授权数据结构 (写死 L6 级别)
    lic = software_id.to_bytes(6, 'little')
    varb7 = 7   # 适用版本: RouterOS v7.x
    varb8 = 22  # 核心特征位: 22 代表 L6 级别授权
    lic += varb7.to_bytes(1, 'little')
    lic += varb8.to_bytes(1, 'little')
    lic += b'\0' * 8 # 填充空字节

    # 3. 使用你的新私钥进行 KCDSA 签名
    sig = mikro_kcdsa_sign(lic, private_key)
    
    # 4. Base64 编码并组合最终结果
    lic_b64 = mikro_base64_encode(mikro_encode(lic) + sig, True)
    
    # 将 Base64 字符串从中间切成两行
    mid = len(lic_b64) // 2
    final_license = (
        MIKRO_LICENSE_HEADER + '\n' +
        lic_b64[:mid] + '\n' +
        lic_b64[mid:] + '\n' +
        MIKRO_LICENSE_FOOTER
    )
    return final_license

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  RouterOS L6 授权码生成器 (基于自定义私钥)")
    print("="*50 + "\n")
    
    sw_id = input("[?] 请输入路由器的 Software ID (例如 XXXX-XXXX): ").strip()

    if not sw_id:
        print("[-] Software ID 不能为空，程序退出。")
        sys.exit(1)

    try:
        license_key = generate_l6_license(sw_id, PRIVATE_KEY_HEX)
        print("\n[+] 授权码生成成功！请复制下方【包含虚线】的所有内容到路由器中：\n")
        print(license_key)
    except Exception as e:
        print(f"\n[-] 生成失败: {e}")
