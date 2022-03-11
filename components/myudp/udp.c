#include "udp.h"
#include "esp_log.h"
static const char *TAG = "myudp.c";

int init_sock() {
    int ip_protocol = IPPROTO_IP;
    int sock;
    while (1) {
        sock = socket(AF_INET, SOCK_DGRAM, ip_protocol);
        if(sock < 0) {
            ESP_LOGI(TAG, "unable to create socket: errno %d. Retrying...", errno);
            vTaskDelay(500/portTICK_PERIOD_MS);
            continue;
        }
        break;
    }

    return sock;
}

void waiting_start_csi_task() {
    int sock = 0;
waitStart:
    sock = init_sock();

    char rx_buffer[10];

    struct sockaddr_in6 dest_addr;
    struct sockaddr_in *dest_addr_ip4 = (struct sockaddr_in *)&dest_addr;
    dest_addr_ip4->sin_addr.s_addr = htonl(INADDR_ANY);
    dest_addr_ip4->sin_family = AF_INET;
    dest_addr_ip4->sin_port = htons(PORT);

    int err = bind(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err < 0) {
        ESP_LOGE(TAG, "Socket unable to bind: errno %d", errno);
        goto closeSoc;
    }
    ESP_LOGI(TAG, "Socket bound, port %d", PORT);

  
    struct sockaddr_storage source_addr; // Large enough for both IPv4 or IPv6
    socklen_t socklen = sizeof(source_addr);
    int len = recvfrom(sock, rx_buffer, sizeof(rx_buffer) - 1, 0, (struct sockaddr *)&source_addr, &socklen);
    if (len < 0) {
        ESP_LOGE(TAG, "recvfrom failed: errno %d", errno);
        goto closeSoc;
    }
    rx_buffer[len] = '\0';
    if(strcmp(rx_buffer, "start") == 0) {
        printf("start CSI\n");
    }
    
    vTaskDelete(NULL);
    return;
    
closeSoc:
    ESP_LOGE(TAG, "Shutting down socket and restarting...");
    shutdown(sock, 0);
    close(sock);
    goto waitStart;
}
