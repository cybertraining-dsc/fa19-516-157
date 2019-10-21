import azure as azure
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.v2017_03_01.models import NetworkSecurityGroup
from azure.mgmt.network.v2017_03_01.models import SecurityRule
from azure.mgmt.compute.models import DiskCreateOption
SUBSCRIPTION_ID = '1b552345-85f2-4a12-97af-c67f27be817b'
GROUP_NAME = 'mySecondResourceGroup'
LOCATION = 'eastus'
VM_NAME = 'myVM'
VNET = 'myVnet'
SUBNET = 'mySubnet'
SUBNETRANGE = '10.0.0.0/24'


def get_credentials():
    credentials = ServicePrincipalCredentials(
        client_id='e1409c33-f364-4cd9-9981-fbd270058389',
        secret=':ydi7/pc9]XZekc/lkBaBDs55hAPOD:O',
        tenant='1113be34-aed1-4d00-ab4b-cdd02510be91'
    )

    return credentials


def create_resource_group(resource_group_client):
    resource_group_params = {'location': LOCATION}
    resource_group_result = resource_group_client.resource_groups.create_or_update(
        GROUP_NAME,
        resource_group_params
    )


def create_availability_set(compute_client):
    avset_params = {
        'location': LOCATION,
        'sku': {'name': 'Aligned'},
        'platform_fault_domain_count': 3
    }
    availability_set_result = compute_client.availability_sets.create_or_update(
        GROUP_NAME,
        'myAVSet',
        avset_params
    )


def create_public_ip_address(network_client):
    public_ip_addess_params = {
        'location': LOCATION,
        'public_ip_allocation_method': 'Dynamic'
    }
    creation_result = network_client.public_ip_addresses.create_or_update(
        GROUP_NAME,
        'myIPAddress',
        public_ip_addess_params
    )

    return creation_result.result()


def create_vnet(network_client):
    vnet_params = {
        'location': LOCATION,
        'address_space': {
            'address_prefixes': ['10.0.0.0/16']
        }
    }
    creation_result = network_client.virtual_networks.create_or_update(
        GROUP_NAME,
        'myVNet',
        vnet_params
    )
    return creation_result.result()


def create_subnet(network_client):
    subnet_params = {
        'address_prefix': '10.0.0.0/24'
    }
    creation_result = network_client.subnets.create_or_update(
        GROUP_NAME,
        'myVNet',
        'mySubnet',
        subnet_params
    )

    return creation_result.result()


# create network interface
def create_nic(network_client):
    subnet_info = network_client.subnets.get(
        GROUP_NAME,
        'myVNet',
        'mySubnet'
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        GROUP_NAME,
        'myIPAddress'
    )
    nic_params = {
        'location': LOCATION,
        'ip_configurations': [{
            'name': 'myIPConfig',
            'public_ip_address': publicIPAddress,
            'subnet': {
                'id': subnet_info.id
            }
        }]
    }
    creation_result = network_client.network_interfaces.create_or_update(
        GROUP_NAME,
        'myNic',
        nic_params
    )

    return creation_result.result()


"""
#Network Srcurity Group section
def create_network_security_group(network_client):
    params_create = azure.mgmt.network.models.NetworkSecurityGroup(
        location=LOCATION,
        security_rules=[
            azure.mgmt.network.models.SecurityRule(
                name='rdprule',
                access=azure.mgmt.network.models.SecurityRuleAccess.allow,
                description='test security rule',
                destination_address_prefix='*',
                destination_port_range='3389',
                direction=azure.mgmt.network.models.SecurityRuleDirection.inbound,
                priority=500,
                protocol=azure.mgmt.network.models.SecurityRuleProtocol.tcp,
                source_address_prefix='*',
                source_port_range='*',
            ),
        ],
    )

    result_create_NSG = network_client.network_security_groups.create_or_update(
        GROUP_NAME,
        'nsg-vm',
        params_create,
    )

    return result_create_NSG.result()


def attach_network_security_group(network_client, creation_result_nsg):
    params_create = azure.mgmt.network.models.Subnet(
        network_security_group=creation_result_nsg,
        address_prefix=SUBNETRANGE,
    )

    result_create = network_client.subnets.create_or_update(
        GROUP_NAME,
        VNET,
        SUBNET,
        params_create,
    )

    return result_create.result()
"""


# create virtual machine
def create_vm(network_client, compute_client):
    nic = network_client.network_interfaces.get(
        GROUP_NAME,
        'myNic'
    )
    avset = compute_client.availability_sets.get(
        GROUP_NAME,
        'myAVSet'
    )
    vm_parameters = {
        'location': LOCATION,
        'os_profile': {
            'computer_name': VM_NAME,
            'admin_username': 'azureuser',
            'admin_password': 'Azure12345678'
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': 'MicrosoftWindowsServer',
                'offer': 'WindowsServer',
                'sku': '2012-R2-Datacenter',
                'version': 'latest'
            }
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic.id
            }]
        },
        'availability_set': {
            'id': avset.id
        }
    }
    creation_result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME,
        VM_NAME,
        vm_parameters
    )

    return creation_result.result()


# Main function calls
if __name__ == "__main__":
    # Gather credentials
    credentials = get_credentials()

    # Stage necessary client
    resource_group_client = ResourceManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )
    network_client = NetworkManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )
    compute_client = ComputeManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )
    # create resource group
    create_resource_group(resource_group_client)
    input('Resource group created. Press enter to continue...')
    # create availability set
    create_availability_set(compute_client)
    print("------------------------------------------------------")
    input('Availability set created. Press enter to continue...')
    # create public ip for access
    creation_result = create_public_ip_address(network_client)
    print("------------------------------------------------------")
    print(creation_result)
    input('Press enter to continue...')
    # create virtual network
    creation_result = create_vnet(network_client)
    print("------------------------------------------------------")
    print(creation_result)
    input('Press enter to continue...')
    # create subnet
    creation_result = create_subnet(network_client)
    print("------------------------------------------------------")
    print(creation_result)
    input('Press enter to continue...')
    # create network interface
    creation_result = create_nic(network_client)
    print("------------------------------------------------------")
    print(creation_result)
    input('Press enter to continue...')
    """
    # Security group section
    creation_result_nsg = create_network_security_group(network_client)
    print("------------------------------------------------------")
    print(creation_result_nsg)
    input('Press enter to continue...')
    # Add Security Group
    creation_result = attach_network_security_group(network_client, creation_result_nsg)
    print("------------------------------------------------------")
    print(creation_result)
    input('Press enter to continue...')"""
    parameters = NetworkSecurityGroup()
    parameters.location = LOCATION
    parameters.security_rules = [SecurityRule(name='rdprule',
                                              access='Allow',
                                              description='test security rule',
                                              destination_address_prefix='*',
                                              destination_port_range='3389',
                                              direction='inbound',
                                              priority=500,
                                              protocol='Tcp',
                                              source_address_prefix='*',
                                              source_port_range='*', )]
    """[SecurityRule('Tcp', '*', '*', 'Allow', 'Inbound', description='Allow RDP port 3389',
                                              source_port_range='*', destination_port_range='3389', priority=100,
                                              name='RDP01')]"""
    network_client.network_security_groups.create_or_update(
        GROUP_NAME, "test-nsg", parameters)
    # actual crate virtual machine, above method calls prepare resource
    creation_result = create_vm(network_client, compute_client)
    print("------------------------------------------------------")
    print(creation_result)
    input('Press enter to continue...')