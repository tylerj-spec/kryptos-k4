// Restrict candidate kernels after their declared inputs/models are loaded.
// Linux x86-64 only; fail closed on another architecture or missing seccomp.
#include <cerrno>
#include <cstddef>
#include <fcntl.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <sys/prctl.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <vector>

inline int r91_lock_io() {
    std::vector<sock_filter> code = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(seccomp_data, arch)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(seccomp_data, nr)),
        BPF_JUMP(BPF_JMP | BPF_JGE | BPF_K, 0x40000000, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
    };
    const int denied[] = {
        __NR_open, __NR_openat, __NR_openat2, __NR_creat, __NR_open_by_handle_at,
        __NR_name_to_handle_at, __NR_socket, __NR_socketpair, __NR_connect,
        __NR_accept, __NR_accept4, __NR_bind, __NR_listen, __NR_sendto,
        __NR_sendmsg, __NR_sendmmsg, __NR_recvfrom, __NR_recvmsg, __NR_recvmmsg,
        __NR_execve, __NR_execveat, __NR_ptrace, __NR_process_vm_readv,
        __NR_process_vm_writev, __NR_pidfd_getfd, __NR_io_uring_setup,
        __NR_io_uring_enter, __NR_io_uring_register, __NR_mount,
        __NR_unshare, __NR_setns, __NR_bpf
    };
    for (const int nr : denied) {
        code.push_back(BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, static_cast<unsigned int>(nr), 0, 1));
        code.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM));
    }
    code.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW));
    sock_fprog prog{static_cast<unsigned short>(code.size()), code.data()};
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) ||
        syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER, SECCOMP_FILTER_FLAG_TSYNC, &prog)) return 1;
    errno = 0;
    int fd = open("/etc/hostname", O_RDONLY);
    if (fd >= 0 || errno != EPERM) return 2;
    errno = 0;
    fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd >= 0 || errno != EPERM) return 3;
    return 0;
}
