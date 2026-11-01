# Gate-OS Dev Container

This container is for Python/API/docs work and defaults to dry-run container behavior. It is not privileged and cannot build or boot-test an ISO.

ISO builds require a reviewed privileged profile in CI, a dedicated Linux VM, or a separately documented environment. Do not add `--privileged`, host sockets, signing keys, or loop-device mounts to this default container.
