#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static void failed(const char *what) {
    fprintf(stderr, "PROBE_ERROR %s errno=%d %s\n", what, errno, strerror(errno));
    exit(2);
}

static void checked(int result, const char *what) {
    if (result < 0) failed(what);
    printf("SYSCALL %s result=%d\n", what, result);
}

static void directory_sync(void) {
    int fd = open("/state", O_DIRECTORY | O_RDONLY);
    if (fd < 0) failed("open directory");
    checked(fsync(fd), "directory fsync");
    checked(close(fd), "close directory");
}

static void put(const char *path, const char *bytes, int durable) {
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd < 0) failed(path);
    size_t size = strlen(bytes), done = 0;
    while (done < size) {
        ssize_t result = write(fd, bytes + done, size - done);
        if (result < 0 && errno == EINTR) continue;
        if (result <= 0) failed("write");
        done += (size_t)result;
    }
    printf("WRITE %s bytes=%zu\n", path, done);
    if (durable) checked(fsync(fd), "file fsync");
    checked(close(fd), "close file");
}

static void barrier(const char *name) {
    printf("BARRIER %s\n", name);
    fflush(stdout);
    for (;;) pause();
}

static void show(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0 && errno == ENOENT) {
        printf("RECORD %s ABSENT\n", path);
        return;
    }
    if (fd < 0) failed(path);
    char data[4096];
    ssize_t count = read(fd, data, sizeof(data) - 1);
    if (count < 0) failed("read");
    if ((size_t)count == sizeof(data) - 1) {
        errno = EFBIG;
        failed("record too large");
    }
    data[count] = 0;
    printf("RECORD %s %s\n", path, data);
    checked(close(fd), "close read");
}

int main(int argc, char **argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    if (argc != 2) return 3;
    const char *zero = "{\"generation\":0,\"value\":\"old-complete\"}";
    const char *one = "{\"generation\":1,\"value\":\"new-complete\"}";
    if (!strcmp(argv[1], "recover")) {
        show("/state/current.json");
        show("/state/next.json");
        show("/state/intent.json");
        show("/state/ref.json");
        show("/state/checkpoint.json");
        barrier("RECOVERED");
    }
    char *end = NULL;
    long stage = strtol(argv[1], &end, 10);
    if (!end || *end || stage < 1 || stage > 8) return 3;
    put("/state/current.json", zero, 1);
    put("/state/ref.json", zero, 1);
    put("/state/checkpoint.json", zero, 1);
    directory_sync();
    if (stage <= 5) {
        put("/state/next.json", one, stage >= 2);
        if (stage >= 3) checked(rename("/state/next.json", "/state/current.json"), "rename");
        if (stage >= 4) directory_sync();
        if (stage == 5) checked(syncfs(open("/state", O_RDONLY | O_DIRECTORY)), "syncfs control");
    } else {
        put("/state/intent.json", "{\"from\":0,\"to\":1,\"value\":\"new-complete\"}", 1);
        directory_sync();
        if (stage >= 7) {
            put("/state/ref.next", one, 1);
            checked(rename("/state/ref.next", "/state/ref.json"), "ref rename");
            directory_sync();
        }
        if (stage >= 8) {
            put("/state/checkpoint.next", one, 1);
            checked(rename("/state/checkpoint.next", "/state/checkpoint.json"), "checkpoint rename");
            directory_sync();
        }
    }
    char name[32];
    snprintf(name, sizeof(name), "CUT%ld", stage);
    barrier(name);
}
