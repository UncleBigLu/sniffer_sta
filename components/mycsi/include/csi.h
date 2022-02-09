#pragma once

#include "esp_wifi.h"

static QueueHandle_t csi_queue;

void csi_init();
static void csi_callback(void* ctx, wifi_csi_info_t* data);

void serial_print_csi_task();

//Help functions to get csi data
/*
 * Function pointer array that points to help functions.
 * First dimension decides Secondary channel.
 * Second dimension decides signal mode.
 * Third dimension decides channel bandwidth.
 * Fourth dimension decides STBC.
 *
 * This array is initialed in _init_csi_help_arr function, called in csi_init();
 * */
static void (*csi_func_ptr[3][2][2][2])(wifi_csi_info_t *data, uint8_t subc_index, int8_t* img, int8_t* real);
static void _init_csi_help_arr();
/*
 * Secondary channel:       None
 * signal mode:             HT
 * channel bandwidth:       20MHz
 * STBC:                    non STBC
 * Theoretical total bytes: 256
 * */
static void _none_ht_20M_nstbc_htcsi(wifi_csi_info_t *data, uint8_t subc_index, int8_t* img, int8_t* real);
/*
 * Theoretical total bytes: 384
 * */
static void _below_ht_40M_nstbc_htcsi(wifi_csi_info_t *data, uint8_t subc_index, int8_t* img, int8_t* real);
/*
 * Theoretical total bytes: 128
 * */
static void _below_nht_20M_nstbc_htcsi(wifi_csi_info_t *data, uint8_t subc_index, int8_t* img, int8_t* real);
