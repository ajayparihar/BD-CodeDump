#!/bin/bash

echo "ENVIRONMENT is ${ENVIRONMENT}"

case $ENVIRONMENT in
  development )
    root_ca_cer="internal_scb_root_ca_cer"
    ssl_ca_cer="internal_scb_intermediate_ca_cer"
    consumer_cer="kong_sit_consumer_cer"
    consumer_key="kong_sit_consumer_key"
    boc_keystore_cer="HK_OB_CJ_BOC_KEYSTORE"
    boc_keystore_key="HK_OB_CJ_BOC_KEYSTORE_KEY"
    citi_keystore_cer="HK_OB_CJ_CITI_KEYSTORE"
    citi_keystore_key="HK_OB_CJ_CITI_KEYSTORE_KEY"
    hsbc_keystore_cer="HK_OB_CJ_HSBC_KEYSTORE"
    hsbc_keystore_key="HK_OB_CJ_HSBC_KEYSTORE_KEY"
    hase_keystore_cer="HK_OB_CJ_RL_HASE_KEYSTORE"
    hase_keystore_key="HK_OB_CJ_RL_HASE_KEYSTORE_KEY"
    citi_root_cer="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_ROOT_CERT"
    citi_inter_cer="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_INTER_CERT"
    hsbc_transport_cer="HK_OB_CJ_PARTNER_TRUST_STORE_HSBC_TRANSPORT_CERT"
    hase_transport_cer="HK_OB_CJ_RL_PARTNER_TRUST_STORE_HASE_TRANSPORT_CERT"
    boc_transport_cer="HK_OB_CJ_PARTNER_TRUST_STORE_BOC_TRANSPORT_CERT"
    mspki_root_cer="Solace_mspki_Root_cer"
    mspki_inter_cer="Solace_mspki_Intermediate_cer"
    solace_batch_consumer_cer="HK_OB_CJ_SOLACE_CER"
    solace_batch_consumer_key="HK_OB_CJ_SOLACE_KEY"
    apm_client_pem="apm_client_pem"
    apm_ca_cer="apm_intermediate_cer"
    solace_root_ca_cer="internal_scb_solace_root_ca_cer_green"
    echo "something development"
    ;;
staging )
    root_ca_cer="internal_scb_root_ca_cer"
    ssl_ca_cer="internal_scb_intermediate_ca_cer"
    consumer_cer="kong_sit_consumer_cer"
    consumer_key="kong_sit_consumer_key"
    boc_keystore_cer="HK_OB_CJ_BOC_KEYSTORE"
    boc_keystore_key="HK_OB_CJ_BOC_KEYSTORE_KEY"
    citi_keystore_cer="HK_OB_CJ_CITI_KEYSTORE"
    citi_keystore_key="HK_OB_CJ_CITI_KEYSTORE_KEY"
    hsbc_keystore_cer="HK_OB_CJ_HSBC_KEYSTORE"
    hsbc_keystore_key="HK_OB_CJ_HSBC_KEYSTORE_KEY"
    hase_keystore_cer="HK_OB_CJ_RL_HASE_KEYSTORE"
    hase_keystore_key="HK_OB_CJ_RL_HASE_KEYSTORE_KEY"
    citi_root_cer="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_ROOT_CERT"
    citi_inter_cer="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_INTER_CERT"
    hsbc_transport_cer="HK_OB_CJ_PARTNER_TRUST_STORE_HSBC_TRANSPORT_CERT"
    hase_transport_cer="HK_OB_CJ_RL_PARTNER_TRUST_STORE_HASE_TRANSPORT_CERT"
    boc_transport_cer="HK_OB_CJ_PARTNER_TRUST_STORE_BOC_TRANSPORT_CERT"
    mspki_root_cer="Solace_mspki_Root_cer"
    mspki_inter_cer="Solace_mspki_Intermediate_cer"
    solace_batch_consumer_cer="HK_OB_CJ_SOLACE_CER"
    solace_batch_consumer_key="HK_OB_CJ_SOLACE_KEY"
    apm_client_pem="apm_client_pem"
    apm_ca_cer="apm_intermediate_cer"
    echo "something staging"
    ;;

