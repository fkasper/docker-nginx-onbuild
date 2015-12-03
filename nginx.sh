#!/bin/bash
set -x

NGINX_VERSION=1.9.6
PAGESPEED_VERSION=1.9.32.10
OPENSSL_VERSION=1.0.2d

apt-get update
apt-get install -y build-essential zlib1g-dev libpcre3 libpcre3-dev unzip libgeoip-dev wget

MODULESDIR=`mktemp -d`
MODULESDIR=`mktemp -d`


# Download NGINX
cd $MODULESDIR
wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz
tar xf nginx-${NGINX_VERSION}.tar.gz
rm -f nginx-${NGINX_VERSION}.tar.gz

# Download SSL
cd $MODULESDIR
wget http://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz
tar xvzf openssl-${OPENSSL_VERSION}.tar.gz
rm -f openssl-${OPENSSL_VERSION}.tar.gz

# Download Pagespeed
cd $MODULESDIR
wget --no-check-certificate https://github.com/pagespeed/ngx_pagespeed/archive/v${PAGESPEED_VERSION}-beta.zip
unzip v${PAGESPEED_VERSION}-beta.zip
rm -f v${PAGESPEED_VERSION}-beta.zip

# Download PSOL
cd ngx_pagespeed-${PAGESPEED_VERSION}-beta/
wget --no-check-certificate https://dl.google.com/dl/page-speed/psol/${PAGESPEED_VERSION}.tar.gz
tar -xzf ${PAGESPEED_VERSION}.tar.gz
rm -f ${PAGESPEED_VERSION}.tar.gz


cd $MODULESDIR/nginx-${NGINX_VERSION}
./configure \
	--prefix=/etc/nginx \
	--sbin-path=/usr/sbin/nginx \
	--conf-path=/etc/nginx/nginx.conf \
	--error-log-path=/var/log/nginx/error.log \
	--http-log-path=/var/log/nginx/access.log \
	--pid-path=/var/run/nginx.pid \
	--lock-path=/var/run/nginx.lock \
	--with-http_ssl_module \
	--with-http_realip_module \
	--with-http_addition_module \
	--with-http_sub_module \
	--with-http_dav_module \
	--with-http_flv_module \
	--with-http_mp4_module \
	--with-http_gunzip_module \
	--with-http_gzip_static_module \
	--with-http_random_index_module \
	--with-http_secure_link_module \
	--with-http_stub_status_module \
	--with-file-aio \
	--with-cc-opt='-g -O2 -fstack-protector --param=ssp-buffer-size=4 -Wformat -Wformat-security -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2' \
	--with-ld-opt='-Wl,-Bsymbolic-functions -Wl,-z,relro -Wl,--as-needed' \
	--with-ipv6 \
	--with-sha1=/usr/include/openssl \
 	--with-md5=/usr/include/openssl \
	--with-openssl=${MODULESDIR}/openssl-${OPENSSL_VERSION} \
	--add-module=${MODULESDIR}/ngx_pagespeed-${PAGESPEED_VERSION}-beta

make
make install
