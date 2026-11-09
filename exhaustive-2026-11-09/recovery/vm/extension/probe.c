#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "expected.h"

static void failed(const char *what) {
    fprintf(stderr, "PROBE_ERROR %s errno=%d %s\n", what, errno, strerror(errno));
    exit(2);
}

static void checked(int result, const char *what) {
    if (result < 0) failed(what);
    printf("SYSCALL %s result=%d\n", what, result);
}

static void directory_sync(void) {
    int fd = open(".", O_RDONLY | O_DIRECTORY);
    if (fd < 0) failed("open directory");
    checked(fsync(fd), "directory fsync");
    checked(close(fd), "close directory");
}

static void put(const char *name, const char *bytes, size_t size, int durable) {
    int fd = open(name, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd < 0) failed(name);
    size_t done = 0;
    while (done < size) {
        ssize_t result = write(fd, bytes + done, size - done);
        if (result < 0 && errno == EINTR) continue;
        if (result <= 0) failed("write");
        done += (size_t)result;
    }
    printf("WRITE %s bytes=%zu\n", name, done);
    if (durable) checked(fsync(fd), "file fsync");
    checked(close(fd), "close file");
}

static void text(const char *name, const char *bytes) {
    put(name, bytes, strlen(bytes), 1);
}

static char *record(int generation) {
    const char *alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    const char *value = generation ? "new-complete" : "old-complete";
    const char *digest = generation ? NEW_PAYLOAD_SHA : OLD_PAYLOAD_SHA;
    size_t capacity = PAYLOAD_SIZE + 512;
    char *bytes = calloc(capacity, 1);
    if (!bytes) failed("allocate record");
    int prefix = snprintf(bytes, capacity, "{\"generation\":%d,\"value\":\"%s\",\"payload\":\"", generation, value);
    if (prefix < 0 || (size_t)prefix >= 256) failed("record header");
    for (size_t i = 0; i < PAYLOAD_SIZE; ++i)
        bytes[(size_t)prefix + i] = alphabet[(i * 7 + (size_t)generation * 11) % strlen(alphabet)];
    int tail = snprintf(bytes + (size_t)prefix + PAYLOAD_SIZE,
                        capacity - (size_t)prefix - PAYLOAD_SIZE,
                        "\",\"payload_sha256\":\"%s\"}", digest);
    if (tail < 0 || (size_t)tail >= capacity - (size_t)prefix - PAYLOAD_SIZE) failed("record tail");
    return bytes;
}

static void barrier(const char *name) {
    printf("BARRIER %s\n", name);
    fflush(stdout);
    for (;;) pause();
}

static void show(const char *name) {
    int fd = open(name, O_RDONLY);
    if (fd < 0 && errno == ENOENT) {
        printf("ABSENTHEX %s\n", name);
        return;
    }
    if (fd < 0) failed(name);
    size_t capacity = 262144, size = 0;
    unsigned char *bytes = malloc(capacity);
    if (!bytes) failed("allocate read");
    for (;;) {
        if (size == capacity) failed("record too large");
        ssize_t count = read(fd, bytes + size, capacity - size);
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) failed("read record");
        if (!count) break;
        size += (size_t)count;
    }
    checked(close(fd), "close read");
    const char *digits = "0123456789abcdef";
    char *encoded = malloc(size * 2 + 1);
    if (!encoded) failed("allocate encoding");
    for (size_t i = 0; i < size; ++i) {
        encoded[i * 2] = digits[bytes[i] >> 4];
        encoded[i * 2 + 1] = digits[bytes[i] & 15];
    }
    encoded[size * 2] = 0;
    printf("RECORDHEX %s %zu %s\n", name, size, encoded);
    free(encoded);
    free(bytes);
}

int main(int argc, char **argv) {
    setvbuf(stdout, NULL, _IOLBF, 0);
    if (argc != 3 || chdir(argv[2])) return 3;
    if (!strcmp(argv[1], "recover") || !strcmp(argv[1], "recover-clean")) {
        const char *names[] = {"current.json", "next.json", "result-old.json", "result-new.json",
                               "intent.json", "ref.json", "checkpoint.json", "done.json"};
        for (size_t i = 0; i < sizeof(names) / sizeof(names[0]); ++i) show(names[i]);
        if (!strcmp(argv[1], "recover-clean")) return 0;
        barrier("RECOVERED");
    }
    char *end = NULL;
    long stage = strtol(argv[1], &end, 10);
    if (!end || *end || stage < 1 || stage > 12) return 3;
    char *old = record(0), *new = record(1);
    const char *ref0 = "{\"generation\":0,\"operation\":\"extension-0\",\"result_sha256\":\"" OLD_RECORD_SHA "\"}";
    const char *ref1 = "{\"generation\":1,\"operation\":\"extension-1\",\"result_sha256\":\"" NEW_RECORD_SHA "\"}";
    const char *intent = "{\"operation\":\"extension-1\",\"from\":0,\"to\":1,\"result_sha256\":\"" NEW_RECORD_SHA "\"}";
    const char *done = "{\"operation\":\"extension-1\",\"result_sha256\":\"" NEW_RECORD_SHA "\",\"accepted_generation\":1}";
    text("current.json", old);
    text("result-old.json", old);
    text("ref.json", ref0);
    text("checkpoint.json", ref0);
    directory_sync();
    if (stage <= 4) {
        put("next.json", new, strlen(new), stage >= 2);
        if (stage >= 3) checked(rename("next.json", "current.json"), "active rename");
        if (stage >= 4) directory_sync();
    } else if (stage == 5 || stage == 6) {
        put("next.json", new, strlen(new) / 2, 1);
        if (stage == 6) checked(rename("next.json", "current.json"), "deliberately invalid active rename");
        directory_sync();
    } else {
        text("result-new.json", new);
        directory_sync();
        text("intent.json", intent);
        directory_sync();
        if (stage >= 8) {
            text("ref.next", ref1);
            checked(rename("ref.next", "ref.json"), "ref rename");
            directory_sync();
        }
        if (stage >= 9 && stage != 11) {
            text("checkpoint.next", ref1);
            checked(rename("checkpoint.next", "checkpoint.json"), "checkpoint rename");
            directory_sync();
        }
        if (stage >= 10) {
            text("done.next", done);
            checked(rename("done.next", "done.json"), "completion rename");
            directory_sync();
        }
        if (stage == 12) {
            char *start = strstr(new, "\"payload\":\"");
            if (!start) failed("locate checksum corruption control");
            start += strlen("\"payload\":\"");
            *start = *start == 'a' ? 'b' : 'a';
            text("result-new.json", new);
            directory_sync();
        }
    }
    free(old);
    free(new);
    char name[32];
    snprintf(name, sizeof(name), "CUT%ld", stage);
    barrier(name);
}
