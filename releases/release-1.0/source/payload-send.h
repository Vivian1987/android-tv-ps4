#ifndef ATV_PAYLOAD_SEND_H
#define ATV_PAYLOAD_SEND_H
#include <stddef.h>
/* One complete delivery to GoldHEN on 127.0.0.1:9090. No external address,
 * receiver probe, automatic retry, local execution or shutdown fallback. */
int atv_send_payload(const unsigned char *data, size_t bytes, size_t *sent);
#endif
