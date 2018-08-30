CREATE TABLE certificate_tree (
    tree_name text NOT NULL,
    date timestamp NOT NULL,
    trust_anchor_name text PRIMARY KEY,
    UNIQUE (tree_name)
);
CREATE TABLE stats (
    certificate_tree text PRIMARY KEY,
    trust_anchor_name text,
    date timestamp NOT NULL,
    total_objects integer,
    total_cer_objects integer,
    total_mft_objects integer,
    total_crl_objects integer,
    total_roa_objects integer, 
    valid_objects integer,
    valid_cer_objects integer,
    valid_mft_objects integer,
    valid_crl_objects integer,
    valid_roa_objects integer, 
    invalid_objects integer,
    invalid_cer_objects integer,
    invalid_mft_objects integer,
    invalid_crl_objects integer,
    invalid_roa_objects integer, 
    warning_objects integer,
    warning_cer_objects integer,
    warning_mft_objects integer,
    warning_crl_objects integer,
    warning_roa_objects integer

);
CREATE TABLE resource_certificate (
    certificate_name text PRIMARY KEY,
    subject text,
    serial_nr numeric,
    issuer text,
    subject_key_identifier text,
    authority_key_identifier text,
    public_key text,
    isEE boolean,
    isCA boolean,
    isRoot boolean,
    validity_period_start timestamp,
    validity_period_end timestamp,
    validation_status text, 
    validation_errors text[],
    validation_warnings text[],
    prefixes cidr[],
    asns bigint[],
    asn_ranges int8range[],
    manifest text,
    crl text,
    parent_certificate text,
    certificate_tree text NOT NULL,
    id bigint,
    parent_id bigint,
    has_kids boolean,
    location text
);
CREATE TABLE roa_resource_certificate (
    subject text,
    serial_nr numeric,
    issuer text,
    subject_key_identifier text,
    authority_key_identifier text,
    public_key text,
    isEE boolean,
    isCA boolean,
    isRoot boolean,
    validity_period_start timestamp,
    validity_period_end timestamp,
    prefixes cidr[],
    asns bigint[],
    asn_ranges int8range[],
    certificate_tree text NOT NULL,
    id bigint,
    parent_id bigint,
    roa_container text PRIMARY KEY
);
CREATE TABLE roa (
    roa_name text PRIMARY KEY,
    asn bigint,
    validity_period_start timestamp,
    validity_period_end timestamp,
    validation_status text, 
    validation_errors text[],
    validation_warnings text[],
    signing_time timestamp,
    prefixes roaprefix[],
    parent_certificate text,
    certificate_tree text NOT NULL,
    id bigint,
    parent_id bigint,
    ee_certificate_id bigint NOT NULL,
    location text
);
CREATE TABLE manifest (
    manifest_name text PRIMARY KEY,
    files text[],
    validity_period_start timestamp,
    validity_period_end timestamp,
    validation_status text, 
    validation_errors text[],
    validation_warnings text[],
    parent_certificate text,
    certificate_tree text NOT NULL,
    id bigint,
    parent_id bigint,
    location text
);
CREATE TABLE crl (
    crl_name text PRIMARY KEY,
    revoked_objects text[],
    validation_status text, 
    validation_errors text[],
    validation_warnings text[],
    parent_certificate text,
    certificate_tree text NOT NULL,
    id bigint,
    parent_id bigint,
    location text
);