#!/bin/bash

echo "ENVIRONMENT is ${ENVIRONMENT}"

#-----------------------------
# Environment Configuration
#-----------------------------
set_env_vars() {
  local env=$1
  local consumer_prefix="kong_${env}_consumer"
  
  root_ca_cer="internal_scb_root_ca_cer"
  ssl_ca_cer="internal_scb_intermediate_ca_cer"
  consumer_cer="${consumer_prefix}_cer"
  consumer_key="${consumer_prefix}_key"

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

  [[ $env == "development" ]] && solace_root_ca_cer="internal_scb_solace_root_ca_cer_green"

  echo "something ${env}"
}

case $ENVIRONMENT in
  development|staging|production)
    set_env_vars "$ENVIRONMENT"
    ;;
  *)
    echo "Invalid ENVIRONMENT: ${ENVIRONMENT}"
    exit 1
    ;;
esac

#-----------------------------
# Directory setup
#-----------------------------
SOURCEDIR="/apps/config/api-services/ssm"
DESTDIR="/apps/config/api-services/cert-store"
JAVA_BIN="/jre/bin"
LOGFILE="${DESTDIR}/ssm.log"

mkdir -p "$DESTDIR"

#-----------------------------
# Helper Functions
#-----------------------------
copy_file() {
  local src="${SOURCEDIR}/$1"
  local dest="${DESTDIR}/$2"
  if [[ -f $src ]]; then
    cp "$src" "$dest"
  else
    echo "$src not found" | tee -a "$LOGFILE"
  fi
}

check_file() {
  local f=$1
  [[ -f $f ]] || echo "$f File not found!" | tee -a "$LOGFILE"
}

#-----------------------------
# File Copies
#-----------------------------
# Basic certificate and key copies
declare -A files_ext=(
  [$root_ca_cer]="${root_ca_cer}.cer"
  [$ssl_ca_cer]="${ssl_ca_cer}.cer"
  [$consumer_cer]="${consumer_cer}.cer"
  [$consumer_key]="${consumer_key}.key"
  [$boc_keystore_cer]="${boc_keystore_cer}.cer"
  [$boc_keystore_key]="${boc_keystore_key}.key"
  [$citi_keystore_cer]="${citi_keystore_cer}.cer"
  [$citi_keystore_key]="${citi_keystore_key}.key"
  [$hsbc_keystore_cer]="${hsbc_keystore_cer}.cer"
  [$hsbc_keystore_key]="${hsbc_keystore_key}.key"
  [$hase_keystore_cer]="${hase_keystore_cer}.cer"
  [$hase_keystore_key]="${hase_keystore_key}.key"
  [$citi_root_cer]="${citi_root_cer}.cer"
  [$citi_inter_cer]="${citi_inter_cer}.cer"
  [$hsbc_transport_cer]="${hsbc_transport_cer}.cer"
  [$boc_transport_cer]="${boc_transport_cer}.cer"
  [$hase_transport_cer]="${hase_transport_cer}.cer"
  [$mspki_root_cer]="${mspki_root_cer}.cer"
  [$mspki_inter_cer]="${mspki_inter_cer}.cer"
  [$solace_batch_consumer_cer]="${solace_batch_consumer_cer}.cer"
  [$solace_batch_consumer_key]="${solace_batch_consumer_key}.key"
)

for src in "${!files_ext[@]}"; do
  copy_file "$src" "${files_ext[$src]}"
done

# Optional files
copy_file "keystore_password" "keystore_password"
copy_file "$apm_ca_cer" "apm_ca_cer.cer"
copy_file "$apm_client_pem" "apm_client_pem.pem"

[[ $ENVIRONMENT == "development" && -n $solace_root_ca_cer ]] && copy_file "$solace_root_ca_cer" "${solace_root_ca_cer}.cer"

#-----------------------------
# Generate P12 and JKS
#-----------------------------
storepass='$[[{storepass}]]'
p12_file="${DESTDIR}/kong_consumer.p12"
jks_file="${DESTDIR}/kong_consumer.jks"

