create table if not exists application (
       application_id varchar(255) primary key,
);

create table if not exists devices (
       device_id varchar(255) primary key,
       application_id varchar(255),
       dev_eui varchar(17),
       join_eui varchar(17),
       dev_addr varchar(25),
       foreign key (application_id) references application
);

create table if not exists uplink_messages (
       msg_id_time time primary key,
       device_id varchar(255),
       session_key_id varchar(255),
       f_port int,
       f_cnt int,
       frm_payload varchar(255),
       rx_metadata varchar(16777215), /*MEDIUMTEXT*/
       settings varchar(65535),
       confirmed boolean,
       consumed_airtime varchar(32),
       foreign key device_id references (devices)
       
);
