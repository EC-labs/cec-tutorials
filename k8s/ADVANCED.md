**This script includes the steps to deploy a single control-plane node and a variable amount of worker nodes. Please note that this is not an all inclusive approach to deploying a k8s cluster, nor necessarily the best approach. Managing a distributed cluster can be complicated, and may require troubleshooting issues that require familiarity with linux concepts. Make sure you check out the [official reference](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)**

# Installation

Install containerd (we will also install the other docker packages as a pre-caution):
> https://docs.docker.com/engine/install/ubuntu/

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Conigure containerd to use `systemd cgroup` driver. Modify `/etc/containerd/config.toml`:
```
# ...
echo 'disabled_plugins = []

version = 2
[plugins]
  [plugins."io.containerd.grpc.v1.cri"]
   [plugins."io.containerd.grpc.v1.cri".containerd]
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
          runtime_type = "io.containerd.runc.v2"
          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
            SystemdCgroup = true
' | sudo tee /etc/containerd/config.toml
# ...
```

```bash
sudo systemctl restart containerd
```

Install kubeadm, kubelet and kubectl (https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/): 
```bash
sudo apt-get update
# apt-transport-https may be a dummy package; if so, you can skip that package
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
```

```bash
# If the directory `/etc/apt/keyrings` does not exist, it should be created before the curl command, read the note below.
# sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
```

```bash
# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
```

```bash
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

# Initialising kubeadm

Make sure you are running the right commands depending on whether you are deploying a control-plane node or a worker node.

## Control Node 

Initialise kubeadm:
```bash
sudo kubeadm init --pod-network-cidr 10.244.0.0/16 --control-plane-endpoint <vm-public-ip>
```

**Check the output of the previous command to configure kubectl.**

**The output also provides the command you will need to run on the worker nodes you would like to add to the cluster. Make sure you take note of the `kubeadm join ...` command for your cluster.**


```bash
sudo modprobe br_netfilter
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```

## Worker Node 

**Make sure you run the Installation section before running the following commands**

The parameters for the `kubeadm join` command is obtained in the output of running `kubeadm init` on the control-plane node.

Client VMs:
```bash
sudo modprobe br_netfilter
sudo kubeadm join <control-plane-ip>:6443 --token <token> --discovery-token-ca-cert-hash <sha-256>
```