production )
    root_ca_cer="internal_scb_root_ca_cer"
    ssl_ca_cer="internal_scb_intermediate_ca_cer"
    consumer_cer="kong_prod_consumer_cer"
    consumer_key="kong_prod_consumer_key"
    boc_keystore_cer="HK_OB_CJ_BOC_KEYSTORE"
    boc_keystore_key="HK_OB_CJ_BOC_KEYSTORE_KEY"
    citi_keystore_cer="HK_OB_CJ_CITI_KEYSTORE"
    citi_keystore_key="HK_OB_CJ_CITI_KEYSTORE_KEY"
    hsbc_keystore_cer="HK_OB_CJ_HSBC_KEYSTORE"
    hsbc_keystore_key="HK_OB_CJ_HSBC_KEYSTORE_KEY"
    hase_keystore_cer="HK_OB_CJ_RL_HASE_KEYSTORE"
    hase_keystore_key="HK_OB_CJ_RL_HASE_KEYSTORE_KEY"
    citi_root_cer="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_ROOT_CERT"
    citi_inter_cer="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_INTER_CERT"
    hsbc_transport_cer="HK_OB_CJ_PARTNER_TRUST_STORE_HSBC_TRANSPORT_CERT"
    hase_transport_cer="HK_OB_CJ_RL_PARTNER_TRUST_STORE_HASE_TRANSPORT_CERT"
    boc_transport_cer="HK_OB_CJ_PARTNER_TRUST_STORE_BOC_TRANSPORT_CERT"
    mspki_root_cer="Solace_mspki_Root_cer"
    mspki_inter_cer="Solace_mspki_Intermediate_cer"
    solace_batch_consumer_cer="HK_OB_CJ_SOLACE_CER"
    solace_batch_consumer_key="HK_OB_CJ_SOLACE_KEY"
    apm_client_pem="apm_client_pem"
    apm_ca_cer="apm_intermediate_cer"
    echo "something production"
    ;;

*)
    echo "something wrong"
    ;;
esac

SOURCEDIR="/apps/config/api-services/ssm"
DESTDIR="/apps/config/api-services/cert-store"
JAVA_BIN="/jre/bin"

mkdir -p $DESTDIR

if [ -f ${SOURCEDIR}/$root_ca_cer ]; then
   cp ${SOURCEDIR}/$root_ca_cer ${DESTDIR}/${root_ca_cer}.cer
else
   echo "${SOURCEDIR}/$root_ca_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$root_ca_cer not found"
fi

if [ -f ${SOURCEDIR}/$ssl_ca_cer ]; then
  cp ${SOURCEDIR}/$ssl_ca_cer ${DESTDIR}/${ssl_ca_cer}.cer
else
   echo "${SOURCEDIR}/$ssl_ca_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$ssl_ca_cer not found"
fi

if [ -f ${SOURCEDIR}/$consumer_cer ]; then
   cp ${SOURCEDIR}/$consumer_cer ${DESTDIR}/${consumer_cer}.cer
else
   echo "${SOURCEDIR}/$consumer_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$consumer_cer not found"
fi

if [ -f ${SOURCEDIR}/$consumer_key ]; then
   cp ${SOURCEDIR}/$consumer_key ${DESTDIR}/${consumer_key}.key
else
   echo "${SOURCEDIR}/$consumer_key not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$consumer_key not found"
fi

if [ -f ${SOURCEDIR}/keystore_password ]; then
   cat ${SOURCEDIR}/keystore_password > ${DESTDIR}/keystore_password
else
   echo "${SOURCEDIR}/keystore_password not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/keystore_password not found"
fi

if [ -f ${SOURCEDIR}/$apm_ca_cer ]; then
   cp ${SOURCEDIR}/$apm_ca_cer ${DESTDIR}/apm_ca_cer.cer
else
   echo "${SOURCEDIR}/$apm_ca_cer not found" >> $DESTDIR/ssm.log
fi

if [ -f ${SOURCEDIR}/$apm_client_pem ]; then
   cp ${SOURCEDIR}/$apm_client_pem ${DESTDIR}/apm_client_pem.pem
else
   echo "${SOURCEDIR}/$apm_client_pem not found" >> $DESTDIR/ssm.log
