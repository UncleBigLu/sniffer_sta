#include "csi.h"
#include <string.h>

static const char* TAG = "mycsi";

void csi_init() {
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(&csi_callback, NULL));

    wifi_csi_config_t csicfg;

    csicfg.lltf_en = true;
    csicfg.htltf_en = true;
    csicfg.stbc_htltf2_en = true;
    // Enable to generate htltf data by averaging lltf and ht_ltf data when receiving HT packet.
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

    _init_csi_help_arr();
}

void csi_callback(void* ctx, wifi_csi_info_t* data) {
    // Copy data into heap memory
    wifi_csi_info_t* data_cp =(wifi_csi_info_t*)malloc(sizeof(*data));
    memcpy(data_cp, data, sizeof(*data));
    // Post data to queue
    xQueueSendToBack(csi_queue, &data_cp, 0);
}

void serial_print_csi_task() {
    uint8_t sec_channel = 0, sig_mode = 0, cbw = 0, stbc = 0;
    while (1) {
        // Get csi from queue
        wifi_csi_info_t *data = NULL;
        xQueueReceive(csi_queue, &data, portMAX_DELAY);
        printf("csi_length: %d\n", data->len);

        printf("Source Mac addr: ");
        for(int i = 0; i < 5; ++i) {
            printf("%X:", data->mac[i]);
        }
        printf("%X\n", data->mac[5]);

        printf("Secondary channel: ");
        switch (data->rx_ctrl.secondary_channel) {
            case 0:
                printf("none\n");
                sec_channel = 0;
                break;
            case 1:
                printf("above\n");
                sec_channel = 2;
                break;
            case 2:
                printf("below\n");
                sec_channel = 1;
                break;
            default:
                printf("Error on secondary channel info\n");
                break;
        }

        printf("sig_mode: ");
        switch (data->rx_ctrl.sig_mode) {
            case 0:
                printf("non HT(11bg)\n");
                sig_mode = 0;
                break;
            case 1:
                printf("HT(11n)\n");
                sig_mode = 1;
                break;
            case 2:
                printf("VHT(11ac)\n");
                break;
            default:
                printf("Error about sig_mode info\n");
                break;
        }

        printf("stbc: ");
        if (data->rx_ctrl.stbc) {
            printf("true\n");
            stbc = 1;
        } else {
            printf("false\n");
            stbc = 0;
        }

        printf("channel bandwidth: ");
        if (data->rx_ctrl.cwb == 1) {
            printf("40MHz\n");
            cbw = 1;
        } else {
            printf("20MHz\n");
            cbw = 0;
        }

        // Call get csi function from function pointer array
        // Get csi from seconde subcarrier of HTLTF
        int8_t img, real;
        (*csi_func_ptr[sec_channel][sig_mode][cbw][stbc])(data, 2, &img, &real);
        printf("img: %d, real: %d\n", img, real);

        free(data);
    }
}

void _none_ht_20M_nstbc_htcsi(wifi_csi_info_t *data, uint8_t subc_index, int8_t* img, int8_t* real) {
    // LLTF: 0~31, -32~-1
    // HTLTF starts from 64th subcarrier
    // HTLTF: 0~31, -32~-1
    const uint8_t start_index = 64;
    *img = data->buf[start_index + subc_index * 2];
    *real = data->buf[start_index + subc_index * 2 + 1];

    printf("none_ht_20M_nstbc\n");
}

void _below_ht_40M_nstbc_htcsi(wifi_csi_info_t *data, uint8_t subc_index, int8_t* img, int8_t* real) {
    /*
     * LLTF: 0~63
     * HT-LTF: 0~63, -64~-1
     * */
    const uint8_t start_index = 64;
    *img = data->buf[start_index + subc_index * 2];
    *real = data->buf[start_index + subc_index * 2 + 1];

    printf("below_ht_40M_nstbc\n");
}

static void _below_nht_20M_nstbc_htcsi(wifi_csi_info_t *data, uint8_t subc_index, int8_t* img, int8_t* real) {
    // No HT-LTF data, return.
    printf("below_nht_20M_nstbc\n");
    return;
}

void _init_csi_help_arr() {
    csi_func_ptr[0][1][0][0] = _none_ht_20M_nstbc_htcsi;
    csi_func_ptr[1][0][0][0] = _below_nht_20M_nstbc_htcsi;
    csi_func_ptr[1][1][1][0] = _below_ht_40M_nstbc_htcsi;
}
