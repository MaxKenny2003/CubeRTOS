#ifndef SCHEDULER_H
#define SCHEDULER_H

#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <sched.h>
#include <dirent.h>
#include <sys/types.h>

#include <time.h>
#include <sys/stat.h>

enum TaskType {
    DEFAULT,
    READ_DATA, 
    WRITE_DATA,
    UPLINK,
    DOWNLINK
};

enum currentMode {
    PREFLIGHT,
    FLIGHT,
    RECOVERY
};

enum error_enum {
    CLEAR,
    POSSIBLE_ERROR,
    ERRORED
};

typedef struct
{
    bool in_use[5];
    pthread_t threadArray[5];
    // Thread 1 and 2 are for reading sensors
    // Thread 3 is for writing data recieved
    // Thread 4 is for uplink
    // Thread 5 is for downlink
}threadStates;

enum heartbeat_status{
    BEAT_OK,
    BEAT_NOT_RECIEVED,
    BEAT_DEAD,
};

extern volatile enum heartbeat_status main_heartbeat;

typedef struct task{
    // Helper struct with useful information on task names
    char *name;
    int period;      // Necessary period of the task. Defaults to 1 second
    int priority;       // Priority of task. Lower number = higher priority. Defaults to 0
    int released;
    int thread;
    int running;
    enum TaskType task_type;
    enum error_enum error_state;
    long last_time_run;
    bool enabled;
    threadStates *threads; 
} Task;

typedef struct Mode{
    int number_mode_tasks;
    char *mode_name;
    Task *Tasks;
    //int write_task_number;
}Mode;

// In this file we are making the scheduler struct. C does not natively support classes, so we have to use a struct. 
// This is the header file that contains all of the necessary functionality
typedef struct Scheduler{
    Mode modes_of_operation[3];
    int time_zero;
    void (*initialize)(struct Scheduler* self);
    void (*run_scheduler)(struct Scheduler* self);
} Scheduler;

void initializeScheduler(Scheduler* self);

void runScheduler(Scheduler* self);

// Thread Functions //

void* scheduler_thread(void* arg);

void* run_python_file(void* arg);

int find_open_thread(int num_threads, threadStates* curr_threads, enum TaskType task_type);

bool check_data_exists();

void check_mode_switch(enum currentMode *current_state);

double get_altitude(enum currentMode *current_state);

bool check_can_run(enum error_enum error_state);

void change_error_state(Task *current_task);


// Appending to the log file
int get_latest_log_number(const char *dirpath);
void get_latest_log_path(char *buffer, size_t bufsize, const char *dirpath);
void append_to_log(const char *filepath, const char *message);
void append_to_log_single_function(const char *message);
int ensure_directory_exists(const char *path);

#endif