fi

if [ -f ${SOURCEDIR}/$boc_keystore_cer ]; then
   cp ${SOURCEDIR}/$boc_keystore_cer ${DESTDIR}/${boc_keystore_cer}.cer
else
   echo "${SOURCEDIR}/$boc_keystore_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$boc_keystore_cer not found"
fi

if [ -f ${SOURCEDIR}/$boc_keystore_key ]; then
   cp ${SOURCEDIR}/$boc_keystore_key ${DESTDIR}/${boc_keystore_key}.key
else
   echo "${SOURCEDIR}/$boc_keystore_key not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$boc_keystore_key not found"
fi

if [ -f ${SOURCEDIR}/$citi_keystore_cer ]; then
   cp ${SOURCEDIR}/$citi_keystore_cer ${DESTDIR}/${citi_keystore_cer}.cer
else
   echo "${SOURCEDIR}/$citi_keystore_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$citi_keystore_cer not found"
fi

if [ -f ${SOURCEDIR}/$citi_keystore_key ]; then
   cp ${SOURCEDIR}/$citi_keystore_key ${DESTDIR}/${citi_keystore_key}.key
else
   echo "${SOURCEDIR}/$citi_keystore_key not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$citi_keystore_key not found"
fi

if [ -f ${SOURCEDIR}/$hsbc_keystore_cer ]; then
   cp ${SOURCEDIR}/$hsbc_keystore_cer ${DESTDIR}/${hsbc_keystore_cer}.cer
else
   echo "${SOURCEDIR}/$hsbc_keystore_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$hsbc_keystore_cer not found"
fi

if [ -f ${SOURCEDIR}/$hsbc_keystore_key ]; then
   cp ${SOURCEDIR}/$hsbc_keystore_key ${DESTDIR}/${hsbc_keystore_key}.key
else
   echo "${SOURCEDIR}/$hsbc_keystore_key not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$hsbc_keystore_key not found"
fi

if [ -f ${SOURCEDIR}/$citi_root_cer ]; then
   cp ${SOURCEDIR}/$citi_root_cer ${DESTDIR}/${citi_root_cer}.cer
else
   echo "${SOURCEDIR}/$citi_root_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$citi_root_cer not found"
fi

if [ -f ${SOURCEDIR}/$citi_inter_cer ]; then
   cp ${SOURCEDIR}/$citi_inter_cer ${DESTDIR}/${citi_inter_cer}.cer
else
   echo "${SOURCEDIR}/$citi_inter_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$citi_inter_cer not found"
fi

if [ -f ${SOURCEDIR}/$hsbc_transport_cer ]; then
   cp ${SOURCEDIR}/$hsbc_transport_cer ${DESTDIR}/${hsbc_transport_cer}.cer
else
   echo "${SOURCEDIR}/$hsbc_transport_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$hsbc_transport_cer not found"
fi

if [ -f ${SOURCEDIR}/$boc_transport_cer ]; then
   cp ${SOURCEDIR}/$boc_transport_cer ${DESTDIR}/${boc_transport_cer}.cer
else
   echo "${SOURCEDIR}/$boc_transport_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$boc_transport_cer not found"
fi

if [ -f ${SOURCEDIR}/$hase_transport_cer ]; then
   cp ${SOURCEDIR}/$hase_transport_cer ${DESTDIR}/${hase_transport_cer}.cer
else
   echo "${SOURCEDIR}/$hase_transport_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$hase_transport_cer not found"
fi

if [ -f ${SOURCEDIR}/$hase_keystore_cer ]; then
   cp ${SOURCEDIR}/$hase_keystore_cer ${DESTDIR}/${hase_keystore_cer}.cer
else
   echo "${SOURCEDIR}/$hase_keystore_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$hase_keystore_cer not found"
fi

if [ -f ${SOURCEDIR}/$hase_keystore_key ]; then
   cp ${SOURCEDIR}/$hase_keystore_key ${DESTDIR}/${hase_keystore_key}.key
else
   echo "${SOURCEDIR}/$hase_keystore_key not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$hase_keystore_key not found"
fi

