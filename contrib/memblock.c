/*******************************************************************************
 * Title       : memblock - block OS memory to simulate smaller memory
 * Description : Allocates requested number of 1MiB memory chunks
 * Author      : Bart Sjerps <bart@dirty-cache.com>
 * License     : GPLv3+
 * Disclaimer  : See https://www.gnu.org/licenses/gpl-3.0.txt
 * -----------------------------------------------------------------------------
 * Do not run this in production! It may cause an unstable system!
 * Compile: gcc memblock.c -o $HOME/bin/memblock
 * Usage: memblock <MiB chunks> <sleeptime_sec>
 ******************************************************************************/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/sysinfo.h>

void printfree(struct sysinfo* info) {
    sysinfo(info);
    printf("Free memory: %ld, ",   info->freeram/1048576);
    printf("Shared: %ld, ", info->sharedram/1048576);
    printf("Buffers: %ld\n", info->bufferram/1048576);
}

int main(int argc, char** argv) {
    size_t reserve_mb = 0;
    long int sleeptime = 30;
    struct sysinfo info;

    char* buffer;

    if(argc > 1)
        reserve_mb = atol(argv[1]);

    if(argc > 2)
        sleeptime = atol(argv[2]);

    printfree(&info);

    printf("Attempting to reserve %ld MiB of memory\n", reserve_mb);
    for(int i=0; i<reserve_mb; i++) {
        sysinfo(&info);
        if (info.freeram < 100*1024*1024) {
            printf("%d - Less than 100MB available\n", i);
            break;
        }
        buffer = malloc(1024*1024);
        if(!buffer) {
            printf("%d - Allocation failed\n", i);
            break;
        }
        memset(buffer, 0, 1024*1024);
    }
    printfree(&info);

    printf("Sleeping for %ld seconds\n", sleeptime);
    sleep(sleeptime);
    return 0;
}
