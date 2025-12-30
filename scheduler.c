#include "scheduler.h"
#include "cJSON.c"

int current_mode;
//int write_task_num = -1;
long modes_last_time_checked_switch = 0;

enum currentMode current_sat_mode = PREFLIGHT;

static threadStates curr_thread_states = {
        .in_use = {false, false, false, false, false}
    };

// Initializes the scheduler to be 
void initializeScheduler(Scheduler* self)
{
    FILE *fp = fopen("tasks.json", "r");
    if(fp == NULL)
    {
        printf("Error: Unable to open the file\n");
        return;
    }

    char buffer[20000];
    int len = fread(buffer, 1, sizeof(buffer), fp);
    fclose(fp);

    cJSON *json = cJSON_Parse(buffer);
    if (json == NULL){
        const char *error_ptr = cJSON_GetErrorPtr();
        if (error_ptr != NULL) {
            printf("Error: %s\n", error_ptr);
        }
        cJSON_Delete(json);
        return;
    }

    // Get the modes array
    cJSON *modes = cJSON_GetObjectItemCaseSensitive(json, "modes");

    cJSON *mode = NULL;
    int i = 0;
    cJSON_ArrayForEach(mode, modes)
    {
        cJSON *mode_entry = NULL;

        cJSON_ArrayForEach(mode_entry, mode)
        {
            /*** This loop go through each entry in the modes array in the task.json file ***/ 

            /*** Debugging print statment for mode names ***/
            // printf("Mode: %s \n", mode_entry->string);       
            self->modes_of_operation[i].mode_name = mode_entry->string;

            cJSON *tasks = mode_entry;
            cJSON *task = NULL;

            int num_tasks_in_mode = 0;
            cJSON_ArrayForEach(task, tasks)
            {
                cJSON *name = cJSON_GetObjectItemCaseSensitive(task, "name");

                /*** Debugging print statement for task names ***/ 
                // printf("    Task: %s\n", name->valuestring);
                num_tasks_in_mode += 1;
            }
            /*** Debugging print statement for number of tasks in each mode ***/
            // printf("%d\n", num_tasks_in_mode);
            self->modes_of_operation[i].number_mode_tasks = num_tasks_in_mode;
            self->modes_of_operation[i].Tasks = malloc(num_tasks_in_mode * sizeof(Task));
            //self->modes_of_operation[i].write_task_number = -1;
            int index = 0;
            cJSON_ArrayForEach(task, tasks)
            {
                // printf("I = %d   Index = %d\n", i, index);
                cJSON *name = cJSON_GetObjectItemCaseSensitive(task, "name");
                if (cJSON_IsString(name)) {
                    // printf("Task Name %s\n", name->valuestring);
                    self->modes_of_operation[i].Tasks[index].name = strdup(name->valuestring);
                }
                cJSON *period = cJSON_GetObjectItemCaseSensitive(task, "period");
                if(cJSON_IsNumber(period)){
                    // printf("Task Period %d\n", period->valueint);
                    self->modes_of_operation[i].Tasks[index].period = period->valueint;
                }
                cJSON *priority = cJSON_GetObjectItemCaseSensitive(task, "priority");
                if(cJSON_IsNumber(priority)){
                    self->modes_of_operation[i].Tasks[index].priority = priority->valueint;
                }
                cJSON *released = cJSON_GetObjectItemCaseSensitive(task, "released");
                if(cJSON_IsNumber(released)){
                    self->modes_of_operation[i].Tasks[index].released = released->valueint;
                }
                cJSON *enabled = cJSON_GetObjectItemCaseSensitive(task, "enabled");
                if(cJSON_IsBool(enabled)){
                    self->modes_of_operation[i].Tasks[index].enabled = cJSON_IsTrue(enabled);
                }
                cJSON *task_type = cJSON_GetObjectItemCaseSensitive(task, "task_type");
                switch(task_type->valuestring[0])
                {
                    case 'R':
                        self->modes_of_operation[i].Tasks[index].task_type = READ_DATA;
                        break;
                    case 'W':
                        //self->modes_of_operation[i].write_task_number = index;
                        self->modes_of_operation[i].Tasks[index].task_type = WRITE_DATA;
                        break;
                    case 'U':
                        self->modes_of_operation[i].Tasks[index].task_type = UPLINK;
                        break;
                    case 'D':
                        self->modes_of_operation[i].Tasks[index].task_type = DOWNLINK;
                        break;
                    default:
                        self->modes_of_operation[i].Tasks[index].task_type = READ_DATA;
                        break;
                }
                self->modes_of_operation[i].Tasks[index].threads = &curr_thread_states;
                index += 1;
            } // loop through tasks in a given mode
            i += 1;
        } // Loop through each of the modes
    } // Initial loop through the JSON
    cJSON_Delete(json);
} // Initialize function end

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
    // if(self->modes_of_operation[current_sat_mode].write_task_number != -1)
    // {
    //     if(check_data_exists() && !self->modes_of_operation[current_sat_mode].Tasks[self->modes_of_operation[current_sat_mode].write_task_number].enabled)
    //         {
    //             // Data directory exists, if there are any files in it, we can start looping through the files and writing them. 
    //             //printf("Cooking");
    //             self->modes_of_operation[current_sat_mode].Tasks[self->modes_of_operation[current_sat_mode].write_task_number].enabled = true; 
    //         }
    //         else
    //         {
    //             self->modes_of_operation[current_sat_mode].Tasks[self->modes_of_operation[current_sat_mode].write_task_number].enabled = false;
    //         }
    // }
    //watchdog check for functions
    for (int i = 0; i < self->modes_of_operation[current_sat_mode].number_mode_tasks; i++) {
        if(self->modes_of_operation[current_sat_mode].Tasks[i].running)
        {
            if(self->modes_of_operation[current_sat_mode].Tasks[i].task_type != DOWNLINK)
            {
                if((now_ms - self->modes_of_operation[current_sat_mode].Tasks[i].last_time_run) > 10000)
                {
                    int result = pthread_cancel(curr_thread_states.threadArray[self->modes_of_operation[current_sat_mode].Tasks[i].thread]);
                    self->modes_of_operation[current_sat_mode].Tasks[i].threads->in_use[self->modes_of_operation[current_sat_mode].Tasks[i].thread] = false;
                    self->modes_of_operation[current_sat_mode].Tasks[i].running = false;
                    change_error_state(&self->modes_of_operation[current_sat_mode].Tasks[i]);
                    printf("   / \\__\n"
                        "  (    @\\___\n"
                        "  /         O\n"
                        " /   (_____/\n"
                        "/_____/   U\n");
                }
            }
            else
            {
                if((now_ms - self->modes_of_operation[current_sat_mode].Tasks[i].last_time_run) > 650000)
                {
                    int result = pthread_cancel(curr_thread_states.threadArray[self->modes_of_operation[current_sat_mode].Tasks[i].thread]);
                    self->modes_of_operation[current_sat_mode].Tasks[i].threads->in_use[self->modes_of_operation[current_sat_mode].Tasks[i].thread] = false;
                    self->modes_of_operation[current_sat_mode].Tasks[i].running = false;
                    change_error_state(&self->modes_of_operation[current_sat_mode].Tasks[i]);
                    printf("   / \\__\n"
                        "  (    @\\___\n"
                        "  /         O\n"
                        " /   (_____/\n"
                        "/_____/   U\n");
                }
            }
        }
    }

    // Check which tasks are ready
    for (int i = 0; i < self->modes_of_operation[current_sat_mode].number_mode_tasks; i++) {
        if (!self->modes_of_operation[current_sat_mode].Tasks[i].released && check_can_run(self->modes_of_operation[current_sat_mode].Tasks[i].error_state)) {
            if ((now_ms - self->modes_of_operation[current_sat_mode].Tasks[i].last_time_run) >= self->modes_of_operation[current_sat_mode].Tasks[i].period) {
                self->modes_of_operation[current_sat_mode].Tasks[i].released = 1;
            }
        }
    }

    // Run released tasks
    //printf("Number of tasks %d\n", self->modes_of_operation[current_sat_mode].number_mode_tasks);
    for (int i = 0; i < self->modes_of_operation[current_sat_mode].number_mode_tasks; i++) {
        if (self->modes_of_operation[current_sat_mode].Tasks[i].released && check_can_run(self->modes_of_operation[current_sat_mode].Tasks[i].error_state) && !self->modes_of_operation[current_sat_mode].Tasks[i].running) {
            int num_threads = sizeof(curr_thread_states.threadArray) / sizeof(curr_thread_states.threadArray[0]);
            int open_thread_num = find_open_thread(num_threads, &curr_thread_states, self->modes_of_operation[current_sat_mode].Tasks[i].task_type);
            
            if (open_thread_num != -1) {
                self->modes_of_operation[current_sat_mode].Tasks[i].last_time_run = now_ms; // absolute ms
                self->modes_of_operation[current_sat_mode].Tasks[i].released = 0;            // reset
                curr_thread_states.in_use[open_thread_num] = true;
                self->modes_of_operation[current_sat_mode].Tasks[i].thread = open_thread_num;
                //printf("%d\n", current_sat_mode);
                //printf("%s\n", self->modes_of_operation[current_sat_mode].Tasks[i].name);
                pthread_create(&curr_thread_states.threadArray[open_thread_num],
                               NULL, run_python_file, &self->modes_of_operation[current_sat_mode].Tasks[i]);
            }
        }
    }
    if(now_ms - modes_last_time_checked_switch > 10000)
    {
        modes_last_time_checked_switch = now_ms;
        check_mode_switch(&current_sat_mode);
    }
    main_heartbeat = BEAT_OK;
}