if [ -f ${SOURCEDIR}/$mspki_root_cer ]; then
   cp ${SOURCEDIR}/$mspki_root_cer ${DESTDIR}/${mspki_root_cer}.cer
else
   echo "${SOURCEDIR}/$mspki_root_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$mspki_root_cer not found"
fi

if [ -f ${SOURCEDIR}/$mspki_inter_cer ]; then
   cp ${SOURCEDIR}/$mspki_inter_cer ${DESTDIR}/${mspki_inter_cer}.cer
else
   echo "${SOURCEDIR}/$mspki_inter_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$mspki_inter_cer not found"
fi

if [ -f ${SOURCEDIR}/$solace_batch_consumer_cer ]; then
   cp ${SOURCEDIR}/$solace_batch_consumer_cer ${DESTDIR}/${solace_batch_consumer_cer}.cer
else
   echo "${SOURCEDIR}/$solace_batch_consumer_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$solace_batch_consumer_cer not found"
fi

if [ -f ${SOURCEDIR}/$solace_batch_consumer_key ]; then
   cp ${SOURCEDIR}/$solace_batch_consumer_key ${DESTDIR}/${solace_batch_consumer_key}.key
else
   echo "${SOURCEDIR}/$solace_batch_consumer_key not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$solace_batch_consumer_key not found"
fi

if [[ $ENVIRONMENT == "development" ]] && [ -f ${SOURCEDIR}/$solace_root_ca_cer ]; then
   cp ${SOURCEDIR}/$solace_root_ca_cer ${DESTDIR}/${solace_root_ca_cer}.cer

else
   echo "${SOURCEDIR}/$solace_root_ca_cer not found" >> $DESTDIR/ssm.log
   echo "${SOURCEDIR}/$solace_root_ca_cer not found"
fi

#Generate P12 file
openssl pkcs12 -export -out ${DESTDIR}/kong_consumer.p12 -inkey ${DESTDIR}/${consumer_key}.key -in ${DESTDIR}/${consumer_cer}.cer -password pass:$[[{storepass}]]

#Generate JKS file
${JAVA_BIN}/keytool -importkeystore -srckeystore ${DESTDIR}/kong_consumer.p12 -srcstoretype pkcs12 -destkeystore ${DESTDIR}/kong_consumer.jks -deststoretype JKS -storepass $[[{storepass}]] -srcstorepass $[[{storepass}]] -deststorepass $[[{storepass}]]

${JAVA_BIN}/keytool -import -trustcacerts -alias scbroot -file ${DESTDIR}/${root_ca_cer}.cer -keystore ${DESTDIR}/kong_consumer.jks -storepass $[[{storepass}]] -noprompt

${JAVA_BIN}/keytool -import -trustcacerts -alias scbuat -file ${DESTDIR}/${ssl_ca_cer}.cer -keystore ${DESTDIR}/kong_consumer.jks -storepass $[[{storepass}]] -noprompt

${JAVA_BIN}/keytool -import -trustcacerts -alias mspkiroot -file ${DESTDIR}/${mspki_root_cer}.cer -keystore ${DESTDIR}/kong_consumer.jks -storepass $[[{storepass}]] -noprompt

${JAVA_BIN}/keytool -import -trustcacerts -alias mspkiuat -file ${DESTDIR}/${mspki_inter_cer}.cer -keystore ${DESTDIR}/kong_consumer.jks -storepass $[[{storepass}]] -noprompt

${JAVA_BIN}/keytool -import -trustcacerts -alias apm_cert -file ${DESTDIR}/${apm_ca_cer}.cer -keystore ${DESTDIR}/kong_consumer.jks -storepass $[[{storepass}]] -noprompt

if [[ $ENVIRONMENT == development ]]; then
    ${JAVA_BIN}/keytool -import -trustcacerts -alias scbsolaceroot -file ${DESTDIR}/${solace_root_ca_cer}.cer -keystore ${DESTDIR}/kong_consumer.jks -storepass $[[{storepass}]] -noprompt
    echo "${solace_root_ca_cer}.cer added in kong_consumer.jks" >> $DESTDIR/ssm.log
fi

