//
// Created by unclebiglu on 2/7/22.
//

#ifndef SNIFFER_STA_STA_H
#define SNIFFER_STA_STA_H

#define SSID "esp_ap"
#define PASSWD "iloveSCU"
#define MAXIMUM_RETRY 5


#include "esp_wifi.h"
#include "esp_log.h"

#include "freertos/event_groups.h"
/* FreeRTOS event group to signal when we are connected*/
EventGroupHandle_t s_wifi_event_group;

/* The event group allows multiple bits for each event, but we only care about two events:
 * - we are connected to the AP with an IP
 * - we failed to connect after the maximum amount of retries */
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT      BIT1

static int s_retry_num = 0;

static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                          int32_t event_id, void* event_data);
void wifi_init_sta();


#endif //SNIFFER_STA_STA_H