//check to see if we need to switch modes
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
    // printf("Running Task Name: %s", current_Task->name);
    current_Task->running = true;
    char* command = malloc(64);  // allocate memory for this thread
    snprintf(command, 64, "python3 %s", current_Task->name);
    int ret = system(command);
    //current_Task->released = 1;
    free(command);  // free memory allocated for this thread
    int exitCode = WEXITSTATUS(ret);
    if(exitCode == 1)
    {
        change_error_state(current_Task);
    }
    else if(exitCode == 2)
    {
        current_Task->enabled = false;
    }
    else if (exitCode == 0)
    {
        current_Task->error_state = CLEAR;
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
        case WRITE_DATA:
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

void check_mode_switch(enum currentMode *current_state)
{
    double altitude = get_altitude(current_state);
    if(altitude == 0.0)
    {
        return;
    }
    switch(*current_state)
    {
        case PREFLIGHT: 
            if(altitude > 400) *current_state = FLIGHT;
            break;
        case FLIGHT:
            if(altitude < 375) *current_state = RECOVERY;
            break;
        default:
            *current_state = *current_state;
            break;
    }
}

double get_altitude(enum currentMode *current_state)
{
    FILE *fp = fopen("main_running_data.json", "r");
    if (!fp) {
        printf("Error: Unable to open file\n");
        return 0.0;
    }

    fseek(fp, 0, SEEK_END);
    long fsize = ftell(fp);
    rewind(fp);

    char *buffer = malloc(fsize + 1);
    if (!buffer) {
        fclose(fp);
        printf("Error: Memory allocation failed\n");
        return 0.0;
    }

    fread(buffer, 1, fsize, fp);
    fclose(fp);
    buffer[fsize] = '\0';

    cJSON *json = cJSON_Parse(buffer);
    free(buffer);

    if (json == NULL) {
        const char *error_ptr = cJSON_GetErrorPtr();
        if (error_ptr)
            printf("JSON Parse Error near: %s\n", error_ptr);
        return 0.0;
    }

    cJSON *alt = cJSON_GetObjectItemCaseSensitive(json, "bme_altitude");
    if (!cJSON_IsNumber(alt)) {
        printf("\033[33mWarning: altitude not found or invalid. Defaulting to 0.0\033[0m\n");
        cJSON_Delete(json);
        return 0.0;
    }

    double altitude = alt->valuedouble;
    cJSON_Delete(json);
    return altitude;
}

bool check_can_run(enum error_enum error_state)
{
    switch(error_state){
        case CLEAR:
            return true;
            break;
        case POSSIBLE_ERROR:
            return true;
            break;
        default:
            return false;
            break;
    }
}

void change_error_state(Task *current_task)
{
    char buf[256];
    switch(current_task->error_state){
            case(CLEAR):
                current_task->error_state = POSSIBLE_ERROR;
                printf("Task: %s failed for the first time\r\n", current_task->name);
                snprintf(buf, sizeof(buf),
                        "Task Failure: Task: %s failed for the first time\r\n",
                        current_task->name);

                append_to_log_single_function(buf);
                break;
            case(POSSIBLE_ERROR):
                current_task->error_state = ERRORED;
                current_task->enabled = false;
                printf("Task: %s failed for the second time. Disabling...\r\n", current_task->name);
                snprintf(buf, sizeof(buf),
                        "Task Failure: Task: %s failed for the second time. Disabling...\r\n",
                        current_task->name);

                append_to_log_single_function(buf);
                break;
            default:
                current_task->error_state = ERRORED;
                current_task->enabled = false;
                printf("Task: %s unknown error state. Disabling...\r\n", current_task->name);
                snprintf(buf, sizeof(buf),
                        "Task Failure: Task: %s unknown error state. Disabling...\r\n",
                        current_task->name);

                append_to_log_single_function(buf);
                break;
        }
}





int ensure_directory_exists(const char *path) {
    struct stat st;

    if (stat(path, &st) == -1) {
        // Directory does not exist → attempt to create it
        if (mkdir(path, 0777) == -1) {
            perror("mkdir");
            return -1;
        }
        return 0;
    }

    // Exists but not a directory?
    if (!S_ISDIR(st.st_mode)) {
        fprintf(stderr, "%s exists but is not a directory!\n", path);
        return -1;
    }

    return 0;
}


// Return the highest log number found in the folder (or -1 if none)
int get_latest_log_number(const char *dirpath) {
    if (ensure_directory_exists(dirpath) != 0)
        return -1;

    DIR *dir = opendir(dirpath);
    if (!dir)
        return -1;

    struct dirent *entry;
    int max_num = -1;

    while ((entry = readdir(dir)) != NULL) {
        int num;
        if (sscanf(entry->d_name, "log_%d.txt", &num) == 1) {
            if (num > max_num)
                max_num = num;
        }
    }

    closedir(dir);
    return max_num;
}


// Produce a full filepath to the newest log, creating log_0.txt if needed
void get_latest_log_path(char *buffer, size_t bufsize, const char *dirpath) {
    if (ensure_directory_exists(dirpath) != 0) {
        // fallback path (should never happen)
        snprintf(buffer, bufsize, "log_0.txt");
        return;
    }

    int latest = get_latest_log_number(dirpath);

    if (latest < 0) {
        // No log files → create log_0.txt
        snprintf(buffer, bufsize, "%s/log_0.txt", dirpath);
    } else {
        snprintf(buffer, bufsize, "%s/log_%d.txt", dirpath, latest);
    }
}


// Append a line to a file, creating it if necessary
void append_to_log(const char *filepath, const char *message) {
    FILE *f = fopen(filepath, "a");
    if (!f) {
        perror("fopen");
        return;
    }

    fprintf(f, "%s\n", message);
    fclose(f);
}


// One-call interface: append to newest log file
void append_to_log_single_function(const char *message)
{
    char path[256];

    get_latest_log_path(path, sizeof(path), "logs");

    append_to_log(path, message);
}