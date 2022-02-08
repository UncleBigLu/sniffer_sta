#include <stdio.h>
#include "nvs_flash.h"
#include "sta.h"
#include "csi.h"

static const char* TAG = "main";
void app_main(void)
{
    ESP_ERROR_CHECK(nvs_flash_init());

    ESP_LOGI(TAG, "ESP_WIFI_MODE_STA");
    wifi_init_sta();

    csi_init();
    xTaskCreate(serial_print_csi_task, "serial_print_csi", 4096, NULL, 1, NULL);

}
