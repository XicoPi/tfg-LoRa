create table if not exists applications (
       application_id varchar(255) primary key
);

create table if not exists devices (
       device_id varchar(255) primary key,
       application_id varchar(255) references applications,
       dev_eui varchar(17),
       join_eui varchar(17),
       dev_addr varchar(25)
);

create table if not exists uplink_messages (
       msg_id_time datetime,
       device_id varchar(255) references devices,
       session_key_id varchar(255),
       f_port int,
       f_cnt int,
       frm_payload varchar(255),
       rx_metadata TEXT(65535),
       settings TEXT(65535),
       /*confirmed boolean,*/
       consumed_airtime varchar(32),
       primary key (msg_id_time, device_id)
);

create table if not exists node_decoded_payloads (
       /*payload_id integer primary key AUTOINCREMENT,*/
       msg_id_time datetime primary key references uplink_messages,
       battery int,
       event varchar(16),
       light int,
       temperature float
);
