#!/bin/bash

echo "ENVIRONMENT is ${ENVIRONMENT}"

declare -A certs

# Define certificates/keys for each environment in associative arrays
declare -A development=(
  [root_ca_cer]="internal_scb_root_ca_cer"
  [ssl_ca_cer]="internal_scb_intermediate_ca_cer"
  [consumer_cer]="kong_sit_consumer_cer"
  [consumer_key]="kong_sit_consumer_key"
  [boc_keystore_cer]="HK_OB_CJ_BOC_KEYSTORE"
  [boc_keystore_key]="HK_OB_CJ_BOC_KEYSTORE_KEY"
  [citi_keystore_cer]="HK_OB_CJ_CITI_KEYSTORE"
  [citi_keystore_key]="HK_OB_CJ_CITI_KEYSTORE_KEY"
  [hsbc_keystore_cer]="HK_OB_CJ_HSBC_KEYSTORE"
  [hsbc_keystore_key]="HK_OB_CJ_HSBC_KEYSTORE_KEY"
  [hase_keystore_cer]="HK_OB_CJ_RL_HASE_KEYSTORE"
  [hase_keystore_key]="HK_OB_CJ_RL_HASE_KEYSTORE_KEY"
  [citi_root_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_ROOT_CERT"
  [citi_inter_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_INTER_CERT"
  [hsbc_transport_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_HSBC_TRANSPORT_CERT"
  [hase_transport_cer]="HK_OB_CJ_RL_PARTNER_TRUST_STORE_HASE_TRANSPORT_CERT"
  [boc_transport_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_BOC_TRANSPORT_CERT"
  [mspki_root_cer]="Solace_mspki_Root_cer"
  [mspki_inter_cer]="Solace_mspki_Intermediate_cer"
  [solace_batch_consumer_cer]="HK_OB_CJ_SOLACE_CER"
  [solace_batch_consumer_key]="HK_OB_CJ_SOLACE_KEY"
  [apm_client_pem]="apm_client_pem"
  [apm_ca_cer]="apm_intermediate_cer"
  [solace_root_ca_cer]="internal_scb_solace_root_ca_cer_green"
)

declare -A staging=(
  [root_ca_cer]="internal_scb_root_ca_cer"
  [ssl_ca_cer]="internal_scb_intermediate_ca_cer"
  [consumer_cer]="kong_sit_consumer_cer"
  [consumer_key]="kong_sit_consumer_key"
  [boc_keystore_cer]="HK_OB_CJ_BOC_KEYSTORE"
  [boc_keystore_key]="HK_OB_CJ_BOC_KEYSTORE_KEY"
  [citi_keystore_cer]="HK_OB_CJ_CITI_KEYSTORE"
  [citi_keystore_key]="HK_OB_CJ_CITI_KEYSTORE_KEY"
  [hsbc_keystore_cer]="HK_OB_CJ_HSBC_KEYSTORE"
  [hsbc_keystore_key]="HK_OB_CJ_HSBC_KEYSTORE_KEY"
  [hase_keystore_cer]="HK_OB_CJ_RL_HASE_KEYSTORE"
  [hase_keystore_key]="HK_OB_CJ_RL_HASE_KEYSTORE_KEY"
  [citi_root_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_ROOT_CERT"
  [citi_inter_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_INTER_CERT"
  [hsbc_transport_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_HSBC_TRANSPORT_CERT"
  [hase_transport_cer]="HK_OB_CJ_RL_PARTNER_TRUST_STORE_HASE_TRANSPORT_CERT"
  [boc_transport_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_BOC_TRANSPORT_CERT"
  [mspki_root_cer]="Solace_mspki_Root_cer"
  [mspki_inter_cer]="Solace_mspki_Intermediate_cer"
  [solace_batch_consumer_cer]="HK_OB_CJ_SOLACE_CER"
  [solace_batch_consumer_key]="HK_OB_CJ_SOLACE_KEY"
  [apm_client_pem]="apm_client_pem"
  [apm_ca_cer]="apm_intermediate_cer"
)

declare -A production=(
  [root_ca_cer]="internal_scb_root_ca_cer"
  [ssl_ca_cer]="internal_scb_intermediate_ca_cer"
  [consumer_cer]="kong_prod_consumer_cer"
  [consumer_key]="kong_prod_consumer_key"
  [boc_keystore_cer]="HK_OB_CJ_BOC_KEYSTORE"
  [boc_keystore_key]="HK_OB_CJ_BOC_KEYSTORE_KEY"
  [citi_keystore_cer]="HK_OB_CJ_CITI_KEYSTORE"
  [citi_keystore_key]="HK_OB_CJ_CITI_KEYSTORE_KEY"
  [hsbc_keystore_cer]="HK_OB_CJ_HSBC_KEYSTORE"
  [hsbc_keystore_key]="HK_OB_CJ_HSBC_KEYSTORE_KEY"
  [hase_keystore_cer]="HK_OB_CJ_RL_HASE_KEYSTORE"
  [hase_keystore_key]="HK_OB_CJ_RL_HASE_KEYSTORE_KEY"
  [citi_root_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_ROOT_CERT"
  [citi_inter_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_CITI_INTER_CERT"
  [hsbc_transport_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_HSBC_TRANSPORT_CERT"
  [hase_transport_cer]="HK_OB_CJ_RL_PARTNER_TRUST_STORE_HASE_TRANSPORT_CERT"
  [boc_transport_cer]="HK_OB_CJ_PARTNER_TRUST_STORE_BOC_TRANSPORT_CERT"
  [mspki_root_cer]="Solace_mspki_Root_cer"
  [mspki_inter_cer]="Solace_mspki_Intermediate_cer"
  [solace_batch_consumer_cer]="HK_OB_CJ_SOLACE_CER"
  [solace_batch_consumer_key]="HK_OB_CJ_SOLACE_KEY"
  [apm_client_pem]="apm_client_pem"
  [apm_ca_cer]="apm_intermediate_cer"
)

# Select the correct environment array
case $ENVIRONMENT in
  development ) certs=("${development[@]}"); env_name="development" ;;
  staging ) certs=("${staging[@]}"); env_name="staging" ;;
  production ) certs=("${production[@]}"); env_name="production" ;;
  * )
    echo "something wrong"
    exit 1
    ;;
esac

# Assign variables from selected environment associative array
for key in "${!development[@]}"; do
  declare "$key"="${certs[${key}]}"
done

echo "something $env_name"

SOURCEDIR="/apps/config/api-services/ssm"
DESTDIR="/apps/config/api-services/cert-store"
JAVA_BIN="/jre/bin"

mkdir -p "$DESTDIR"

# Array of simple copy files (certificates and keys)
simple_copy_files=(
  root_ca_cer ssl_ca_cer consumer_cer consumer_key apm_ca_cer apm_client_pem
  boc_keystore_cer boc_keystore_key citi_keystore_cer citi_keystore_key
  hsbc_keystore_cer hsbc_keystore_key citi_root_cer citi_inter_cer hsbc_transport_cer
  boc_transport_cer hase_transport_cer hase_keystore_cer hase_keystore_key
  mspki_root_cer mspki_inter_cer solace_batch_consumer_cer solace_batch_consumer_key
)

# Function to copy a file and log errors
copy_file() {
  local varname=$1
  local src_file="${SOURCEDIR}/${!varname}"
  local dest_file="${DESTDIR}/${!varname}.cer"
  # For keys, extension changes to .key
  if [[ $varname == *key ]]; then
    dest_file="${DESTDIR}/${!varname}.key"
  elif [[ $varname == apm_client_pem ]]; then
    dest_file="${DESTDIR}/apm_client_pem.pem"
  elif [[ $varname == apm_ca_cer ]]; then
    dest_file="${DESTDIR}/apm_ca_cer.cer"
  fi

  if [ -f "$src_file" ]; then
    cp "$src_file" "$dest_file"
  else
    echo "$src_file not found" | tee -a "$DESTDIR/ssm.log"
  fi
}

for file_key in "${simple_copy_files[@]}"; do
  copy_file "$file_key"
done

if [[ $ENVIRONMENT == "development" ]]; then
  solace_src="${SOURCEDIR}/${solace_root_ca_cer}"
  solace_dest="${DESTDIR}/${solace_root_ca_cer}.cer"
  if [ -f "$solace_src" ]; then
    cp "$solace_src" "$solace_dest"
  else
    echo "$solace_src not found" | tee -a "$DESTDIR/ssm.log"
  fi
fi

storepass=$(cat "${SOURCEDIR}/keystore_password" 2>/dev/null)
if [ -z "$storepass" ]; then
  echo "keystore_password not found" | tee -a "$DESTDIR/ssm.log"
  exit 1
fi

# Generate P12 and JKS for consumer
openssl pkcs12 -export -out "${DESTDIR}/kong_consumer.p12" -inkey "${DESTDIR}/${consumer_key}.key" -in "${DESTDIR}/${consumer_cer}.cer" -password pass:"$storepass"

${JAVA_BIN}/keytool -importkeystore -srckeystore "${DESTDIR}/kong_consumer.p12" -srcstoretype pkcs12 -destkeystore "${DESTDIR}/kong_consumer.jks" -deststoretype JKS -storepass "$storepass" -srcstorepass "$storepass" -deststorepass "$storepass"

# Import CA certs into kong_consumer.jks
declare -A import_certs=(
  [scbroot]="$root_ca_cer"
  [scbuat]="$ssl_ca_cer"
  [mspkiroot]="$mspki_root_cer"
  [mspkiuat]="$mspki_inter_cer"
  [apm_cert]="$apm_ca_cer"
)

for alias in "${!import_certs[@]}"; do
  ${JAVA_BIN}/keytool -import -trustcacerts -alias "$alias" -file "${DESTDIR}/${import_certs[$alias]}.cer" -keystore "${DESTDIR}/kong_consumer.jks" -storepass "$storepass" -noprompt
done

if [[ $ENVIRONMENT == development ]]; then
  ${JAVA_BIN}/keytool -import -trustcacerts -alias scbsolaceroot -file "${DESTDIR}/${solace_root_ca_cer}.cer" -keystore "${DESTDIR}/kong_consumer.jks" -storepass "$storepass" -noprompt
  echo "${solace_root_ca_cer}.cer added in kong_consumer.jks" >> "$DESTDIR/ssm.log"
fi

# Convert JKS list to txt
${JAVA_BIN}/keytool -list -v -keystore "${DESTDIR}/kong_consumer.jks" -storepass "$storepass" > "${DESTDIR}/kong_consumer.txt"

# Keystore generation helper function
generate_keystore() {
  local name=$1
  local cer_var=$2
  local key_var=$3

  openssl pkcs12 -export -out "${DESTDIR}/${name}_keystore.p12" -inkey "${DESTDIR}/${!key_var}.key" -in "${DESTDIR}/${!cer_var}.cer" -password pass:"$storepass"
  if [ ! -f "${DESTDIR}/${name}_keystore.p12" ]; then
    echo "${DESTDIR}/${name}_keystore.p12 File not found!" | tee -a "$DESTDIR/ssm.log"
  fi

  ${JAVA_BIN}/keytool -importkeystore -srckeystore "${DESTDIR}/${name}_keystore.p12" -srcstoretype pkcs12 -destkeystore "${DESTDIR}/${name}_keystore.jks" -deststoretype JKS -storepass "$storepass" -srcstorepass "$storepass" -deststorepass "$storepass"
  if [ ! -f "${DESTDIR}/${name}_keystore.jks" ]; then
    echo "${DESTDIR}/${name}_keystore.jks File not found!" | tee -a "$DESTDIR/ssm.log"
  fi
}

generate_keystore "boc" boc_keystore_cer boc_keystore_key
generate_keystore "citi" citi_keystore_cer citi_keystore_key
generate_keystore "hsbc" hsbc_keystore_cer hsbc_keystore_key
generate_keystore "hase" hase_keystore_cer hase_keystore_key

# Partner Bank Truststore imports
partner_aliases=(
  "citi-root-base64 $citi_root_cer"
  "citi-inter-base64 $citi_inter_cer"
  "hsbc-transport $hsbc_transport_cer"
  "boc-transport $boc_transport_cer"
  "hase-transport $hase_transport_cer"
)

for entry in "${partner_aliases[@]}"; do
  alias=$(echo "$entry" | awk '{print $1}')
  cert_var=$(echo "$entry" | awk '{print $2}')
  ${JAVA_BIN}/keytool -import -trustcacerts -alias "$alias" -file "${DESTDIR}/${cert_var}.cer" -keystore "${DESTDIR}/partner_bank_truststore.jks" -storepass "$storepass" -noprompt
  if [ ! -f "${DESTDIR}/partner_bank_truststore.jks" ]; then
    echo "After $alias ${DESTDIR}/partner_bank_truststore.jks File not found!" | tee -a "$DESTDIR/ssm.log"
  fi
done

# Solace PFX generation
openssl pkcs12 -export -out "${DESTDIR}/51077-apisvcs-solace.pfx" -inkey "${DESTDIR}/${solace_batch_consumer_key}.key" -in "${DESTDIR}/${solace_batch_consumer_cer}.cer" -password pass:"$storepass"

echo "File generate completed" >> "$DESTDIR/ssm.log"
echo "postStart completed" >> /tmp/postStart-done