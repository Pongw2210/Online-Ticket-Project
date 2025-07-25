CREATE DATABASE ticket_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ticket_db;

CREATE TABLE event (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,                      -- Giới thiệu chương trình
    date VARCHAR(100),                     -- Thời gian
    location VARCHAR(255),                 -- Địa điểm
    location_detail TEXT,                  -- Địa chỉ chi tiết
    rules TEXT,                            -- Quy định chung
    authors TEXT,                          -- Nhóm tác giả
    producers TEXT,                        -- Nhà sản xuất
    image_url VARCHAR(255)                 -- Ảnh bìa sự kiện (nếu có)
);


CREATE TABLE ticket_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    price FLOAT,
    event_id INT,
    FOREIGN KEY (event_id) REFERENCES event(id)
);

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL
);

ALTER TABLE user MODIFY password_hash VARCHAR(256);


-- ALTER TABLE ticket_type DROP FOREIGN KEY ticket_type_ibfk_1; Xoa rang buoc
DROP TABLE event;