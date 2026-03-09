#!/bin/bash

set -e

echo "==============================="
echo " MikroTik RouterOS Patch Tool "
echo "        ARCH: arm64            "
echo "==============================="
echo ""

# 输入 RouterOS 版本
read -p "请输入 RouterOS 版本 (例如 7.16.1): " VERSION

ARCH="arm64"

echo ""
echo "RouterOS Version: $VERSION"
echo "Architecture   : $ARCH"
echo ""

# KEY
export MIKRO_NPK_SIGN_PUBLIC_KEY="8D3F887C64A04CA147872995DAEE2C73DD2D04DD3D1B2A2A289B239958803439"
export MIKRO_LICENSE_PUBLIC_KEY="271501494893987A0A50D41DFC7500FFD4F7B32F455F2C0E7C7439D3BD7B0876"
export CUSTOM_NPK_SIGN_PRIVATE_KEY="7D008D9B80B036FB0205601FEE79D550927EBCA937B7008CC877281F2F8AC640"
export CUSTOM_NPK_SIGN_PUBLIC_KEY="28F886E32C141123126CFBCAD56766E99D1720CEB1F12BE2468BEBE7662FBEDB"
export CUSTOM_LICENSE_PRIVATE_KEY="9DBC845E9018537810FDAE62824322EEE1B12BAD81FCA28EC295FB397C61CE0B"
export CUSTOM_LICENSE_PUBLIC_KEY="723A34A6E3300F23E4BAA06156B9327514AEC170732655F16E04C17928DD770F"

echo "下载 RouterOS NPK..."
wget -q --show-progress https://github.com/elseif/MikroTikPatch/releases/download/${VERSION}-${ARCH}/routeros-${VERSION}-${ARCH}.npk

echo "下载 All Packages..."
wget -q --show-progress https://github.com/elseif/MikroTikPatch/releases/download/${VERSION}-${ARCH}/all_packages-${ARCH}-${VERSION}.zip

echo "创建目录..."
mkdir -p ./all_packages-${ARCH}

echo "解压 packages..."
unzip -q all_packages-${ARCH}-${VERSION}.zip -d ./all_packages-${ARCH}/

echo "Patch routeros..."
yes "" | python3 patch.py npk routeros-${VERSION}-${ARCH}.npk

mv routeros-${VERSION}-${ARCH}.npk routeros-${VERSION}-${ARCH}-patch.npk

echo "删除原始 zip..."
rm all_packages-${ARCH}-${VERSION}.zip

echo "签名所有 NPK..."
NPK_FILES=$(find ./all_packages-${ARCH} -name "*.npk")

for file in $NPK_FILES
do
    echo "Signing $file"
    yes "" | python3 npk.py sign "$file" "$file"
done

echo "重新打包 packages..."
cd ./all_packages-${ARCH}
zip ../all_packages-${ARCH}-${VERSION}-patched.zip *.npk >/dev/null
cd ..

echo "清理临时文件..."
rm -rf ./all_packages-${ARCH}

echo ""
echo "==============================="
echo "完成"
echo "==============================="
echo ""
echo "生成文件:"
echo "routeros-${VERSION}-${ARCH}-patch.npk"
echo "all_packages-${ARCH}-${VERSION}-patched.zip"
echo ""
