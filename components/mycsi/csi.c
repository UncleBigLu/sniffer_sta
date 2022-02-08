#include "csi.h"
#include <string.h>

static const char* TAG = "mycsi";

void csi_init() {
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(&csi_callback, NULL));

    wifi_csi_config_t csicfg;

    csicfg.lltf_en = true;
    csicfg.htltf_en = true;
    csicfg.stbc_htltf2_en = true;
    // Enable to generate htlft data by averaging lltf and ht_ltf data when receiving HT packet.
    // Otherwise, use ht_ltf data directly. Default enabled
    csicfg.ltf_merge_en = true;
    //enable to turn on channel filter to smooth adjacent sub-carrier.
    // Disable it to keep independence of adjacent sub-carrier. Default enabled
    csicfg.channel_filter_en = true;
    // Maybe should be enabled to oberve csi amplitude change.....? To be tested.
    csicfg.manu_scale = false;

    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csicfg));

    ESP_ERROR_CHECK(esp_wifi_set_csi(true));

    csi_queue = xQueueCreate(5, sizeof(wifi_csi_info_t*));
}

void csi_callback(void* ctx, wifi_csi_info_t* data) {
    // Copy data into heap memory
    wifi_csi_info_t* data_cp =(wifi_csi_info_t*)malloc(sizeof(*data));
    memcpy(data_cp, data, sizeof(*data));
    // Post data to queue
    xQueueSendToBack(csi_queue, &data_cp, 0);
}

void serial_print_csi_task() {
    while (1) {
        // Get csi from queue
        wifi_csi_info_t *data = NULL;
        xQueueReceive(csi_queue, &data, portMAX_DELAY);
        printf("csi_length: %d", data->len);
        free(data);
    }
}