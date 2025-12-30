#include "scheduler.h"

int pack_count = 1; // start with 1 packet

static threadStates curr_thread_states = {
        .in_use = {false, false, false, false, false}
    };

// Initializes the scheduler to be 
void initializeScheduler(Scheduler* self)
{
    // Declare the # of tasks. Will most likely change this into a function that reads from a text file
    self->num_of_tasks = 11;
    // Allocate the memory for a dynamic array that stores this info.
    self->task_names = malloc(self->num_of_tasks * sizeof(Task));

    self->task_names[0] = (Task){"read_GPS.py", 10000, 0, 1, .enabled = true};
    self->task_names[0].task_type = READ_DATA;
    //self->task_names[1] = (Task){"read_RTC.py", 10000, 0, 1, .enabled = true};
    //self->task_names[1].task_type = READ_DATA;
    self->task_names[1] = (Task){"read_TMP1.py", 5000, 0, 1, .enabled = true};
    self->task_names[1].task_type = READ_DATA;
    self->task_names[2] = (Task){"read_TMP2.py", 5000, 0, 1, .enabled = true};
    self->task_names[2].task_type = READ_DATA;
    self->task_names[3] = (Task){"read_BME680.py", 4000, 0, 1, .enabled = true};
    self->task_names[3].task_type = READ_DATA;
    self->task_names[4] = (Task){"read_rm3100.py", 4000, 0, 1, .enabled = true};
    self->task_names[4].task_type = READ_DATA;
    self->task_names[5] = (Task){"read_PiStatus.py", 4000, 0, 1, .enabled = true};
    self->task_names[5].task_type = READ_DATA;
    self->task_names[6] = (Task){"read_IMU.py", 4000, 0, 1, .enabled = true};
    self->task_names[6].task_type = READ_DATA;
    self->task_names[7] = (Task){"eddy_pdu.py", 4000, 0, 1, .enabled = true};
    self->task_names[7].task_type = READ_DATA;
    self->task_names[8] = (Task){"read_reboot.py", 4000, 0, 1, .enabled = true};
    self->task_names[8].task_type = READ_DATA;
    self->task_names[9] = (Task){"write_data.py", 1000, 0, 1, .enabled = false};
    self->task_names[9].task_type = WRTIE_DATA;
    self->task_names[10] = (Task){"ALPHA_TX_LORA.py", 10000, 0, 1, .enabled = true};
    self->task_names[10].task_type = UPLINK;
    pack_count = pack_count + 1;

    //self->task_names[0] = (Task){"test3.py", 5000, 0, 1, .enabled = true, .threads = &curr_thread_states};
    //self->task_names[0].task_type = READ_DATA;

    for(int i = 0; i < self->num_of_tasks; i++)
    {
        self->task_names[i].threads = &curr_thread_states;
    }
    
}