openssl pkcs12 -export -out "$p12_file" \
  -inkey "${DESTDIR}/${consumer_key}.key" \
  -in "${DESTDIR}/${consumer_cer}.cer" \
  -password pass:$storepass

$JAVA_BIN/keytool -importkeystore \
  -srckeystore "$p12_file" -srcstoretype pkcs12 \
  -destkeystore "$jks_file" -deststoretype JKS \
  -storepass $storepass -srcstorepass $storepass -deststorepass $storepass

# Import certs into JKS
for alias in \
  "scbroot:$root_ca_cer" \
  "scbuat:$ssl_ca_cer" \
  "mspkiroot:$mspki_root_cer" \
  "mspkiuat:$mspki_inter_cer" \
  "apm_cert:$apm_ca_cer"
do
  IFS=: read -r alias_name cert_name <<< "$alias"
  $JAVA_BIN/keytool -import -trustcacerts -alias "$alias_name" \
    -file "${DESTDIR}/${cert_name}.cer" -keystore "$jks_file" \
    -storepass $storepass -noprompt
done

if [[ $ENVIRONMENT == "development" && -n $solace_root_ca_cer ]]; then
  $JAVA_BIN/keytool -import -trustcacerts -alias scbsolaceroot \
    -file "${DESTDIR}/${solace_root_ca_cer}.cer" -keystore "$jks_file" \
    -storepass $storepass -noprompt
  echo "${solace_root_ca_cer}.cer added in kong_consumer.jks" >> "$LOGFILE"
fi

# Convert JKS to TXT
$JAVA_BIN/keytool -list -v -keystore "$jks_file" -storepass $storepass > "${DESTDIR}/kong_consumer.txt"

#-----------------------------
# Generate PKCS12 and JKS for banks
#-----------------------------
generate_keystore() {
  local bank=$1
  openssl pkcs12 -export -out "${DESTDIR}/${bank}_keystore.p12" \
    -inkey "${DESTDIR}/${!bank"_keystore_key"}.key" \
    -in "${DESTDIR}/${!bank"_keystore_cer"}.cer" \
    -password pass:$storepass
  check_file "${DESTDIR}/${bank}_keystore.p12"

  $JAVA_BIN/keytool -importkeystore \
    -srckeystore "${DESTDIR}/${bank}_keystore.p12" \
    -srcstoretype pkcs12 \
    -destkeystore "${DESTDIR}/${bank}_keystore.jks" \
    -deststoretype JKS \
    -storepass $storepass -srcstorepass $storepass -deststorepass $storepass
  check_file "${DESTDIR}/${bank}_keystore.jks"
}

for bank in boc citi hsbc hase; do
  generate_keystore "$bank"
done

#-----------------------------
# Partner Bank Truststore
#-----------------------------
truststore="${DESTDIR}/partner_bank_truststore.jks"
for alias in \
  "citi-root-base64:$citi_root_cer" \
  "citi-inter-base64:$citi_inter_cer" \
  "hsbc-transport:$hsbc_transport_cer" \
  "boc-transport:$boc_transport_cer" \
  "hase-transport:$hase_transport_cer"
do
  IFS=: read -r alias_name cert <<< "$alias"
  $JAVA_BIN/keytool -import -trustcacerts -alias "$alias_name" \
    -file "${DESTDIR}/${cert}.cer" -keystore "$truststore" \
    -storepass $storepass -noprompt
  check_file "$truststore"
done

#-----------------------------
# Solace
#-----------------------------
openssl pkcs12 -export -out "${DESTDIR}/51077-apisvcs-solace.pfx" \
  -inkey "${DESTDIR}/${solace_batch_consumer_key}.key" \
  -in "${DESTDIR}/${solace_batch_consumer_cer}.cer" \
  -password pass:$storepass

echo "File generation completed" >> "$LOGFILE"
echo "postStart completed" >> /tmp/postStart-done