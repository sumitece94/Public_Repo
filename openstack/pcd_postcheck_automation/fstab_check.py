with open('vms-with-fstab') as f:
    affected_vms = [line.split('.')[0] for line in f.readlines() if line.strip()]

with open('vms-for-today') as f:
    today_vms  = [line.split('.')[0] for line in f.readlines() if line.strip()]

for vm in today_vms:
    if vm in affected_vms:
        print(vm)