void runScheduler(Scheduler* self)
{
    // Make variable for new thread once
    // Currently running on a thread that makes threads :)
    // Rather than intterupt threads (hard) we will create new ones or wait for one to become available;
    
    struct timespec start, now;
    self->time_zero = clock_gettime(CLOCK_MONOTONIC, &start);   // Start the timer 

    while (1)
    {   
    // curr_thread_states.in_use[0] = false;
    // curr_thread_states.in_use[1] = false;   // Still need some way to reset these naturally when the task is done.
    // curr_thread_states.in_use[2] = false;
    // curr_thread_states.in_use[3] = false;
    clock_gettime(CLOCK_MONOTONIC, &now);
    long now_ms = (now.tv_sec * 1000) + (now.tv_nsec / 1000000);
    
    // Check to see if the data directory has been created.
    if(check_data_exists() && !self->task_names[9].enabled)
    {
        // Data directory exists, if there are any files in it, we can start looping through the files and writing them. 
        //printf("Cooking");
        self->task_names[9].enabled = true; 
    }
    else
    {
        self->task_names[9].enabled = false;
    }

    //watchdog check for functions
    for (int i = 0; i < self->num_of_tasks; i++) {
        if (self->task_names[i].running) {
            if ((now_ms - self->task_names[i].last_time_run) > 10000) {
                int result = pthread_cancel(curr_thread_states.threadArray[self->task_names[i].thread]);
                self->task_names[i].threads->in_use[self->task_names[i].thread] = false;
                self->task_names[i].running = false;
                self->task_names[i].enabled = false;
                printf("Bark\r\n");
                self->task_names[i] = (Task){"rebootcounter.py", 1000, 0, 1, .enabled = false};
                self->task_names[i].task_type = WRTIE_DATA;
            }
        }
    }

    // Check which tasks are ready
    for (int i = 0; i < self->num_of_tasks; i++) {
        if (!self->task_names[i].released && self->task_names[i].enabled) {
            if ((now_ms - self->task_names[i].last_time_run) >= self->task_names[i].period) {
                self->task_names[i].released = 1;
            }
        }
    }

    // Run released tasks
    for (int i = 0; i < self->num_of_tasks; i++) {
        // if (self->task_names[i].running) {
        //     if ((now_ms - self->task_names[i].last_time_run) > 10000) {
        //         int result = pthread_cancel(curr_thread_states.threadArray[self->task_names[i].thread]);
        //         self->task_names[i].threads->in_use[self->task_names[i].thread] = false;
        //         self->task_names[i].running = false;
        //         self->task_names[i].enabled = false;
        //         printf("   / \\__\r\n  (    @\\___\r\n  /         O\r\n /   (_____/\r\n/_____/   U\r\n");
        //     }
        // }
        // if (!self->task_names[i].released && self->task_names[i].enabled) {
        //     if ((now_ms - self->task_names[i].last_time_run) >= self->task_names[i].period) {
        //         self->task_names[i].released = 1;
        //     }
        // }
        if (self->task_names[i].released && self->task_names[i].enabled && !self->task_names[i].running) {
            int num_threads = sizeof(curr_thread_states.threadArray) / sizeof(curr_thread_states.threadArray[0]);
            int open_thread_num = find_open_thread(num_threads, &curr_thread_states, self->task_names[i].task_type);

            if (open_thread_num != -1) {
                self->task_names[i].last_time_run = now_ms; // absolute ms
                self->task_names[i].released = 0;            // reset
                curr_thread_states.in_use[open_thread_num] = true;
                self->task_names[i].thread = open_thread_num;
                 pthread_create(&curr_thread_states.threadArray[open_thread_num],
                               NULL, run_python_file, &self->task_names[i]);
            }
        }
    }
}
}

void* scheduler_thread(void* arg) {
    Scheduler sched;

    sched.initialize = initializeScheduler;
    sched.run_scheduler = runScheduler;

    sched.initialize(&sched);
    sched.run_scheduler(&sched);
    return NULL;
}

void* run_python_file(void* arg) {
    //char* command = (char*) arg;
    Task* current_Task = (Task*) arg;
    current_Task->running = true;
    char* command = malloc(64);  // allocate memory for this thread
    snprintf(command, 64, "python3 %s", current_Task->name);
    int ret = system(command);
    //current_Task->released = 1;
    free(command);  // free memory allocated for this thread
    int exitCode = WEXITSTATUS(ret);
    if(exitCode == 1)
    {
        current_Task->enabled = false;
    }
    // pthread_t tid = pthread_self();
    /* Debugging for thread running */
    //printf("Hello from thread %lu\n", (unsigned long)tid);
    //current_Task->running = false;
    current_Task->running = false;
    current_Task->threads->in_use[current_Task->thread] = false;
    return NULL;
}

int find_open_thread(int num_threads, threadStates* curr_threads, enum TaskType task_type)
{
    switch (task_type){
        case READ_DATA:
            if(!curr_threads->in_use[0]) return 0;
            if(!curr_threads->in_use[1]) return 1;
            break;
        case WRTIE_DATA:
            if(!curr_threads->in_use[2]) return 2;
            break;
        case UPLINK:
            if(!curr_threads->in_use[3]) return 3;
            break;
        case DOWNLINK:
            if(!curr_threads->in_use[4]) return 4;
            break;
        default:
            return -1;
            break;
    }
    return -1;
}

bool check_data_exists()
{
    struct stat statbuf;
    const char* path = "data/";
    if (stat(path, &statbuf) != 0) {
        return false;  // Path does not exist
    }
    return S_ISDIR(statbuf.st_mode);  // True if directory
}
