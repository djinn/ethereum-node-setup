#!/usr/bin/env python3
import os

import aws_cdk as cdk
import os.path as path

from aws_cdk import (
  Stack,
  aws_ec2,
  aws_s3_assets
)
from constructs import Construct


class EthereumOnAWS(Stack):

  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    EC2_KEY_PAIR_NAME = cdk.CfnParameter(self, 'EC2KeyPairName',
      type='String',
      description='Amazon EC2 Instance KeyPair name'
    )

    vpc_name = self.node.try_get_context("vpc_name")
    vpc = aws_ec2.Vpc.from_lookup(self, "ExistingVPC",
      is_default=True,
      vpc_name=vpc_name)

    
    ec2_instance_type = aws_ec2.InstanceType.of(aws_ec2.InstanceClass.STANDARD6_GRAVITON, aws_ec2.InstanceSize.XLARGE2)

    ethereum_host = aws_ec2.SecurityGroup(self, "EthereumSecurityGroup",
      vpc=vpc,
      allow_all_outbound=True,
      description='security group for an ethereum host',
      security_group_name='ethereum-host'
    )
    cdk.Tags.of(ethereum_host).add('Name', 'ethereum-host-sg')

    #TODO: SHOULD restrict IP range allowed to ssh acces
    ethereum_host.add_ingress_rule(peer=aws_ec2.Peer.ipv4("0.0.0.0/0"), connection=aws_ec2.Port.tcp(22), description='SSH access')
    ethereum_host.add_ingress_rule(peer=aws_ec2.Peer.ipv4("0.0.0.0/0"), connection=aws_ec2.Port.tcp(30303), description='Ethereum port')
    ethereum_host.add_ingress_rule(peer=aws_ec2.Peer.ipv4("0.0.0.0/0"), connection=aws_ec2.Port.udp(30303), description='Ethereum port')

    user_data = open(os.path.join(os.path.dirname(__file__), "user-data/install_ethereum.sh"), 'r').read()

    ethereum_host = aws_ec2.Instance(self, "EthereumHost",
      vpc=vpc,
      instance_type=ec2_instance_type,
      machine_image=aws_ec2.MachineImage.latest_amazon_linux(
        generation=aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
        edition=aws_ec2.AmazonLinuxEdition.STANDARD,
        kernel=aws_ec2.AmazonLinuxKernel.KERNEL5_X,
        cpu_type=aws_ec2.AmazonLinuxCpuType.ARM_64,
      ),
      vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PUBLIC),
      #XXX: Create a jenkins in the private subnets
      # vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT),
      security_group=ethereum_host,
      key_name=EC2_KEY_PAIR_NAME.value_as_string,
      block_devices = [
      aws_ec2.BlockDevice(device_name="/dev/sdf", 
            volume=aws_ec2.BlockDeviceVolume.ebs(1000,
                delete_on_termination=True,
                volume_type=aws_ec2.EbsDeviceVolumeType.STANDARD    
            )  
      ),
      ],
      user_data=aws_ec2.UserData.custom(user_data)
        
    )
    cdk.CfnOutput(self, 'EthereumHostId', value=ethereum_host.instance_id, export_name='EthereumHostId')
    #XXX: comments out the follwing line if you create a jenkins in the private subnets
    cdk.CfnOutput(self, 'EthereumHostPublicDNSName', value=ethereum_host.instance_public_dns_name, export_name='EthereumPublicDNSName')


app = cdk.App()
EthereumOnAWS(app, "EthereumOnAWS", env=cdk.Environment(
  account=os.getenv('CDK_DEFAULT_ACCOUNT'),
  region=os.getenv('CDK_DEFAULT_REGION')))

app.synth()