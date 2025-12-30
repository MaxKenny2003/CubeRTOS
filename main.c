#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <sched.h>
#include <unistd.h> 


#include "scheduler.h"

volatile enum heartbeat_status main_heartbeat;

int main()
{
    // Main functions
    pthread_t thread1; // Create a thread variable for use later.
    pthread_create(&thread1, NULL, scheduler_thread, NULL);


    sleep(5);   // Sleep for the first loop as we expect to take a while to recieve the heartbeat
    while(1)
    {
        // Busy looping
        switch (main_heartbeat){
            case BEAT_OK:
                main_heartbeat = BEAT_NOT_RECIEVED;
                break;
            case BEAT_NOT_RECIEVED:
                main_heartbeat = BEAT_DEAD;
                break;
            case BEAT_DEAD:
                printf(
                    "  /^ ^\\\n"
                    " / 0 0 \\\n"
                    " V\\ Y /V\n"
                    "  / - \\\n"
                    " /    |\n"
                    "V__) ||\n"
                );
                //system.command("")
            default:
                break;
        }
        sleep(5);
    }
    pthread_join(thread1, NULL);

}
