#pragma once

#include "esp_wifi.h"

static QueueHandle_t csi_queue;

void csi_init();
static void csi_callback(void* ctx, wifi_csi_info_t* data);

void serial_print_csi_task();