#Convert JKS file to txt file
${JAVA_BIN}/keytool -list -v -keystore ${DESTDIR}/kong_consumer.jks -storepass $[[{storepass}]] -deststorepass $[[{storepass}]] > ${DESTDIR}/kong_consumer.txt


# BOC
openssl pkcs12 -export -out ${DESTDIR}/boc_keystore.p12 -inkey ${DESTDIR}/${boc_keystore_key}.key -in ${DESTDIR}/${boc_keystore_cer}.cer -password pass:$[[{storepass}]]

if [ ! -f ${DESTDIR}/boc_keystore.p12 ]; then
    echo "${DESTDIR}/boc_keystore.p12 File not found!" >> $DESTDIR/ssm.log
    echo "${DESTDIR}/boc_keystore.p12 File not found!"
fi

${JAVA_BIN}/keytool -importkeystore -srckeystore ${DESTDIR}/boc_keystore.p12 -srcstoretype pkcs12 -destkeystore ${DESTDIR}/boc_keystore.jks -deststoretype JKS -storepass $[[{storepass}]] -srcstorepass $[[{storepass}]] -deststorepass $[[{storepass}]]

if [ ! -f ${DESTDIR}/boc_keystore.jks ]; then
    echo "${DESTDIR}/boc_keystore.jks File not found!" >> $DESTDIR/ssm.log
    echo "${DESTDIR}/boc_keystore.jks File not found!"
fi

# CITI
openssl pkcs12 -export -out ${DESTDIR}/citi_keystore.p12 -inkey ${DESTDIR}/${citi_keystore_key}.key -in ${DESTDIR}/${citi_keystore_cer}.cer -password pass:$[[{storepass}]]

if [ ! -f ${DESTDIR}/citi_keystore.p12 ]; then
    echo "${DESTDIR}/citi_keystore.p12 File not found!" >> $DESTDIR/ssm.log
    echo "${DESTDIR}/citi_keystore.p12 File not found!"
fi

${JAVA_BIN}/keytool -importkeystore -srckeystore ${DESTDIR}/citi_keystore.p12 -srcstoretype pkcs12 -destkeystore ${DESTDIR}/citi_keystore.jks -deststoretype JKS -storepass $[[{storepass}]] -srcstorepass $[[{storepass}]] -deststorepass $[[{storepass}]]

if [ ! -f ${DESTDIR}/citi_keystore.jks ]; then
    echo "${DESTDIR}/citi_keystore.jks File not found!" >> $DESTDIR/ssm.log
    echo "${DESTDIR}/citi_keystore.jks File not found!"
fi

# HSBC
openssl pkcs12 -export -out ${DESTDIR}/hsbc_keystore.p12 -inkey ${DESTDIR}/${hsbc_keystore_key}.key -in ${DESTDIR}/${hsbc_keystore_cer}.cer -password pass:$[[{storepass}]]

if [ ! -f ${DESTDIR}/hsbc_keystore.p12 ]; then
    echo "${DESTDIR}/hsbc_keystore.p12 File not found!" >> $DESTDIR/ssm.log
    echo "${DESTDIR}/hsbc_keystore.p12 File not found!"
fi

${JAVA_BIN}/keytool -importkeystore -srckeystore ${DESTDIR}/hsbc_keystore.p12 -srcstoretype pkcs12 -destkeystore ${DESTDIR}/hsbc_keystore.jks -deststoretype JKS -storepass $[[{storepass}]] -srcstorepass $[[{storepass}]] -deststorepass $[[{storepass}]]

if [ ! -f ${DESTDIR}/hsbc_keystore.jks ]; then
    echo "${DESTDIR}/hsbc_keystore.jks File not found!" >> $DESTDIR/ssm.log
    echo "${DESTDIR}/hsbc_keystore.jks File not found!"
fi

# HASE
openssl pkcs12 -export -out ${DESTDIR}/hase_keystore.p12 -inkey ${DESTDIR}/${hase_keystore_key}.key -in ${DESTDIR}/${hase_keystore_cer}.cer -password pass:$[[{storepass}]]

if [ ! -f ${DESTDIR}/hase_keystore.p12 ]; then
    echo "${DESTDIR}/hase_keystore.p12 File not found!" >> $DESTDIR/ssm.log
    echo "${DESTDIR}/hase_keystore.p12 File not found!"
