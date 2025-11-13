#!/bin/bash

set -e          # Exit on error
set -o pipefail # Catch errors in pipes
set -u          # Exit on undefined variables

# ============================================================================
# Configuration
# ============================================================================

readonly SOURCEDIR="/apps/config/api-services/ssm"
readonly DESTDIR="/apps/config/api-services/cert-store"
readonly JAVA_BIN="/jre/bin"
readonly LOG_FILE="${DESTDIR}/ssm.log"
readonly STOREPASS='$[[{storepass}]]'

echo "ENVIRONMENT is ${ENVIRONMENT}"

# ============================================================================
# Functions
# ============================================================================

# Log message to both file and stdout
log_message() {
    local message="$1"
    echo "${message}" | tee -a "${LOG_FILE}"
}

# Copy file with logging
copy_cert_file() {
    local var_name="$1"
    local extension="$2"
    local source_file="${SOURCEDIR}/${!var_name}"
    local dest_file="${DESTDIR}/${!var_name}.${extension}"
    
    if [[ -f "${source_file}" ]]; then
        cp "${source_file}" "${dest_file}"
    else
        log_message "${source_file} not found"
    fi
}

# Generate keystore for a bank
generate_bank_keystore() {
    local bank_name="$1"
    local cert_var="$2"
    local key_var="$3"
    
    local cert_file="${DESTDIR}/${!cert_var}.cer"
    local key_file="${DESTDIR}/${!key_var}.key"
    local p12_file="${DESTDIR}/${bank_name}_keystore.p12"
    local jks_file="${DESTDIR}/${bank_name}_keystore.jks"
    
    # Generate P12
    openssl pkcs12 -export -out "${p12_file}" \
        -inkey "${key_file}" -in "${cert_file}" \
        -password pass:"${STOREPASS}"
    
    [[ ! -f "${p12_file}" ]] && log_message "${p12_file} File not found!"
    
    # Convert to JKS
    "${JAVA_BIN}/keytool" -importkeystore \
        -srckeystore "${p12_file}" -srcstoretype pkcs12 \
        -destkeystore "${jks_file}" -deststoretype JKS \
        -storepass "${STOREPASS}" -srcstorepass "${STOREPASS}" \
        -deststorepass "${STOREPASS}"
    
    [[ ! -f "${jks_file}" ]] && log_message "${jks_file} File not found!"
}

# Import certificate into keystore
import_cert() {
    local alias="$1"
    local cert_file="$2"
    local keystore="$3"
    
    "${JAVA_BIN}/keytool" -import -trustcacerts \
        -alias "${alias}" -file "${cert_file}" \
        -keystore "${keystore}" -storepass "${STOREPASS}" -noprompt
}

# Set environment-specific variables
configure_environment() {
    # Common variables for all environments
    root_ca_cer="internal_scb_root_ca_cer"
    ssl_ca_cer="internal_scb_intermediate_ca_cer"
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
    
    # Environment-specific variables
    case "${ENVIRONMENT}" in
        development)
            consumer_cer="kong_sit_consumer_cer"
            consumer_key="kong_sit_consumer_key"
            solace_root_ca_cer="internal_scb_solace_root_ca_cer_green"
            echo "Configured for development"
            ;;
        staging)
            consumer_cer="kong_sit_consumer_cer"
            consumer_key="kong_sit_consumer_key"
            echo "Configured for staging"
            ;;
        production)
            consumer_cer="kong_prod_consumer_cer"
            consumer_key="kong_prod_consumer_key"
            echo "Configured for production"
            ;;
        *)
            log_message "ERROR: Invalid ENVIRONMENT: ${ENVIRONMENT}"
            exit 1
            ;;
    esac
}

# ============================================================================
# Main Execution
# ============================================================================

# Configure environment
configure_environment

# Create destination directory
mkdir -p "${DESTDIR}"

# Define certificate files to copy (variable_name:extension)
declare -A cert_files=(
    [root_ca_cer]="cer"
    [ssl_ca_cer]="cer"
    [consumer_cer]="cer"
    [consumer_key]="key"
    [apm_ca_cer]="cer"
    [apm_client_pem]="pem"
    [boc_keystore_cer]="cer"
    [boc_keystore_key]="key"
    [citi_keystore_cer]="cer"
    [citi_keystore_key]="key"
    [hsbc_keystore_cer]="cer"
    [hsbc_keystore_key]="key"
    [hase_keystore_cer]="cer"
    [hase_keystore_key]="key"
    [citi_root_cer]="cer"
    [citi_inter_cer]="cer"
    [hsbc_transport_cer]="cer"
    [boc_transport_cer]="cer"
    [hase_transport_cer]="cer"
    [mspki_root_cer]="cer"
    [mspki_inter_cer]="cer"
    [solace_batch_consumer_cer]="cer"
    [solace_batch_consumer_key]="key"
)

