#ifndef ATV_LAUNCH_PROGRESS_H
#define ATV_LAUNCH_PROGRESS_H
/* Returns only on failure. Success leaves this app alive until Linux takes over. */
int atv_launch_with_progress(void);
#endif