fi

${JAVA_BIN}/keytool -importkeystore -srckeystore ${DESTDIR}/hase_keystore.p12 -srcstoretype pkcs12 -destkeystore ${DESTDIR}/hase_keystore.jks -deststoretype JKS -storepass $[[{storepass}]] -srcstorepass $[[{storepass}]] -deststorepass $[[{storepass}]]

if [ ! -f ${DESTDIR}/hase_keystore.jks ]; then
    echo "${DESTDIR}/hase_keystore.jks File not found!" >> $DESTDIR/ssm.log
    echo "${DESTDIR}/hase_keystore.jks File not found!"
fi


# PARTNER BANK TRUSTSTORE
${JAVA_BIN}/keytool -import -trustcacerts -alias citi-root-base64 -file ${DESTDIR}/${citi_root_cer}.cer -keystore ${DESTDIR}/partner_bank_truststore.jks -storepass $[[{storepass}]] -noprompt

if [ ! -f ${DESTDIR}/partner_bank_truststore.jks ]; then
    echo "After citi-root-base64 ${DESTDIR}/partner_bank_truststore.jks File not found!" >> $DESTDIR/ssm.log
    echo "After citi-root-base64 ${DESTDIR}/partner_bank_truststore.jks File not found!"
fi

${JAVA_BIN}/keytool -import -trustcacerts -alias citi-inter-base64 -file ${DESTDIR}/${citi_inter_cer}.cer -keystore ${DESTDIR}/partner_bank_truststore.jks -storepass $[[{storepass}]] -noprompt

if [ ! -f ${DESTDIR}/partner_bank_truststore.jks ]; then
    echo "After citi-inter-base64 ${DESTDIR}/partner_bank_truststore.jks File not found!" >> $DESTDIR/ssm.log
    echo "After citi-inter-base64 ${DESTDIR}/partner_bank_truststore.jks File not found!"
fi

${JAVA_BIN}/keytool -import -trustcacerts -alias hsbc-transport -file ${DESTDIR}/${hsbc_transport_cer}.cer -keystore ${DESTDIR}/partner_bank_truststore.jks -storepass $[[{storepass}]] -noprompt

if [ ! -f ${DESTDIR}/partner_bank_truststore.jks ]; then
    echo "After hsbc-transport ${DESTDIR}/partner_bank_truststore.jks File not found!" >> $DESTDIR/ssm.log
    echo "After hsbc-transport ${DESTDIR}/partner_bank_truststore.jks File not found!"
fi

${JAVA_BIN}/keytool -import -trustcacerts -alias boc-transport -file ${DESTDIR}/${boc_transport_cer}.cer -keystore ${DESTDIR}/partner_bank_truststore.jks -storepass $[[{storepass}]] -noprompt

if [ ! -f ${DESTDIR}/partner_bank_truststore.jks ]; then
    echo "After boc-transport ${DESTDIR}/partner_bank_truststore.jks File not found!" >> $DESTDIR/ssm.log
    echo "After boc-transport ${DESTDIR}/partner_bank_truststore.jks File not found!"
fi

${JAVA_BIN}/keytool -import -trustcacerts -alias hase-transport -file ${DESTDIR}/${hase_transport_cer}.cer -keystore ${DESTDIR}/partner_bank_truststore.jks -storepass $[[{storepass}]] -noprompt

if [ ! -f ${DESTDIR}/partner_bank_truststore.jks ]; then
    echo "After hase-transport ${DESTDIR}/partner_bank_truststore.jks File not found!" >> $DESTDIR/ssm.log
    echo "After hase-transport ${DESTDIR}/partner_bank_truststore.jks File not found!"
fi

# Solace
openssl pkcs12 -export -out ${DESTDIR}/51077-apisvcs-solace.pfx -inkey ${DESTDIR}/${solace_batch_consumer_key}.key -in ${DESTDIR}/${solace_batch_consumer_cer}.cer -password pass:$[[{storepass}]]

echo "File generate completed" >> $DESTDIR/ssm.log

echo "postStart completed" >> /tmp/postStart-done