# Copy all certificate files
for var_name in "${!cert_files[@]}"; do
    copy_cert_file "${var_name}" "${cert_files[${var_name}]}"
done

# Copy keystore password
if [[ -f "${SOURCEDIR}/keystore_password" ]]; then
    cat "${SOURCEDIR}/keystore_password" > "${DESTDIR}/keystore_password"
else
    log_message "${SOURCEDIR}/keystore_password not found"
fi

# Copy development-specific certificate
if [[ "${ENVIRONMENT}" == "development" ]] && [[ -f "${SOURCEDIR}/${solace_root_ca_cer}" ]]; then
    cp "${SOURCEDIR}/${solace_root_ca_cer}" "${DESTDIR}/${solace_root_ca_cer}.cer"
fi

# ============================================================================
# Generate Kong Consumer Keystore
# ============================================================================

# Generate P12
openssl pkcs12 -export -out "${DESTDIR}/kong_consumer.p12" \
    -inkey "${DESTDIR}/${consumer_key}.key" \
    -in "${DESTDIR}/${consumer_cer}.cer" \
    -password pass:"${STOREPASS}"

# Convert to JKS
"${JAVA_BIN}/keytool" -importkeystore \
    -srckeystore "${DESTDIR}/kong_consumer.p12" -srcstoretype pkcs12 \
    -destkeystore "${DESTDIR}/kong_consumer.jks" -deststoretype JKS \
    -storepass "${STOREPASS}" -srcstorepass "${STOREPASS}" \
    -deststorepass "${STOREPASS}"

# Import certificates into Kong consumer keystore
import_cert "scbroot" "${DESTDIR}/${root_ca_cer}.cer" "${DESTDIR}/kong_consumer.jks"
import_cert "scbuat" "${DESTDIR}/${ssl_ca_cer}.cer" "${DESTDIR}/kong_consumer.jks"
import_cert "mspkiroot" "${DESTDIR}/${mspki_root_cer}.cer" "${DESTDIR}/kong_consumer.jks"
import_cert "mspkiuat" "${DESTDIR}/${mspki_inter_cer}.cer" "${DESTDIR}/kong_consumer.jks"
import_cert "apm_cert" "${DESTDIR}/${apm_ca_cer}.cer" "${DESTDIR}/kong_consumer.jks"

# Import Solace root certificate for development
if [[ "${ENVIRONMENT}" == "development" ]]; then
    import_cert "scbsolaceroot" "${DESTDIR}/${solace_root_ca_cer}.cer" "${DESTDIR}/kong_consumer.jks"
    log_message "${solace_root_ca_cer}.cer added in kong_consumer.jks"
fi

# Export keystore details
"${JAVA_BIN}/keytool" -list -v \
    -keystore "${DESTDIR}/kong_consumer.jks" \
    -storepass "${STOREPASS}" -deststorepass "${STOREPASS}" \
    > "${DESTDIR}/kong_consumer.txt"

# ============================================================================
# Generate Bank Keystores
# ============================================================================

generate_bank_keystore "boc" "boc_keystore_cer" "boc_keystore_key"
generate_bank_keystore "citi" "citi_keystore_cer" "citi_keystore_key"
generate_bank_keystore "hsbc" "hsbc_keystore_cer" "hsbc_keystore_key"
generate_bank_keystore "hase" "hase_keystore_cer" "hase_keystore_key"

# ============================================================================
# Generate Partner Bank Truststore
# ============================================================================

declare -A partner_certs=(
    [citi-root-base64]="${citi_root_cer}"
    [citi-inter-base64]="${citi_inter_cer}"
    [hsbc-transport]="${hsbc_transport_cer}"
    [boc-transport]="${boc_transport_cer}"
    [hase-transport]="${hase_transport_cer}"
)

for alias in "${!partner_certs[@]}"; do
    cert_var="${partner_certs[${alias}]}"
    import_cert "${alias}" "${DESTDIR}/${!cert_var}.cer" "${DESTDIR}/partner_bank_truststore.jks"
    
    if [[ ! -f "${DESTDIR}/partner_bank_truststore.jks" ]]; then
        log_message "After ${alias} ${DESTDIR}/partner_bank_truststore.jks File not found!"
    fi
done

# ============================================================================
# Generate Solace Certificate
# ============================================================================

openssl pkcs12 -export -out "${DESTDIR}/51077-apisvcs-solace.pfx" \
    -inkey "${DESTDIR}/${solace_batch_consumer_key}.key" \
    -in "${DESTDIR}/${solace_batch_consumer_cer}.cer" \
    -password pass:"${STOREPASS}"

# ============================================================================
# Completion
# ============================================================================

log_message "File generation completed"
echo "postStart completed" >> /tmp/postStart-done