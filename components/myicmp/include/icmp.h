//
// Created by unclebiglu on 2/8/22.
//
#include "ping/ping_sock.h"

#ifndef SNIFFER_STA_ICMP_H
#define SNIFFER_STA_ICMP_H

#define PING_TARGET_ADDR 0x0104A8C0 // 192.168.4.1
#define PING_INTERVAL_MS 10

esp_ping_handle_t ping_session;

void init_ping();
void on_ping_success(esp_ping_handle_t hdl, void *args);
void on_ping_timeout(esp_ping_handle_t hdl, void *args);
void on_ping_end(esp_ping_handle_t hdl, void *args);

#endif //SNIFFER_STA_ICMP_H
