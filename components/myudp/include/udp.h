#ifndef SNIFFER_STA_UDP_H
#define SNIFFER_STA_UDP_H

#include "lwip/sockets.h"
#include "lwip/err.h"

#define PORT 3333
int init_sock();
void waiting_start_csi_task();

#endif //SNIFFER_STA_UDP_H
